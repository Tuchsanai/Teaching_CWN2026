"""LAB 8 baseline: synchronous receipt-reading API on ONE GPU (no job queue service).

POST /v1/jobs  (header X-API-Key, multipart field "files" = receipt images)
  -> the request waits on the same HTTP connection until the job is done and
     returns {"job_id", "receipts": [{file, ok, data:{items,subtotal,tax,total}}], timings}
GET  /v1/stats (header X-API-Key) -> how many jobs are done, waiting, running ...
GET  /health   (no key)

Design
- One worker thread owns the model on the first GPU (cuda:0) and reads one job at
  a time, one receipt at a time, greedy decoding (do_sample=False).
- Other jobs wait in an in-process FIFO (asyncio side) inside the server.
- If the client goes away (timeout / dropped connection) the server keeps going:
  the job is still read and counted as "read after the client left".

Run (keep it alive after SSH drops):
  LAB8_KEY_FILE=/workspace/lab8/.api_key setsid nohup python sync_api.py > server.log 2>&1 &
"""
import asyncio
import io
import json
import os
import re
import threading
import time
import uuid
from collections import deque
from concurrent.futures import Future

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")  # first GPU only

import torch
import uvicorn
from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

MODEL_DIR = os.environ.get("LAB8_MODEL", "/workspace/models/Qwen3-VL-2B-Instruct")
KEY_FILE = os.environ.get("LAB8_KEY_FILE", "/workspace/lab8/.api_key")
PORT = int(os.environ.get("LAB8_PORT", "8000"))
MAX_NEW_TOKENS = int(os.environ.get("LAB8_MAX_NEW_TOKENS", "512"))
MAX_FILES = 8

PROMPT = (
    "Read this receipt and return ONLY one JSON object, no other text, in this exact shape:\n"
    '{"items": [{"name": string, "qty": number, "price": number}], '
    '"subtotal": number or null, "tax": number or null, "total": number or null}\n'
    "price = the line amount printed for the item. Write numbers without thousand "
    "separators (60.000 -> 60000). Use null when a value is not printed."
)


def load_key():
    with open(KEY_FILE) as f:
        return f.read().strip()


API_KEY = load_key()

# ------------------------------------------------------------------ model
processor = AutoProcessor.from_pretrained(MODEL_DIR)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_DIR, dtype=torch.bfloat16, device_map="cuda:0", attn_implementation="sdpa"
).eval()


def _num(v):
    if v is None or isinstance(v, (int, float)):
        return v
    s = re.sub(r"[^0-9.\-]", "", str(v))
    if s.count(".") == 1 and len(s.split(".")[1]) == 3:  # 60.000 style thousands
        s = s.replace(".", "")
    try:
        return float(s) if "." in s else int(s)
    except ValueError:
        return None


def parse_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    d = json.loads(m.group(0))
    items = []
    for it in d.get("items") or []:
        if isinstance(it, dict):
            items.append({"name": str(it.get("name", "")), "qty": _num(it.get("qty")),
                          "price": _num(it.get("price"))})
    return {"items": items, "subtotal": _num(d.get("subtotal")),
            "tax": _num(d.get("tax")), "total": _num(d.get("total"))}


@torch.inference_mode()
def read_receipt(img: Image.Image):
    messages = [{"role": "user", "content": [{"type": "image", "image": img},
                                             {"type": "text", "text": PROMPT}]}]
    inputs = processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                           return_dict=True, return_tensors="pt").to("cuda:0")
    out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    text = processor.batch_decode(out[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0]
    return text


# ------------------------------------------------------------------ state
lock = threading.Lock()
cond = threading.Condition(lock)
waiting = deque()          # jobs not yet on the GPU (FIFO)
stats = {
    "started_at": time.time(),
    "jobs_received": 0,
    "jobs_done": 0,               # finished reading (whether or not the client still waited)
    "jobs_failed": 0,             # model/parse crashed for the whole job
    "receipts_done": 0,
    "receipts_parse_error": 0,
    "jobs_done_client_gone": 0,   # read by the GPU although the client had already left
    "gpu_busy_seconds": 0.0,
    "running_job": None,
}


class Job:
    def __init__(self, files):
        self.id = uuid.uuid4().hex[:12]
        self.files = files            # list of (name, bytes)
        self.t_received = time.time()
        self.t_start = None
        self.t_end = None
        self.client_gone = False
        self.future = Future()


def worker():
    while True:
        with cond:
            while not waiting:
                cond.wait()
            job = waiting.popleft()
            stats["running_job"] = job.id
        job.t_start = time.time()
        try:
            receipts = []
            for name, data in job.files:   # one receipt at a time
                t0 = time.time()
                try:
                    img = Image.open(io.BytesIO(data)).convert("RGB")
                    raw = read_receipt(img)
                    try:
                        receipts.append({"file": name, "ok": True, "data": parse_json(raw),
                                         "seconds": round(time.time() - t0, 3)})
                    except Exception as e:  # model answered, but not valid JSON
                        receipts.append({"file": name, "ok": False, "error": f"parse: {e}",
                                         "raw": raw[:500], "seconds": round(time.time() - t0, 3)})
                        with lock:
                            stats["receipts_parse_error"] += 1
                except Exception as e:
                    receipts.append({"file": name, "ok": False, "error": str(e)})
                with lock:
                    stats["receipts_done"] += 1
            job.t_end = time.time()
            with lock:
                stats["jobs_done"] += 1
                stats["gpu_busy_seconds"] += job.t_end - job.t_start
                if job.client_gone:
                    stats["jobs_done_client_gone"] += 1
                stats["running_job"] = None
            job.future.set_result(receipts)
        except Exception as e:
            job.t_end = time.time()
            with lock:
                stats["jobs_failed"] += 1
                stats["running_job"] = None
            job.future.set_exception(e)


threading.Thread(target=worker, daemon=True).start()

# ------------------------------------------------------------------ API
app = FastAPI(title="LAB8 sync receipt API")


def check_key(key):
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/v1/stats")
def get_stats(x_api_key: str = Header(None)):
    check_key(x_api_key)
    with lock:
        s = dict(stats)
        s["jobs_waiting"] = len(waiting)
        s["busy"] = s["running_job"] is not None
        s["uptime_seconds"] = round(time.time() - s.pop("started_at"), 1)
        s["gpu_busy_seconds"] = round(s["gpu_busy_seconds"], 2)
    return s


@app.post("/v1/jobs")
async def submit(request: Request, files: list[UploadFile] = File(...),
                 x_api_key: str = Header(None)):
    check_key(x_api_key)
    if not 1 <= len(files) <= MAX_FILES:
        raise HTTPException(status_code=400, detail=f"send 1..{MAX_FILES} images")
    job = Job([(f.filename, await f.read()) for f in files])
    with cond:
        stats["jobs_received"] += 1
        position = len(waiting)
        waiting.append(job)
        cond.notify()
    fut = asyncio.wrap_future(job.future)
    # wait for the result on this same connection; notice if the client leaves
    while True:
        done, _ = await asyncio.wait({fut}, timeout=0.5)
        if done:
            break
        if not job.client_gone and await request.is_disconnected():
            job.client_gone = True      # keep the job: the GPU will still read it
    receipts = fut.result()
    if not job.client_gone and await request.is_disconnected():
        job.client_gone = True
        with lock:
            stats["jobs_done_client_gone"] += 1
    return {
        "job_id": job.id,
        "queue_position_at_submit": position,
        "wait_seconds": round(job.t_start - job.t_received, 3),
        "gpu_seconds": round(job.t_end - job.t_start, 3),
        "total_seconds": round(job.t_end - job.t_received, 3),
        "receipts": receipts,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning", timeout_keep_alive=5)
