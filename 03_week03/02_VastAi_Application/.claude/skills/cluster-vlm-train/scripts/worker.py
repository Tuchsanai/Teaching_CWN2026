"""LAB 5 · One replica (= one full copy of Qwen3-VL-8B + LoRA) of the cluster trainer.

    Approach A: the model is split over 2 GPUs (layers ~half/half), Gradient Checkpointing OFF
    Approach B: the model lives on 1 GPU, Gradient Checkpointing ON

Each replica gets its own, non-overlapping share of the Training Set (shuffled with seed 0,
replica r takes receipts r, r+world, r+2*world, ...). It feeds 1 receipt at a time,
accumulates the gradient over --accum receipts, sends the LoRA gradient as bf16 to the
coordinator, receives the average of all replicas and applies it with AdamW (lr 2e-4).
Loss is computed on the answer JSON only (prompt + image tokens are masked with -100).

Logged for every update: compute time · communication time (send / wait / receive) ·
gradient MB sent · peak VRAM per GPU · mean GPU util per GPU. At the end: checksum
(sha256) of the LoRA weights, sent to the coordinator and written to the log.

Usage (Node 1):
    python worker.py --mode A --gpus 0,1 --accum 8 --coord 127.0.0.1:9000 --out runs/A_eb8
    python worker.py --mode B --gpus 0   --accum 4 --coord 127.0.0.1:9000 --out runs/B_eb8
"""
import argparse
import hashlib
import json
import os
import random
import socket
import sys
import threading
import time


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["A", "B"], required=True)
    ap.add_argument("--gpus", required=True, help="physical GPU ids, A: '0,1'  B: '0' or '1'")
    ap.add_argument("--accum", type=int, required=True, help="receipts accumulated per update")
    ap.add_argument("--coord", default="127.0.0.1:9000")
    ap.add_argument("--secret-file", default="/workspace/lab5/cluster_secret")
    ap.add_argument("--model", default="/workspace/models/Qwen3-VL-8B-Instruct")
    ap.add_argument("--data", default="/workspace/lab5/data")
    ap.add_argument("--split", type=int, default=19, help="A: language layers on the first GPU (step 3)")
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--train-limit", type=int, default=None, help="use only the first N shuffled receipts")
    ap.add_argument("--save-adapter", default=None, help="rank 0 saves the LoRA adapter here")
    ap.add_argument("--out", required=True, help="run folder for worker_r<rank>.json")
    return ap.parse_args()


a = parse()
os.environ["CUDA_VISIBLE_DEVICES"] = a.gpus          # before importing torch
PHYS = [int(x) for x in a.gpus.split(",")]

import torch  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coordinator import recv_msg, send_msg  # noqa: E402
from receipt_data import PROMPT, answer_text, load_split  # noqa: E402

GiB = 1024 ** 3


# ---------------------------------------------------------------- GPU util sampler
class UtilSampler(threading.Thread):
    """Samples utilization.gpu of this replica's physical GPUs every 100 ms."""

    def __init__(self, phys):
        super().__init__(daemon=True)
        import pynvml
        pynvml.nvmlInit()
        self.nv = pynvml
        self.h = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in phys]
        self.samples = []                           # (t, [util per gpu])
        self.lock = threading.Lock()

    def run(self):
        while True:
            u = [self.nv.nvmlDeviceGetUtilizationRates(h).gpu for h in self.h]
            with self.lock:
                self.samples.append((time.time(), u))
                if len(self.samples) > 20000:
                    self.samples = self.samples[-10000:]
            time.sleep(0.1)

    def mean(self, t0, t1):
        with self.lock:
            win = [u for t, u in self.samples if t0 <= t <= t1]
        if not win:
            return [None] * len(self.h)
        return [round(sum(x[i] for x in win) / len(win), 1) for i in range(len(self.h))]


# ---------------------------------------------------------------- model + data
def build_model():
    from peft import LoraConfig, get_peft_model
    from transformers import AutoConfig, AutoModelForImageTextToText, AutoProcessor

    processor = AutoProcessor.from_pretrained(a.model)
    if a.mode == "A":
        n = AutoConfig.from_pretrained(a.model).text_config.num_hidden_layers
        lm = "model.language_model"
        dm = {"model.visual": 0, f"{lm}.embed_tokens": 0, f"{lm}.rotary_emb": 0, f"{lm}.norm": 1, "lm_head": 1}
        dm.update({f"{lm}.layers.{i}": (0 if i < a.split else 1) for i in range(n)})
    else:
        dm = {"": 0}
    model = AutoModelForImageTextToText.from_pretrained(a.model, dtype=torch.bfloat16, device_map=dm)
    model.config.use_cache = False
    torch.manual_seed(a.seed)                       # identical LoRA init on every replica
    lora = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
                      target_modules=r".*language_model.*\.(q_proj|v_proj)")
    model = get_peft_model(model, lora)
    if a.mode == "B":
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    model.train()
    return processor, model


def encode(processor, row):
    """One receipt -> model inputs; labels only on the answer JSON (+ the <|im_end|> that ends it)."""
    from PIL import Image
    img = Image.open(row["image"]).convert("RGB")
    user = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
    full = user + [{"role": "assistant", "content": [{"type": "text", "text": answer_text(row["answer"])}]}]
    p_txt = processor.apply_chat_template(user, tokenize=False, add_generation_prompt=True)
    f_txt = processor.apply_chat_template(full, tokenize=False).rstrip("\n")
    enc = processor(text=[f_txt], images=[img], return_tensors="pt")
    n_prompt = processor(text=[p_txt], images=[img], return_tensors="pt")["input_ids"].shape[1]
    labels = enc["input_ids"].clone()
    labels[:, :n_prompt] = -100
    enc["labels"] = labels
    return enc


def checksum(params):
    h = hashlib.sha256()
    for name, p in params:
        h.update(name.encode())
        h.update(p.detach().float().cpu().numpy().tobytes())
    return h.hexdigest()


# ---------------------------------------------------------------- main
def main():
    with open(a.secret_file) as f:
        secret = f.read().strip()
    t_load0 = time.time()
    processor, model = build_model()
    params = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    sizes = [p.numel() for _, p in params]
    ngpu = len(PHYS)
    load_s = round(time.time() - t_load0, 1)
    opt = torch.optim.AdamW([p for _, p in params], lr=a.lr)
    sampler = UtilSampler(PHYS)
    sampler.start()

    host, port = a.coord.rsplit(":", 1)
    sock = socket.create_connection((host, int(port)), timeout=1800)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    send_msg(sock, {"type": "hello", "secret": secret, "host": socket.gethostname(),
                    "mode": a.mode, "gpus": PHYS, "accum": a.accum})
    start, _ = recv_msg(sock)
    if start["type"] != "start":
        raise SystemExit("coordinator rejected this replica")
    rank, world, steps = start["rank"], start["world"], start["steps"]
    print(f"[r{rank}] joined: world {world} · accum {a.accum} · effective batch {start['effective_batch']}", flush=True)

    rows = load_split(a.data, "train")
    order = list(range(len(rows)))
    random.Random(a.seed).shuffle(order)
    if a.train_limit:
        order = order[:a.train_limit]
    shard = order[rank::world]                       # non-overlapping share of this replica
    need = steps * a.accum
    if need > len(shard):
        print(f"[r{rank}] note: {need} receipts needed, shard has {len(shard)} -> wraps around", flush=True)
    seen = []

    log = []
    t_train0 = time.time()
    for s in range(steps):
        for d in range(ngpu):
            torch.cuda.reset_peak_memory_stats(d)
        t0 = time.time()
        loss_sum = 0.0
        ids = []
        for k in range(a.accum):
            row = rows[shard[(s * a.accum + k) % len(shard)]]
            ids.append(row["id"])
            enc = {kk: v.to("cuda:0") for kk, v in encode(processor, row).items()}
            out = model(**enc)
            (out.loss / a.accum).backward()
            loss_sum += out.loss.item()
            del out, enc
        for d in range(ngpu):
            torch.cuda.synchronize(d)
        t1 = time.time()                             # ---- compute done

        flat = torch.cat([p.grad.reshape(-1).to("cpu", torch.bfloat16) for _, p in params])
        payload = flat.view(torch.int16).numpy().tobytes()
        send_msg(sock, {"type": "grad", "step": s, "loss": loss_sum / a.accum}, payload)
        t2 = time.time()                             # ---- sent
        sock.recv(4, socket.MSG_PEEK)                # blocks until the average starts arriving
        t3 = time.time()                             # ---- waited
        h, avg = recv_msg(sock)
        t4 = time.time()                             # ---- received

        g = torch.frombuffer(bytearray(avg), dtype=torch.bfloat16)
        for (name, p), chunk in zip(params, torch.split(g, sizes)):
            p.grad = chunk.view_as(p).to(p.device, p.dtype)
        opt.step()
        opt.zero_grad(set_to_none=True)
        for d in range(ngpu):
            torch.cuda.synchronize(d)
        t5 = time.time()                             # ---- applied

        rec = {"step": s + 1, "receipts": ids, "loss": round(loss_sum / a.accum, 5),
               "compute_s": round(t1 - t0, 3),
               "comm_s": round(t4 - t1, 3), "send_s": round(t2 - t1, 3),
               "wait_s": round(t3 - t2, 3), "recv_s": round(t4 - t3, 3),
               "update_s": round(t5 - t4, 3), "step_s": round(t5 - t0, 3),
               "grad_mb_sent": round(len(payload) / 1e6, 3),
               "peak_vram_gib": [round(torch.cuda.max_memory_allocated(d) / GiB, 2) for d in range(ngpu)],
               "gpu_util_pct": sampler.mean(t0, t5)}
        log.append(rec)
        seen += ids
        print(f"[r{rank}] update {s + 1}/{steps} loss {rec['loss']:.4f} compute {rec['compute_s']:.2f}s "
              f"comm {rec['comm_s']:.2f}s (send {rec['send_s']:.2f} wait {rec['wait_s']:.2f} "
              f"recv {rec['recv_s']:.2f}) util {rec['gpu_util_pct']} vram {rec['peak_vram_gib']}", flush=True)
    t_train1 = time.time()

    csum = checksum(params)
    if a.save_adapter and rank == 0:
        model.save_pretrained(a.save_adapter)
    send_msg(sock, {"type": "done", "rank": rank, "checksum": csum})
    recv_msg(sock)
    sock.close()

    res = {"rank": rank, "world": world, "mode": a.mode, "physical_gpus": PHYS,
           "gpu_name": torch.cuda.get_device_name(0),
           "gradient_checkpointing": a.mode == "B", "accum": a.accum,
           "effective_batch": start["effective_batch"], "steps": steps,
           "lr": a.lr, "seed": a.seed, "split_layers_gpu0": a.split if a.mode == "A" else None,
           "trainable_params": sum(sizes), "load_s": load_s,
           "train_wall_s": round(t_train1 - t_train0, 2),
           "unique_receipts": len(set(seen)), "receipts_used": len(seen),
           "lora_checksum_sha256": csum, "per_step": log}
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, f"worker_r{rank}.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(f"[r{rank}] done · checksum {csum[:16]}", flush=True)


if __name__ == "__main__":
    main()
