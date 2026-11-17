# วัดผลบน Test Set: โมเดล COCO เดิม (ก่อนเทรน) เทียบกับโมเดลที่เทรนแล้ว (หลังเทรน)
# ผลลัพธ์: metrics.json, ภาพก่อน/หลัง, กราฟ loss/mAP ต่อ epoch
# ใช้: python eval.py --out /workspace/results
import argparse
import csv
import json
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import yaml
from ultralytics import YOLO
from ultralytics.utils.metrics import ap_per_class, box_iou

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--data", default="/workspace/data/ppe/data.yaml")
p.add_argument("--run", default="/workspace/runs/ppe")
p.add_argument("--base", default="yolo11s.pt")
p.add_argument("--out", default="/workspace/results")
p.add_argument("--pairs", type=int, default=5)
a = p.parse_args()

out = Path(a.out)
(out / "images").mkdir(parents=True, exist_ok=True)
cfg = yaml.safe_load(Path(a.data).read_text())
names = cfg["names"]
test_dir = Path(cfg["test"])
images = sorted(test_dir.glob("*.jpg")) + sorted(test_dir.glob("*.png"))
label_dir = test_dir.parent / "labels"

# โมเดล COCO รู้จัก person/car/bus/truck → จับคู่กับคลาสของ dataset ได้แค่ Person และ vehicle
COCO_TO_DS = {0: names.index("Person"), 2: names.index("vehicle"),
              5: names.index("vehicle"), 7: names.index("vehicle")}


def load_gt(img_path, w, h):
    f = label_dir / (img_path.stem + ".txt")
    rows = [list(map(float, ln.split())) for ln in f.read_text().splitlines() if ln.strip()] if f.exists() else []
    if not rows:
        return np.zeros((0,)), np.zeros((0, 4))
    r = np.array(rows)[:, :5]
    cls, xc, yc, bw, bh = r.T
    boxes = np.stack([(xc - bw / 2) * w, (yc - bh / 2) * h, (xc + bw / 2) * w, (yc + bh / 2) * h], 1)
    return cls, boxes


def match(pred_cls, gt_cls, iou, iouv):
    """จับคู่กรอบทำนายกับกรอบจริง (วิธีเดียวกับ Ultralytics) คืนค่า TP ต่อ IoU threshold"""
    correct = np.zeros((len(pred_cls), len(iouv)), bool)
    iou = iou * (gt_cls[:, None] == pred_cls[None, :])
    for i, t in enumerate(iouv):
        m = np.array(np.nonzero(iou >= t)).T
        if len(m):
            m = m[iou[m[:, 0], m[:, 1]].argsort()[::-1]]
            m = m[np.unique(m[:, 1], return_index=True)[1]]
            m = m[np.unique(m[:, 0], return_index=True)[1]]
            correct[m[:, 1], i] = True
    return correct


def evaluate(model, class_map=None):
    """mAP ต่อคลาสบน Test Set ด้วยโค้ดเดียวกันทั้งก่อนและหลังเทรน"""
    iouv = np.linspace(0.5, 0.95, 10)
    tps, confs, pcls, tcls, ms = [], [], [], [], []
    for img in images:
        r = model.predict(str(img), conf=0.001, iou=0.7, imgsz=640, verbose=False)[0]
        ms.append(sum(r.speed.values()))
        h, w = r.orig_shape
        gcls, gbox = load_gt(img, w, h)
        pb = r.boxes.xyxy.cpu().numpy()
        pc = r.boxes.cls.cpu().numpy().astype(int)
        cf = r.boxes.conf.cpu().numpy()
        if class_map is not None:  # แปลงคลาส COCO → คลาสของ dataset ทิ้งคลาสที่ไม่เกี่ยว
            keep = np.isin(pc, list(class_map))
            pb, cf = pb[keep], cf[keep]
            pc = np.array([class_map[c] for c in pc[keep]], dtype=int)
        tcls.append(gcls)
        if len(pc) == 0:
            continue
        if len(gcls):
            import torch
            iou = box_iou(torch.tensor(gbox, dtype=torch.float32), torch.tensor(pb, dtype=torch.float32)).numpy()
            tp = match(pc, gcls, iou, iouv)
        else:
            tp = np.zeros((len(pc), 10), bool)
        tps.append(tp), confs.append(cf), pcls.append(pc)
    tcls = np.concatenate(tcls)
    per = {n: {"ap50": 0.0, "ap50_95": 0.0} for n in names}
    if tps:
        res = ap_per_class(np.concatenate(tps), np.concatenate(confs), np.concatenate(pcls), tcls)
        ap, ucls = res[5], res[6]
        for k, c in enumerate(ucls):
            per[names[int(c)]] = {"ap50": round(float(ap[k, 0]), 4), "ap50_95": round(float(ap[k].mean()), 4)}
    for n in names:
        per[n]["instances"] = int((tcls == names.index(n)).sum())
    return {"mAP50": round(float(np.mean([v["ap50"] for v in per.values()])), 4),
            "mAP50_95": round(float(np.mean([v["ap50_95"] for v in per.values()])), 4),
            "ms_per_image": round(float(np.median(ms)), 1), "per_class": per}


base = YOLO(a.base)
tuned = YOLO(str(Path(a.run) / "weights" / "best.pt"))

# 1) ผลทางการของ Ultralytics บน Test Set (โมเดลหลังเทรน)
v = tuned.val(data=a.data, split="test", imgsz=640, batch=16, plots=False, verbose=False)
official = {"mAP50": round(float(v.box.map50), 4), "mAP50_95": round(float(v.box.map), 4),
            "precision": round(float(v.box.mp), 4), "recall": round(float(v.box.mr), 4)}

# 2) ก่อน vs หลัง ด้วยโค้ดวัดผลเดียวกัน
before = evaluate(base, COCO_TO_DS)
after = evaluate(tuned)

# 3) ภาพคู่ก่อน/หลัง: เลือกภาพหน้างานก่อสร้างที่มีทั้งคนสวมและไม่สวมหมวก
no_hat, hat = names.index("NO-Hardhat"), names.index("Hardhat")
vests = {names.index("Safety Vest"), names.index("NO-Safety Vest")}
score = []
for img in images:
    f = label_dir / (img.stem + ".txt")
    c = [int(ln.split()[0]) for ln in f.read_text().splitlines() if ln.strip()] if f.exists() else []
    n_no, n_hat, n_vest = c.count(no_hat), c.count(hat), sum(x in vests for x in c)
    score.append((n_no > 0) * (n_hat > 0) * (2 * n_no + n_hat + n_vest))
picked = [images[i] for i in np.argsort(score, kind="stable")[::-1][: a.pairs]]


def title(im, text):
    bar = np.full((44, im.shape[1], 3), 255, np.uint8)
    cv2.putText(bar, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (30, 30, 30), 2, cv2.LINE_AA)
    return np.vstack([bar, im])


pairs = []
for i, img in enumerate(picked, 1):
    rb = base.predict(str(img), conf=0.35, verbose=False)[0]
    ra = tuned.predict(str(img), conf=0.35, verbose=False)[0]
    n_before = int((rb.boxes.cls == 0).sum())  # COCO class 0 = person
    n_after = int((ra.boxes.cls == no_hat).sum())
    n_hat = int((ra.boxes.cls == hat).sum())
    left = title(rb.plot(line_width=2), f"Before (COCO): {n_before} person, 0 NO-Hardhat")
    right = title(ra.plot(line_width=2), f"After (fine-tuned): {n_hat} Hardhat, {n_after} NO-Hardhat")
    gap = np.full((left.shape[0], 12, 3), 255, np.uint8)
    cv2.imwrite(str(out / "images" / f"before_after_{i}.jpg"), np.hstack([left, gap, right]), [cv2.IMWRITE_JPEG_QUALITY, 88])
    pairs.append({"file": f"before_after_{i}.jpg", "image": img.name,
                  "after_hardhat": n_hat, "after_no_hardhat": n_after, "before_person": n_before})

# 4) กราฟ loss / mAP ต่อ epoch จาก results.csv
rows = list(csv.DictReader(open(Path(a.run) / "results.csv")))
df = {k.strip(): np.array([float(r[k]) for r in rows]) for k in rows[0]}
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(df["epoch"], df["train/box_loss"], label="train box loss")
ax[0].plot(df["epoch"], df["val/box_loss"], label="val box loss")
ax[0].plot(df["epoch"], df["train/cls_loss"], "--", label="train class loss")
ax[0].set(title="Loss per epoch", xlabel="epoch", ylabel="loss")
ax[1].plot(df["epoch"], df["metrics/mAP50(B)"], label="mAP50")
ax[1].plot(df["epoch"], df["metrics/mAP50-95(B)"], label="mAP50-95")
ax[1].set(title="Validation mAP per epoch", xlabel="epoch", ylabel="mAP", ylim=(0, 1))
for x in ax:
    x.grid(alpha=0.3)
    x.legend()
fig.tight_layout()
fig.savefig(out / "images" / "curves.png", dpi=130)

# 5) กราฟแท่ง AP50 ต่อคลาส ก่อน vs หลัง
fig, ax = plt.subplots(figsize=(11, 4))
x = np.arange(len(names))
ax.bar(x - 0.2, [before["per_class"][n]["ap50"] for n in names], 0.4, label="Before (COCO yolo11s)")
ax.bar(x + 0.2, [after["per_class"][n]["ap50"] for n in names], 0.4, label="After (fine-tuned)")
ax.set_xticks(x, names, rotation=25, ha="right")
ax.set(title="AP50 per class on the Test Set", ylabel="AP50", ylim=(0, 1))
ax.grid(axis="y", alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(out / "images" / "ap50_per_class.png", dpi=130)

info_f = Path(a.run) / "train_info.json"
metrics = {
    "dataset": {"name": "construction-site-safety v28 (Roboflow Universe, CC BY 4.0)",
                "train": len(list(Path(cfg["train"]).glob("*"))), "valid": len(list(Path(cfg["val"]).glob("*"))),
                "test": len(images), "classes": names},
    "train": json.loads(info_f.read_text()) if info_f.exists() else {},
    "epochs_run": int(df["epoch"].max()),
    "history": {k: [round(float(x), 4) for x in df[k]] for k in ["epoch", "time", "train/box_loss", "val/box_loss", "metrics/mAP50(B)", "metrics/mAP50-95(B)"] if k in df},
    "test_official_ultralytics": official,
    "before": before, "after": after, "before_after_images": pairs,
}
(out / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
print(json.dumps({"official": official, "before_mAP50": before["mAP50"], "after_mAP50": after["mAP50"],
                  "after_ms": after["ms_per_image"]}, indent=2))
