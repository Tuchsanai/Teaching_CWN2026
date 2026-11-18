"""LAB 6 · AI server ตรวจภาพ (YOLO PPE) ด้วย FastAPI

ตั้งค่าด้วย environment variable
  API_KEY      key สำหรับ Bearer (จำเป็น)
  MODEL_PATH   path ของ best.pt               (ค่าเริ่ม best.pt)
  MODE         single | microbatch            (ค่าเริ่ม single)
  MAX_BATCH    รูปสูงสุดต่อการเรียกโมเดล      (single = 1, microbatch = 32)
  MAX_WAIT_MS  เวลารอรวมคำขอเพิ่ม (ms)        (ค่าเริ่ม 5, ใช้เฉพาะ microbatch)
  REPLICA      ชื่อ replica ที่ใส่ในคำตอบ      (ค่าเริ่ม hostname-gpu<id>)
  IMGSZ / CONF ขนาดภาพ / ความมั่นใจขั้นต่ำ      (640 / 0.35)
  SLOW_MS      หน่วงเพิ่มรูปละกี่ ms (จำลอง GPU ช้า) (ค่าเริ่ม 0 = ไม่หน่วง)

รัน:  CUDA_VISIBLE_DEVICES=0 uvicorn server:app --host 0.0.0.0 --port 8080
"""
import asyncio
import hmac
import os
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO

API_KEY = os.environ.get("API_KEY", "")
MODEL_PATH = os.environ.get("MODEL_PATH", "best.pt")
MODE = os.environ.get("MODE", "single").lower()
MAX_BATCH = int(os.environ.get("MAX_BATCH", "1" if MODE == "single" else "32"))
MAX_WAIT_MS = float(os.environ.get("MAX_WAIT_MS", "5"))
IMGSZ = int(os.environ.get("IMGSZ", "640"))
CONF = float(os.environ.get("CONF", "0.35"))
SLOW_MS = float(os.environ.get("SLOW_MS", "0"))
REPLICA = os.environ.get(
    "REPLICA", f"{socket.gethostname()}-gpu{os.environ.get('CUDA_VISIBLE_DEVICES', '0')}"
)
if MODE == "single":
    MAX_BATCH = 1
if not API_KEY:
    raise SystemExit("ต้องตั้ง API_KEY ก่อนเปิด server")

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
# เรียกโมเดลจาก thread เดียวเสมอ: cuDNN เก็บแผนการคำนวณแยกต่อ thread x ขนาด batch
# ถ้าสลับ thread ทุกครั้ง (asyncio.to_thread) จะต้องสร้างแผนใหม่ครั้งละ ~2.6 วินาที
GPU_THREAD = ThreadPoolExecutor(max_workers=1, thread_name_prefix="gpu")


@dataclass
class Job:
    tensor: np.ndarray            # ภาพ letterbox 3x640x640 (float32 0–1)
    meta: tuple                   # (ratio, pad_x, pad_y, w0, h0) สำหรับแปลงกล่องกลับ
    t_enqueue: float
    future: asyncio.Future = field(default=None)


state = {"ready": False, "warmed": [], "model": None, "queue": None}


# ---------- แปลงรูป (CPU) ----------
def letterbox(img: np.ndarray):
    """ย่อ/ขยายรักษาสัดส่วนแล้วเติมขอบให้เป็น IMGSZ x IMGSZ เสมอ → shape คงที่ทุกคำขอ"""
    h0, w0 = img.shape[:2]
    r = min(IMGSZ / h0, IMGSZ / w0)
    nw, nh = round(w0 * r), round(h0 * r)
    if (nw, nh) != (w0, h0):
        img = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    px, py = (IMGSZ - nw) // 2, (IMGSZ - nh) // 2
    canvas = np.full((IMGSZ, IMGSZ, 3), 114, dtype=np.uint8)
    canvas[py:py + nh, px:px + nw] = img
    x = canvas[:, :, ::-1].transpose(2, 0, 1)  # BGR→RGB, HWC→CHW
    return np.ascontiguousarray(x, dtype=np.float32) / 255.0, (r, px, py, w0, h0)


def decode(data: bytes):
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไฟล์ไม่ใช่รูปภาพ")
    return letterbox(img)


# ---------- เรียกโมเดล (GPU ทีละครั้ง) ----------
def run_model(batch: np.ndarray):
    x = torch.from_numpy(batch).to(DEVICE)
    with torch.inference_mode():
        res = state["model"].predict(x, imgsz=IMGSZ, conf=CONF, device=DEVICE,
                                     half=DEVICE != "cpu", verbose=False)
    if DEVICE != "cpu":
        torch.cuda.synchronize()
    return res


def run_model_served(batch: np.ndarray):
    """เรียกโมเดลสำหรับคำขอจริง: ถ้าตั้ง SLOW_MS จะถือ GPU thread ไว้เพิ่มรูปละ SLOW_MS
    (batch b รูป หน่วงเพิ่ม b x SLOW_MS) เหมือน GPU ที่ช้ากว่าใบอื่น — warmup ไม่หน่วง"""
    res = run_model(batch)
    if SLOW_MS > 0:
        time.sleep(len(batch) * SLOW_MS / 1000)
    return res


def to_detections(result, meta):
    r, px, py, w0, h0 = meta
    names = result.names
    out = []
    if result.boxes is None:
        return out
    xyxy = result.boxes.xyxy.cpu().numpy()
    confs = result.boxes.conf.cpu().numpy()
    clss = result.boxes.cls.cpu().numpy().astype(int)
    for (x1, y1, x2, y2), c, k in zip(xyxy, confs, clss):
        x1 = float(np.clip((x1 - px) / r, 0, w0)); x2 = float(np.clip((x2 - px) / r, 0, w0))
        y1 = float(np.clip((y1 - py) / r, 0, h0)); y2 = float(np.clip((y2 - py) / r, 0, h0))
        out.append({"class": names[int(k)], "confidence": round(float(c), 4),
                    "box": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)]})
    return out


async def batch_worker():
    """ตัวเดียวที่เรียกโมเดล: ดึงคำขอจากคิว รวมเป็น batch (ไม่เกิน MAX_BATCH) แล้วเรียกครั้งเดียว"""
    q: asyncio.Queue = state["queue"]
    loop = asyncio.get_running_loop()
    while True:
        jobs = [await q.get()]
        if MAX_BATCH > 1:
            deadline = loop.time() + MAX_WAIT_MS / 1000
            while len(jobs) < MAX_BATCH:
                try:  # หยิบที่รออยู่ในคิวก่อน แล้วค่อยรอเพิ่มไม่เกิน MAX_WAIT_MS
                    jobs.append(q.get_nowait())
                    continue
                except asyncio.QueueEmpty:
                    pass
                left = deadline - loop.time()
                if left <= 0:
                    break
                try:
                    jobs.append(await asyncio.wait_for(q.get(), left))
                except asyncio.TimeoutError:
                    break
        t_start = time.perf_counter()
        try:
            batch = np.stack([j.tensor for j in jobs])
            results = await loop.run_in_executor(GPU_THREAD, run_model_served, batch)
            infer_ms = (time.perf_counter() - t_start) * 1000
            for j, res in zip(jobs, results):
                if not j.future.done():
                    j.future.set_result((to_detections(res, j.meta),
                                         (t_start - j.t_enqueue) * 1000, infer_ms, len(jobs)))
        except Exception as e:  # ส่ง error กลับทุกคำขอใน batch
            for j in jobs:
                if not j.future.done():
                    j.future.set_exception(e)


def warmup():
    """อุ่นโมเดลทุกขนาด batch 1..MAX_BATCH ให้ CUDA/cuDNN เตรียม kernel ไว้ก่อนรับคำขอจริง"""
    state["model"] = YOLO(MODEL_PATH)
    dummy = np.random.rand(MAX_BATCH, 3, IMGSZ, IMGSZ).astype(np.float32)
    run_model(dummy[:1])  # รอบแรก: โหลดโมเดลขึ้น GPU + fuse layer
    for b in range(1, MAX_BATCH + 1):
        run_model(dummy[:b])
        state["warmed"].append(b)


async def startup():
    await asyncio.get_running_loop().run_in_executor(GPU_THREAD, warmup)
    state["worker"] = asyncio.create_task(batch_worker())
    state["ready"] = True  # /health ตอบ 200 หลังอุ่นครบทุกขนาด batch เท่านั้น


@asynccontextmanager
async def lifespan(app: FastAPI):
    # เปิดพอร์ตทันที (/health ตอบ 503 "warming") แล้วอุ่นโมเดลอยู่เบื้องหลัง
    state["queue"] = asyncio.Queue()
    boot = asyncio.create_task(startup())
    yield
    boot.cancel()
    if state.get("worker"):
        state["worker"].cancel()


app = FastAPI(title="PPE detection API", lifespan=lifespan)


def check_key(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing API key", headers={"WWW-Authenticate": "Bearer"})
    if not hmac.compare_digest(authorization[7:].strip(), API_KEY):
        raise HTTPException(401, "invalid API key", headers={"WWW-Authenticate": "Bearer"})


@app.get("/health")
async def health():
    body = {"status": "ready" if state["ready"] else "warming", "replica": REPLICA,
            "mode": MODE, "max_batch": MAX_BATCH, "slow_ms_per_image": SLOW_MS, "max_wait_ms": MAX_WAIT_MS if MAX_BATCH > 1 else 0,
            "warmed_batch_sizes": f"1-{max(state['warmed'])}" if state["warmed"] else "none",
            "queue_depth": state["queue"].qsize() if state["queue"] else 0, "device": DEVICE}
    return JSONResponse(body, status_code=200 if state["ready"] else 503)


@app.post("/v1/detect")
async def detect(file: UploadFile = File(...), authorization: str | None = Header(None)):
    check_key(authorization)
    if not state["ready"]:
        raise HTTPException(503, "model warming up")
    t0 = time.perf_counter()
    data = await file.read()
    try:
        tensor, meta = await asyncio.to_thread(decode, data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    decode_ms = (time.perf_counter() - t0) * 1000
    fut = asyncio.get_running_loop().create_future()
    await state["queue"].put(Job(tensor, meta, time.perf_counter(), fut))
    dets, queue_ms, infer_ms, bs = await fut
    return {
        "detections": dets,
        "count": len(dets),
        "replica": REPLICA,
        "timing_ms": {"decode": round(decode_ms, 2), "queue": round(queue_ms, 2),
                      "inference": round(infer_ms, 2)},
        "batch_size": bs,
        "image": {"width": meta[3], "height": meta[4]},
    }
