# Training: เทรน YOLO ต่อจากโมเดลที่เทรนบน COCO มาแล้ว ด้วย Dataset ของเรา
# ใช้: python train.py --epochs 50        (หา Dataset รูปแบบ YOLO ใต้ /workspace เอง หรือระบุ --data โฟลเดอร์)
# ต้องมี: ultralytics
import argparse
import json
import sys
import time
from pathlib import Path

import torch
import yaml
from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("--data", default="")  # โฟลเดอร์ Dataset (มี train/ valid/ test/ data.yaml) เว้นว่าง = หาเอง
p.add_argument("--model", default="yolo11s.pt")  # โมเดลตั้งต้น (Pre-trained บน COCO)
p.add_argument("--epochs", type=int, default=50)
p.add_argument("--batch", type=int, default=32)
p.add_argument("--device", default="0")  # "cpu" ใช้ทดสอบสคริปต์เท่านั้น
p.add_argument("--fraction", type=float, default=1.0)  # ใช้ข้อมูลบางส่วน (ทดสอบสคริปต์เร็ว ๆ)
p.add_argument("--out", default="/workspace/runs")
a = p.parse_args()

if a.device != "cpu" and not torch.cuda.is_available():
    sys.exit("ไม่พบ GPU (torch.cuda.is_available() = False) — ตรวจเครื่องก่อนเทรน")

# data.yaml จาก Roboflow ใช้ path แบบ ../train ซึ่งชี้ผิดที่ได้ → เขียนใหม่เป็น path เต็ม
if not a.data:  # หาโฟลเดอร์ที่มี data.yaml และ train/images ใต้ /workspace และโฟลเดอร์ปัจจุบัน
    found = [f.parent for base in ("/workspace", ".") for f in sorted(Path(base).glob("**/data.yaml"))
             if (f.parent / "train" / "images").is_dir()]
    if not found:
        sys.exit("ไม่พบ Dataset (data.yaml + train/images) ใต้ /workspace — ดาวน์โหลดก่อน หรือระบุ --data")
    a.data = str(found[0])
root = Path(a.data).resolve()
print("Dataset:", root)
cfg = yaml.safe_load((root / "data.yaml").read_text())
for split, folder in [("train", "train"), ("val", "valid"), ("test", "test")]:
    d = root / folder / "images"
    if not d.is_dir():
        sys.exit(f"ไม่พบโฟลเดอร์ {d} — ดาวน์โหลด Dataset ให้ครบก่อน")
    cfg[split] = str(d)
    print(f"{folder}: {len(list(d.glob('*')))} ภาพ")
cfg.pop("path", None)
(root / "data.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))

model = YOLO(a.model)
# พิมพ์ 1 บรรทัดต่อ 1 Epoch ให้ตามความคืบหน้าได้ง่าย (grep PROGRESS ใน log)
model.add_callback("on_fit_epoch_end", lambda t: print(
    f"PROGRESS Epoch {t.epoch + 1}/{t.epochs} Validation mAP50={t.metrics.get('metrics/mAP50(B)', 0):.3f}", flush=True))

t0 = time.time()
model.train(data=str(root / "data.yaml"), epochs=a.epochs, imgsz=640, batch=a.batch, workers=8, device=a.device,
            fraction=a.fraction, project=str(Path(a.out).resolve()), name="ppe", exist_ok=True, plots=True, seed=0)
run = Path(model.trainer.save_dir)  # /workspace/runs/ppe

info = {"base_model": a.model, "epochs": a.epochs, "imgsz": 640, "batch": a.batch,
        "train_seconds": round(time.time() - t0, 1),
        "gpu": torch.cuda.get_device_name(0) if a.device != "cpu" else "cpu"}
(run / "train_info.json").write_text(json.dumps(info, indent=2))
print("DONE", json.dumps(info), "→", run / "weights" / "best.pt")
