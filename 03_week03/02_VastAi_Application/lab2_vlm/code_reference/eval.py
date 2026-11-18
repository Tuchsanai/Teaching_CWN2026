"""LAB 2 · Evaluation: receipt-base vs receipt-ft on the CORD-v2 Test Set (100 receipts).

Sends every Test Set receipt, one at a time, to both models on the AI server from step 4
(OpenAI-compatible, vLLM) with the same PROMPT used in training, temperature 0, then scores:
  - JSON readable (%)  : the reply parses as a JSON object (a ```json fence around it is allowed)
  - Total exact (%)    : predicted total == ground-truth total, every digit
                         (only receipts whose ground truth has a total)
  - Item F1 (%)        : micro F1 over all items; an item is correct when its name AND price
                         match a ground-truth item (name compared ignoring case, spaces, symbols)
  - Seconds / receipt  : mean wall-clock time of one request

Usage (on the rented machine, server running):
    python eval.py --data /workspace/lab2/data --out /workspace/lab2/eval \
                   --train-info /workspace/lab2/out/train_info.json
Re-running resumes: receipts already in predictions_<model>.jsonl are skipped.
The API key is read from a file on the machine (never printed).
"""
import argparse
import base64
import json
import os
import re
import time
import urllib.request
from collections import Counter

from receipt_data import PROMPT, load_split, to_int

MODELS = {"base": "receipt-base", "ft": "receipt-ft"}
LABEL = {"base": "Base", "ft": "Fine-tuned"}


# ---------------------------------------------------------------- server call
def ask(url, key, model, image_path, timeout=300):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    body = {
        "model": model,
        "temperature": 0,
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": PROMPT}]}],
    }
    req = urllib.request.Request(f"{url}/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {key}"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.load(r)
    return out["choices"][0]["message"]["content"], time.time() - t0


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
    """Per-receipt scores; also marks which predicted items are correct (for the figure)."""
    g, p = Counter(item_keys(gt)), item_keys(pred)
    left, ok = Counter(g), []
    for k in p:
        hit = left[k] > 0
        left[k] -= hit
        ok.append(hit)
    tp = sum(ok)
    total_ok = None
    if gt["total"] is not None:
        total_ok = pred is not None and to_int(pred.get("total")) == gt["total"]
    return {"json_ok": pred is not None, "total_ok": total_ok,
            "tp": tp, "n_pred": len(p), "n_gt": sum(g.values()), "item_ok": ok}


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
    }


# ---------------------------------------------------------------- run
def run_model(tag, test, url, key, out):
    path = f"{out}/predictions_{tag}.jsonl"
    done = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                done[r["id"]] = r
    with open(path, "a", encoding="utf-8") as f:
        for i, ex in enumerate(test):
            if ex["id"] in done:
                continue
            text, sec = ask(url, key, MODELS[tag], ex["image"])
            pred = parse(text)
            r = {"id": ex["id"], "model": MODELS[tag], "sec": round(sec, 3), "reply": text,
                 "parsed": pred, "answer": ex["answer"], "score": score_one(ex["answer"], pred)}
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            done[ex["id"]] = r
            if (i + 1) % 10 == 0:
                print(f"[{tag}] {i + 1}/{len(test)}", flush=True)
    return [done[ex["id"]] for ex in test]


# ---------------------------------------------------------------- figures
def bar_chart(m, save):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    keys = [("json_readable_pct", "JSON readable"), ("total_exact_pct", "Total exact"),
            ("item_f1_pct", "Item F1")]
    x = np.arange(len(keys))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [3, 1.1]})
    for j, (tag, color) in enumerate([("base", "#9aa5b8"), ("ft", "#2b6cb0")]):
        vals = [m[tag][k] for k, _ in keys]
        bars = ax.bar(x + (j - 0.5) * 0.36, vals, 0.36, color=color, label=LABEL[tag])
        ax.bar_label(bars, fmt="%.1f", fontsize=11, padding=2)
    ax.set_xticks(x, [lbl for _, lbl in keys], fontsize=12)
    ax.set_ylim(0, 122)
    ax.set_ylabel("%", fontsize=12)
    ax.set_title("Accuracy on CORD-v2 Test Set (100 receipts)", fontsize=13)
    ax.legend(fontsize=11, loc="upper center", ncol=2, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    secs = [m["base"]["sec_per_receipt"], m["ft"]["sec_per_receipt"]]
    bars = ax2.bar(["Base", "Fine-tuned"], secs, color=["#9aa5b8", "#2b6cb0"], width=0.6)
    ax2.bar_label(bars, fmt="%.2f s", fontsize=11, padding=2)
    ax2.set_ylim(0, max(secs) * 1.25)
    ax2.set_title("Seconds per receipt", fontsize=13)
    ax2.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Qwen3-VL-2B: Base vs Fine-tuned (LoRA)", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(save, dpi=120)
    plt.close(fig)


def _fmt(v):
    return "null" if v is None else str(v)


def _lines(ans, item_ok=None, total_ok=None, max_items=16):
    """Text lines + colour for one answer panel. Red = wrong."""
    out = []
    items = (ans or {}).get("items") or []
    for k, it in enumerate(items[:max_items]):
        if not isinstance(it, dict):
            continue
        name = str(it.get("name"))
        name = name if len(name) <= 28 else name[:27] + "…"
        color = "black" if item_ok is None or item_ok[k] else "#d62728"
        out.append((f"{name:<28} {_fmt(it.get('qty')):>2} {_fmt(it.get('price')):>8}", color))
    if len(items) > max_items:
        out.append((f"... +{len(items) - max_items} more items", "gray"))
    out.append(("", "black"))
    for key in ("subtotal", "tax"):
        out.append((f"{key:<12}{_fmt((ans or {}).get(key)):>28}", "black"))
    color = "black" if total_ok is None or total_ok else "#d62728"
    out.append((f"{'total':<12}{_fmt((ans or {}).get('total')):>28}", color))
    return out


def examples_figure(test, res, picks, save):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    by_id = {ex["id"]: ex for ex in test}
    fig, axes = plt.subplots(len(picks), 4, figsize=(28, 6.5 * len(picks)),
                             gridspec_kw={"width_ratios": [0.8, 1, 1, 1]})
    for row, rid in enumerate(picks):
        ex = by_id[rid]
        ax = axes[row][0]
        ax.imshow(Image.open(ex["image"]))
        ax.set_title(rid, fontsize=15, fontweight="bold")
        ax.axis("off")
        panels = [("Ground truth", ex["answer"], None, None)]
        for tag in ("base", "ft"):
            r = res[tag][rid]
            sc = r["score"]
            title = (f"{LABEL[tag]} · items {sc['tp']}/{sc['n_gt']} · "
                     f"total {'OK' if sc['total_ok'] else 'WRONG'}")
            panels.append((title, r["parsed"], sc["item_ok"], sc["total_ok"]))
        for col, (title, ans, ok, tok) in enumerate(panels, start=1):
            ax = axes[row][col]
            ax.axis("off")
            ax.set_title(title, fontsize=14, loc="left",
                         color="#d62728" if tok is False else "black")
            if ans is None:
                raw = res["base" if col == 2 else "ft"][rid]["reply"][:400]
                ax.text(0.01, 0.98, "Not readable JSON:\n" + raw, va="top", ha="left",
                        family="monospace", fontsize=11, color="#d62728", wrap=True,
                        transform=ax.transAxes)
                continue
            y = 0.98
            ax.text(0.01, y, f"{'name':<28} {'qty':>2} {'price':>8}", va="top", ha="left",
                    family="monospace", fontsize=11.5, fontweight="bold", transform=ax.transAxes)
            for text, color in _lines(ans, ok, tok):
                y -= 0.06
                ax.text(0.01, y, text, va="top", ha="left", family="monospace", fontsize=11.5,
                        color=color, transform=ax.transAxes)
    fig.suptitle("CORD-v2 Test Set examples · red = wrong (item name/price or total "
                 "does not match the ground truth)", fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    fig.savefig(save, dpi=90, pil_kwargs={"quality": 88})
    plt.close(fig)


def pick_examples(test, res, n=4):
    """Receipts (2–8 items) that show the gap best: first those where Fine-tuned gets the
    total right and Base gets it wrong, then those with the largest gain in correct items."""
    cands = []
    for ex in test:
        b, f = res["base"][ex["id"]]["score"], res["ft"][ex["id"]]["score"]
        if not 2 <= f["n_gt"] <= 8 or f["tp"] < b["tp"]:
            continue
        flip = bool(f["total_ok"]) and not b["total_ok"]
        cands.append((flip, f["tp"] - b["tp"], ex["id"]))
    cands.sort(reverse=True)
    picks = sorted(c[-1] for c in cands[:n])
    return picks


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/workspace/lab2/data")
    ap.add_argument("--out", default="/workspace/lab2/eval")
    ap.add_argument("--url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--key-file", default="/workspace/lab2/secret/api_key")
    ap.add_argument("--train-info", default="/workspace/lab2/out/train_info.json")
    a = ap.parse_args()
    os.makedirs(f"{a.out}/images", exist_ok=True)
    with open(a.key_file) as f:
        key = f.read().strip()
    test = load_split(a.data, "test")

    res, metrics = {}, {}
    for tag in ("base", "ft"):
        rows = run_model(tag, test, a.url, key, a.out)
        res[tag] = {r["id"]: r for r in rows}
        metrics[tag] = {"model": MODELS[tag], **summarize(rows)}
        print(tag, metrics[tag], flush=True)

    with open(a.train_info) as f:
        train = json.load(f)
    picks = pick_examples(test, res)
    out = {
        "dataset": "naver-clova-ix/cord-v2 · test split",
        "settings": {"temperature": 0, "max_tokens": 2048, "requests": "one receipt at a time",
                     "server": "vLLM OpenAI-compatible, receipt-base / receipt-ft"},
        "scoring": {
            "json_readable": "reply parses as a JSON object (a ```json fence is allowed)",
            "total_exact": "predicted total equals ground-truth total in every digit; "
                           "receipts without a ground-truth total are skipped",
            "item_f1": "micro F1; item correct when name (lower-case, no spaces/symbols) "
                       "and price both match a ground-truth item, each GT item used once",
        },
        "base": metrics["base"],
        "fine_tuned": metrics["ft"],
        "improvement_points": {k: round(metrics["ft"][k] - metrics["base"][k], 1)
                               for k in ("json_readable_pct", "total_exact_pct", "item_f1_pct")},
        "training": train,
        "examples": picks,
    }
    with open(f"{a.out}/metrics.json", "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    bar_chart(metrics, f"{a.out}/images/base_vs_ft.png")
    examples_figure(test, res, picks, f"{a.out}/images/examples.jpg")
    print("saved", a.out, "examples:", picks, flush=True)


if __name__ == "__main__":
    main()
