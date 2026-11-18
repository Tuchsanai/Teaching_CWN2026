"""LAB 8 load generator for the JOB QUEUE (gateway.py + worker.py), same machine as the gateway.

Closed-loop users, same as the baseline: each simulated user picks 4 random receipts ->
POST /jobs (gets a job_id at once) -> asks GET /jobs/{id} every 0.5 s until done/failed
(no 30 s cap: the user keeps waiting) -> thinks 10 s -> sends again.

  python loadtest.py level --users 4                   # one level (75 s, first 15 s not counted)
  python loadtest.py sweep                             # N = 1,2,4,6,8,... stop after 2 levels miss SLO
  python loadtest.py sweep --start-users 4 --gpus 0,1  # 2 workers: N = 4,6,8,... GPU util of both GPUs
  python loadtest.py burst --jobs 60 --within 10       # 60 jobs within 10 s
  python loadtest.py sweep --then-burst                # both, like step 2
  python loadtest.py killtest --jobs 60 --within 10 --kill-gpu 1 --kill-at 20 --gpus 0,1 \
      --out ../results/worker_kill                     # burst, then SIGKILL the GPU-1 worker at 20 s

Every experiment is saved as JSON in --out. Queue length (GET /stats) is recorded every 1 s.
Counting rule (same as the baseline): a request belongs to the measured window if it was SENT
in [warmup, duration). latency = submit -> result seen by the user. A job fails if the gateway
refuses it (e.g. 503 queue full), the job ends as "failed", or the connection errors.
jobs/min = successful measured jobs / measured minutes.
"""
import argparse
import asyncio
import json
import os
import random
import signal
import statistics
import threading
import time
from pathlib import Path

import httpx
import psutil

try:
    import pynvml
    pynvml.nvmlInit()
except Exception:  # noqa
    pynvml = None

HERE = Path(__file__).resolve().parent


def pct(values, p):
    if not values:
        return None
    v = sorted(values)
    k = (len(v) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(v) - 1)
    return round(v[f] + (v[c] - v[f]) * (k - f), 3)


class Sampler:
    """Samples GPU util (mean of the GPUs in use) and this process' CPU % once per second."""

    def __init__(self, gpu_indexes=(0,)):
        self.gpus = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in gpu_indexes] if pynvml else []
        self.proc = psutil.Process()
        self.rows = []  # (t, mean gpu_util, cpu_percent, [util per gpu])
        self._stop = threading.Event()

    def start(self):
        self.proc.cpu_percent(None)
        threading.Thread(target=self._run, daemon=True).start()
        return self

    def _run(self):
        while not self._stop.wait(1.0):
            per = [pynvml.nvmlDeviceGetUtilizationRates(h).gpu for h in self.gpus]
            g = statistics.mean(per) if per else None
            self.rows.append((time.time(), g, self.proc.cpu_percent(None), per))

    def stop(self):
        self._stop.set()

    def window(self, t0, t1):
        rows = [r for r in self.rows if t0 <= r[0] <= t1]
        g = [r[1] for r in rows if r[1] is not None]
        c = [r[2] for r in rows]
        per = [[r[3][i] for r in rows] for i in range(len(self.gpus))]
        return {
            "gpu_util_avg_pct": round(statistics.mean(g), 1) if g else None,
            "gpu_util_per_gpu_pct": [round(statistics.mean(x), 1) if x else None for x in per],
            "loadgen_cpu_avg_pct": round(statistics.mean(c), 1) if c else None,
            "loadgen_cpu_max_pct": round(max(c), 1) if c else None,
            "loadgen_cpu_cores": psutil.cpu_count(),
        }


class QueueSampler:
    """Asks GET /stats once per second: queue length, running jobs, connected workers."""

    def __init__(self, cli):
        self.cli = cli
        self.rows = []
        self.task = None

    def start(self, t0):
        async def run():
            while True:
                try:
                    s = await self.cli.stats()
                    self.rows.append({"t": round(time.time() - t0, 2),
                                      "queue_length": s["queue_length"],
                                      "running": s["jobs"]["running"],
                                      "queued_db": s["jobs"]["queued"],
                                      "workers_connected": s["workers_connected"]})
                except Exception as e:  # noqa
                    self.rows.append({"t": round(time.time() - t0, 2), "error": type(e).__name__})
                await asyncio.sleep(1)
        self.task = asyncio.create_task(run())
        return self

    async def stop(self):
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass

    def summary(self):
        ql = [r["queue_length"] for r in self.rows if r.get("queue_length") is not None]
        return {"queue_length_max": max(ql) if ql else None,
                "queue_length_avg": round(statistics.mean(ql), 2) if ql else None}


class Client:
    def __init__(self, args):
        self.url = args.url.rstrip("/")
        self.key = Path(args.key_file).read_text().strip()
        self.poll = args.poll
        self.samples = sorted(p for p in Path(args.samples).iterdir()
                              if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
        self.blobs = {p.name: p.read_bytes() for p in self.samples}
        self.per_job = args.receipts
        self.http = httpx.AsyncClient(limits=httpx.Limits(max_connections=1000,
                                                          max_keepalive_connections=100))

    @property
    def h(self):
        return {"X-API-Key": self.key}

    async def stats(self):
        r = await self.http.get(f"{self.url}/stats", headers=self.h, timeout=10)
        r.raise_for_status()
        return r.json()

    async def wait_idle(self, max_wait=1800):
        t0 = time.time()
        while time.time() - t0 < max_wait:
            s = await self.stats()
            if s["queue_length"] == 0 and s["jobs"]["queued"] == 0 and s["jobs"]["running"] == 0:
                return s
            await asyncio.sleep(1)
        return await self.stats()

    async def one_job(self, user):
        names = random.sample(list(self.blobs), self.per_job)
        files = [("files", (n, self.blobs[n], "image/jpeg")) for n in names]
        t0 = time.time()
        rec = {"user": user, "sent": t0, "files": names}
        try:
            r = await self.http.post(f"{self.url}/jobs", files=files, headers=self.h, timeout=30)
            rec["submit_s"] = round(time.time() - t0, 3)
            rec["status"] = r.status_code
            if r.status_code not in (200, 202):
                rec.update(ok=False, error=f"http {r.status_code}", latency=time.time() - t0)
                return rec
            jid = r.json()["job_id"]
            rec["job_id"] = jid
            polls = 0
            while True:          # no cap: the user waits until the job ends
                await asyncio.sleep(self.poll)
                polls += 1
                try:
                    g = await self.http.get(f"{self.url}/jobs/{jid}", headers=self.h, timeout=10)
                except httpx.HTTPError:
                    continue
                if g.status_code != 200:
                    continue
                body = g.json()
                if body["status"] in ("done", "failed"):
                    break
            rec["latency"] = time.time() - t0
            rec["polls"] = polls
            rec["worker"] = body["worker"]
            rec["server_wait"] = body["queue_wait_seconds"]
            rec["server_gpu"] = body["gpu_seconds"]
            rec["redelivered"] = body["redelivered"]
            rec["deliveries"] = body.get("deliveries")
            if body.get("total_seconds") is not None:   # server-side finish time (epoch)
                rec["server_finished"] = body["created"] + body["total_seconds"]
            if body["status"] == "done":
                rec["ok"] = True
                rec["receipts_ok"] = sum(x["ok"] for x in body["receipts"])
            else:
                rec["ok"] = False
                rec["error"] = "job failed"
        except Exception as e:  # connection error etc.
            rec["latency"] = time.time() - t0
            rec["ok"] = False
            rec["error"] = type(e).__name__
        return rec


def summarize(recs, t0, warmup, duration):
    m = [r for r in recs if t0 + warmup <= r["sent"] < t0 + duration]
    ok = [r for r in m if r["ok"]]
    lat = [r["latency"] for r in m]
    minutes = (duration - warmup) / 60
    return {
        "measured_requests": len(m),
        "succeeded": len(ok),
        "failed": len(m) - len(ok),
        "fail_pct": round(100 * (len(m) - len(ok)) / len(m), 2) if m else None,
        "jobs_per_min": round(len(ok) / minutes, 2),
        "latency_p50_s": pct(lat, 50),
        "latency_p95_s": pct(lat, 95),
        "latency_p99_s": pct(lat, 99),
        "ok_latency_p50_s": pct([r["latency"] for r in ok], 50),
        "server_wait_p50_s": pct([r["server_wait"] for r in ok], 50),
        "server_wait_p95_s": pct([r["server_wait"] for r in ok], 95),
        "server_gpu_p50_s": pct([r["server_gpu"] for r in ok], 50),
        "errors": {e: sum(1 for r in m if r.get("error") == e)
                   for e in {r.get("error") for r in m if not r["ok"]}},
    }


async def run_level(cli, n, args):
    await cli.wait_idle()
    before = await cli.stats()
    sampler = Sampler(args.gpu_list).start()
    t0 = time.time()
    qs = QueueSampler(cli).start(t0)
    stop_at = t0 + args.duration
    recs = []

    async def user(u):
        await asyncio.sleep(random.uniform(0, min(args.think, 5)))  # spread the first sends
        while time.time() < stop_at:
            recs.append(await cli.one_job(u))
            remaining = stop_at - time.time()
            if remaining <= 0:
                break
            await asyncio.sleep(min(args.think, remaining))

    await asyncio.gather(*(user(u) for u in range(n)))
    t_end = time.time()
    sampler.stop()
    after = await cli.wait_idle()
    await qs.stop()
    res = {"mode": "level", "system": "queue", "users": n, "duration_s": args.duration,
           "warmup_s": args.warmup, "think_s": args.think, "timeout_s": None,
           "poll_s": args.poll, "receipts_per_job": args.receipts,
           "started": t0, "ended": t_end, "workers": [w["worker"] for w in before["workers"]
                                                       if w["connected"]]}
    res.update(summarize(recs, t0, args.warmup, args.duration))
    res.update(sampler.window(t0 + args.warmup, t0 + args.duration))
    res.update(qs.summary())
    res["slo_pass"] = (res["latency_p95_s"] is not None and res["latency_p95_s"] <= args.slo_p95
                       and res["fail_pct"] < args.slo_fail_pct)
    res["server_jobs_redelivered"] = after["jobs_redelivered"] - before["jobs_redelivered"]
    res["server_parse_errors"] = after["receipts_parse_error"] - before["receipts_parse_error"]
    res["queue_timeline"] = qs.rows
    res["requests"] = recs
    return res


async def run_burst(cli, args):
    await cli.wait_idle()
    before = await cli.stats()
    sampler = Sampler(args.gpu_list).start()
    t0 = time.time()
    qs = QueueSampler(cli).start(t0)
    gap = args.within / args.jobs

    async def fire(i):
        await asyncio.sleep(i * gap)
        return await cli.one_job(i)

    recs = await asyncio.gather(*(fire(i) for i in range(args.jobs)))
    t_clients_done = time.time()
    after = await cli.wait_idle()
    t_drained = time.time()
    sampler.stop()
    await qs.stop()
    ok = [r for r in recs if r["ok"]]
    qsum = qs.summary()
    peak_t = next((r["t"] for r in qs.rows if r.get("queue_length") == qsum["queue_length_max"]), None)
    empty_t = next((r["t"] for r in qs.rows
                    if peak_t is not None and r["t"] > peak_t and r.get("queue_length") == 0), None)
    res = {"mode": "burst", "system": "queue", "jobs": args.jobs, "within_s": args.within,
           "timeout_s": None, "poll_s": args.poll, "receipts_per_job": args.receipts,
           "started": t0, "workers": [w["worker"] for w in before["workers"] if w["connected"]],
           "succeeded": len(ok), "failed": len(recs) - len(ok),
           "fail_pct": round(100 * (len(recs) - len(ok)) / len(recs), 2),
           "latency_p50_s": pct([r["latency"] for r in recs], 50),
           "latency_p95_s": pct([r["latency"] for r in recs], 95),
           "latency_p99_s": pct([r["latency"] for r in recs], 99),
           "ok_latency_max_s": round(max((r["latency"] for r in ok), default=0), 3),
           "submit_p95_s": pct([r["submit_s"] for r in recs if "submit_s" in r], 95),
           "server_wait_p95_s": pct([r["server_wait"] for r in ok], 95),
           "errors": {e: sum(1 for r in recs if r.get("error") == e)
                      for e in {r.get("error") for r in recs if not r["ok"]}},
           "clients_done_after_s": round(t_clients_done - t0, 1),
           "server_drained_after_s": round(t_drained - t0, 1),
           "queue_peak_at_s": peak_t,
           "queue_empty_at_s": empty_t,
           "server_jobs_done": after["jobs"]["done"] - before["jobs"]["done"],
           "server_jobs_failed": after["jobs"]["failed"] - before["jobs"]["failed"],
           "server_jobs_redelivered": after["jobs_redelivered"] - before["jobs_redelivered"],
           "server_gpu_busy_s": round(after["gpu_busy_seconds"] - before["gpu_busy_seconds"], 1)}
    res.update(qsum)
    res.update(sampler.window(t0, t_drained))
    res["queue_timeline"] = qs.rows
    res["requests"] = recs
    return res


def find_worker_pid(gpu):
    """PID of the python worker.py process started with LAB8_GPU=<gpu> (same machine)."""
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            if "worker.py" in (p.info["cmdline"] or []) and \
                    p.environ().get("LAB8_GPU") == str(gpu):
                return p.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


async def run_killtest(cli, args):
    """Burst of jobs, then SIGKILL one worker mid-run (power cut: no ack, no goodbye)."""
    await cli.wait_idle()
    before = await cli.stats()
    pid = find_worker_pid(args.kill_gpu)
    if pid is None:
        raise SystemExit(f"no worker.py with LAB8_GPU={args.kill_gpu} is running")
    sampler = Sampler(args.gpu_list).start()
    t0 = time.time()
    qs = QueueSampler(cli).start(t0)
    gap = args.within / args.jobs
    kill = {"gpu": args.kill_gpu, "pid": pid, "signal": "SIGKILL", "planned_at_s": args.kill_at}

    async def fire(i):
        await asyncio.sleep(i * gap)
        return await cli.one_job(i)

    async def killer():
        await asyncio.sleep(max(0.0, t0 + args.kill_at - time.time()))
        s = await cli.stats()
        w = next((w for w in s["workers"] if w.get("gpu") == args.kill_gpu), {})
        kill["worker"] = w.get("worker")
        kill["job_in_hand"] = w.get("current_job")
        kill["jobs_done_before_kill"] = w.get("jobs_done", 0) - next(
            (b.get("jobs_done", 0) for b in before["workers"] if b["worker"] == w.get("worker")), 0)
        os.kill(pid, signal.SIGKILL)
        kill["at_s"] = round(time.time() - t0, 2)
        kill["queue_length_at_kill"] = s["queue_length"]
        print(f"[killtest] SIGKILL pid {pid} ({kill['worker']}) at {kill['at_s']} s, "
              f"job in hand: {kill['job_in_hand']}", flush=True)

    kt = asyncio.create_task(killer())
    recs = await asyncio.gather(*(fire(i) for i in range(args.jobs)))
    await kt
    t_clients_done = time.time()
    after = await cli.wait_idle()
    t_drained = time.time()
    sampler.stop()
    await qs.stop()
    kill["process_gone"] = not psutil.pid_exists(pid)
    ok = [r for r in recs if r["ok"]]
    for r in recs:
        if r.get("server_finished"):
            r["finished_at_s"] = round(r["server_finished"] - t0, 2)
    by_worker = {}
    for r in ok:
        by_worker[r["worker"]] = by_worker.get(r["worker"], 0) + 1
    redelivered = [{"job_id": r["job_id"], "deliveries": r.get("deliveries"),
                    "finished_by": r["worker"], "finished_at_s": r.get("finished_at_s")}
                   for r in recs if r.get("redelivered")]
    timeline = [{"t": r["finished_at_s"], "worker": r["worker"], "job_id": r["job_id"],
                 "redelivered": bool(r.get("redelivered"))}
                for r in sorted(ok, key=lambda r: r.get("finished_at_s") or 0)]
    res = {"mode": "killtest", "system": "queue", "jobs": args.jobs, "within_s": args.within,
           "poll_s": args.poll, "receipts_per_job": args.receipts, "started": t0,
           "workers": [w["worker"] for w in before["workers"] if w["connected"]],
           "kill": kill,
           "sent": len(recs), "accepted": sum(1 for r in recs if r.get("job_id")),
           "succeeded": len(ok), "failed": len(recs) - len(ok),
           "lost": sum(1 for r in recs if r.get("job_id") and not r["ok"]),
           "done_by_worker": by_worker,
           "redelivered_jobs": redelivered,
           "latency_p50_s": pct([r["latency"] for r in recs], 50),
           "latency_p95_s": pct([r["latency"] for r in recs], 95),
           "ok_latency_max_s": round(max((r["latency"] for r in ok), default=0), 3),
           "errors": {e: sum(1 for r in recs if r.get("error") == e)
                      for e in {r.get("error") for r in recs if not r["ok"]}},
           "clients_done_after_s": round(t_clients_done - t0, 1),
           "server_drained_after_s": round(t_drained - t0, 1),
           "server_jobs_done": after["jobs"]["done"] - before["jobs"]["done"],
           "server_jobs_failed": after["jobs"]["failed"] - before["jobs"]["failed"],
           "server_jobs_redelivered": after["jobs_redelivered"] - before["jobs_redelivered"],
           "dead_letter_queue": after["dead_letter_queue"],
           "workers_connected_after": after["workers_connected"]}
    res.update(qs.summary())
    res.update(sampler.window(t0, t_drained))
    res["done_timeline"] = timeline
    res["queue_timeline"] = qs.rows
    res["requests"] = recs
    return res


def save(res, out, name):
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{name}.json"
    p.write_text(json.dumps(res, indent=2, ensure_ascii=False))
    brief = {k: v for k, v in res.items() if k not in ("requests", "queue_timeline")}
    print(json.dumps(brief, ensure_ascii=False), flush=True)
    return p


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["level", "sweep", "burst", "killtest"])
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--key-file", default=os.environ.get("LAB8_KEY_FILE", "/workspace/lab8/.api_key"))
    ap.add_argument("--samples", default=str(HERE.parent / "samples"))
    ap.add_argument("--out", default=str(HERE.parent / "results" / "queue_1worker"))
    ap.add_argument("--users", type=int, default=1)
    ap.add_argument("--receipts", type=int, default=4)
    ap.add_argument("--duration", type=float, default=75)
    ap.add_argument("--warmup", type=float, default=15)
    ap.add_argument("--think", type=float, default=10)
    ap.add_argument("--poll", type=float, default=0.5, help="seconds between GET /jobs/{id}")
    ap.add_argument("--slo-p95", type=float, default=20)
    ap.add_argument("--slo-fail-pct", type=float, default=1)
    ap.add_argument("--max-users", type=int, default=64)
    ap.add_argument("--start-users", type=int, default=1, help="first N of the sweep")
    ap.add_argument("--gpus", default="0", help="GPU indexes to sample, e.g. 0,1")
    ap.add_argument("--jobs", type=int, default=60)
    ap.add_argument("--within", type=float, default=10)
    ap.add_argument("--then-burst", action="store_true", help="sweep, then run the burst")
    ap.add_argument("--kill-gpu", type=int, default=1, help="killtest: GPU whose worker is killed")
    ap.add_argument("--kill-at", type=float, default=20, help="killtest: seconds after the first job")
    args = ap.parse_args()
    args.gpu_list = [int(x) for x in args.gpus.split(",") if x.strip()]
    out = Path(args.out)
    cli = Client(args)

    if args.mode == "level":
        save(await run_level(cli, args.users, args), out, f"level_N{args.users:02d}")
    elif args.mode == "burst":
        save(await run_burst(cli, args), out, "burst")
    elif args.mode == "killtest":
        save(await run_killtest(cli, args), out, "killtest")
    else:
        n, misses, table = args.start_users, 0, []
        while n <= args.max_users:
            res = await run_level(cli, n, args)
            save(res, out, f"level_N{n:02d}")
            table.append({k: res[k] for k in ("users", "jobs_per_min", "latency_p50_s",
                                              "latency_p95_s", "latency_p99_s", "fail_pct",
                                              "gpu_util_avg_pct", "loadgen_cpu_avg_pct",
                                              "queue_length_max", "slo_pass")})
            misses = 0 if res["slo_pass"] else misses + 1
            if misses >= 2:
                break
            n = 2 if n == 1 else n + 2
        passing = [r["users"] for r in table if r["slo_pass"]]
        summary = {"mode": "sweep", "system": "queue", "gpus": args.gpu_list,
                   "slo": {"p95_s_max": args.slo_p95, "fail_pct_below": args.slo_fail_pct},
                   "max_users_meeting_slo": max(passing) if passing else 0, "levels": table}
        save(summary, out, "sweep_summary")
        if args.then_burst:
            save(await run_burst(cli, args), out, "burst")


if __name__ == "__main__":
    asyncio.run(main())
