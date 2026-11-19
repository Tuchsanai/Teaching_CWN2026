#!/usr/bin/env python3
"""Step 09 · stop the GPU worker in the middle of a batch, start it again, write a timeline.

Runs on the GPU machine (in tmux) BEFORE the jobs are sent:
    worker_stop_test.py --after 6 --down 20 --expect 20 --log <file>

1. remembers which jobs are already in the gateway's jobs.db (they are not counted)
2. waits until --after new jobs are DONE, then waits for the next job to be PROCESSING
   (a job really in flight) and sends SIGKILL to the worker at that moment
3. keeps the worker down for --down seconds (new jobs pile up in RabbitMQ), starts it again
4. waits until --expect new jobs are finished and prints the counts
jobs.db is opened read-only; nothing of the team's code is touched.
"""
import argparse, json, os, signal, sqlite3, subprocess, time
from datetime import datetime, timezone

D = "/workspace/e2e_sitesafe/deploy"
ap = argparse.ArgumentParser()
ap.add_argument("--after", type=int, default=6)
ap.add_argument("--down", type=float, default=20)
ap.add_argument("--expect", type=int, default=20)
ap.add_argument("--log", default=f"{D}/logs/worker_stop_test.json")
ap.add_argument("--timeout", type=float, default=600)
a = ap.parse_args()

db = sqlite3.connect(f"file:{D}/data/jobs.db?mode=ro", uri=True, timeout=5)
old = {r[0] for r in db.execute("SELECT job_id FROM jobs")}
events, t0 = [], time.time()


def counts():
    c = {"QUEUED": 0, "PROCESSING": 0, "DONE": 0, "FAILED": 0}
    rows = [r for r in db.execute("SELECT job_id, status, delivery_count FROM jobs") if r[0] not in old]
    for _, status, _ in rows:
        c[status] += 1
    return c, rows


def note(what, **extra):
    c, _ = counts()
    e = {"t_s": round(time.time() - t0, 2), "utc": datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3],
         "event": what, "received": sum(c.values()), **c, **extra}
    events.append(e)
    print(json.dumps(e), flush=True)
    json.dump(events, open(a.log, "w"), indent=1)


def worker_pids():
    out = subprocess.run(["pgrep", "-f", "ai.worker.worker"], capture_output=True, text=True).stdout.split()
    return [int(p) for p in out]


pids = worker_pids()
note("watching", worker_pids=pids)
# phase 1: --after jobs done
while counts()[0]["DONE"] < a.after:
    if time.time() - t0 > a.timeout: note("timeout before kill"); raise SystemExit(1)
    time.sleep(0.02)
note(f"{a.after} jobs done, waiting for a job in flight")
# phase 2: kill while a job is PROCESSING
inflight = None
while inflight is None:
    for job_id, status, _ in db.execute("SELECT job_id, status, delivery_count FROM jobs WHERE status = 'PROCESSING'"):
        if job_id not in old:
            inflight = job_id
            break
    else:
        time.sleep(0.001)
for p in pids:
    os.kill(p, signal.SIGKILL)
t_kill = time.time()
note("WORKER KILLED (SIGKILL)", job_in_flight=inflight)
time.sleep(1)
note("1 s after kill", worker_pids=worker_pids())
# phase 3: stay down
last = None
while time.time() - t_kill < a.down:
    c, _ = counts()
    if c != last:
        note("worker down"); last = c
    time.sleep(0.25)
note("before restart", worker_pids=worker_pids(), down_s=round(time.time() - t_kill, 1))
done_before_restart = counts()[0]["DONE"]
subprocess.run([f"{D}/bin/svc.sh", "start", "worker"], check=False)
t_start = time.time()
note("WORKER STARTED AGAIN")
# phase 4: until everything is finished
last = None
while True:
    c, rows = counts()
    if c != last:
        note("worker up"); last = c
    if sum(c.values()) >= a.expect and c["QUEUED"] + c["PROCESSING"] == 0:
        break
    if time.time() - t0 > a.timeout: note("timeout after restart"); break
    time.sleep(0.25)
c, rows = counts()
redelivered = [{"job_id": j, "status": s, "delivery_count": n} for j, s, n in rows if n and n > 1]
note("FINISHED", done_before_restart=done_before_restart, done_after_restart=c["DONE"] - done_before_restart,
     job_in_flight_at_kill=inflight, jobs_delivered_more_than_once=redelivered,
     first_done_after_restart_s=None, restart_to_all_done_s=round(time.time() - t_start, 1))
