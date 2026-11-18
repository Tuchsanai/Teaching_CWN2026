"""LAB 8 GPU worker: one process per GPU, reads receipts exactly like sync_api.py.

- Takes one job at a time from the durable RabbitMQ queue (prefetch = 1).
- Acks only after the whole job has been read; a crash before that -> RabbitMQ gives the
  job to a worker again (redelivered).
- A job that breaks the worker code -> nack(requeue=False) -> dead-letter queue.
- Reports started / done / failed / heartbeat events to the gateway via receipts.events.
- Reconnects to RabbitMQ by itself when the connection drops.

Run (one per GPU, keeps going after SSH drops):
  LAB8_GPU=0 setsid nohup python worker.py > worker_gpu0.log 2>&1 &
"""
import base64
import io
import json
import os
import re
import socket
import threading
import time

GPU = os.environ.get("LAB8_GPU", "0")
os.environ["CUDA_VISIBLE_DEVICES"] = GPU          # this process only sees its own GPU

import pika
import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

from common import EVENT_QUEUE, JOB_QUEUE, PERSISTENT, connect, declare

MODEL_DIR = os.environ.get("LAB8_MODEL", "/workspace/models/Qwen3-VL-2B-Instruct")
MAX_NEW_TOKENS = int(os.environ.get("LAB8_MAX_NEW_TOKENS", "512"))
NAME = os.environ.get("LAB8_WORKER_NAME", f"{socket.gethostname()}-gpu{GPU}")
HEARTBEAT_S = 5

# same prompt / parsing / decoding as sync_api.py
PROMPT = (
    "Read this receipt and return ONLY one JSON object, no other text, in this exact shape:\n"
    '{"items": [{"name": string, "qty": number, "price": number}], '
    '"subtotal": number or null, "tax": number or null, "total": number or null}\n'
    "price = the line amount printed for the item. Write numbers without thousand "
    "separators (60.000 -> 60000). Use null when a value is not printed."
)

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
def read_receipt(img):
    messages = [{"role": "user", "content": [{"type": "image", "image": img},
                                             {"type": "text", "text": PROMPT}]}]
    inputs = processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                           return_dict=True, return_tensors="pt").to("cuda:0")
    out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    return processor.batch_decode(out[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0]


def read_job(job):
    receipts = []
    for f in job["files"]:          # one receipt at a time, like sync_api.py
        t0 = time.time()
        try:
            img = Image.open(io.BytesIO(base64.b64decode(f["b64"]))).convert("RGB")
            raw = read_receipt(img)
            try:
                receipts.append({"file": f["name"], "ok": True, "data": parse_json(raw),
                                 "seconds": round(time.time() - t0, 3)})
            except Exception as e:
                receipts.append({"file": f["name"], "ok": False, "error": f"parse: {e}",
                                 "raw": raw[:500], "seconds": round(time.time() - t0, 3)})
        except Exception as e:
            receipts.append({"file": f["name"], "ok": False, "error": str(e)})
    return receipts


state = {"current_job": None, "jobs_done": 0, "jobs_failed": 0, "started_at": time.time()}


def event(ch, kind, **kw):
    ev = {"type": kind, "worker": NAME, "gpu": int(GPU), "t": time.time(), **kw}
    ch.basic_publish("", EVENT_QUEUE, json.dumps(ev, ensure_ascii=False).encode(), PERSISTENT)


def heartbeat(ch):
    event(ch, "heartbeat", current_job=state["current_job"], jobs_done=state["jobs_done"],
          jobs_failed=state["jobs_failed"])


def serve_once():
    conn = connect(NAME)
    ch = conn.channel()
    declare(ch)
    ch.basic_qos(prefetch_count=1)
    print(f"[{NAME}] connected, waiting for jobs", flush=True)
    last_hb = 0
    for method, props, body in ch.consume(JOB_QUEUE, inactivity_timeout=1):
        if time.time() - last_hb >= HEARTBEAT_S:
            heartbeat(ch)
            last_hb = time.time()
        if method is None:          # idle tick
            continue
        try:
            job = json.loads(body)
            jid = job["job_id"]
        except Exception as e:      # unreadable message -> dead letter
            ch.basic_nack(method.delivery_tag, requeue=False)
            print(f"[{NAME}] bad message -> DLQ: {e}", flush=True)
            continue
        state["current_job"] = jid
        event(ch, "started", job_id=jid, redelivered=bool(method.redelivered))
        heartbeat(ch)
        box = {}

        def run():
            try:
                box["receipts"] = read_job(job)
            except Exception as e:  # noqa
                box["error"] = f"{type(e).__name__}: {e}"

        th = threading.Thread(target=run, daemon=True)
        th.start()
        while th.is_alive():        # keep AMQP heartbeats + our heartbeat going while the GPU works
            conn.sleep(1)
            if time.time() - last_hb >= HEARTBEAT_S:
                heartbeat(ch)
                last_hb = time.time()
        if "error" in box:
            state["jobs_failed"] += 1
            event(ch, "failed", job_id=jid, error=box["error"])
            ch.basic_nack(method.delivery_tag, requeue=False)   # -> dead-letter queue
            print(f"[{NAME}] job {jid} failed -> DLQ: {box['error']}", flush=True)
        else:
            event(ch, "done", job_id=jid, receipts=box["receipts"])
            ch.basic_ack(method.delivery_tag)                   # ack only after the job is read
            state["jobs_done"] += 1
            print(f"[{NAME}] job {jid} done ({len(box['receipts'])} receipts)", flush=True)
        state["current_job"] = None
        heartbeat(ch)
        last_hb = time.time()


if __name__ == "__main__":
    while True:                     # survive broker restarts / dropped connections
        try:
            serve_once()
        except KeyboardInterrupt:
            break
        except Exception as e:
            state["current_job"] = None
            print(f"[{NAME}] connection lost ({type(e).__name__}: {e}); reconnect in 3 s", flush=True)
            time.sleep(3)
