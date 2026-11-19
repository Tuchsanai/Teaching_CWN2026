"""Choose the confidence threshold on the VALIDATION split (NFR-01), then freeze it in threshold.json.

Rule: highest image-level Recall of NO_HARDHAT while Precision >= 0.80; ties -> the highest threshold.
Uses the team's own helpers (ai/train/evaluate.py) so labels, class names and inference match the test run.
"""
import argparse, json, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--team", required=True, help="folder that holds the team's evaluate.py and classes.json")
p.add_argument("--data", type=Path, required=True)
p.add_argument("--model", required=True)
p.add_argument("--out", type=Path, required=True)
p.add_argument("--imgsz", type=int, default=640)
a = p.parse_args()
sys.path.insert(0, a.team)
import evaluate as ev
import yaml
from PIL import Image
from ultralytics import YOLO

aliases = ev.read_class_aliases(Path(a.team, "classes.json"))
data = yaml.safe_load(a.data.read_text(encoding="utf-8"))
root = a.data.absolute().parent / (data.get("path") or "")
images = sorted(ev.split_images(root, data["val"]).values())
ids, known = ev.class_ids(data["names"], aliases, a.data)
model = YOLO(a.model, task="detect")
mids, _ = ev.class_ids(model.names, aliases, a.model)
target = sorted(set().union(*mids.values()))

actual = {n: [] for n in ev.PPE_CLASSES}
score = {n: [] for n in ev.PPE_CLASSES}          # highest confidence of the class in each image
for path in images:
    present = ev.label_classes(path, known)
    with Image.open(path) as src, src.convert("RGB") as im:
        (r,) = model.predict(source=im, conf=0.001, classes=target, imgsz=a.imgsz, device=0, verbose=False)
    for n in ev.PPE_CLASSES:
        actual[n].append(bool(present & ids[n]))
        s = [c for k, c in zip(r.boxes.cls.tolist(), r.boxes.conf.tolist()) if int(k) in mids[n]]
        score[n].append(max(s) if s else 0.0)


def sweep(name):
    rows = []
    for i in range(1, 100):
        t = i / 100
        m = ev.image_level_metrics(actual[name], [s >= t for s in score[name]])
        rows.append({"threshold": t, **m})
    return rows


rows = sweep("NO_HARDHAT")
ok = [r for r in rows if r["precision"] >= ev.MIN_METRIC]
if ok:
    best = max(ok, key=lambda r: (r["recall"], r["threshold"]))
    rule_met = True
else:                                              # no threshold reaches the precision floor
    best = max(rows, key=lambda r: (r["precision"], r["recall"]))
    rule_met = False
positive = sum(actual["NO_HARDHAT"])
doc = {"conf_threshold": best["threshold"], "split": "val", "image_count": len(images),
       "rule": "max image-level Recall of NO_HARDHAT with Precision >= 0.80; ties -> highest threshold",
       "precision_floor_met_on_val": rule_met, "val_metrics_at_threshold": best,
       "positive_images": positive, "negative_images": len(images) - positive}
a.out.mkdir(parents=True, exist_ok=True)
(a.out / "threshold.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
(a.out / "threshold_sweep_val.json").write_text(
    json.dumps({"NO_HARDHAT": rows, "NO_VEST": sweep("NO_VEST")}), encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot([r["threshold"] for r in rows], [r["recall"] for r in rows], label="Recall (image-level)")
ax.plot([r["threshold"] for r in rows], [r["precision"] for r in rows], label="Precision (image-level)")
ax.axhline(0.80, color="gray", ls="--", lw=1, label="criterion 0.80")
ax.axvline(best["threshold"], color="red", ls=":", label=f"chosen threshold {best['threshold']:.2f}")
ax.set_xlabel("Confidence threshold")
ax.set_ylabel("value")
ax.set_ylim(0, 1.02)
ax.set_title("NO-Hardhat on Validation Set: threshold selection")
ax.legend()
ax.grid(alpha=.3)
fig.tight_layout()
fig.savefig(a.out / "threshold_selection_val.png", dpi=130)
print("THRESHOLD", doc)
