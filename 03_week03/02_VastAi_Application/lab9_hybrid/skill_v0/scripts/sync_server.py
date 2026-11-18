"""LAB 9: synchronous text-to-image API (caller waits until the JPEG is ready).

POST /generate {"prompt": "..."} + header X-API-Key -> image/jpeg
GET  /health, GET /stats  (stats: requests received, images done)
SDXL-Turbo, 512x512, 4 steps, GPU 0, one image at a time; extra requests wait in line.
Run: uvicorn sync_server:app --host 0.0.0.0 --port 8000 --backlog 2048
"""
import asyncio, io, os, secrets, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

MODEL, SIZE, STEPS, DEVICE = "stabilityai/sdxl-turbo", 512, 4, "cuda:0"
KEY_FILE = Path(os.environ.get("API_KEY_FILE", "/workspace/lab9/api_key.txt"))

# --- 1) API key: random once, kept in a file only the owner can read ---
if not KEY_FILE.exists():
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(secrets.token_urlsafe(32))
    KEY_FILE.chmod(0o600)
API_KEY = KEY_FILE.read_text().strip()

# --- 2) model: loaded once on the first GPU, warmed up before serving ---
pipe = AutoPipelineForText2Image.from_pretrained(MODEL, torch_dtype=torch.float16, variant="fp16").to(DEVICE)
pipe.set_progress_bar_config(disable=True)
pipe(prompt="warm up", num_inference_steps=STEPS, guidance_scale=0.0, height=SIZE, width=SIZE)

# --- 3) one worker thread = one image at a time; waiting requests queue up in front of it ---
gpu = ThreadPoolExecutor(max_workers=1)
stats = {"received": 0, "done": 0, "failed": 0, "gen_seconds_total": 0.0, "started": time.time()}
lock = threading.Lock()

def make_jpeg(prompt: str) -> bytes:
    t = time.perf_counter()
    img = pipe(prompt=prompt, num_inference_steps=STEPS, guidance_scale=0.0, height=SIZE, width=SIZE).images[0]
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=90)
    with lock:
        stats["done"] += 1; stats["gen_seconds_total"] += time.perf_counter() - t
    return buf.getvalue()

# --- 4) HTTP endpoints ---
app = FastAPI(title="LAB 9 sync image API")

class GenReq(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)

@app.post("/generate", responses={200: {"content": {"image/jpeg": {}}}})
async def generate(req: GenReq, x_api_key: str | None = Header(default=None)):
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(401, "invalid or missing API key")
    with lock:
        stats["received"] += 1
    t = time.perf_counter()
    try:
        jpeg = await asyncio.get_running_loop().run_in_executor(gpu, make_jpeg, req.prompt)
    except Exception as e:
        with lock: stats["failed"] += 1
        raise HTTPException(500, f"generation failed: {type(e).__name__}")
    return Response(jpeg, media_type="image/jpeg",
                    headers={"X-Total-Seconds": f"{time.perf_counter() - t:.3f}"})

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "gpu": torch.cuda.get_device_name(0)}

@app.get("/stats")
def get_stats():
    with lock:
        s = dict(stats)
    return {"received": s["received"], "done": s["done"], "failed": s["failed"],
            "waiting_or_running": s["received"] - s["done"] - s["failed"],
            "avg_gen_seconds": round(s["gen_seconds_total"] / s["done"], 3) if s["done"] else None,
            "uptime_seconds": round(time.time() - s["started"])}
