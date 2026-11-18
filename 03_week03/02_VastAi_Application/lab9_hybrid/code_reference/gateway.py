"""LAB 9: async front door of the hybrid system (accept job -> RabbitMQ -> answer at once).

Endpoints (every one needs header X-API-Key, same key file as sync_server.py):
  POST /jobs {"prompt": "...", "priority": "normal"|"express"} -> 202 {job_id, status, eta_seconds}
       429 + Retry-After when normal jobs waiting >= 100 x live workers (express is always accepted)
  GET  /jobs/{id}?wait=10   status; waits up to 10 s for the job to finish (long poll)
  GET  /jobs/{id}/image     JPEG of a finished job
  GET  /stats               queue counts, cap, per-worker status, last 12 finished jobs

RabbitMQ layout (declared here, workers must use the same arguments):
  queue  "jobs"       durable, x-max-priority=10 (express=9, normal=1), dead-letter -> "jobs.dlx"
  queue  "jobs.dead"  durable, bound to fanout exchange "jobs.dlx" (worker nack requeue=False lands here)
  exchange "jobs.events" (topic, durable): workers publish JSON events, gateway keeps job state from them
     {"type":"started","job_id","worker","redelivered":bool}
     {"type":"done","job_id","worker","seconds","image":"/workspace/lab9/images/<id>.jpg"}
     {"type":"failed","job_id","worker","error","requeue":bool}
     {"type":"heartbeat","worker","state":"idle"|"busy","job_id","working","done"}   (every 1 s)
Run: uvicorn gateway:app --host 0.0.0.0 --port 8000
"""
import asyncio, json, math, os, secrets, sqlite3, time, uuid
from collections import deque
from pathlib import Path

import aio_pika
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@127.0.0.1/")
KEY_FILE = Path(os.environ.get("API_KEY_FILE", "/workspace/lab9/api_key.txt"))
DB_FILE = Path(os.environ.get("JOBS_DB", "/workspace/lab9/jobs.db"))
PER_WORKER_CAP = 100          # normal jobs allowed to wait per live worker
WORKER_TIMEOUT = 15           # seconds without heartbeat -> worker counted as gone
DEFAULT_SEC_PER_IMAGE = 0.47  # single-image time measured in step 3 (RTX 3090, 4 steps)
PRIORITY = {"normal": 1, "express": 9}
API_KEY = KEY_FILE.read_text().strip()

# --- 1) job state: SQLite on disk (survives a gateway restart) + small in-memory views ---
db = sqlite3.connect(DB_FILE, check_same_thread=False)
db.execute("""CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, prompt TEXT, priority TEXT,
              status TEXT, worker TEXT, created REAL, started REAL, finished REAL,
              seconds REAL, image TEXT, error TEXT, attempts INTEGER DEFAULT 0)""")
db.commit()
counters = {"rejected_429": 0, "redelivered": 0}
workers: dict[str, dict] = {}
recent: deque = deque(maxlen=12)
waiters: dict[str, asyncio.Event] = {}
amqp: dict = {}

def job_row(job_id: str) -> dict | None:
    cur = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    row = cur.fetchone()
    return dict(zip([c[0] for c in cur.description], row)) if row else None

def count(status: str, priority: str | None = None) -> int:
    q, a = "SELECT COUNT(*) FROM jobs WHERE status=?", [status]
    if priority:
        q += " AND priority=?"; a.append(priority)
    return db.execute(q, a).fetchone()[0]

def live_workers() -> int:
    now = time.time()
    return sum(1 for w in workers.values() if now - w["last_seen"] < WORKER_TIMEOUT)

def sec_per_image() -> float:
    r = db.execute("SELECT AVG(seconds) FROM (SELECT seconds FROM jobs WHERE status='done' "
                   "ORDER BY finished DESC LIMIT 50)").fetchone()[0]
    return r or DEFAULT_SEC_PER_IMAGE

def cap_now() -> int:
    return PER_WORKER_CAP * max(1, live_workers())   # 0 workers still lets jobs wait for the first one

# --- 2) worker events -> job state ---
async def on_event(msg: aio_pika.abc.AbstractIncomingMessage):
    async with msg.process():
        e = json.loads(msg.body); t = time.time(); jid = e.get("job_id"); w = e.get("worker")
        if w:
            info = workers.setdefault(w, {"worker": w, "state": "idle", "job_id": None, "done": 0})
            info["last_seen"] = t
        if e["type"] == "heartbeat":
            info.update(state=e.get("state", "idle"), job_id=e.get("job_id"), done=e.get("done", info["done"]),
                        working=e.get("working", 0))   # images the worker is drawing right now
        elif e["type"] == "started":
            if e.get("redelivered"):
                counters["redelivered"] += 1
            db.execute("UPDATE jobs SET status='running', worker=?, started=?, attempts=attempts+1 WHERE id=?",
                       (w, t, jid))
            info.update(state="busy", job_id=jid)
        elif e["type"] == "done":
            db.execute("UPDATE jobs SET status='done', finished=?, seconds=?, image=? WHERE id=?",
                       (t, e.get("seconds"), e.get("image"), jid))
            info.update(state="idle", job_id=None, done=info["done"] + 1)
            row = job_row(jid)
            if row:
                recent.appendleft({k: row[k] for k in ("id", "priority", "worker", "seconds", "prompt")}
                                  | {"total_seconds": round(t - row["created"], 2)})
        elif e["type"] == "failed":
            status = "queued" if e.get("requeue") else "dead"
            db.execute("UPDATE jobs SET status=?, error=? WHERE id=?", (status, e.get("error"), jid))
            info.update(state="idle", job_id=None)
        db.commit()
        if jid in waiters and e["type"] in ("done", "failed"):
            waiters.pop(jid).set()

# --- 3) app start: connect, declare durable queues, consume events ---
app = FastAPI(title="LAB 9 job gateway")

@app.on_event("startup")
async def startup():
    conn = await aio_pika.connect_robust(AMQP_URL)
    ch = await conn.channel(publisher_confirms=True)
    dlx = await ch.declare_exchange("jobs.dlx", aio_pika.ExchangeType.FANOUT, durable=True)
    dead = await ch.declare_queue("jobs.dead", durable=True)
    await dead.bind(dlx)
    jobs_q = await ch.declare_queue("jobs", durable=True,
                                    arguments={"x-max-priority": 10, "x-dead-letter-exchange": "jobs.dlx"})
    events = await ch.declare_exchange("jobs.events", aio_pika.ExchangeType.TOPIC, durable=True)
    ev_q = await ch.declare_queue("gateway.events", durable=True)
    await ev_q.bind(events, routing_key="#")
    await ev_q.consume(on_event)
    amqp.update(conn=conn, ch=ch, jobs=jobs_q, dead=dead)

@app.on_event("shutdown")
async def shutdown():
    if amqp.get("conn"):
        await amqp["conn"].close()

def require_key(x_api_key: str | None = Header(default=None)):
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(401, "invalid or missing API key")

# --- 4) endpoints ---
class JobReq(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)
    priority: str = Field(default="normal", pattern="^(normal|express)$")

@app.post("/jobs", status_code=202, dependencies=[Depends(require_key)])
async def submit(req: JobReq):
    workers_n = max(1, live_workers()); spi = sec_per_image()
    normal_waiting = count("queued", "normal")
    if req.priority == "normal" and normal_waiting >= cap_now():
        counters["rejected_429"] += 1
        retry = max(1, math.ceil((normal_waiting - cap_now() + 1) * spi / workers_n))
        return JSONResponse({"detail": "queue full, try again later", "retry_after_seconds": retry,
                             "normal_waiting": normal_waiting, "cap": cap_now()},
                            status_code=429, headers={"Retry-After": str(retry)})
    job_id = uuid.uuid4().hex[:12]
    ahead = count("queued", "express") + count("running") + (normal_waiting if req.priority == "normal" else 0)
    db.execute("INSERT INTO jobs (id, prompt, priority, status, created) VALUES (?,?,?,?,?)",
               (job_id, req.prompt, req.priority, "queued", time.time()))
    db.commit()
    body = json.dumps({"job_id": job_id, "prompt": req.prompt, "priority": req.priority}).encode()
    await amqp["ch"].default_exchange.publish(
        aio_pika.Message(body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                         priority=PRIORITY[req.priority], message_id=job_id,
                         content_type="application/json"), routing_key="jobs")
    return {"job_id": job_id, "status": "queued", "priority": req.priority, "jobs_ahead": ahead,
            "eta_seconds": round((ahead + 1) * spi / workers_n, 1), "live_workers": live_workers()}

@app.get("/jobs/{job_id}", dependencies=[Depends(require_key)])
async def status(job_id: str, wait: float = Query(10, ge=0, le=10)):
    row = job_row(job_id)
    if not row:
        raise HTTPException(404, "no such job")
    if row["status"] in ("queued", "running") and wait > 0:
        ev = waiters.setdefault(job_id, asyncio.Event())
        try:
            await asyncio.wait_for(ev.wait(), wait)
        except asyncio.TimeoutError:
            pass
        row = job_row(job_id)
    out = {k: row[k] for k in ("id", "status", "priority", "worker", "seconds", "error", "attempts")}
    if row["status"] == "done":
        out["image_url"] = f"/jobs/{job_id}/image"
    return out

@app.get("/jobs/{job_id}/image", dependencies=[Depends(require_key)])
async def image(job_id: str):
    row = job_row(job_id)
    if not row:
        raise HTTPException(404, "no such job")
    if row["status"] != "done" or not row["image"] or not Path(row["image"]).exists():
        raise HTTPException(409, f"image not ready (status: {row['status']})")
    return FileResponse(row["image"], media_type="image/jpeg")

@app.get("/stats", dependencies=[Depends(require_key)])
async def stats():
    async with amqp["conn"].channel() as c:   # fresh channel: live counts, not the cached declare
        jobs_q = await c.declare_queue("jobs", passive=True)
        dead_q = await c.declare_queue("jobs.dead", passive=True)
    now = time.time()
    return {
        "waiting": {"normal": count("queued", "normal"), "express": count("queued", "express"),
                    "in_rabbitmq": jobs_q.declaration_result.message_count},
        "running": count("running"), "done": count("done"),
        "rejected_429": counters["rejected_429"], "redelivered": counters["redelivered"],
        "dead": {"jobs": count("dead"), "in_dead_letter_queue": dead_q.declaration_result.message_count},
        "cap_normal_now": cap_now(), "live_workers": live_workers(),
        "sec_per_image": round(sec_per_image(), 3),
        "workers": [w | {"alive": now - w["last_seen"] < WORKER_TIMEOUT,
                         "last_seen_sec_ago": round(now - w["last_seen"], 1)} for w in workers.values()],
        "recent_done": list(recent),
    }
