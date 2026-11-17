# AI server ตรวจ PPE: รับรูป → คืนกรอบ/คลาส/ความมั่นใจเป็น JSON
# ใช้: python serve.py   (เปิดพอร์ต 8080 · API key อยู่ที่ /workspace/yolo_api_key.txt ถ้ายังไม่มีจะสุ่มให้)
# ต้องมี: ultralytics fastapi uvicorn python-multipart
import io
import os
import secrets
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from PIL import Image
from ultralytics import YOLO

WEIGHTS = os.environ.get("YOLO_WEIGHTS", "/workspace/runs/ppe/weights/best.pt")
MODEL_NAME = os.environ.get("YOLO_MODEL", "ppe-yolo11s")
KEY_FILE = Path(os.environ.get("YOLO_API_KEY_FILE", "/workspace/yolo_api_key.txt"))
if not KEY_FILE.exists():  # สุ่ม key ครั้งแรก แล้วใช้ค่าเดิมทุกครั้งที่เปิด server ใหม่
    KEY_FILE.write_text(secrets.token_hex(24))
API_KEY = KEY_FILE.read_text().strip()

model = YOLO(WEIGHTS)
model.predict(Image.new("RGB", (640, 640)), verbose=False)  # อุ่นเครื่อง GPU ก่อนรับงานจริง
app = FastAPI(title="PPE detector")


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME, "classes": list(model.names.values())}


@app.post("/v1/detect")
async def detect(file: UploadFile = File(...), conf: float = 0.35, authorization: str = Header("")):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(401, "invalid api key")
    try:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception:  # noqa: BLE001
        raise HTTPException(400, "not an image")
    t0 = time.perf_counter()
    r = model.predict(img, conf=conf, imgsz=640, verbose=False)[0]
    total_ms = (time.perf_counter() - t0) * 1000
    dets = [{"class": model.names[int(c)], "confidence": round(float(s), 3),
             "box": [round(float(v), 1) for v in b]}
            for b, c, s in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist())]
    return {"model": MODEL_NAME, "width": img.width, "height": img.height,
            "inference_ms": round(r.speed["inference"], 1), "total_ms": round(total_ms, 1),
            "detections": dets}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
