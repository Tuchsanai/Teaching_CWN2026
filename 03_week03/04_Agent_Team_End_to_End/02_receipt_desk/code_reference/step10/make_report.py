#!/usr/bin/env python3
"""Collect step-10 results on the GPU machine into ./out (no model weights): speed table, plots, samples."""
import json, shutil, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

S = Path("/workspace/e2e_receipt/step10"); OUT = S / "out"; OUT.mkdir(exist_ok=True)
PRICE_HR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.4142   # whole 2x RTX 3090 machine
TOTAL_GPUS = 2

# ---------- training speed (NFR-08 style) ----------
speed = []
for g in (1, 2):
    meta = json.load(open(S / f"runs/g{g}/receiptdesk_train_meta.json"))
    wall = json.load(open(S / f"runs/wall_g{g}.json"))
    t = meta["metrics"]["train_runtime"]
    speed.append({"gpus": g, "epoch_s": round(t, 1), "wall_incl_load_s": round(wall["wall_s"], 1),
                  "train_loss": round(meta["metrics"]["train_loss"], 4),
                  "samples_per_s": round(400 / t, 2), "grad_accum": meta["gradient_accumulation_steps"],
                  "usd_per_epoch_gpu_share": round(t / 3600 * PRICE_HR * g / TOTAL_GPUS, 5),
                  "usd_per_epoch_whole_machine": round(t / 3600 * PRICE_HR, 5)})
s1 = speed[0]["epoch_s"]
for r in speed:
    r["speedup"] = round(s1 / r["epoch_s"], 3); r["efficiency"] = round(r["speedup"] / r["gpus"], 3)
json.dump({"price_per_hour_usd_machine": PRICE_HR, "rows": speed}, open(OUT / "train_speed.json", "w"), indent=1)

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].bar(["1 GPU", "2 GPUs"], [r["epoch_s"] for r in speed], color=["#7a8ca3", "#2a6fdb"])
for i, r in enumerate(speed):
    ax[0].text(i, r["epoch_s"], f'{r["epoch_s"]} s\n×{r["speedup"]}', ha="center", va="bottom")
ax[0].set_ylabel("seconds per epoch (400 receipts)"); ax[0].set_title("Time per epoch")
ax[0].set_ylim(0, s1 * 1.25)
for g, c in ((1, "#7a8ca3"), (2, "#2a6fdb")):
    st = json.load(open(S / f"runs/g{g}/checkpoint-25/trainer_state.json"))
    h = [x for x in st["log_history"] if "loss" in x]
    ax[1].plot([x["step"] for x in h], [x["loss"] for x in h], "o-", color=c, label=f"{g} GPU")
ax[1].set_xlabel("optimizer step (global batch 16)"); ax[1].set_ylabel("training loss")
ax[1].set_title("Training loss (same seed, same steps)"); ax[1].legend()
fig.tight_layout(); fig.savefig(OUT / "train_speed_loss.png", dpi=130)

# ---------- evaluation ----------
reports = {}
for name in ("base_val", "ft_val", "base_test", "ft_test"):
    d = S / "eval" / name
    if (d / "report.json").exists():
        dst = OUT / "eval" / name; dst.mkdir(parents=True, exist_ok=True)
        for f in ("report.json", "report.md", "predictions.jsonl", "wall.json"):
            if (d / f).exists():
                shutil.copy(d / f, dst / f)
        reports[name] = json.load(open(d / "report.json"))

if "base_test" in reports and "ft_test" in reports:
    ids = ["M1", "M2", "M3", "M4", "M6", "M7"]
    get = lambda r: {m["id"]: m["value"] or 0 for m in r["metrics"]}
    b, f = get(reports["base_test"]), get(reports["ft_test"])
    fig, ax = plt.subplots(figsize=(9, 4)); x = range(len(ids))
    ax.bar([i - 0.2 for i in x], [b[k] for k in ids], 0.4, label="before (base)", color="#b0b8c4")
    ax.bar([i + 0.2 for i in x], [f[k] for k in ids], 0.4, label="after (LoRA, 2 GPU run)", color="#2a6fdb")
    for i, k in enumerate(ids):
        ax.text(i - 0.2, b[k], f"{b[k]:.1f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + 0.2, f[k], f"{f[k]:.1f}", ha="center", va="bottom", fontsize=8)
    thr = {"M1": 95, "M2": 1, "M3": 80, "M4": 20, "M6": 99}
    for i, k in enumerate(ids):
        if k in thr:
            ax.hlines(thr[k], i - 0.45, i + 0.45, colors="red", linestyles="--")
    ax.set_xticks(list(x)); ax.set_xticklabels(ids); ax.set_ylabel("%"); ax.set_ylim(0, 112)
    ax.set_title("Test Set (95 readable + 20 unreadable): before vs after · red = NFR-01 threshold")
    ax.legend(loc="upper right"); fig.tight_layout(); fig.savefig(OUT / "metrics_before_after.png", dpi=130)

if "ft_val" in reports:
    sw = reports["ft_val"]["threshold_sweep"]
    fig, ax = plt.subplots(figsize=(7, 4)); t = [float(s["threshold"]) for s in sw]
    for k, c in (("M2", "#d33"), ("M3", "#2a6fdb"), ("M4", "#e69f00")):
        ax.plot(t, [s[k] or 0 for s in sw], "o-", color=c, label=k)
    ax.axvline(0.90, color="gray", ls=":"); ax.set_xlabel("confidence threshold (BR-04 = 0.90)")
    ax.set_ylabel("%"); ax.set_title("Validation set (98): threshold sweep of the LoRA model"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "threshold_sweep_val.png", dpi=130)

# ---------- sample answers ----------
def preds(name):
    p = S / "eval" / name / "predictions.jsonl"
    return {json.loads(l)["id"]: json.loads(l) for l in open(p)} if p.exists() else {}
pb, pf = preds("base_test"), preds("ft_test")
gold = {json.loads(l)["id"]: json.loads(l) for l in open(S / "data/test.jsonl")}
gold.update({json.loads(l)["id"]: json.loads(l) for l in open(S / "data/unreadable.jsonl")})
pick = [i for i in gold if i.startswith("te")][20:26] + ["un00", "un15"]
samples = []
for rid in pick:
    g = gold[rid]
    samples.append({"id": rid, "gold_total": g.get("total", "unreadable"),
                     "gold_items": [it["name"] for it in g.get("items", [])][:6],
                     "base": {k: pb.get(rid, {}).get(k) for k in ("output", "total_confidence", "total_correct", "pile")},
                     "lora": {k: pf.get(rid, {}).get(k) for k in ("output", "total_confidence", "total_correct", "pile",
                                                               "flag_low_confidence", "flag_mismatch")}})
    im = Image.open(S / "data" / g["image"]).convert("RGB"); im.thumbnail((360, 520))
    (OUT / "samples").mkdir(exist_ok=True); im.save(OUT / "samples" / f"{rid}.jpg", quality=85)
json.dump(samples, open(OUT / "sample_answers.json", "w"), ensure_ascii=False, indent=1)
with open(OUT / "sample_answers.md", "w", encoding="utf-8") as fh:
    fh.write("# Sample answers (Test Set) · before = base Qwen3-VL-2B · after = LoRA r16 (2-GPU run)\n\n")
    for s in samples:
        fh.write(f"## {s['id']}  ·  true total = {s['gold_total']}\n\n![{s['id']}](samples/{s['id']}.jpg)\n\n")
        for k in ("base", "lora"):
            o = s[k]
            fh.write(f"**{'before' if k == 'base' else 'after'}** · total correct = {o.get('total_correct')} · "
                     f"confidence = {o.get('total_confidence')} · pile = {o.get('pile')}\n\n```json\n"
                     f"{(o.get('output') or '')[:900]}\n```\n\n")
print(json.dumps(speed, indent=1)); print("reports:", list(reports))
