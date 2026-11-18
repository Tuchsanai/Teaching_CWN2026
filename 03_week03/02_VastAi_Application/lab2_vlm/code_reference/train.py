"""LAB 2 · Fine-tune Qwen3-VL-2B-Instruct with LoRA to read receipts and answer JSON.

- LoRA rank 8, alpha 16 on the Linear layers of the language model only
  (q/k/v/o_proj + gate/up/down_proj); the vision encoder (model.visual) and lm_head stay frozen.
- 800 training receipts, 2 epochs, lr 2e-4, seed 0, batch 1 x gradient accumulation 4.
- Same PROMPT as receipt_data.py; loss only on the answer JSON tokens.
- Validation loss on all 100 validation receipts before training and after every epoch.
- Resumable: a checkpoint (adapter + optimizer + scheduler + history) is written every
  --ckpt-every optimizer steps; rerunning the same command continues from it.

Usage (on the rented machine):
    python train.py --data /workspace/lab2/data --out /workspace/lab2/out
Outputs in --out: adapter/ · loss_curve.png · train_info.json · history.json · train.log
"""
import argparse
import json
import math
import os
import random
import shutil
import sys
import time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from receipt_data import PROMPT, answer_text, load_split  # noqa: E402

MODEL = "Qwen/Qwen3-VL-2B-Instruct"
LORA_TARGET = r"model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|mlp\.(gate|up|down)_proj)"


def log(msg, path):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(path, "a") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------- data -> tensors
def encode(processor, row):
    """One receipt -> input tensors + labels (-100 everywhere except the answer JSON)."""
    from PIL import Image
    img = Image.open(row["image"]).convert("RGB")
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    answer = answer_text(row["answer"]) + "<|im_end|>"
    p = processor(text=[prompt], images=[img], return_tensors="pt")
    full = processor(text=[prompt + answer], images=[img], return_tensors="pt")
    n_prompt = p["input_ids"].shape[1]
    labels = full["input_ids"].clone()
    labels[:, :n_prompt] = -100
    full["labels"] = labels
    return full


def to_dev(batch, dev):
    return {k: (v.to(dev) if torch.is_tensor(v) else v) for k, v in batch.items()}


@torch.no_grad()
def val_loss(model, processor, rows, dev):
    """Token-weighted mean loss over the answer tokens of every validation receipt."""
    model.eval()
    tot, n = 0.0, 0
    for r in rows:
        b = to_dev(encode(processor, r), dev)
        k = int((b["labels"][:, 1:] != -100).sum())
        out = model(**b)
        tot += out.loss.item() * k
        n += k
    model.train()
    return tot / n


# ---------------------------------------------------------------- checkpoint
def save_ckpt(path, model, opt, sched, state):
    tmp = path + ".tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    model.save_pretrained(f"{tmp}/adapter")
    torch.save({"opt": opt.state_dict(), "sched": sched.state_dict(),
                "cuda_rng": torch.cuda.get_rng_state(), "cpu_rng": torch.get_rng_state()},
               f"{tmp}/optim.pt")
    with open(f"{tmp}/state.json", "w") as f:
        json.dump(state, f, indent=1)
    shutil.rmtree(path, ignore_errors=True)
    os.replace(tmp, path)          # atomic swap: a crash never leaves a half-written ckpt


def plot(history, epochs, steps_per_epoch, save):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tr = history["train"]
    xs = [t["step"] / steps_per_epoch for t in tr]
    ys = [t["loss"] for t in tr]
    w = 10
    smooth = [sum(ys[max(0, i - w + 1):i + 1]) / len(ys[max(0, i - w + 1):i + 1]) for i in range(len(ys))]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, ys, color="#9db8e0", lw=0.8, label="Train loss (per optimizer step)")
    ax.plot(xs, smooth, color="#1f5fbf", lw=2, label=f"Train loss (moving avg, {w} steps)")
    vx = [v["epoch"] for v in history["val"]]
    vy = [v["loss"] for v in history["val"]]
    ax.plot(vx, vy, "o-", color="#d9480f", lw=2, ms=8, label="Validation loss (100 receipts)")
    for x, y in zip(vx, vy):
        ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 10),
                    ha="center", color="#d9480f", fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Cross-entropy loss (answer JSON tokens only)")
    ax.set_title("Qwen3-VL-2B-Instruct + LoRA (r=8, alpha=16) on CORD-v2 receipts")
    ax.set_xticks(range(epochs + 1))
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(save, dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/workspace/lab2/data")
    ap.add_argument("--out", default="/workspace/lab2/out")
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--rank", type=int, default=8)
    ap.add_argument("--alpha", type=int, default=16)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--warmup", type=int, default=10, help="warmup optimizer steps")
    ap.add_argument("--ckpt-every", type=int, default=25, help="optimizer steps between checkpoints")
    a = ap.parse_args()

    from peft import LoraConfig, PeftModel, get_peft_model
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration, get_linear_schedule_with_warmup

    os.makedirs(a.out, exist_ok=True)
    logf, ckpt = f"{a.out}/train.log", f"{a.out}/ckpt"
    random.seed(a.seed)
    torch.manual_seed(a.seed)
    dev = "cuda"

    train_rows = load_split(a.data, "train")
    val_rows = load_split(a.data, "val")
    steps_per_epoch = math.ceil(len(train_rows) / a.grad_accum)
    total_steps = steps_per_epoch * a.epochs

    processor = AutoProcessor.from_pretrained(MODEL)
    model = Qwen3VLForConditionalGeneration.from_pretrained(MODEL, dtype=torch.bfloat16,
                                                            attn_implementation="sdpa").to(dev)
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    n_total = sum(p.numel() for p in model.parameters())

    resume = os.path.exists(f"{ckpt}/state.json")
    if resume:
        model = PeftModel.from_pretrained(model, f"{ckpt}/adapter", is_trainable=True)
    else:
        model = get_peft_model(model, LoraConfig(r=a.rank, lora_alpha=a.alpha, lora_dropout=0.05,
                                                 target_modules=LORA_TARGET, task_type="CAUSAL_LM"))
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert not any("visual" in n for n, p in model.named_parameters() if p.requires_grad)

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=a.lr, weight_decay=0.0)
    sched = get_linear_schedule_with_warmup(opt, a.warmup, total_steps)

    if resume:
        st = torch.load(f"{ckpt}/optim.pt", weights_only=False)
        opt.load_state_dict(st["opt"])
        sched.load_state_dict(st["sched"])
        torch.cuda.set_rng_state(st["cuda_rng"])
        torch.set_rng_state(st["cpu_rng"])
        state = json.load(open(f"{ckpt}/state.json"))
        log(f"RESUME from optimizer step {state['step']}/{total_steps}", logf)
    else:
        state = {"step": 0, "elapsed_s": 0.0, "peak_vram_gb": 0.0,
                 "history": {"train": [], "val": []}}
        log(f"model params {n_total:,} · trainable LoRA {n_train:,} ({100 * n_train / n_total:.3f}%)", logf)
        log(f"train {len(train_rows)} · val {len(val_rows)} · {steps_per_epoch} steps/epoch · "
            f"{total_steps} optimizer steps", logf)

    t0 = time.time() - state["elapsed_s"]
    torch.cuda.reset_peak_memory_stats()

    def peak():
        state["peak_vram_gb"] = max(state["peak_vram_gb"], torch.cuda.max_memory_allocated() / 1e9)

    if not state["history"]["val"]:
        v = val_loss(model, processor, val_rows, dev)
        state["history"]["val"].append({"epoch": 0, "step": 0, "loss": v})
        log(f"VAL epoch 0 (before training): {v:.4f}", logf)

    model.train()
    while state["step"] < total_steps:
        epoch = state["step"] // steps_per_epoch               # 0-based
        order = list(range(len(train_rows)))
        random.Random(a.seed + epoch).shuffle(order)           # same order after a resume
        start = (state["step"] % steps_per_epoch) * a.grad_accum
        for s in range(start, len(order), a.grad_accum):
            chunk = order[s:s + a.grad_accum]
            batches = [encode(processor, train_rows[i]) for i in chunk]
            ntok = [int((b["labels"][:, 1:] != -100).sum()) for b in batches]
            loss_sum = 0.0
            for b, k in zip(batches, ntok):                    # token-weighted over the 4 receipts
                out = model(**to_dev(b, dev))
                (out.loss * k / sum(ntok)).backward()
                loss_sum += out.loss.item() * k
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            state["step"] += 1
            loss = loss_sum / sum(ntok)
            state["history"]["train"].append({"step": state["step"], "loss": loss,
                                              "lr": sched.get_last_lr()[0]})
            peak()
            state["elapsed_s"] = time.time() - t0
            if state["step"] % 10 == 0:
                recent = [t["loss"] for t in state["history"]["train"][-10:]]
                eta = state["elapsed_s"] / state["step"] * (total_steps - state["step"])
                log(f"epoch {epoch + 1}/{a.epochs} step {state['step']}/{total_steps} "
                    f"loss {sum(recent) / len(recent):.4f} lr {sched.get_last_lr()[0]:.2e} "
                    f"peak {state['peak_vram_gb']:.1f} GB · elapsed {state['elapsed_s'] / 60:.1f} min "
                    f"· eta {eta / 60:.1f} min", logf)
            end_of_epoch = state["step"] % steps_per_epoch == 0
            if end_of_epoch:
                v = val_loss(model, processor, val_rows, dev)
                state["history"]["val"].append({"epoch": epoch + 1, "step": state["step"], "loss": v})
                peak()
                state["elapsed_s"] = time.time() - t0
                log(f"VAL epoch {epoch + 1}: {v:.4f}", logf)
            if end_of_epoch or state["step"] % a.ckpt_every == 0:
                save_ckpt(ckpt, model, opt, sched, state)
            if end_of_epoch:
                break

    # ---------------------------------------------------------------- final outputs
    adapter_dir = f"{a.out}/adapter"
    shutil.rmtree(adapter_dir, ignore_errors=True)
    model.save_pretrained(adapter_dir)
    size_mb = sum(os.path.getsize(os.path.join(adapter_dir, f)) for f in os.listdir(adapter_dir)) / 1e6
    with open(f"{a.out}/history.json", "w") as f:
        json.dump(state["history"], f, indent=1)
    plot(state["history"], a.epochs, steps_per_epoch, f"{a.out}/loss_curve.png")
    info = {
        "base_model": MODEL,
        "lora": {"rank": a.rank, "alpha": a.alpha, "dropout": 0.05,
                 "target": "language model Linear layers (q/k/v/o_proj, gate/up/down_proj); vision frozen"},
        "train_receipts": len(train_rows), "val_receipts": len(val_rows),
        "epochs": a.epochs, "lr": a.lr, "seed": a.seed, "batch_size": 1,
        "grad_accum": a.grad_accum, "optimizer_steps": total_steps, "warmup_steps": a.warmup,
        "trainable_params": n_train, "total_params": n_total,
        "trainable_pct": round(100 * n_train / n_total, 4),
        "val_loss": {f"epoch_{v['epoch']}": round(v["loss"], 4) for v in state["history"]["val"]},
        "train_time_min": round(state["elapsed_s"] / 60, 1),
        "peak_vram_gb": round(state["peak_vram_gb"], 2),
        "adapter_size_mb": round(size_mb, 1),
        "gpu": torch.cuda.get_device_name(0),
    }
    with open(f"{a.out}/train_info.json", "w") as f:
        json.dump(info, f, indent=2)
    log("DONE " + json.dumps(info), logf)


if __name__ == "__main__":
    main()
