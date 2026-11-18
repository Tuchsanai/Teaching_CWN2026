"""Fine-tune YOLO11s (COCO-pretrained) on construction-site-safety v28.

Run on the rented GPU (from /workspace):  python code/train.py
Settings via env: EPOCHS (50) IMGSZ (640) BATCH (32) SEED (0) BASE_MODEL (yolo11s.pt) DATA_DIR OUT_DIR NAME
If the run stops (connection lost, crash), run the same command again: it resumes from last.pt.
"""
import json
import os
import time
from pathlib import Path

import yaml
from ultralytics import YOLO

DATA_DIR = Path(os.environ.get("DATA_DIR", "/workspace/datasets/construction-site-safety-28"))
OUT_DIR = Path(os.environ.get("OUT_DIR", "/workspace/runs"))
NAME = os.environ.get("NAME", "ppe_yolo11s")
EPOCHS = int(os.environ.get("EPOCHS", "50"))
IMGSZ = int(os.environ.get("IMGSZ", "640"))
BATCH = int(os.environ.get("BATCH", "32"))
SEED = int(os.environ.get("SEED", "0"))
BASE_MODEL = os.environ.get("BASE_MODEL", "yolo11s.pt")

# 1) Dataset config with absolute paths (the Roboflow data.yaml uses relative "../train/images")
src = yaml.safe_load((DATA_DIR / "data.yaml").read_text())
data_cfg = {
    "path": str(DATA_DIR),
    "train": "train/images",
    "val": "valid/images",
    "test": "test/images",
    "names": src["names"],
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
data_yaml = OUT_DIR / "data_abs.yaml"
data_yaml.write_text(yaml.safe_dump(data_cfg, sort_keys=False))

# 2) Progress line after every epoch (validation runs each epoch)
def on_fit_epoch_end(trainer):
    m = trainer.metrics
    t = trainer.tloss  # running-mean losses (dict in ultralytics 8.4, tensor in older versions)
    loss = [float(v) for v in (t.values() if isinstance(t, dict) else t)] if t is not None else [0, 0]
    print(
        f"[progress] epoch {trainer.epoch + 1}/{trainer.epochs} "
        f"box_loss={loss[0]:.3f} cls_loss={loss[1]:.3f} "
        f"val_mAP50={m.get('metrics/mAP50(B)', 0):.4f} "
        f"val_mAP50-95={m.get('metrics/mAP50-95(B)', 0):.4f} "
        f"elapsed={time.time() - T0:.0f}s",
        flush=True,
    )

# 3) Start fresh from COCO weights, or resume if a previous run left last.pt
last = OUT_DIR / NAME / "weights" / "last.pt"
info_path = OUT_DIR / NAME / "train_info.json"
prev_seconds = json.loads(info_path.read_text())["train_seconds"] if info_path.exists() else 0.0
T0 = time.time()
if last.exists():
    print(f"[progress] resuming from {last}", flush=True)
    model = YOLO(str(last))
    model.add_callback("on_fit_epoch_end", on_fit_epoch_end)
    model.train(resume=True)
else:
    model = YOLO(BASE_MODEL)  # COCO-pretrained
    model.add_callback("on_fit_epoch_end", on_fit_epoch_end)
    model.train(
        data=str(data_yaml), epochs=EPOCHS, imgsz=IMGSZ, batch=BATCH, seed=SEED,
        deterministic=True, workers=8, project=str(OUT_DIR), name=NAME, exist_ok=True,
    )

# 4) Record training time (adds up across resumes)
train_seconds = prev_seconds + (time.time() - T0)
info = {
    "model": f"{BASE_MODEL} (COCO) -> fine-tuned",
    "epochs": EPOCHS, "imgsz": IMGSZ, "batch": BATCH, "seed": SEED,
    "train_seconds": round(train_seconds, 1),
    "train_minutes": round(train_seconds / 60, 2),
    "best": str(OUT_DIR / NAME / "weights" / "best.pt"),
}
info_path.write_text(json.dumps(info, indent=2))
print(f"[done] training time {info['train_minutes']} min -> {info_path}", flush=True)
