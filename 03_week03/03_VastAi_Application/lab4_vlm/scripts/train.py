"""Fine-tune VLM ด้วย LoRA ให้ตอบใบเสร็จเป็น JSON · เทรนเฉพาะ adapter (น้ำหนักเดิมของโมเดลไม่เปลี่ยน)
ผล: <out>/adapter/ (LoRA adapter) และ <out>/train_log.json (loss ทุก step, validation loss ทุก epoch)"""
import argparse
import json
import math
import random
import time

import torch
from peft import LoraConfig, get_peft_model
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

from receipt_common import MODEL_ID, PROMPT, target_text

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data")
ap.add_argument("--out", default="out")
ap.add_argument("--epochs", type=int, default=2)
ap.add_argument("--batch", type=int, default=1, help="จำนวนใบต่อ 1 รอบคำนวณ (ใบเสร็จ 1 ใบใช้ VRAM ราว 10 GB ตอนเทรน)")
ap.add_argument("--accum", type=int, default=4, help="สะสม gradient กี่รอบก่อนปรับน้ำหนัก (batch จริง = batch x accum)")
ap.add_argument("--lr", type=float, default=2e-4)
ap.add_argument("--rank", type=int, default=8)
ap.add_argument("--limit", type=int, default=0, help="ใช้กี่ใบแรก (0 = ทั้งหมด) สำหรับลองสั้นๆ")
args = ap.parse_args()
torch.manual_seed(0)
random.seed(0)

processor = AutoProcessor.from_pretrained(MODEL_ID)
processor.tokenizer.padding_side = "right"
model = AutoModelForImageTextToText.from_pretrained(MODEL_ID, dtype=torch.bfloat16, device_map={"": 0})

# LoRA เฉพาะชั้น Linear ของส่วนภาษา (ส่วนมองภาพใช้ชื่อชั้นอื่น จึงไม่ถูกแตะ)
lora = LoraConfig(
    r=args.rank, lora_alpha=2 * args.rank, lora_dropout=0.05, task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)
model = get_peft_model(model, lora)
n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
n_all = sum(p.numel() for p in model.parameters())
print(f"พารามิเตอร์ที่เทรน {n_train/1e6:.2f} M จากทั้งหมด {n_all/1e6:.0f} M ({100*n_train/n_all:.2f}%)", flush=True)


def load(split):
    rows = [json.loads(x) for x in open(f"{args.data}/{split}.jsonl", encoding="utf-8")]
    return rows[: args.limit] if args.limit else rows


train_rows, val_rows = load("train"), load("validation")
messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
prompt_text = processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
im_start = processor.tokenizer.convert_tokens_to_ids("<|im_start|>")
n_head = len(processor.tokenizer("<|im_start|>assistant\n", add_special_tokens=False).input_ids)


def make_batch(rows):
    images = [Image.open(f"{args.data}/{r['image']}").convert("RGB") for r in rows]
    texts = [prompt_text + target_text(r["target"]) + "<|im_end|>" for r in rows]
    batch = processor(text=texts, images=images, padding=True, return_tensors="pt")
    labels = batch["input_ids"].clone()
    labels[batch["attention_mask"] == 0] = -100
    for i in range(len(rows)):  # คิด loss เฉพาะคำตอบ (หลัง "<|im_start|>assistant\n" ตัวสุดท้าย)
        start = (batch["input_ids"][i] == im_start).nonzero()[-1].item() + n_head
        labels[i, :start] = -100
    return batch.to(model.device), labels.to(model.device)


core = model.get_base_model()  # โมเดลเดิมที่มี LoRA แทรกอยู่แล้ว


def loss_of(rows):
    """loss เฉพาะตำแหน่งคำตอบ · คำนวณ logits เฉพาะตำแหน่งนั้น (ไม่ทำทั้งลำดับ) เพื่อประหยัด VRAM"""
    batch, labels = make_batch(rows)
    hidden = core.model(**batch).last_hidden_state[:, :-1]
    target = labels[:, 1:]
    keep = target != -100
    return torch.nn.functional.cross_entropy(core.lm_head(hidden[keep]).float(), target[keep])


@torch.no_grad()
def val_loss():
    model.eval()
    total, n = 0.0, 0
    for i in range(0, len(val_rows), args.batch):
        rows = val_rows[i : i + args.batch]
        with torch.autocast("cuda", dtype=torch.bfloat16):
            total += loss_of(rows).item() * len(rows)
        n += len(rows)
    model.train()
    return total / n


micro_per_epoch = math.ceil(len(train_rows) / args.batch)
total_steps = math.ceil(micro_per_epoch / args.accum) * args.epochs  # จำนวนครั้งที่ปรับน้ำหนัก
warmup = max(1, int(0.05 * total_steps))
opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr, weight_decay=0.0)
sched = torch.optim.lr_scheduler.LambdaLR(
    opt, lambda s: (s + 1) / warmup if s < warmup else 0.5 * (1 + math.cos(math.pi * (s - warmup) / max(1, total_steps - warmup)))
)

log = {"model": MODEL_ID, "args": vars(args), "trainable_params": n_train, "total_params": n_all,
       "n_train": len(train_rows), "n_val": len(val_rows), "steps": [], "val": []}
log["val"].append({"epoch": 0, "step": 0, "val_loss": round(val_loss(), 4)})
print(f"ก่อนเทรน: validation loss {log['val'][0]['val_loss']}", flush=True)

model.train()
t0, step = time.time(), 0
for epoch in range(1, args.epochs + 1):
    order = list(range(len(train_rows)))
    random.shuffle(order)
    micro = [order[i : i + args.batch] for i in range(0, len(order), args.batch)]
    acc = 0.0
    for k, idx in enumerate(micro, 1):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            loss = loss_of([train_rows[j] for j in idx])
        (loss / args.accum).backward()
        acc += loss.item() / args.accum
        if k % args.accum and k != len(micro):
            continue
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        opt.zero_grad(set_to_none=True)
        step += 1
        log["steps"].append({"step": step, "epoch": epoch, "loss": round(acc, 4)})
        if step % 10 == 0 or step == total_steps:
            print(f"epoch {epoch} step {step}/{total_steps} loss {acc:.4f} · {time.time()-t0:.0f}s", flush=True)
        acc = 0.0
    v = round(val_loss(), 4)
    log["val"].append({"epoch": epoch, "step": step, "val_loss": v})
    print(f"จบ epoch {epoch}: validation loss {v}", flush=True)

log["train_seconds"] = round(time.time() - t0, 1)
log["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)
log["gpu"] = torch.cuda.get_device_name(0)
model.save_pretrained(f"{args.out}/adapter")
json.dump(log, open(f"{args.out}/train_log.json", "w"), indent=1)
print(f"เสร็จ: {log['train_seconds']} วินาที · VRAM สูงสุด {log['peak_vram_gb']} GB · adapter อยู่ที่ {args.out}/adapter", flush=True)
