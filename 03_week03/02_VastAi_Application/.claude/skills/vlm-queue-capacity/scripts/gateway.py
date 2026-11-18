"""LAB 8 API gateway: accepts receipt jobs, puts them on RabbitMQ, keeps every job in SQLite.

POST /jobs       (X-API-Key, multipart "files" = 1..8 receipt images) -> 202 {"job_id"} at once
                 503 when the queue already holds 1000 jobs
GET  /jobs/{id}  status queued/running/done/failed, worker, queue wait, total time, receipts read
GET  /jobs       latest jobs (?limit=20)
GET  /stats      queue length, connected workers (current job, jobs done), jobs per status,
                 redelivered jobs, dead-letter count
GET  /health     no key

Workers never talk to the gateway over HTTP: they publish events (started / done / failed /
heartbeat) to the durable queue receipts.events and this process writes them into SQLite.

Run (keeps going after SSH drops):
  LAB8_KEY_FILE=/workspace/lab8/.api_key setsid nohup python gateway.py > gateway.log 2>&1 &
"""
import base64
import json
import os
import sqlite3
import threading
import time
import uuid

import pika
import uvicorn
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from common import DLQ, EVENT_QUEUE, JOB_QUEUE, MAX_QUEUE, PERSISTENT, connect, declare

KEY_FILE = os.environ.get("LAB8_KEY_FILE", "/workspace/lab8/.api_key")
DB_PATH = os.environ.get("LAB8_DB", "/workspace/lab8/jobs.db")
PORT = int(os.environ.get("LAB8_PORT", "8000"))
MAX_FILES = 8
WORKER_ALIVE_S = 20  # a worker that sent no heartbeat for this long counts as disconnected

with open(KEY_FILE) as f:
    API_KEY = f.read().strip()

# ------------------------------------------------------------------ SQLite
db_lock = threading.Lock()
db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
db.execute("PRAGMA journal_mode=WAL")
db.execute("""CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY, status TEXT NOT NULL, files TEXT, n_files INTEGER,
    created REAL, started REAL, finished REAL, worker TEXT,
    deliveries INTEGER DEFAULT 0, redelivered INTEGER DEFAULT 0,
    receipts_failed INTEGER, result TEXT, error TEXT)""")
db.execute("CREATE INDEX IF NOT EXISTS jobs_created ON jobs(created)")


def q(sql, args=(), one=False):
    with db_lock:
        cur = db.execute(sql, args)
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description] if cur.description else []
    rows = [dict(zip(cols, r)) for r in rows]
    return (rows[0] if rows else None) if one else rows


# ------------------------------------------------------------------ publisher
class Publisher:
    """One AMQP connection for publishing (publisher confirms on); reconnects on any error."""

    def __init__(self):
        self.lock = threading.Lock()
        self.conn = self.ch = None
        threading.Thread(target=self._keepalive, daemon=True).start()

    def _open(self):
        if self.conn and self.conn.is_open:
            return
        self.conn = connect("gateway-publisher")
        self.ch = self.conn.channel()
        self.ch.confirm_delivery()
        declare(self.ch)

    def _call(self, fn):
        with self.lock:
            for attempt in range(2):
                try:
                    self._open()
                    return fn(self.ch)
                except (pika.exceptions.NackError, pika.exceptions.UnroutableError):
                    raise
                except Exception:
                    try:
                        self.conn and self.conn.close()
                    except Exception:
                        pass
                    self.conn = None
                    if attempt:
                        raise

    def publish(self, body):
        self._call(lambda ch: ch.basic_publish("", JOB_QUEUE, body, PERSISTENT, mandatory=True))

    def depth(self):
        def f(ch):
            jobs = ch.queue_declare(JOB_QUEUE, passive=True).method
            dlq = ch.queue_declare(DLQ, passive=True).method
            return {"ready": jobs.message_count, "consumers": jobs.consumer_count,
                    "dead_letter": dlq.message_count}
        return self._call(f)

    def _keepalive(self):  # service heartbeats while the gateway is idle
        while True:
            time.sleep(5)
            try:
                with self.lock:
                    if self.conn and self.conn.is_open:
                        self.conn.process_data_events(0)
            except Exception:
                self.conn = None


pub = Publisher()

# ------------------------------------------------------------------ event consumer
workers = {}            # name -> last heartbeat payload
workers_lock = threading.Lock()


def handle_event(ev):
    kind, jid = ev.get("type"), ev.get("job_id")
    if kind == "heartbeat":
        with workers_lock:
            workers[ev["worker"]] = dict(ev, seen=time.time())
        return
    if kind == "started":
        q("""UPDATE jobs SET status=CASE WHEN status IN ('done','failed') THEN status ELSE 'running' END,
             started=?, worker=?, deliveries=deliveries+1,
             redelivered=CASE WHEN ? OR deliveries>=1 THEN 1 ELSE redelivered END WHERE id=?""",
          (ev["t"], ev["worker"], 1 if ev.get("redelivered") else 0, jid))
    elif kind == "done":
        q("""UPDATE jobs SET status='done', finished=?, worker=?, result=?, receipts_failed=?,
             error=NULL WHERE id=?""",
          (ev["t"], ev["worker"], json.dumps(ev["receipts"], ensure_ascii=False),
           sum(1 for r in ev["receipts"] if not r["ok"]), jid))
    elif kind == "failed":
        q("UPDATE jobs SET status='failed', finished=?, worker=?, error=? WHERE id=?",
          (ev["t"], ev["worker"], ev.get("error", "")[:2000], jid))
    with workers_lock:  # also refresh the worker's live view from job events
        w = workers.setdefault(ev["worker"], {"worker": ev["worker"]})
        w["seen"] = time.time()
        w["current_job"] = jid if kind == "started" else None


def event_loop():
    while True:
        try:
            conn = connect("gateway-events")
            ch = conn.channel()
            declare(ch)
            ch.basic_qos(prefetch_count=50)

            def on_msg(ch_, method, props, body):
                try:
                    handle_event(json.loads(body))
                except Exception as e:  # never block the event queue on one bad event
                    print("bad event:", e, flush=True)
                ch_.basic_ack(method.delivery_tag)

            ch.basic_consume(EVENT_QUEUE, on_msg)
            ch.start_consuming()
        except Exception as e:
            print("event consumer reconnect:", type(e).__name__, e, flush=True)
            time.sleep(3)


threading.Thread(target=event_loop, daemon=True).start()

# ------------------------------------------------------------------ API
app = FastAPI(title="LAB8 receipt job gateway")


def check_key(key):
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")


def job_view(r, full=True):
    out = {"job_id": r["id"], "status": r["status"], "worker": r["worker"],
           "files": json.loads(r["files"] or "[]"),
           "created": r["created"], "deliveries": r["deliveries"],
           "redelivered": bool(r["redelivered"]),
           "queue_wait_seconds": round(r["started"] - r["created"], 3) if r["started"] else None,
           "total_seconds": round(r["finished"] - r["created"], 3) if r["finished"] else None,
           "gpu_seconds": (round(r["finished"] - r["started"], 3)
                           if r["finished"] and r["started"] else None)}
    if r["status"] == "queued":
        out["waiting_seconds_so_far"] = round(time.time() - r["created"], 3)
    if full:
        out["receipts"] = json.loads(r["result"]) if r["result"] else None
        out["error"] = r["error"]
    return out


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/jobs", status_code=202)
def submit(files: list[UploadFile] = File(...), x_api_key: str = Header(None)):
    check_key(x_api_key)
    if not 1 <= len(files) <= MAX_FILES:
        raise HTTPException(status_code=400, detail=f"send 1..{MAX_FILES} images")
    try:
        if pub.depth()["ready"] >= MAX_QUEUE:
            raise HTTPException(status_code=503, detail="queue full, try again later")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="queue unavailable")
    jid = uuid.uuid4().hex[:12]
    blobs = [(f.filename, f.file.read()) for f in files]
    now = time.time()
    q("INSERT INTO jobs(id,status,files,n_files,created) VALUES (?,?,?,?,?)",
      (jid, "queued", json.dumps([n for n, _ in blobs]), len(blobs), now))
    body = json.dumps({"job_id": jid, "created": now,
                       "files": [{"name": n, "b64": base64.b64encode(b).decode()} for n, b in blobs]})
    try:
        pub.publish(body.encode())
    except pika.exceptions.NackError:        # broker refused: queue reached x-max-length
        q("DELETE FROM jobs WHERE id=?", (jid,))
        raise HTTPException(status_code=503, detail="queue full, try again later")
    except Exception:
        q("DELETE FROM jobs WHERE id=?", (jid,))
        raise HTTPException(status_code=503, detail="queue unavailable")
    return {"job_id": jid, "status": "queued"}


@app.get("/jobs/{jid}")
def get_job(jid: str, x_api_key: str = Header(None)):
    check_key(x_api_key)
    r = q("SELECT * FROM jobs WHERE id=?", (jid,), one=True)
    if not r:
        raise HTTPException(status_code=404, detail="no such job")
    return job_view(r)


@app.get("/jobs")
def list_jobs(limit: int = 20, x_api_key: str = Header(None)):
    check_key(x_api_key)
    rows = q("SELECT * FROM jobs ORDER BY created DESC LIMIT ?", (max(1, min(limit, 500)),))
    return {"jobs": [job_view(r, full=False) for r in rows]}


@app.get("/stats")
def stats(x_api_key: str = Header(None)):
    check_key(x_api_key)
    try:
        depth = pub.depth()
    except Exception as e:
        depth = {"ready": None, "consumers": None, "dead_letter": None, "error": type(e).__name__}
    counts = {s: 0 for s in ("queued", "running", "done", "failed")}
    for r in q("SELECT status, COUNT(*) n FROM jobs GROUP BY status"):
        counts[r["status"]] = r["n"]
    done_by = {r["worker"]: r["n"] for r in
               q("SELECT worker, COUNT(*) n FROM jobs WHERE status='done' GROUP BY worker")}
    agg = q("""SELECT COALESCE(SUM(redelivered),0) redelivered,
                      COALESCE(SUM(receipts_failed),0) receipts_failed,
                      COALESCE(SUM(CASE WHEN status='done' THEN n_files END),0) receipts_done,
                      COALESCE(SUM(CASE WHEN status='done' THEN finished-started END),0) gpu_busy
               FROM jobs""", one=True)
    now = time.time()
    with workers_lock:
        wl = [{"worker": n, "connected": now - w.get("seen", 0) < WORKER_ALIVE_S,
               "gpu": w.get("gpu"), "current_job": w.get("current_job"),
               "jobs_done": done_by.get(n, 0),
               "last_seen_seconds_ago": round(now - w.get("seen", 0), 1)}
              for n, w in sorted(workers.items())]
    return {"queue_length": depth["ready"], "queue_max": MAX_QUEUE,
            "dead_letter_queue": depth["dead_letter"], "amqp_consumers": depth["consumers"],
            "workers": wl, "workers_connected": sum(w["connected"] for w in wl),
            "jobs": counts, "jobs_redelivered": agg["redelivered"],
            "receipts_done": agg["receipts_done"], "receipts_parse_error": agg["receipts_failed"],
            "gpu_busy_seconds": round(agg["gpu_busy"], 2)}


@app.exception_handler(HTTPException)
def http_err(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning", timeout_keep_alive=5)
