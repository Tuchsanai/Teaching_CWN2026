"""AI server for the fine-tuned PPE detector (YOLO11s).

Run on the rented GPU:  python serve.py
- Loads best.pt once and keeps it on the GPU.
- Listens on 0.0.0.0:8080.
- On first start it creates a random API key and saves it to API_KEY_FILE (reused on restart).

Routes
  GET  /health      -> {"ready", "model", "classes"}           (no key)
  POST /v1/detect   -> multipart field "file" + "Authorization: Bearer <key>"
"""
import io
import os
import secrets
import time
from pathlib import Path

import torch
import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from PIL import Image
from ultralytics import YOLO

WEIGHTS = os.environ.get("WEIGHTS", "/workspace/runs/ppe_yolo11s/weights/best.pt")
API_KEY_FILE = Path(os.environ.get("API_KEY_FILE", "/workspace/serve_api_key.txt"))
MODEL_NAME = "ppe-yolo11s"
CONF_MIN = 0.35
PORT = int(os.environ.get("PORT", "8080"))

# 1) API key: create once, keep it across restarts (never printed)
if API_KEY_FILE.exists() and API_KEY_FILE.read_text().strip():
    API_KEY = API_KEY_FILE.read_text().strip()
else:
    API_KEY = "sk-" + secrets.token_urlsafe(32)
    API_KEY_FILE.write_text(API_KEY)
    API_KEY_FILE.chmod(0o600)
    print(f"[serve] new API key saved to {API_KEY_FILE}", flush=True)

# 2) Load the model once and keep it on the GPU (warm-up so the first request is fast)
DEVICE = 0 if torch.cuda.is_available() else "cpu"
model = YOLO(WEIGHTS)
model.predict(Image.new("RGB", (640, 640)), device=DEVICE, verbose=False)
CLASSES = [model.names[i] for i in sorted(model.names)]
print(f"[serve] {MODEL_NAME} loaded on {DEVICE}, {len(CLASSES)} classes", flush=True)

app = FastAPI(title="PPE detector")
bearer = HTTPBearer(auto_error=False)


def check_key(cred: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if cred is None or cred.scheme.lower() != "bearer" or not secrets.compare_digest(cred.credentials, API_KEY):
        raise HTTPException(status_code=401, detail="missing or invalid API key")


@app.get("/health")
def health():
    return {"ready": True, "model": MODEL_NAME, "classes": CLASSES}


@app.post("/v1/detect", dependencies=[Depends(check_key)])
async def detect(file: UploadFile = File(...)):
    try:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="file is not a readable image")

    t0 = time.perf_counter()
    r = model.predict(img, device=DEVICE, conf=CONF_MIN, verbose=False)[0]
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    inference_ms = (time.perf_counter() - t0) * 1000

    detections = []
    for xyxy, conf, cls in zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist(), r.boxes.cls.tolist()):
        if conf < CONF_MIN:
            continue
        detections.append({
            "class": model.names[int(cls)],
            "confidence": round(conf, 4),
            "box": [round(v, 1) for v in xyxy],  # x1, y1, x2, y2 in pixels
        })

    return {
        "model": MODEL_NAME,
        "width": img.width,
        "height": img.height,
        "inference_ms": round(inference_ms, 1),
        "detections": detections,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
