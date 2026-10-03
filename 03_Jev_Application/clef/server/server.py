"""Clef-NVFP4 SystemOne API บน vLLM (RTX 5090 / Blackwell — NVFP4 native)

POST /v1/systemone   (Bearer CLEF_API_KEY)   GET /health
"""
import base64, gc, io, os, sys, threading, time

import requests
import torch
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from huggingface_hub import snapshot_download
from PIL import Image

MODEL_DIR = snapshot_download("simonlehmann/clef-NVFP4", local_dir=os.environ.get("CLEF_DIR", "/workspace/clef-NVFP4"))
sys.path.insert(0, MODEL_DIR)
from clef_vllm import ClefVLLM  # noqa: E402

API_KEY = os.environ["CLEF_API_KEY"]
MAX_SIDE = int(os.environ.get("CLEF_MAX_IMAGE_SIDE", "1024"))
clef = ClefVLLM(MODEL_DIR,
                max_model_len=int(os.environ.get("CLEF_MAX_MODEL_LEN", "16384")),
                gpu_memory_utilization=float(os.environ.get("CLEF_GPU_UTIL", "0.85")),
                max_images=int(os.environ.get("CLEF_MAX_IMAGES", "4")),
                # server ทำทีละ request (lock) — default max_num_seqs=256 ทำให้ state ของ linear-attention
                # ตอน profile cudagraph จองเกิน 12 GiB จน OOM บน 32 GB
                max_num_seqs=int(os.environ.get("CLEF_MAX_NUM_SEQS", "4")))
lock = threading.Lock()
app = FastAPI(title="clef-NVFP4")


def load_image(src):
    if not isinstance(src, str):
        raise ValueError("images must be URL or data URI strings")
    if src.startswith("data:"):
        raw = base64.b64decode(src.split(",", 1)[1])
    elif src.startswith(("http://", "https://")):
        r = requests.get(src, timeout=20, headers={"User-Agent": "clef-server"})
        r.raise_for_status(); raw = r.content
    else:
        raise ValueError("images must be http(s) URL or data URI")
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))  # ย่อก่อนให้ทั้ง HF processor และ vLLM เห็นรูปเดียวกัน
    return img


@app.get("/health")
def health():
    free, total = torch.cuda.mem_get_info()
    return {"ok": True, "model": "clef-NVFP4", "gpu": torch.cuda.get_device_name(0),
            "vram_used_gib": round((total - free) / 2**30, 2), "vram_total_gib": round(total / 2**30, 2)}


@app.post("/v1/systemone")
async def systemone(request: Request, authorization: str = Header(default="")):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(401, "invalid api key")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "body must be JSON")
    t0 = time.perf_counter()
    try:
        if body.get("images"):
            body["images"] = [load_image(x) for x in body["images"]]
        with lock:
            res = clef.systemone(body)
    except (ValueError, KeyError, TypeError) as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except requests.RequestException as e:
        return JSONResponse({"error": f"image download failed: {e}"}, status_code=400)
    except torch.OutOfMemoryError:
        gc.collect(); torch.cuda.empty_cache()
        return JSONResponse({"error": "GPU out of memory"}, status_code=503)
    res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return res
