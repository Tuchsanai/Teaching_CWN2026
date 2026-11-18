"""LAB 8 load generator (runs on the same machine as the server).

Closed-loop users: each simulated user picks 4 random receipts from the samples
folder -> sends one job -> waits for the answer (gives up after 30 s = failed)
-> thinks 10 s -> sends again.

  python loadtest.py level --users 4                   # one level (75 s, first 15 s not counted)
  python loadtest.py sweep                             # N = 1,2,4,6,8,... stop after 2 levels miss SLO
  python loadtest.py burst --jobs 60 --within 10       # 60 jobs within 10 s

Every experiment is saved as JSON in --out.
Counting rule: a request belongs to the measured window if it was SENT in
[warmup, duration). Latency percentiles use every measured request; a failed
request counts with the time the user actually waited (timeouts = 30 s).
jobs/min = successful measured jobs / measured minutes.
"""
import argparse
import asyncio
import json
import os
import random
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
    """Samples GPU util (first GPU) and this process' CPU % once per second."""

    def __init__(self, gpu_index=0):
        self.gpu = pynvml.nvmlDeviceGetHandleByIndex(gpu_index) if pynvml else None
        self.proc = psutil.Process()
        self.rows = []  # (t, gpu_util, cpu_percent)
        self._stop = threading.Event()

    def start(self):
        self.proc.cpu_percent(None)
        threading.Thread(target=self._run, daemon=True).start()
        return self

    def _run(self):
        while not self._stop.wait(1.0):
            g = pynvml.nvmlDeviceGetUtilizationRates(self.gpu).gpu if self.gpu else None
            self.rows.append((time.time(), g, self.proc.cpu_percent(None)))

    def stop(self):
        self._stop.set()

    def window(self, t0, t1):
        rows = [r for r in self.rows if t0 <= r[0] <= t1]
        g = [r[1] for r in rows if r[1] is not None]
        c = [r[2] for r in rows]
        return {
            "gpu_util_avg_pct": round(statistics.mean(g), 1) if g else None,
            "loadgen_cpu_avg_pct": round(statistics.mean(c), 1) if c else None,
            "loadgen_cpu_max_pct": round(max(c), 1) if c else None,
            "loadgen_cpu_cores": psutil.cpu_count(),
        }


class Client:
    def __init__(self, args):
        self.url = args.url.rstrip("/")
        self.key = Path(args.key_file).read_text().strip()
        self.timeout = args.timeout
        self.samples = sorted(p for p in Path(args.samples).iterdir()
                              if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
        self.blobs = {p.name: p.read_bytes() for p in self.samples}
        self.per_job = args.receipts
        self.http = httpx.AsyncClient(limits=httpx.Limits(max_connections=1000,
                                                          max_keepalive_connections=0))

    async def stats(self):
        r = await self.http.get(f"{self.url}/v1/stats", headers={"X-API-Key": self.key}, timeout=10)
        r.raise_for_status()
        return r.json()

    async def wait_idle(self, max_wait=900):
        t0 = time.time()
        while time.time() - t0 < max_wait:
            s = await self.stats()
            if s["jobs_waiting"] == 0 and not s["busy"]:
                return s
            await asyncio.sleep(1)
        return await self.stats()

    async def one_job(self, user):
        names = random.sample(list(self.blobs), self.per_job)
        files = [("files", (n, self.blobs[n], "image/jpeg")) for n in names]
        t0 = time.time()
        rec = {"user": user, "sent": t0, "files": names}
        try:
            r = await self.http.post(f"{self.url}/v1/jobs", files=files,
                                     headers={"X-API-Key": self.key}, timeout=self.timeout)
            rec["latency"] = time.time() - t0
            rec["status"] = r.status_code
            if r.status_code == 200:
                body = r.json()
                rec["ok"] = True
                rec["server_wait"] = body["wait_seconds"]
                rec["server_gpu"] = body["gpu_seconds"]
                rec["receipts_ok"] = sum(x["ok"] for x in body["receipts"])
            else:
                rec["ok"] = False
                rec["error"] = f"http {r.status_code}"
        except httpx.TimeoutException:
            rec["latency"] = time.time() - t0
            rec["ok"] = False
            rec["error"] = "timeout"
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
        "server_gpu_p50_s": pct([r["server_gpu"] for r in ok], 50),
        "errors": {e: sum(1 for r in m if r.get("error") == e)
                   for e in {r.get("error") for r in m if not r["ok"]}},
    }


async def run_level(cli, n, args):
    await cli.wait_idle()
    before = await cli.stats()
    sampler = Sampler().start()
    t0 = time.time()
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
    res = {"mode": "level", "users": n, "duration_s": args.duration, "warmup_s": args.warmup,
           "think_s": args.think, "timeout_s": args.timeout, "receipts_per_job": args.receipts,
           "started": t0, "ended": t_end}
    res.update(summarize(recs, t0, args.warmup, args.duration))
    res.update(sampler.window(t0 + args.warmup, t0 + args.duration))
    res["slo_pass"] = (res["latency_p95_s"] is not None and res["latency_p95_s"] <= args.slo_p95
                       and res["fail_pct"] < args.slo_fail_pct)
    res["server_jobs_done_client_gone"] = (after["jobs_done_client_gone"]
                                           - before["jobs_done_client_gone"])
    res["server_parse_errors"] = after["receipts_parse_error"] - before["receipts_parse_error"]
    res["requests"] = recs
    return res


async def run_burst(cli, args):
    await cli.wait_idle()
    before = await cli.stats()
    sampler = Sampler().start()
    t0 = time.time()
    gap = args.within / args.jobs

    async def fire(i):
        await asyncio.sleep(i * gap)
        return await cli.one_job(i)

    recs = await asyncio.gather(*(fire(i) for i in range(args.jobs)))
    t_clients_done = time.time()
    after = await cli.wait_idle()
    t_drained = time.time()
    sampler.stop()
    ok = [r for r in recs if r["ok"]]
    res = {"mode": "burst", "jobs": args.jobs, "within_s": args.within, "timeout_s": args.timeout,
           "receipts_per_job": args.receipts, "started": t0,
           "succeeded": len(ok), "failed": len(recs) - len(ok),
           "fail_pct": round(100 * (len(recs) - len(ok)) / len(recs), 2),
           "latency_p50_s": pct([r["latency"] for r in recs], 50),
           "latency_p95_s": pct([r["latency"] for r in recs], 95),
           "latency_p99_s": pct([r["latency"] for r in recs], 99),
           "ok_latency_max_s": round(max((r["latency"] for r in ok), default=0), 3),
           "errors": {e: sum(1 for r in recs if r.get("error") == e)
                      for e in {r.get("error") for r in recs if not r["ok"]}},
           "clients_done_after_s": round(t_clients_done - t0, 1),
           "server_drained_after_s": round(t_drained - t0, 1),
           "server_jobs_done": after["jobs_done"] - before["jobs_done"],
           "server_jobs_done_client_gone": (after["jobs_done_client_gone"]
                                            - before["jobs_done_client_gone"]),
           "server_gpu_busy_s": round(after["gpu_busy_seconds"] - before["gpu_busy_seconds"], 1)}
    res.update(sampler.window(t0, t_drained))
    res["requests"] = recs
    return res


def save(res, out, name):
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{name}.json"
    p.write_text(json.dumps(res, indent=2, ensure_ascii=False))
    brief = {k: v for k, v in res.items() if k != "requests"}
    print(json.dumps(brief, ensure_ascii=False), flush=True)
    return p


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["level", "sweep", "burst"])
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--key-file", default=os.environ.get("LAB8_KEY_FILE", "/workspace/lab8/.api_key"))
    ap.add_argument("--samples", default=str(HERE.parent / "samples"))
    ap.add_argument("--out", default=str(HERE.parent / "results" / "baseline"))
    ap.add_argument("--users", type=int, default=1)
    ap.add_argument("--receipts", type=int, default=4)
    ap.add_argument("--duration", type=float, default=75)
    ap.add_argument("--warmup", type=float, default=15)
    ap.add_argument("--think", type=float, default=10)
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("--slo-p95", type=float, default=20)
    ap.add_argument("--slo-fail-pct", type=float, default=1)
    ap.add_argument("--max-users", type=int, default=64)
    ap.add_argument("--jobs", type=int, default=60)
    ap.add_argument("--within", type=float, default=10)
    ap.add_argument("--then-burst", action="store_true", help="sweep, then run the burst")
    args = ap.parse_args()
    out = Path(args.out)
    cli = Client(args)

    if args.mode == "level":
        save(await run_level(cli, args.users, args), out, f"level_N{args.users:02d}")
    elif args.mode == "burst":
        save(await run_burst(cli, args), out, "burst")
    else:
        levels, n, misses, table = [], 1, 0, []
        while n <= args.max_users:
            res = await run_level(cli, n, args)
            save(res, out, f"level_N{n:02d}")
            table.append({k: res[k] for k in ("users", "jobs_per_min", "latency_p50_s",
                                              "latency_p95_s", "latency_p99_s", "fail_pct",
                                              "gpu_util_avg_pct", "loadgen_cpu_avg_pct",
                                              "slo_pass")})
            misses = 0 if res["slo_pass"] else misses + 1
            if misses >= 2:
                break
            n = 2 if n == 1 else n + 2
        passing = [r["users"] for r in table if r["slo_pass"]]
        summary = {"mode": "sweep", "slo": {"p95_s_max": args.slo_p95, "fail_pct_below": args.slo_fail_pct},
                   "max_users_meeting_slo": max(passing) if passing else 0, "levels": table}
        save(summary, out, "sweep_summary")
        if args.then_burst:
            save(await run_burst(cli, args), out, "burst")


if __name__ == "__main__":
    asyncio.run(main())
