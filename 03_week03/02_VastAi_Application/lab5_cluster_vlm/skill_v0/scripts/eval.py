"""LAB 5 · Evaluation: how much better does the cluster-trained Qwen3-VL-8B read receipts?

Three models on the CORD-v2 Test Set (100 receipts):
  base : Qwen/Qwen3-VL-8B-Instruct as downloaded
  A    : base + LoRA adapter trained with approach A (model split over 2 GPUs per node)
  B    : base + LoRA adapter trained with approach B (one full replica per GPU)
Every receipt is read one at a time, with the same PROMPT as training, image long side 1280 px,
greedy decoding (temperature 0 = do_sample False).

One model copy fits one RTX 3090, so the work is spread over every GPU of both nodes:
  python eval.py run --gpu 0 --shard 0/4 --out /workspace/lab5/eval   # Node 1 GPU 0
  python eval.py run --gpu 1 --shard 1/4 ...                           # Node 1 GPU 1
  python eval.py run --gpu 0 --shard 2/4 ...                           # Node 2 GPU 0
  python eval.py run --gpu 1 --shard 3/4 ...                           # Node 2 GPU 1
Shard k/n takes receipts k, k+n, k+2n, ... and runs all three models on them (base model loaded
once, both adapters attached, base = adapters disabled), so every model sees the same mix of
receipts on every GPU. Re-running resumes from predictions_shard<k>.jsonl.

After all shards are collected into one folder:
  python eval.py report --out /workspace/lab5/eval
scores everything and writes metrics.json, predictions_<model>.jsonl, images/accuracy_3models.png
and images/examples.jpg.

Scoring (same rules as the Qwen3-VL-2B lab):
  JSON readable (%) : reply parses as a JSON object (a ```json fence is allowed)
  Total exact (%)   : predicted total == ground-truth total in every digit
                      (receipts whose ground truth has no total are skipped)
  Item F1 (%)       : micro F1; an item is correct when name AND price match a ground-truth item
                      (name compared ignoring case, spaces and symbols; each GT item used once)
  Seconds / receipt : mean wall-clock time to read one receipt (preprocess + generate + decode)
"""
import argparse
import json
import os
import re
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from receipt_data import PROMPT, load_split, resize, to_int  # noqa: E402

TAGS = ["base", "A", "B"]
LABEL = {"base": "Base", "A": "Fine-tuned A", "B": "Fine-tuned B"}
COLOR = {"base": "#9aa5b8", "A": "#2b6cb0", "B": "#dd6b20"}
MODEL_ID = "Qwen/Qwen3-VL-8B-Instruct"
REF_2B = {  # Qwen3-VL-2B, same Test Set and scoring (LAB 2)
    "2B Base": {"total_exact_pct": 88.4, "item_f1_pct": 69.9},
    "2B Fine-tuned": {"total_exact_pct": 100.0, "item_f1_pct": 88.4,
                      "training": "800 receipts, 2 Epochs"},
}


# ---------------------------------------------------------------- run (one GPU)
def run(a):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(a.gpu)
    import torch
    from peft import PeftModel
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor

    k, n = (int(x) for x in a.shard.split("/"))
    test = load_split(a.data, "test")[k::n]
    os.makedirs(a.out, exist_ok=True)
    path = f"{a.out}/predictions_shard{k}.jsonl"
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            done = {(r["id"], r["model"]) for r in map(json.loads, f)}

    processor = AutoProcessor.from_pretrained(a.model)
    model = AutoModelForImageTextToText.from_pretrained(a.model, dtype=torch.bfloat16,
                                                        device_map={"": 0})
    adapters = {"A": a.adapter_a, "B": a.adapter_b}
    ft = [t for t in TAGS if t != "base"]          # --models picks which fine-tuned adapters to load
    for j, tag in enumerate(ft):
        if j == 0:
            model = PeftModel.from_pretrained(model, adapters[tag], adapter_name=tag)
        else:
            model.load_adapter(adapters[tag], adapter_name=tag)
    model.eval()
    print(f"shard {k}/{n}: {len(test)} receipts x {len(TAGS)} models ({','.join(TAGS)}) on GPU {a.gpu}", flush=True)

    msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
    prompt = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

    def read(img):
        torch.cuda.synchronize()
        t0 = time.time()
        enc = processor(text=[prompt], images=[img], return_tensors="pt").to("cuda:0")
        with torch.inference_mode():
            out = model.generate(**enc, do_sample=False, max_new_tokens=a.max_new_tokens)
        new = out[0, enc["input_ids"].shape[1]:]
        text = processor.decode(new, skip_special_tokens=True)
        torch.cuda.synchronize()
        return text, time.time() - t0, int(new.shape[0])

    # warm-up (not recorded): first CUDA kernels / allocator
    read(resize(Image.open(test[0]["image"])))

    with open(path, "a", encoding="utf-8") as f:
        for i, ex in enumerate(test):
            img = resize(Image.open(ex["image"]))
            for tag in TAGS:
                if (ex["id"], tag) in done:
                    continue
                if tag == "base":
                    if ft:
                        with model.disable_adapter():
                            text, sec, ntok = read(img)
                    else:
                        text, sec, ntok = read(img)
                else:
                    model.set_adapter(tag)
                    text, sec, ntok = read(img)
                r = {"id": ex["id"], "model": tag, "shard": k, "gpu": a.gpu,
                     "host": a.host, "sec": round(sec, 3), "new_tokens": ntok, "reply": text}
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                f.flush()
            print(f"[shard {k}] {i + 1}/{len(test)} {ex['id']}", flush=True)
    print("DONE", flush=True)


# ---------------------------------------------------------------- scoring
def parse(text):
    """Model reply -> dict, or None when it is not a readable JSON object."""
    s = text.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, re.S)
    if m:
        s = m.group(1)
    try:
        d = json.loads(s)
    except Exception:
        return None
    return d if isinstance(d, dict) else None


def norm_name(n):
    return re.sub(r"[\W_]+", "", str(n or "").lower())


def item_keys(ans):
    keys = []
    for it in (ans or {}).get("items") or []:
        if isinstance(it, dict):
            keys.append((norm_name(it.get("name")), to_int(it.get("price"))))
    return keys


def score_one(gt, pred):
    g, p = Counter(item_keys(gt)), item_keys(pred)
    left, ok = Counter(g), []
    for key in p:
        hit = left[key] > 0
        left[key] -= hit
        ok.append(hit)
    total_ok = None
    if gt["total"] is not None:
        total_ok = pred is not None and to_int(pred.get("total")) == gt["total"]
    return {"json_ok": pred is not None, "total_ok": total_ok,
            "tp": sum(ok), "n_pred": len(p), "n_gt": sum(g.values()), "item_ok": ok}


def summarize(rows):
    n = len(rows)
    tot = [r["score"]["total_ok"] for r in rows if r["score"]["total_ok"] is not None]
    tp = sum(r["score"]["tp"] for r in rows)
    npred = sum(r["score"]["n_pred"] for r in rows)
    ngt = sum(r["score"]["n_gt"] for r in rows)
    prec = tp / npred if npred else 0.0
    rec = tp / ngt if ngt else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {
        "receipts": n,
        "json_readable_pct": round(100 * sum(r["score"]["json_ok"] for r in rows) / n, 1),
        "total_exact_pct": round(100 * sum(tot) / len(tot), 1),
        "total_receipts_scored": len(tot),
        "item_precision_pct": round(100 * prec, 1),
        "item_recall_pct": round(100 * rec, 1),
        "item_f1_pct": round(100 * f1, 1),
        "items_correct": tp, "items_predicted": npred, "items_ground_truth": ngt,
        "sec_per_receipt": round(sum(r["sec"] for r in rows) / n, 2),
        "new_tokens_mean": round(sum(r["new_tokens"] for r in rows) / n, 1),
    }


# ---------------------------------------------------------------- figures
def bar_chart(m, save):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    keys = [("json_readable_pct", "JSON readable"), ("total_exact_pct", "Total exact"),
            ("item_f1_pct", "Item F1")]
    x = np.arange(len(keys))
    w = 0.26
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [3, 1.2]})
    for j, tag in enumerate(TAGS):
        vals = [m[tag][key] for key, _ in keys]
        bars = ax.bar(x + (j - (len(TAGS) - 1) / 2) * w, vals, w, color=COLOR[tag], label=LABEL[tag])
        ax.bar_label(bars, fmt="%.1f", fontsize=10.5, padding=2)
    ax.set_xticks(x, [lbl for _, lbl in keys], fontsize=12)
    ax.set_ylim(0, 122)
    ax.set_ylabel("%", fontsize=12)
    ax.set_title("Accuracy on CORD-v2 Test Set (100 receipts)", fontsize=13)
    ax.legend(fontsize=11, loc="upper center", ncol=3, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    secs = [m[t]["sec_per_receipt"] for t in TAGS]
    bars = ax2.bar([LABEL[t].replace("Fine-tuned ", "FT ") for t in TAGS], secs,
                   color=[COLOR[t] for t in TAGS], width=0.6)
    ax2.bar_label(bars, fmt="%.1f s", fontsize=11, padding=2)
    ax2.set_ylim(0, max(secs) * 1.25)
    ax2.set_title("Seconds per receipt (RTX 3090)", fontsize=13)
    ax2.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Qwen3-VL-8B: " + " vs ".join(LABEL[t] for t in TAGS) + " (LoRA, cluster)",
                 fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(save, dpi=120)
    plt.close(fig)


def _fmt(v):
    return "null" if v is None else str(v)


def _lines(ans, item_ok=None, total_ok=None, max_items=14):
    out = []
    items = [it for it in ((ans or {}).get("items") or []) if isinstance(it, dict)]
    for k, it in enumerate(items[:max_items]):
        name = str(it.get("name"))
        name = name if len(name) <= 24 else name[:23] + "…"
        color = "black" if item_ok is None or item_ok[k] else "#d62728"
        out.append((f"{name:<24} {_fmt(it.get('qty')):>2} {_fmt(it.get('price')):>8}", color))
    if len(items) > max_items:
        out.append((f"... +{len(items) - max_items} more items", "gray"))
    out.append(("", "black"))
    for key in ("subtotal", "tax"):
        out.append((f"{key:<10}{_fmt((ans or {}).get(key)):>26}", "black"))
    color = "black" if total_ok is None or total_ok else "#d62728"
    out.append((f"{'total':<10}{_fmt((ans or {}).get('total')):>26}", color))
    return out


def examples_figure(test, res, picks, save):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    by_id = {ex["id"]: ex for ex in test}
    ncol = 2 + len(TAGS)
    fig, axes = plt.subplots(len(picks), ncol, figsize=(6.6 * ncol, 6.5 * len(picks)), squeeze=False,
                             gridspec_kw={"width_ratios": [0.75] + [1] * (ncol - 1)})
    for row, rid in enumerate(picks):
        ex = by_id[rid]
        ax = axes[row][0]
        ax.imshow(Image.open(ex["image"]))
        ax.set_title(rid, fontsize=15, fontweight="bold")
        ax.axis("off")
        panels = [("Ground truth", ex["answer"], None, None, None)]
        for tag in TAGS:
            r = res[tag][rid]
            sc = r["score"]
            title = (f"{LABEL[tag]} · items {sc['tp']}/{sc['n_gt']} · "
                     f"total {'OK' if sc['total_ok'] else 'WRONG'}")
            panels.append((title, r["parsed"], sc["item_ok"], sc["total_ok"], r["reply"]))
        for col, (title, ans, ok, tok, reply) in enumerate(panels, start=1):
            ax = axes[row][col]
            ax.axis("off")
            ax.set_title(title, fontsize=13.5, loc="left",
                         color="#d62728" if tok is False else "black")
            if ans is None:
                ax.text(0.01, 0.98, "Not readable JSON:\n" + reply[:400], va="top", ha="left",
                        family="monospace", fontsize=10.5, color="#d62728", wrap=True,
                        transform=ax.transAxes)
                continue
            y = 0.98
            ax.text(0.01, y, f"{'name':<24} {'qty':>2} {'price':>8}", va="top", ha="left",
                    family="monospace", fontsize=11, fontweight="bold", transform=ax.transAxes)
            for text, color in _lines(ans, ok, tok):
                y -= 0.06
                ax.text(0.01, y, text, va="top", ha="left", family="monospace", fontsize=11,
                        color=color, transform=ax.transAxes)
    fig.suptitle("CORD-v2 Test Set examples · red = wrong (item name/price or total does not "
                 "match the ground truth)", fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    fig.savefig(save, dpi=85, pil_kwargs={"quality": 88})
    plt.close(fig)


def pick_examples(test, res, n=4):
    """Receipts (2-8 items) where both fine-tuned models get the total right and Base gets it
    wrong come first, then the largest gain in correct items over Base."""
    cands = []
    ft = [t for t in TAGS if t != "base"]
    if not ft:
        return [ex["id"] for ex in test[:n]]
    for ex in test:
        b = res["base"][ex["id"]]["score"]
        fs = [res[t][ex["id"]]["score"] for t in ft]
        if not 2 <= b["n_gt"] <= 8 or min(f["tp"] for f in fs) < b["tp"]:
            continue
        flip = all(bool(f["total_ok"]) for f in fs) and not b["total_ok"]
        cands.append((flip, min(f["tp"] for f in fs) - b["tp"], ex["id"]))
    cands.sort(reverse=True)
    return sorted(c[-1] for c in cands[:n])


# ---------------------------------------------------------------- report
def report(a):
    test = load_split(a.data, "test")
    rows = []
    for fn in sorted(os.listdir(a.out)):
        if fn.startswith("predictions_shard") and fn.endswith(".jsonl"):
            with open(f"{a.out}/{fn}", encoding="utf-8") as f:
                rows += [json.loads(line) for line in f]
    gt = {ex["id"]: ex["answer"] for ex in test}
    res = {t: {} for t in TAGS}
    for r in rows:
        r["parsed"] = parse(r["reply"])
        r["answer"] = gt[r["id"]]
        r["score"] = score_one(r["answer"], r["parsed"])
        if r["model"] in res:
            res[r["model"]][r["id"]] = r
    missing = {t: [ex["id"] for ex in test if ex["id"] not in res[t]] for t in TAGS}
    if any(missing.values()):
        sys.exit(f"not complete yet: { {t: len(v) for t, v in missing.items()} }")

    metrics = {}
    for t in TAGS:
        ordered = [res[t][ex["id"]] for ex in test]
        with open(f"{a.out}/predictions_{t}.jsonl", "w", encoding="utf-8") as f:
            for r in ordered:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        metrics[t] = summarize(ordered)
        print(t, metrics[t], flush=True)

    ft = [t for t in TAGS if t != "base"]
    flips = [ex["id"] for ex in test
             if res["base"][ex["id"]]["score"]["total_ok"] is False
             and all(res[t][ex["id"]]["score"]["total_ok"] for t in ft)]
    picks = pick_examples(test, res)
    os.makedirs(f"{a.out}/images", exist_ok=True)
    out = {
        "dataset": "naver-clova-ix/cord-v2 · test split (100 receipts)",
        "base_model": MODEL_ID,
        "settings": {"decoding": "greedy (temperature 0, do_sample False)",
                     "max_new_tokens": a.max_new_tokens, "image_long_side_px": 1280,
                     "requests": "one receipt at a time",
                     "runtime": "transformers generate, bf16, 1 RTX 3090 per model copy",
                     "parallel": "one shard per GPU (receipt i -> shard i % shards) on every node; "
                                 "each shard runs Base, A and B on its receipts"},
        "scoring": {
            "json_readable": "reply parses as a JSON object (a ```json fence is allowed)",
            "total_exact": "predicted total equals ground-truth total in every digit; "
                           "receipts without a ground-truth total are skipped",
            "item_f1": "micro F1; item correct when name (lower-case, no spaces/symbols) "
                       "and price both match a ground-truth item, each GT item used once",
            "sec_per_receipt": "mean wall-clock per receipt: preprocess + generate + decode",
        },
        "models": {t: {"label": LABEL[t], **metrics[t]} for t in TAGS},
        "improvement_points_vs_base": {
            t: {k: round(metrics[t][k] - metrics["base"][k], 1)
                for k in ("json_readable_pct", "total_exact_pct", "item_f1_pct")}
            for t in ft},
        "reference_qwen3_vl_2b": REF_2B,
        "total_fixed_by_both_ft": flips,
        "examples": picks,
    }
    with open(f"{a.out}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    bar_chart(metrics, f"{a.out}/images/accuracy_3models.png")
    examples_figure(test, res, picks, f"{a.out}/images/examples.jpg")
    print("saved", a.out, "examples:", picks, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--data", default="/workspace/lab5/data")
    ap.add_argument("--out", default="/workspace/lab5/eval")
    ap.add_argument("--model", default="/workspace/models/Qwen3-VL-8B-Instruct")
    ap.add_argument("--adapter-a", default="/workspace/lab5/adapters/A")
    ap.add_argument("--adapter-b", default="/workspace/lab5/adapters/B")
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--host", default=os.uname().nodename if hasattr(os, "uname") else "?")
    ap.add_argument("--max-new-tokens", type=int, default=2048)
    ap.add_argument("--models", default="base,A,B", help="comma list from base,A,B (base is always read)")
    a = ap.parse_args()
    TAGS = ["base"] + [t for t in ("A", "B") if t in a.models.split(",")]
    run(a) if a.cmd == "run" else report(a)
