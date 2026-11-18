"""LAB 2 · CORD-v2 receipt data.

Loads naver-clova-ix/cord-v2 (official train / validation / test split), resizes every
receipt so its long side is at most 1280 px, converts each ground truth into the JSON
the model must answer, and keeps the one PROMPT shared by training, evaluation and the web.

Usage (on the rented machine):
    python receipt_data.py prepare --out /workspace/lab2/data
    python receipt_data.py samples --out /workspace/lab2/data --save dataset_samples.jpg
HF_TOKEN is read from the environment only (never written to disk).
"""
import argparse
import json
import os
import random
import re

# ---------------------------------------------------------------- shared prompt
PROMPT = (
    "Read this receipt image and extract its contents as JSON. "
    "Reply with JSON only, no other text, using exactly this format:\n"
    '{"items":[{"name":string,"qty":integer,"price":integer|null}],'
    '"subtotal":integer|null,"tax":integer|null,"total":integer|null}\n'
    "Rules: copy each item name as printed. qty is the printed quantity (1 if none is printed). "
    "price is the line price printed for that item. Write all numbers as plain integers "
    "without separators or decimals (\"25,000\" -> 25000). Sub-items such as toppings or "
    "add-ons are separate items. Use null for any value that is not printed on the receipt."
)

SPLITS = {"train": "train", "validation": "val", "test": "test"}  # HF split -> name prefix
MAX_SIDE = 1280


# ---------------------------------------------------------------- answer JSON
def _first(v):
    """CORD sometimes stores a field as a list of strings; take the first one."""
    if isinstance(v, list):
        v = v[0] if v else None
    return v


def to_int(v):
    """'25,000' -> 25000 · '@12.500' -> 12500 · '30.000,00' -> 30000 · '-5,000' -> -5000."""
    v = _first(v)
    if v is None:
        return None
    s = str(v).strip()
    s = re.sub(r"[.,]\d{1,2}$", "", s)          # drop a trailing decimal part (.00 / ,5)
    digits = re.sub(r"\D", "", s)
    if not digits:
        return None
    n = int(digits)
    return -n if re.match(r"^\s*[-(]", s) else n


def to_qty(v):
    """'2' / '2x' / 'x2' / '1.00' -> int; missing -> 1."""
    v = _first(v)
    if v is None:
        return 1
    m = re.search(r"\d+(?:[.,]\d+)?", str(v))
    if not m:
        return 1
    q = round(float(m.group().replace(",", ".")))
    return q if q > 0 else 1


def _as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def _item(d):
    name = _first(d.get("nm"))
    return {"name": str(name).strip() if name is not None else None,
            "qty": to_qty(d.get("cnt")),
            "price": to_int(d.get("price"))}


def to_answer(ground_truth):
    """CORD ground_truth (JSON string) -> answer dict in the model's output format."""
    gt = json.loads(ground_truth)["gt_parse"]
    items = []
    for m in _as_list(gt.get("menu")):
        if not isinstance(m, dict):
            continue
        if m.get("nm") is not None:
            items.append(_item(m))
        for s in _as_list(m.get("sub")):            # toppings / add-ons = own line
            if isinstance(s, dict) and s.get("nm") is not None:
                items.append(_item(s))
    sub = gt.get("sub_total") or {}
    tot = gt.get("total") or {}
    sub = sub[0] if isinstance(sub, list) else sub
    tot = tot[0] if isinstance(tot, list) else tot
    return {"items": items,
            "subtotal": to_int(sub.get("subtotal_price")),
            "tax": to_int(sub.get("tax_price")),
            "total": to_int(tot.get("total_price"))}


def answer_text(ans):
    """The exact string the model is trained to produce."""
    return json.dumps(ans, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- prepare
def resize(img):
    img = img.convert("RGB")
    w, h = img.size
    s = MAX_SIDE / max(w, h)
    if s < 1:
        img = img.resize((round(w * s), round(h * s)))
    return img


def prepare(out):
    from datasets import load_dataset
    ds = load_dataset("naver-clova-ix/cord-v2", token=os.environ.get("HF_TOKEN"))
    stats = {}
    for split, prefix in SPLITS.items():
        os.makedirs(f"{out}/images", exist_ok=True)
        rows, n_items = [], 0
        for i, ex in enumerate(ds[split]):
            rid = f"{prefix}_{i:03d}"
            path = f"{out}/images/{rid}.jpg"
            resize(ex["image"]).save(path, quality=92)
            ans = to_answer(ex["ground_truth"])
            n_items += len(ans["items"])
            rows.append({"id": rid, "image": path, "answer": ans})
        with open(f"{out}/{prefix}.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        stats[prefix] = {"receipts": len(rows), "items": n_items}
        print(prefix, stats[prefix], flush=True)
    with open(f"{out}/stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    with open(f"{out}/prompt.txt", "w") as f:
        f.write(PROMPT)


def load_split(out, prefix):
    with open(f"{out}/{prefix}.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# ---------------------------------------------------------------- sample figure
def samples(out, save, n=6, seed=0):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image

    rows = [r for r in load_split(out, "train") if 2 <= len(r["answer"]["items"]) <= 6]
    pick = sorted(random.Random(seed).sample(rows, n), key=lambda r: r["id"])
    cols = 3
    rows_n = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows_n, cols * 2, figsize=(26, 10 * rows_n),
                             gridspec_kw={"width_ratios": [1, 1.05] * cols})
    for k, r in enumerate(pick):
        ax_img, ax_txt = axes[k // cols][2 * (k % cols)], axes[k // cols][2 * (k % cols) + 1]
        ax_img.imshow(Image.open(r["image"]))
        ax_img.set_title(r["id"], fontsize=13, fontweight="bold")
        ax_img.axis("off")
        a = r["answer"]
        lines = ['{"items": [']
        for it in a["items"]:
            name = it["name"] if len(it["name"] or "") <= 20 else it["name"][:19] + "…"
            lines.append(f' {{"name": "{name}",\n   "qty": {it["qty"]}, "price": {json.dumps(it["price"])}}},')
        lines.append("],")
        for key in ("subtotal", "tax", "total"):
            lines.append(f'"{key}": {json.dumps(a[key])},')
        lines[-1] = lines[-1].rstrip(",") + "}"
        ax_txt.text(0.02, 0.97, "\n".join(lines), va="top", ha="left",
                    family="monospace", fontsize=12.5, transform=ax_txt.transAxes,
                    bbox={"boxstyle": "round", "facecolor": "#f4f6fa", "edgecolor": "#c5ccd8"})
        ax_txt.axis("off")
    fig.suptitle("CORD-v2 Training Set: receipt image → ground-truth JSON", fontsize=22)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(save, dpi=110, pil_kwargs={"quality": 90})
    print("saved", save)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "samples"])
    ap.add_argument("--out", default="/workspace/lab2/data")
    ap.add_argument("--save", default="/workspace/lab2/dataset_samples.jpg")
    a = ap.parse_args()
    prepare(a.out) if a.cmd == "prepare" else samples(a.out, a.save)
