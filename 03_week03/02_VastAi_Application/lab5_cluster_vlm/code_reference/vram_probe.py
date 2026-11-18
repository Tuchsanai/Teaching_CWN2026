"""LAB 5 · How far can a 24 GB GPU go when training Qwen3-VL-8B-Instruct with LoRA?

Loads the model in bfloat16, adds LoRA rank 8 / alpha 16 on q_proj and v_proj of the
language model only (vision encoder untouched, fully frozen), then trains 10 steps on the
Training-Set receipt with the longest answer JSON (the worst case for VRAM), image long
side 1280 px, prompt from receipt_data.PROMPT. Every batch row is that same receipt.

Records: VRAM of the weights per GPU · peak VRAM per GPU · seconds per step · OOM error.

Usage (one case per process, so an OOM never pollutes the next case):
    python vram_probe.py --gpus 1 --batch 1 --gc off --case A-1gpu --out vram_probe.json
    python vram_probe.py --gpus 2 --batch 1 --gc off --split 18 --case A-2gpu --out ...
    python vram_probe.py --gpus 1 --batch 2 --gc on  --case B-b2 --out vram_probe.json
--split N = number of language-model layers on GPU 0 when --gpus 2 (the vision encoder and
embeddings live on GPU 0, the remaining layers + final norm + lm_head on GPU 1).
"""
import argparse
import json
import os
import sys
import time
import traceback

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from receipt_data import PROMPT, answer_text, load_split  # noqa: E402

GiB = 1024 ** 3


def gib(x):
    return round(x / GiB, 2)


def longest_receipt(data_dir):
    rows = load_split(data_dir, "train")
    return max(rows, key=lambda r: len(answer_text(r["answer"])))


def build_device_map(n_layers, split):
    lm = "model.language_model"
    dm = {"model.visual": 0, f"{lm}.embed_tokens": 0, f"{lm}.rotary_emb": 0}
    for i in range(n_layers):
        dm[f"{lm}.layers.{i}"] = 0 if i < split else 1
    dm[f"{lm}.norm"] = 1
    dm["lm_head"] = 1
    return dm


def make_batch(processor, row, batch):
    from PIL import Image
    img = Image.open(row["image"]).convert("RGB")
    user = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
    full = user + [{"role": "assistant", "content": [{"type": "text", "text": answer_text(row["answer"])}]}]
    prompt_txt = processor.apply_chat_template(user, tokenize=False, add_generation_prompt=True)
    full_txt = processor.apply_chat_template(full, tokenize=False)
    enc = processor(text=[full_txt] * batch, images=[img] * batch, return_tensors="pt")
    n_prompt = processor(text=[prompt_txt], images=[img], return_tensors="pt")["input_ids"].shape[1]
    labels = enc["input_ids"].clone()
    labels[:, :n_prompt] = -100                         # learn the answer only
    enc["labels"] = labels
    info = {"image_size": list(img.size), "seq_len": int(enc["input_ids"].shape[1]),
            "prompt_tokens": int(n_prompt), "answer_tokens": int(enc["input_ids"].shape[1] - n_prompt),
            "image_tokens": int((enc["input_ids"][0] == processor.tokenizer.convert_tokens_to_ids("<|image_pad|>")).sum())}
    return enc, info


def run(a):
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForImageTextToText, AutoProcessor

    ngpu = a.gpus
    res = {"case": a.case, "gpus": ngpu, "batch": a.batch, "gradient_checkpointing": a.gc == "on",
           "steps": a.steps, "dtype": "bfloat16", "lora": {"r": 8, "alpha": 16, "targets": "language q_proj,v_proj"},
           "gpu_name": torch.cuda.get_device_name(0),
           "gpu_total_gib": gib(torch.cuda.get_device_properties(0).total_memory)}
    row = longest_receipt(a.data)
    res["receipt"] = row["id"]
    res["answer_chars"] = len(answer_text(row["answer"]))
    res["answer_items"] = len(row["answer"]["items"])

    processor = AutoProcessor.from_pretrained(a.model)
    if ngpu == 1:
        device_map = {"": 0}
    else:
        from transformers import AutoConfig
        n_layers = AutoConfig.from_pretrained(a.model).text_config.num_hidden_layers
        split = a.split if a.split is not None else n_layers // 2
        device_map = build_device_map(n_layers, split)
        res["layers_gpu0"], res["layers_gpu1"] = split, n_layers - split
    model = AutoModelForImageTextToText.from_pretrained(a.model, dtype=torch.bfloat16, device_map=device_map)
    model.config.use_cache = False

    lora = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
                      target_modules=r".*language_model.*\.(q_proj|v_proj)")
    model = get_peft_model(model, lora)
    if a.gc == "on":
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    res["trainable_params"], res["total_params"] = trainable, total
    res["lora_on_vision"] = any(("visual" in n and p.requires_grad) for n, p in model.named_parameters())
    for d in range(ngpu):
        torch.cuda.synchronize(d)
    res["weights_gib_per_gpu"] = [gib(torch.cuda.memory_allocated(d)) for d in range(ngpu)]
    res["weights_gib_total"] = round(sum(res["weights_gib_per_gpu"]), 2)

    enc, info = make_batch(processor, row, a.batch)
    res.update(info)
    first = 0
    enc = {k: v.to(first) for k, v in enc.items()}
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
    model.train()
    for d in range(ngpu):
        torch.cuda.reset_peak_memory_stats(d)

    times, losses = [], []
    try:
        for step in range(a.steps):
            for d in range(ngpu):
                torch.cuda.synchronize(d)
            t0 = time.time()
            out = model(**enc)
            out.loss.backward()
            opt.step()
            opt.zero_grad(set_to_none=True)
            for d in range(ngpu):
                torch.cuda.synchronize(d)
            times.append(round(time.time() - t0, 3))
            losses.append(round(out.loss.item(), 4))
            print(f"step {step + 1}/{a.steps} {times[-1]:.2f}s loss {losses[-1]:.4f}", flush=True)
            del out
        res["result"] = "ok"
        res["error"] = None
    except torch.OutOfMemoryError as e:
        res["result"] = "oom"
        res["error"] = str(e).strip().splitlines()[0]
        res["failed_at_step"] = len(times) + 1
    res["peak_gib_per_gpu"] = [gib(torch.cuda.max_memory_allocated(d)) for d in range(ngpu)]
    res["peak_reserved_gib_per_gpu"] = [gib(torch.cuda.max_memory_reserved(d)) for d in range(ngpu)]
    res["step_times_s"], res["losses"] = times, losses
    warm = times[1:] if len(times) > 1 else times
    res["sec_per_step"] = round(sum(warm) / len(warm), 3) if warm else None
    res["samples_per_sec"] = round(a.batch / res["sec_per_step"], 3) if warm else None
    return res


def save(path, res):
    data = []
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
    data = [r for r in data if r.get("case") != res["case"]] + [res]
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpus", type=int, choices=[1, 2], default=1)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--gc", choices=["on", "off"], default="off")
    ap.add_argument("--split", type=int, default=None, help="LM layers on GPU 0 when --gpus 2")
    ap.add_argument("--steps", type=int, default=10)
    ap.add_argument("--case", required=True)
    ap.add_argument("--model", default="/workspace/models/Qwen3-VL-8B-Instruct")
    ap.add_argument("--data", default="/workspace/lab5/data")
    ap.add_argument("--out", default="/workspace/lab5/vram_probe.json")
    a = ap.parse_args()
    try:
        r = run(a)
    except torch.OutOfMemoryError as e:                # OOM while loading weights / building batch
        r = {"case": a.case, "gpus": a.gpus, "batch": a.batch, "gradient_checkpointing": a.gc == "on",
             "result": "oom", "error": str(e).strip().splitlines()[0],
             "peak_gib_per_gpu": [gib(torch.cuda.max_memory_allocated(d)) for d in range(a.gpus)]}
    except Exception as e:
        traceback.print_exc()
        r = {"case": a.case, "gpus": a.gpus, "batch": a.batch, "gradient_checkpointing": a.gc == "on",
             "result": "error", "error": f"{type(e).__name__}: {e}"}
    save(a.out, r)
    print(json.dumps({k: r.get(k) for k in ("case", "result", "weights_gib_per_gpu", "peak_gib_per_gpu",
                                             "sec_per_step", "error")}, ensure_ascii=False), flush=True)
