# เทรน YOLO ต่อจากโมเดล COCO ด้วย dataset PPE แล้ว export เป็น ONNX
# ใช้: python train.py --epochs 50
import argparse
import json
import time
from pathlib import Path

from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("--data", default="/workspace/data/ppe/data.yaml")
p.add_argument("--model", default="yolo11s.pt")  # โมเดลตั้งต้นที่เทรนบน COCO มาแล้ว
p.add_argument("--epochs", type=int, default=50)
p.add_argument("--imgsz", type=int, default=640)
p.add_argument("--batch", type=int, default=32)
p.add_argument("--workers", type=int, default=8)
p.add_argument("--device", default="0")
p.add_argument("--fraction", type=float, default=1.0)  # ใช้ข้อมูลบางส่วน (ทดสอบสคริปต์เร็ว ๆ)
p.add_argument("--out", default="/workspace/runs")
a = p.parse_args()

t0 = time.time()
model = YOLO(a.model)
model.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch, workers=a.workers,
            device=a.device, fraction=a.fraction, project=str(Path(a.out).resolve()), name="ppe", exist_ok=True, plots=True, seed=0)
train_sec = time.time() - t0

run = Path(model.trainer.save_dir)  # โฟลเดอร์ผลการเทรน เช่น /workspace/runs/ppe
best = run / "weights" / "best.pt"

# export เป็น ONNX (ไม่บังคับ ถ้าไม่ผ่านก็ข้าม)
onnx_ok = False
try:
    YOLO(str(best)).export(format="onnx", imgsz=a.imgsz, dynamic=False)
    onnx_ok = (run / "weights" / "best.onnx").exists()
except Exception as e:  # noqa: BLE001
    print("ONNX export ไม่ผ่าน:", e)

info = {"base_model": a.model, "epochs": a.epochs, "imgsz": a.imgsz, "batch": a.batch,
        "train_seconds": round(train_sec, 1), "onnx_exported": onnx_ok}
(run / "train_info.json").write_text(json.dumps(info, indent=2))
print(json.dumps(info, indent=2))
