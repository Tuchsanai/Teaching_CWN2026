"""รวมผลเป็น metrics.json และวาดภาพจากข้อมูลจริง:
compare.png (Base vs Fine-tuned), loss.png (loss ระหว่างเทรน), example_1..4.png (ใบเสร็จ + คำตอบ 3 แบบ)"""
import argparse
import json
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from receipt_common import item_pairs, norm_name, to_int

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data")
ap.add_argument("--out", default="out")
args = ap.parse_args()
OUT = args.out
BLUE, ORANGE, RED, GREEN, GRAY = "#4878a8", "#e07b39", "#c62828", "#2e7d32", "#555555"

base = json.load(open(f"{OUT}/metrics_base.json"))
ft = json.load(open(f"{OUT}/metrics_ft.json"))
log = json.load(open(f"{OUT}/train_log.json"))
metrics = {
    "dataset": "naver-clova-ix/cord-v2", "n_train": log["n_train"], "n_val": log["n_val"], "n_test": base["n"],
    "model": log["model"], "base": base, "finetuned": ft,
    "train": {k: log[k] for k in ("train_seconds", "peak_vram_gb", "gpu", "trainable_params", "total_params")}
    | {"epochs": log["args"]["epochs"], "batch": log["args"]["batch"] * log["args"]["accum"], "lr": log["args"]["lr"],
       "lora_rank": log["args"]["rank"], "val_loss": log["val"]},
}
json.dump(metrics, open(f"{OUT}/metrics.json", "w"), indent=1)

# ---------- กราฟแท่ง Base vs Fine-tuned ----------
names = [("json_ok_pct", "Valid JSON (%)"), ("total_exact_pct", "Total exact match (%)"), ("item_f1_pct", "Item F1: name+price (%)")]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [3, 1]})
x = range(len(names))
for off, m, color, label in ((-0.2, base, BLUE, "Base"), (0.2, ft, ORANGE, "Fine-tuned (LoRA)")):
    vals = [m[k] for k, _ in names]
    bars = axes[0].bar([i + off for i in x], vals, 0.38, color=color, label=label)
    axes[0].bar_label(bars, fmt="%.1f", fontsize=10)
axes[0].set_xticks(list(x), [n for _, n in names])
axes[0].set_ylim(0, 125)
axes[0].set_title(f"CORD-v2 Test Set ({base['n']} receipts)")
axes[0].legend(loc="upper center", ncol=2, frameon=False)
bars = axes[1].bar(["Base", "Fine-tuned"], [base["sec_per_receipt"], ft["sec_per_receipt"]], color=[BLUE, ORANGE])
axes[1].bar_label(bars, fmt="%.2f s")
axes[1].set_title("Seconds per receipt")
axes[1].set_ylim(0, max(base["sec_per_receipt"], ft["sec_per_receipt"]) * 1.25)
for a in axes:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/compare.png", dpi=150)

# ---------- loss ----------
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot([s["step"] for s in log["steps"]], [s["loss"] for s in log["steps"]], color=BLUE, lw=1, alpha=0.8, label="Training loss (per step)")
ax.plot([v["step"] for v in log["val"]], [v["val_loss"] for v in log["val"]], "o-", color=ORANGE, lw=2, label="Validation loss (per epoch)")
for v in log["val"]:
    ax.annotate(f"{v['val_loss']:.3f}", (v["step"], v["val_loss"]), textcoords="offset points", xytext=(6, 8), color=ORANGE)
ax.set_xlabel("Step")
ax.set_ylabel("Loss")
ax.set_yscale("log")
ax.set_title(f"LoRA fine-tuning: {log['n_train']} receipts, {log['args']['epochs']} epochs, {log['train_seconds']/60:.1f} min")
ax.legend()
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/loss.png", dpi=150)


# ---------- ตัวอย่างรายใบ ----------
def load(tag):
    return {r["id"]: r for r in (json.loads(x) for x in open(f"{OUT}/pred_{tag}.jsonl", encoding="utf-8"))}


def f1(s):
    return 2 * s["tp"] / (s["n_pred"] + s["n_gt"]) if s["n_pred"] + s["n_gt"] else 1.0


def lines(obj, target, raw=""):
    """คืน [(ข้อความ, สี)] · สีแดง = ต่างจากเฉลย"""
    if obj is None:
        return [("JSON parse failed", RED)] + [(raw[i : i + 34], GRAY) for i in range(0, min(len(raw), 170), 34)]
    left = Counter(item_pairs(target))
    out = []
    for it in obj.get("items") or []:
        if not isinstance(it, dict):
            continue
        k = (norm_name(it.get("name")), to_int(it.get("price")))
        ok = left[k] > 0
        left[k] -= ok
        out.append((f"{str(it.get('name'))[:22]:<22} {str(it.get('price')):>8}", "#111111" if obj is target else (GREEN if ok else RED)))
    miss = sum(v for v in left.values() if v > 0)
    if miss and obj is not target:
        out.append((f"({miss} item(s) missing or wrong)", RED))
    for k in ("subtotal", "tax", "total"):
        ok = to_int(obj.get(k)) == target[k]
        out.append((f"{k:<22} {str(obj.get(k)):>8}", GRAY if obj is target else (GREEN if ok else RED)))
    return out


pb, pf = load("base"), load("ft")
small = [i for i in pb if len(pb[i]["target"]["items"]) <= 8]
gain = sorted(small, key=lambda i: (f1(pf[i]["score"]) + pf[i]["score"]["total_ok"]) - (f1(pb[i]["score"]) + pb[i]["score"]["total_ok"]), reverse=True)
picks = gain[:3]
still_wrong = [i for i in small if i not in picks and (f1(pf[i]["score"]) < 1 or not pf[i]["score"]["total_ok"])]
picks += still_wrong[:1] or gain[3:4]  # ใบที่ 4 = ใบที่ Fine-tuned ยังผิด (ถ้ามี)
for n, i in enumerate(picks, 1):
    t = pb[i]["target"]
    fig, axes = plt.subplots(1, 4, figsize=(17, 6.5), gridspec_kw={"width_ratios": [1.1, 1, 1, 1]})
    axes[0].imshow(Image.open(f"{args.data}/{pb[i]['image']}"))
    axes[0].set_title(i)
    cols = (("Ground truth", lines(t, t)), ("Base", lines(pb[i]["pred"], t, pb[i]["raw"])), ("Fine-tuned (LoRA)", lines(pf[i]["pred"], t, pf[i]["raw"])))
    for ax, (title, ls) in zip(axes[1:], cols):
        ax.set_title(title, fontweight="bold")
        for j, (txt, color) in enumerate(ls[:24]):
            ax.text(0.0, 0.97 - j * 0.04, txt, color=color, family="monospace", fontsize=9, transform=ax.transAxes, va="top")
    for ax in axes:
        ax.axis("off")
    fig.suptitle("green = matches ground truth · red = differs", fontsize=10, color=GRAY, y=0.03)
    fig.tight_layout()
    fig.savefig(f"{OUT}/example_{n}.png", dpi=130)
    plt.close(fig)
json.dump(picks, open(f"{OUT}/example_ids.json", "w"))
print(json.dumps({"base": base, "finetuned": ft}, ensure_ascii=False, indent=1))
