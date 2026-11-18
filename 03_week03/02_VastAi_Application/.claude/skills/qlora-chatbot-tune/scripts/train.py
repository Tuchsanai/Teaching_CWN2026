"""QLoRA fine-tuning of Qwen3-4B-Instruct-2507 on the Sabaijai receptionist dataset.

- Base model loaded in 4-bit (NF4); only LoRA adapters (r=8) are trained.
- LoRA on every Linear layer of attention (q,k,v,o) and MLP (gate,up,down).
- Loss only on assistant tokens. Validation loss before training and every 20 steps;
  the adapter with the lowest validation loss is kept.
- Resumable: re-running the same command continues from the last checkpoint.

Usage:  python train.py --data_dir ../data --out_dir ../results [--epochs 3] [--model Qwen/Qwen3-4B-Instruct-2507]
"""
import argparse, json, os, time, glob
import torch
from torch.utils.data import Dataset
from transformers import (AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig,
                          Trainer, TrainingArguments, TrainerCallback, set_seed)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"


def build_example(tok, messages):
    """Tokenize one conversation; labels = -100 everywhere except assistant replies."""
    full = tok.apply_chat_template(messages, tokenize=False)
    spans = []  # character spans of assistant replies (incl. the closing <|im_end|>)
    for i, m in enumerate(messages):
        if m["role"] != "assistant":
            continue
        start = len(tok.apply_chat_template(messages[:i], tokenize=False, add_generation_prompt=True))
        end = len(tok.apply_chat_template(messages[:i + 1], tokenize=False))
        assert full.startswith(tok.apply_chat_template(messages[:i + 1], tokenize=False))
        spans.append((start, end))
    enc = tok(full, return_offsets_mapping=True, add_special_tokens=False)
    labels = []
    for tid, (s, e) in zip(enc["input_ids"], enc["offset_mapping"]):
        inside = any(s >= a and s < b for a, b in spans)
        labels.append(tid if inside else -100)
    return {"input_ids": enc["input_ids"], "labels": labels}


class ChatDataset(Dataset):
    def __init__(self, path, tok):
        rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        self.items = [build_example(tok, r["messages"]) for r in rows]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]


def collate(batch, pad_id):
    n = max(len(b["input_ids"]) for b in batch)
    ids = torch.full((len(batch), n), pad_id, dtype=torch.long)
    lab = torch.full((len(batch), n), -100, dtype=torch.long)
    att = torch.zeros((len(batch), n), dtype=torch.long)
    for k, b in enumerate(batch):
        L = len(b["input_ids"])
        ids[k, :L] = torch.tensor(b["input_ids"])
        lab[k, :L] = torch.tensor(b["labels"])
        att[k, :L] = 1
    return {"input_ids": ids, "labels": lab, "attention_mask": att}


class ProgressCallback(TrainerCallback):
    """Writes progress.json (step, losses) so progress can be checked from outside."""
    def __init__(self, path):
        self.path = path

    def on_log(self, args, state, control, logs=None, **kw):
        tr = [h for h in state.log_history if "loss" in h]
        ev = [h for h in state.log_history if "eval_loss" in h]
        json.dump({"step": state.global_step, "max_steps": state.max_steps,
                   "epoch": round(state.epoch or 0, 3),
                   "train_loss": tr[-1]["loss"] if tr else None,
                   "val_loss": ev[-1]["eval_loss"] if ev else None,
                   "best_val_loss": state.best_metric, "time": time.strftime("%H:%M:%S")},
                  open(self.path, "w"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", default="../data")
    ap.add_argument("--out_dir", default="../results")
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--eval_steps", type=int, default=20)
    ap.add_argument("--model", default=MODEL_ID, help="โมเดลตั้งต้นบน Hugging Face (ค่าเริ่มต้น Qwen/Qwen3-4B-Instruct-2507)")
    a = ap.parse_args()

    set_seed(0)
    os.makedirs(a.out_dir, exist_ok=True)
    ckpt_dir = os.path.join(a.out_dir, "checkpoints")
    state_path = os.path.join(a.out_dir, "run_state.json")  # survives restarts
    run_state = json.load(open(state_path)) if os.path.exists(state_path) else {}

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    train_ds = ChatDataset(os.path.join(a.data_dir, "train.jsonl"), tok)
    val_ds = ChatDataset(os.path.join(a.data_dir, "val.jsonl"), tok)
    print(f"train={len(train_ds)} val={len(val_ds)} "
          f"max_len={max(len(x['input_ids']) for x in train_ds.items)}", flush=True)

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(a.model, quantization_config=bnb,
                                                 dtype=torch.bfloat16, device_map={"": 0})
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    lora = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"])
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=ckpt_dir, seed=0, data_seed=0,
        num_train_epochs=a.epochs, learning_rate=a.lr,
        per_device_train_batch_size=1, gradient_accumulation_steps=8, per_device_eval_batch_size=1,
        bf16=True, gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        logging_steps=1, eval_strategy="steps", eval_steps=a.eval_steps,
        save_strategy="steps", save_steps=a.eval_steps, save_total_limit=2,
        load_best_model_at_end=True, metric_for_best_model="eval_loss", greater_is_better=False,
        report_to="none", remove_unused_columns=False, dataloader_num_workers=0)

    trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=val_ds,
                      data_collator=lambda b: collate(b, tok.pad_token_id),
                      callbacks=[ProgressCallback(os.path.join(a.out_dir, "progress.json"))])

    # Validation loss before training (computed once, kept across restarts)
    if "val_loss_before" not in run_state:
        run_state["val_loss_before"] = trainer.evaluate()["eval_loss"]
        json.dump(run_state, open(state_path, "w"))
    print(f"val_loss_before={run_state['val_loss_before']:.4f}", flush=True)

    resume = bool(glob.glob(os.path.join(ckpt_dir, "checkpoint-*")))
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    trainer.train(resume_from_checkpoint=resume)
    run_state["train_seconds"] = run_state.get("train_seconds", 0) + (time.time() - t0)
    peak = torch.cuda.max_memory_reserved() / 2**30
    run_state["peak_vram_gb"] = max(run_state.get("peak_vram_gb", 0), peak)
    json.dump(run_state, open(state_path, "w"))

    # Save best adapter (load_best_model_at_end already restored it)
    adapter_dir = os.path.join(a.out_dir, "adapter")
    trainer.model.save_pretrained(adapter_dir)
    tok.save_pretrained(adapter_dir)
    adapter_mb = sum(os.path.getsize(os.path.join(adapter_dir, f))
                     for f in os.listdir(adapter_dir) if f.startswith("adapter_")) / 2**20

    hist = trainer.state.log_history
    train_hist = [{"step": h["step"], "loss": h["loss"]} for h in hist if "loss" in h]
    val_hist = [{"step": 0, "val_loss": run_state["val_loss_before"]}] + \
               [{"step": h["step"], "val_loss": h["eval_loss"]} for h in hist if "eval_loss" in h]
    best = min(val_hist[1:], key=lambda h: h["val_loss"])
    log = {
        "model": a.model, "gpu": torch.cuda.get_device_name(0),
        "config": {"quant": "4-bit NF4 (double quant), bf16 compute", "lora_r": 8, "lora_alpha": 16,
                   "lora_dropout": 0.05, "target_modules": lora.target_modules and sorted(lora.target_modules),
                   "epochs": a.epochs, "lr": a.lr, "batch_size": 1, "grad_accum": 8, "seed": 0,
                   "loss_on": "assistant tokens only", "eval_steps": a.eval_steps},
        "n_train": len(train_ds), "n_val": len(val_ds), "total_steps": trainer.state.global_step,
        "val_loss_before": run_state["val_loss_before"],
        "best_step": best["step"], "best_val_loss": best["val_loss"],
        "final_val_loss": val_hist[-1]["val_loss"],
        "train_seconds": round(run_state["train_seconds"], 1),
        "train_minutes": round(run_state["train_seconds"] / 60, 2),
        "peak_vram_gb": round(run_state["peak_vram_gb"], 2),
        "adapter_mb": round(adapter_mb, 2),
        "train_loss": train_hist, "val_loss": val_hist,
    }
    json.dump(log, open(os.path.join(a.out_dir, "train_log.json"), "w"), indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot([h["step"] for h in train_hist], [h["loss"] for h in train_hist],
            color="#9db4d6", lw=1, label="Training loss (per step)")
    ax.plot([h["step"] for h in val_hist], [h["val_loss"] for h in val_hist],
            "o-", color="#d1495b", lw=2, label="Validation loss")
    ax.scatter([best["step"]], [best["val_loss"]], s=160, facecolors="none", edgecolors="black",
               lw=2, zorder=5, label=f"Best adapter (step {best['step']}, {best['val_loss']:.3f})")
    ax.set_xlabel("Optimizer step"); ax.set_ylabel("Cross-entropy loss (assistant tokens)")
    ax.set_title(f"QLoRA fine-tuning: {a.model.split('/')[-1]} (r=8)")
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(a.out_dir, "loss_curve.png"), dpi=150)
    print("DONE", json.dumps({k: v for k, v in log.items() if k not in ("train_loss", "val_loss")}),
          flush=True)


if __name__ == "__main__":
    main()
