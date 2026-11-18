"""Evaluate YOLO11s before (COCO) vs after fine-tuning on the Test Set (never used for training).

Run on the rented GPU:  python eval.py
Both models go through the SAME pipeline: predict every test image (conf 0.001, IoU-NMS 0.7, imgsz 640,
batch 1) -> map classes to the dataset -> match with ground truth at IoU 0.50:0.95 -> AP per class.
The COCO model has no PPE classes, so only matching classes count: person -> Person,
car/bus/truck -> vehicle. Every other class gets AP 0.

Outputs (OUT_DIR): metrics.json · images/before_after_1..5.jpg · images/ap50_per_class.png ·
images/curves.png · samples/ (3 images with NO-Hardhat, 3 images where everyone wears a hardhat)
"""
import csv
import json
import os
import shutil
import time
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import yaml
from ultralytics import YOLO
from ultralytics.utils.metrics import ap_per_class, box_iou

DATA_DIR = Path(os.environ.get("DATA_DIR", "/workspace/datasets/construction-site-safety-28"))
RUN_DIR = Path(os.environ.get("RUN_DIR", "/workspace/runs/ppe_yolo11s"))
OUT_DIR = Path(os.environ.get("OUT_DIR", "/workspace/eval_out"))
BEFORE_W = os.environ.get("BEFORE_W", "/workspace/yolo11s.pt")
AFTER_W = str(RUN_DIR / "weights" / "best.pt")
IMGSZ, CONF_EVAL, IOU_NMS, CONF_SHOW = 640, 0.001, 0.7, 0.35

NAMES = yaml.safe_load((DATA_DIR / "data.yaml").read_text())["names"]  # 10 dataset classes
CID = {n: i for i, n in enumerate(NAMES)}
COCO_TO_DS = {"person": CID["Person"], "car": CID["vehicle"], "bus": CID["vehicle"], "truck": CID["vehicle"]}
IOUV = torch.linspace(0.5, 0.95, 10)  # 10 IoU thresholds for mAP50-95

(OUT_DIR / "images").mkdir(parents=True, exist_ok=True)
images = sorted((DATA_DIR / "test" / "images").glob("*.jpg"))


def load_gt(img_path, w, h):
    """YOLO label file (cls cx cy bw bh, normalised) -> (classes, xyxy boxes in pixels)."""
    lbl = DATA_DIR / "test" / "labels" / (img_path.stem + ".txt")
    rows = np.loadtxt(lbl, ndmin=2) if lbl.exists() and lbl.stat().st_size else np.zeros((0, 5))
    cls = rows[:, 0].astype(int)
    cx, cy, bw, bh = rows[:, 1] * w, rows[:, 2] * h, rows[:, 3] * w, rows[:, 4] * h
    return cls, np.stack([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], 1)


def predict_all(weights, class_map):
    """Predict every test image; class_map converts model class names to dataset class ids."""
    model = YOLO(weights)
    for _ in range(5):  # GPU warm-up so the first images are not counted slow
        model.predict(str(images[0]), imgsz=IMGSZ, conf=CONF_EVAL, iou=IOU_NMS, verbose=False)
    preds, ms = {}, []
    for p in images:
        r = model.predict(str(p), imgsz=IMGSZ, conf=CONF_EVAL, iou=IOU_NMS, max_det=300, verbose=False)[0]
        ms.append(sum(r.speed.values()))  # preprocess + inference + postprocess (ms)
        names = [model.names[int(c)] for c in r.boxes.cls.tolist()]
        keep = [i for i, n in enumerate(names) if n in class_map]
        preds[p.name] = {
            "cls": np.array([class_map[names[i]] for i in keep], dtype=int),
            "conf": r.boxes.conf.cpu().numpy()[keep],
            "xyxy": r.boxes.xyxy.cpu().numpy()[keep],
            "hw": r.orig_shape,
        }
    return preds, float(np.mean(ms))


def match(pred_cls, pred_xyxy, gt_cls, gt_xyxy):
    """Ultralytics-style matching: TP[i, t] = prediction i hits an unmatched GT of the same class at IoU >= IOUV[t]."""
    tp = np.zeros((len(pred_cls), len(IOUV)), dtype=bool)
    if len(pred_cls) == 0 or len(gt_cls) == 0:
        return tp
    iou = box_iou(torch.tensor(gt_xyxy, dtype=torch.float32), torch.tensor(pred_xyxy, dtype=torch.float32)).numpy()
    iou = iou * (gt_cls[:, None] == pred_cls[None, :])
    for t, thr in enumerate(IOUV.tolist()):
        m = np.array(np.nonzero(iou >= thr)).T  # (gt, pred) pairs
        if m.shape[0]:
            m = np.concatenate((m, iou[m[:, 0], m[:, 1]][:, None]), 1)
            m = m[m[:, 2].argsort()[::-1]]
            m = m[np.unique(m[:, 1], return_index=True)[1]]
            m = m[np.unique(m[:, 0], return_index=True)[1]]
            tp[m[:, 1].astype(int), t] = True
    return tp


def evaluate(preds, gts):
    tps, confs, pcls, tcls = [], [], [], []
    for name, p in preds.items():
        g_cls, g_xyxy = gts[name]
        tps.append(match(p["cls"], p["xyxy"], g_cls, g_xyxy))
        confs.append(p["conf"]); pcls.append(p["cls"]); tcls.append(g_cls)
    tp, conf, pc, tc = (np.concatenate(x, 0) for x in (tps, confs, pcls, tcls))
    out = ap_per_class(tp, conf, pc, tc, names={i: n for i, n in enumerate(NAMES)})
    ap, ucls = out[5], out[6]  # ap: (n_classes_in_GT, 10 IoU thresholds)
    ap50 = {n: 0.0 for n in NAMES}
    ap5095 = {n: 0.0 for n in NAMES}
    for row, c in zip(ap, ucls):
        ap50[NAMES[int(c)]] = float(row[0])
        ap5095[NAMES[int(c)]] = float(row.mean())
    present = [NAMES[int(c)] for c in ucls]  # mAP = mean over classes that appear in the Test Set
    return {
        "mAP50": float(np.mean([ap50[n] for n in present])),
        "mAP50-95": float(np.mean([ap5095[n] for n in present])),
        "AP50_per_class": ap50,
        "AP50-95_per_class": ap5095,
    }


# 1) Ground truth + predictions of both models with the same settings
gts = {}
for p in images:
    h, w = cv2.imread(str(p)).shape[:2]
    gts[p.name] = load_gt(p, w, h)

t0 = time.time()
before_preds, before_ms = predict_all(BEFORE_W, COCO_TO_DS)
after_model_names = YOLO(AFTER_W).names
after_preds, after_ms = predict_all(AFTER_W, {n: CID[n] for n in after_model_names.values()})

before = evaluate(before_preds, gts) | {"ms_per_image": round(before_ms, 2)}
after = evaluate(after_preds, gts) | {"ms_per_image": round(after_ms, 2)}

gt_counts = {n: 0 for n in NAMES}
for c, _ in gts.values():
    for k in c:
        gt_counts[NAMES[int(k)]] += 1

metrics = {
    "test_images": len(images),
    "test_boxes_per_class": gt_counts,
    "settings": {"imgsz": IMGSZ, "conf": CONF_EVAL, "iou_nms": IOU_NMS, "batch": 1,
                 "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
                 "ms_per_image": "preprocess + inference + postprocess, mean over test images"},
    "class_mapping_before": {"person": "Person", "car": "vehicle", "bus": "vehicle", "truck": "vehicle",
                             "other dataset classes": "AP 0 (COCO has no such class)"},
    "before": {"model": "yolo11s.pt (COCO-pretrained)"} | before,
    "after": {"model": "best.pt (fine-tuned 50 epochs)"} | after,
    "eval_seconds": round(time.time() - t0, 1),
}
(OUT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps({k: metrics[k] for k in ("before", "after")}, indent=2))

# 2) Before/after side-by-side on 5 test images that contain both Hardhat and NO-Hardhat (ground truth)
COLORS = {"Hardhat": (0, 170, 0), "NO-Hardhat": (0, 0, 230), "Safety Vest": (0, 200, 255),
          "NO-Safety Vest": (180, 0, 200), "Person": (230, 120, 0), "vehicle": (128, 128, 128)}


def draw(img, pred, title):
    img = img.copy()
    for c, s, b in zip(pred["cls"], pred["conf"], pred["xyxy"]):
        if s < CONF_SHOW:
            continue
        n = NAMES[c]
        col = COLORS.get(n, (200, 200, 200))
        x1, y1, x2, y2 = map(int, b)
        cv2.rectangle(img, (x1, y1), (x2, y2), col, 2)
        txt = f"{n} {s:.2f}"
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, max(0, y1 - th - 6)), (x1 + tw + 4, max(th + 6, y1)), col, -1)
        cv2.putText(img, txt, (x1 + 2, max(th + 2, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    bar = np.full((40, img.shape[1], 3), 30, np.uint8)
    cv2.putText(bar, title, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return np.vstack([bar, img])


both = [p for p in images if CID["Hardhat"] in gts[p.name][0] and CID["NO-Hardhat"] in gts[p.name][0]]
both.sort(key=lambda p: -len(gts[p.name][0]))
# Too few in the ground truth? fill up with images where the fine-tuned model finds both (conf >= 0.35)
extra = [p for p in images if p not in both
         and all(((after_preds[p.name]["cls"] == CID[c]) & (after_preds[p.name]["conf"] >= CONF_SHOW)).any()
                 for c in ("Hardhat", "NO-Hardhat"))]
both += sorted(extra, key=lambda p: -len(gts[p.name][0]))
for i, p in enumerate(both[:5], 1):
    img = cv2.imread(str(p))
    pair = np.hstack([draw(img, before_preds[p.name], "BEFORE: yolo11s COCO"),
                      np.full((img.shape[0] + 40, 8, 3), 255, np.uint8),
                      draw(img, after_preds[p.name], "AFTER: fine-tuned")])
    cv2.imwrite(str(OUT_DIR / "images" / f"before_after_{i}.jpg"), pair, [cv2.IMWRITE_JPEG_QUALITY, 90])

# 3) Bar chart: AP50 per class, before vs after
x = np.arange(len(NAMES))
fig, ax = plt.subplots(figsize=(12, 5))
b1 = ax.bar(x - 0.2, [before["AP50_per_class"][n] for n in NAMES], 0.4, label="Before (COCO)", color="#9aa5b1")
b2 = ax.bar(x + 0.2, [after["AP50_per_class"][n] for n in NAMES], 0.4, label="After (fine-tuned)", color="#1f6feb")
ax.bar_label(b1, fmt="%.2f", fontsize=8); ax.bar_label(b2, fmt="%.2f", fontsize=8)
ax.set_xticks(x, NAMES, rotation=20); ax.set_ylim(0, 1.05); ax.set_ylabel("AP50")
ax.set_title(f"AP50 per class on Test Set ({len(images)} images) - mAP50 {before['mAP50']:.3f} -> {after['mAP50']:.3f}")
ax.legend(); ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(OUT_DIR / "images" / "ap50_per_class.png", dpi=150); plt.close(fig)

# 4) Training curves: loss and validation mAP per epoch (from results.csv of the training run)
with open(RUN_DIR / "results.csv") as f:
    rows = [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]
df = {k: [r[k] for r in rows] for k in rows[0]}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.5))
for col, lab in [("train/box_loss", "train box"), ("train/cls_loss", "train cls"), ("train/dfl_loss", "train dfl"),
                 ("val/box_loss", "val box"), ("val/cls_loss", "val cls")]:
    a1.plot(df["epoch"], df[col], label=lab, linestyle="--" if col.startswith("val") else "-")
a1.set_title("Loss per epoch"); a1.set_xlabel("Epoch"); a1.set_ylabel("Loss"); a1.legend(); a1.grid(alpha=0.3)
a2.plot(df["epoch"], df["metrics/mAP50(B)"], label="val mAP50")
a2.plot(df["epoch"], df["metrics/mAP50-95(B)"], label="val mAP50-95")
a2.set_title("Validation mAP per epoch"); a2.set_xlabel("Epoch"); a2.set_ylim(0, 1); a2.legend(); a2.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(OUT_DIR / "images" / "curves.png", dpi=150); plt.close(fig)

# 5) Web samples chosen by the fine-tuned model (conf >= 0.35):
#    fail = NO-Hardhat found · pass = no NO-Hardhat and at least as many hardhats as people
def shown(p, cls):
    pr = after_preds[p.name]
    return int(((pr["cls"] == CID[cls]) & (pr["conf"] >= CONF_SHOW)).sum())


def top_conf(p, cls):
    pr = after_preds[p.name]
    s = pr["conf"][(pr["cls"] == CID[cls]) & (pr["conf"] >= CONF_SHOW)]
    return float(s.max()) if len(s) else 0.0


fail = sorted([p for p in images if shown(p, "NO-Hardhat") > 0],
              key=lambda p: (-shown(p, "NO-Hardhat"), -top_conf(p, "NO-Hardhat")))[:3]
ok = sorted([p for p in images if shown(p, "NO-Hardhat") == 0 and shown(p, "Hardhat") >= 2
             and shown(p, "Hardhat") >= shown(p, "Person")],  # a hardhat for every person found
            key=lambda p: (-shown(p, "Hardhat"), -top_conf(p, "Hardhat")))[:3]
sdir = OUT_DIR / "samples"
shutil.rmtree(sdir, ignore_errors=True); sdir.mkdir(parents=True)
chosen = []
for tag, group in (("no_hardhat", fail), ("all_hardhat", ok)):
    for i, p in enumerate(group, 1):
        dst = f"{tag}_{i}.jpg"
        shutil.copy(p, sdir / dst)
        chosen.append({"file": dst, "source": p.name, "hardhat": shown(p, "Hardhat"),
                       "no_hardhat": shown(p, "NO-Hardhat"), "person": shown(p, "Person")})
(sdir / "samples.json").write_text(json.dumps(chosen, indent=2))
print("samples:", json.dumps(chosen, indent=2))
print(f"[done] {OUT_DIR}")
