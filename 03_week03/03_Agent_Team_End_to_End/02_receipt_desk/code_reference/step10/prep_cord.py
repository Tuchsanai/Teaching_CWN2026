#!/usr/bin/env python3
"""Convert CORD-v2 (parquet) into the team's JSONL format (app/ai/train/README.md "Data").

- train.jsonl : 400 receipts sampled from CORD train with seed 0
- val.jsonl   : CORD validation (100)   -> used only to fix decisions before the test set
- test.jsonl  : CORD test (100)
- unreadable.jsonl : 20 "unreadable" receipts made from test images (10 heavy blur, 10 cut off above the total)
CORD has no shop name / date labels (header blurred), so every readable row gets the fixed placeholders
merchant="UNKNOWN", date="1900-01-01" to fill the 5-field contract. Amounts are Indonesian rupiah strings
("41,500", "28.000", "118.000,00") -> normalised to integer "41500.00".
"""
import glob, io, json, random, re, sys
from pathlib import Path
import pyarrow.parquet as pq
from PIL import Image, ImageFilter

SRC = Path("/workspace/e2e_receipt/data/cord-v2/data")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/e2e_receipt/step10/data")
MERCHANT, DATE = "UNKNOWN", "1900-01-01"


def idr(v):
    if isinstance(v, list):
        v = v[0] if v else None
    if not isinstance(v, str):
        return None
    s = re.sub(r"[^\d.,-]", "", v)
    s = re.sub(r"[.,]00$", "", s)
    s = s.replace(".", "").replace(",", "")
    if not re.fullmatch(r"-?\d+", s):
        return None
    return f"{int(s)}.00"


def text(v):
    if isinstance(v, list):
        v = " ".join(str(x) for x in v)
    return str(v).strip() if v is not None else ""


def convert(gt):
    p = json.loads(gt)["gt_parse"]
    total = (p.get("total") or {}) if isinstance(p.get("total"), dict) else {}
    tp = idr(total.get("total_price"))
    menu = p.get("menu") or []
    if isinstance(menu, dict):
        menu = [menu]
    items = []
    for m in menu:
        if not isinstance(m, dict):
            continue
        nm, pr = text(m.get("nm")), idr(m.get("price"))
        if nm and pr is not None:
            items.append({"name": nm, "price": pr})
    return tp, items


def load(split):
    files = sorted(glob.glob(str(SRC / f"{split}-*.parquet")))
    rows = []
    for f in files:
        rows += pq.read_table(f).to_pylist()
    return rows


def write(name, rows, idxs, prefix):
    (OUT / "images").mkdir(parents=True, exist_ok=True)
    kept, skipped = [], []
    with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as fh:
        for i in idxs:
            r = rows[i]
            tp, items = convert(r["ground_truth"])
            if tp is None:
                skipped.append(i)
                continue
            rid = f"{prefix}{i:04d}"
            img = Image.open(io.BytesIO(r["image"]["bytes"])).convert("RGB")
            img.save(OUT / "images" / f"{rid}.jpg", quality=92)
            fh.write(json.dumps({"id": rid, "image": f"images/{rid}.jpg", "merchant": MERCHANT, "date": DATE,
                                 "items": items, "total": tp, "cord_index": i}, ensure_ascii=False) + "\n")
            kept.append(rid)
    return kept, skipped


def main():
    stats = {}
    train = load("train")
    rng = random.Random(0)
    order = list(range(len(train)))
    rng.shuffle(order)
    # take the first 400 receipts (seed-0 order) that have a readable total
    picked = [i for i in order if convert(train[i]["ground_truth"])[0] is not None][:400]
    stats["train"] = write("train", train, picked, "tr")
    val = load("validation"); stats["val"] = write("val", val, range(len(val)), "va")
    test = load("test"); stats["test"] = write("test", test, range(len(test)), "te")
    # unreadable set from the first 20 test receipts: 10 heavy blur, 10 cut off at 35% height
    with open(OUT / "unreadable.jsonl", "w", encoding="utf-8") as fh:
        for k in range(20):
            img = Image.open(io.BytesIO(test[k]["image"]["bytes"])).convert("RGB")
            if k < 10:
                img, kind = img.filter(ImageFilter.GaussianBlur(radius=max(img.size) / 60)), "blur"
            else:
                img, kind = img.crop((0, 0, img.width, int(img.height * 0.35))), "cut"
            rid = f"un{k:02d}"
            img.save(OUT / "images" / f"{rid}.jpg", quality=92)
            fh.write(json.dumps({"id": rid, "image": f"images/{rid}.jpg", "unreadable": True, "kind": kind,
                                 "from": f"te{k:04d}"}) + "\n")
    summary = {k: {"kept": len(v[0]), "skipped_no_total": v[1]} for k, v in stats.items()}
    summary["unreadable"] = 20
    json.dump(summary, open(OUT / "prep_summary.json", "w"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
