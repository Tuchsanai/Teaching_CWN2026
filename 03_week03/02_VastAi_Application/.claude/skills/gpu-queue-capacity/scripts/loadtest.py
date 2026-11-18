"""LAB 9: load test for the synchronous image API - how many concurrent users fit on 1 GPU?

Runs on the same rented machine as the API. Each simulated user: send a prompt -> wait for the
JPEG (give up after 30 s = failed) -> look at it for 2.5-7.5 s (mean 5) -> send again.
Levels N = 1, 8, 16, ... 320, 30 s each, first 10 s not counted; drain the server queue between
levels; stop at the first level that breaks the SLO (p95 <= 10 s and failed < 1 %), then try the
midpoint twice to narrow the answer. Saves everything to a JSON file.
Run: python loadtest.py [--url http://127.0.0.1:8000] [--out loadtest.json]
     [--levels 16,32,64] [--level-sec 30] [--warmup-sec 10] [--refine 2]   (skill v0: shorter ladders)

--mode hybrid: the same users, levels and SLO against gateway.py (job queue + GPU worker).
A user's request = POST /jobs -> long-poll GET /jobs/{id}?wait=.. until done -> GET /jobs/{id}/image;
the clock runs from submit until the JPEG is downloaded (still 30 s max). 429 (queue full) = failed.
It also listens to the workers' "done" events on RabbitMQ (exchange jobs.events) to report how many
images the worker drew together per batch at each level.
Run: python loadtest.py --mode hybrid --out loadtest_hybrid.json

--burst: a short overload instead of the ladder. 200 jobs arrive at random moments inside 10 s
(no thinking, each job = one user), then the script waits until the server has no queued/running work.
  sync   : each user gives up after 30 s (connection closed). The server still draws those images;
           wasted images = images the server finished during the test - images users received.
  hybrid : 10 % of the jobs are express. A 429 answer -> sleep Retry-After seconds, then submit again.
           Each user is willing to wait 300 s in total (429 waits included).
  Records per job (arrival, first answer, wait, ok, 429s), wait p50/p95/max (all / express / normal),
  429 count, the server backlog every 0.5 s, wasted images, drain time -> JSON.
Run: python loadtest.py --burst --url http://127.0.0.1:8001 --out burst_sync.json
     python loadtest.py --burst --mode hybrid --out burst_hybrid.json
"""
import argparse, asyncio, itertools, json, os, random, statistics, subprocess, threading, time
from pathlib import Path
from urllib.parse import urlparse

LEVELS = [1, 8, 16, 24, 32, 48, 64, 96, 128, 160, 192, 256, 320]
LEVEL_SEC, WARMUP_SEC, TIMEOUT_SEC = 30.0, 10.0, 30.0
THINK_MIN, THINK_MAX = 2.5, 7.5
SLO_P95_SEC, SLO_FAIL_PCT = 10.0, 1.0
REFINE_STEPS = 2

ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://127.0.0.1:8000")
ap.add_argument("--key-file", default="/workspace/lab9/api_key.txt")
ap.add_argument("--prompts", default=str(Path(__file__).with_name("prompts.txt")))
ap.add_argument("--out", default="loadtest.json")
ap.add_argument("--mode", choices=["sync", "hybrid"], default="sync",
                help="sync = POST /generate returns the JPEG; hybrid = POST /jobs -> wait -> GET image")
ap.add_argument("--amqp", default=os.environ.get("AMQP_URL", "amqp://guest:guest@127.0.0.1/"),
                help="hybrid only: RabbitMQ, to count images per worker batch")
ap.add_argument("--burst", action="store_true", help="run the short-overload burst test instead of the ladder")
ap.add_argument("--burst-jobs", type=int, default=200)
ap.add_argument("--burst-sec", type=float, default=10.0, help="all jobs arrive within this many seconds")
ap.add_argument("--express-pct", type=float, default=10.0, help="hybrid burst: share of express jobs")
ap.add_argument("--sync-giveup", type=float, default=30.0, help="sync burst: user gives up after this")
ap.add_argument("--hybrid-giveup", type=float, default=300.0, help="hybrid burst: total wait a user accepts")
ap.add_argument("--seed", type=int, default=8)
ap.add_argument("--levels", default=None, help="comma list of N, e.g. 16,32,64 (default: 1,8,16,...,320)")
ap.add_argument("--level-sec", type=float, default=None, help="seconds per level (default 30)")
ap.add_argument("--warmup-sec", type=float, default=None, help="first seconds of a level not counted (default 10)")
ap.add_argument("--refine", type=int, default=None, help="midpoint retries after the first failing level (default 2)")
args = ap.parse_args()
if args.levels: LEVELS = [int(x) for x in args.levels.split(",") if x.strip()]
if args.level_sec: LEVEL_SEC = args.level_sec
if args.warmup_sec is not None: WARMUP_SEC = args.warmup_sec
if args.refine is not None: REFINE_STEPS = args.refine
assert WARMUP_SEC < LEVEL_SEC, "warm-up must be shorter than a level"
U = urlparse(args.url); HOST, PORT = U.hostname, U.port or 80
API_KEY = Path(args.key_file).read_text().strip()
PROMPTS = [l.strip() for l in open(args.prompts, encoding="utf-8") if l.strip()]
next_prompt = itertools.cycle(PROMPTS).__next__   # all users take turns through the 12 prompts


# ---------- tiny HTTP/1.1 client (stdlib only, one connection per request) ----------
async def http(method, path, body=b"", headers=None):
    code, _, payload = await http_h(method, path, body, headers)
    return code, payload

async def http_h(method, path, body=b"", headers=None):
    """same as http() but also returns the response headers (lower-case names)"""
    r, w = await asyncio.open_connection(HOST, PORT)
    try:
        h = {"Host": f"{HOST}:{PORT}", "Connection": "close", "Content-Length": str(len(body)), **(headers or {})}
        w.write((f"{method} {path} HTTP/1.1\r\n" + "".join(f"{k}: {v}\r\n" for k, v in h.items()) + "\r\n").encode() + body)
        await w.drain()
        data = await r.read()                       # server closes -> whole response
        head, _, payload = data.partition(b"\r\n\r\n")
        lines = head.decode("latin-1").split("\r\n")
        hdrs = {k.strip().lower(): v.strip() for k, _, v in (l.partition(":") for l in lines[1:])}
        return int(lines[0].split(" ", 2)[1]), hdrs, payload
    finally:
        w.close()

async def stats():
    _, p = await http("GET", "/stats", headers={"X-API-Key": API_KEY})
    return json.loads(p)

def busy(s):
    """jobs still queued or running on the server (sync_server and gateway report it differently)"""
    if "waiting_or_running" in s:
        return s["waiting_or_running"]
    w = s["waiting"]
    return w["normal"] + w["express"] + w["in_rabbitmq"] + s["running"]


# ---------- hybrid: watch worker "done" events -> images per batch ----------
batch_events = []   # (time, batch size) - one event per finished image
async def watch_batches():
    import aio_pika
    conn = await aio_pika.connect_robust(args.amqp)
    ch = await conn.channel()
    ex = await ch.declare_exchange("jobs.events", aio_pika.ExchangeType.TOPIC, durable=True)
    q = await ch.declare_queue("", exclusive=True, auto_delete=True)   # private, gone when we exit
    await q.bind(ex, routing_key="done.#")
    async def on_msg(m):
        async with m.process():
            e = json.loads(m.body)
            batch_events.append((time.monotonic(), int(e.get("batch", 1))))
    await q.consume(on_msg)
    return conn

def mean_batch(t0, t1):
    ev = [b for t, b in batch_events if t0 <= t < t1]
    if not ev: return None
    batches = sum(1 / b for b in ev)          # a batch of b images sends b events
    return round(len(ev) / batches, 2)


# ---------- one request: sync (one POST) or hybrid (submit -> wait -> download) ----------
JSON_HDR = {"Content-Type": "application/json", "X-API-Key": API_KEY}

async def request_sync(prompt):
    code, payload = await http("POST", "/generate", json.dumps({"prompt": prompt}).encode(), JSON_HDR)
    return code == 200 and payload[:2] == b"\xff\xd8"           # got a real JPEG

async def request_hybrid(prompt):
    code, payload = await http("POST", "/jobs", json.dumps({"prompt": prompt}).encode(), JSON_HDR)
    if code != 202:                                         # 429 queue full (or any error) = failed
        return False
    jid = json.loads(payload)["job_id"]
    while True:                                             # long poll: server answers when done (<= 10 s)
        code, payload = await http("GET", f"/jobs/{jid}?wait=10", headers={"X-API-Key": API_KEY})
        if code != 200: return False
        st = json.loads(payload)["status"]
        if st == "done": break
        if st not in ("queued", "running"): return False    # dead
    code, payload = await http("GET", f"/jobs/{jid}/image", headers={"X-API-Key": API_KEY})
    return code == 200 and payload[:2] == b"\xff\xd8"           # picture downloaded = success

do_request = request_hybrid if args.mode == "hybrid" else request_sync


# ---------- GPU utilization sampler (nvidia-smi every 0.5 s, in a thread) ----------
gpu_samples = []   # (time, [util per GPU])
def gpu_sampler(stop):
    while not stop.is_set():
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=5).stdout
            gpu_samples.append((time.monotonic(), [float(x) for x in out.split()]))
        except Exception:
            pass
        stop.wait(0.5)


# ---------- one simulated user ----------
async def user(t_end, log):
    await asyncio.sleep(random.uniform(0, THINK_MAX))   # spread out the first clicks
    while time.monotonic() < t_end:
        t0 = time.monotonic(); ok = False
        try:
            ok = await asyncio.wait_for(do_request(next_prompt()), TIMEOUT_SEC)
        except (asyncio.TimeoutError, OSError, ValueError, IndexError, KeyError):
            ok = False
        t1 = time.monotonic()
        log.append((t0, t1, t1 - t0, ok))
        await asyncio.sleep(random.uniform(THINK_MIN, THINK_MAX))  # user looks at the picture


def pct(xs, q):
    if not xs: return None
    xs = sorted(xs); k = (len(xs) - 1) * q / 100; f = int(k); c = min(f + 1, len(xs) - 1)
    return round(xs[f] + (xs[c] - xs[f]) * (k - f), 3)


# ---------- one level of N concurrent users ----------
async def run_level(n):
    log = []
    t_start = time.monotonic(); t_end = t_start + LEVEL_SEC; w0 = t_start + WARMUP_SEC
    tasks = [asyncio.create_task(user(t_end, log)) for _ in range(n)]
    await asyncio.sleep(WARMUP_SEC); c0, tc0 = os.times(), time.monotonic()
    await asyncio.sleep(max(0, t_end - time.monotonic()))
    c1, tc1 = os.times(), time.monotonic()
    cpu_pct = round(100 * ((c1.user + c1.system) - (c0.user + c0.system)) / (tc1 - tc0), 1)
    # stop: users still waiting finish their request (or hit the 30 s timeout); thinking users stop
    await asyncio.gather(*tasks, return_exceptions=True)
    # wait until the server has no queued/running work left (abandoned requests still run on the GPU)
    t_drain = time.monotonic()
    while time.monotonic() - t_drain < 300:
        try:
            if busy(await stats()) == 0: break
        except Exception:
            pass
        await asyncio.sleep(0.5)
    drain_sec = round(time.monotonic() - t_drain, 1)

    win = [x for x in log if w0 <= x[1] < t_end]          # requests that finished inside the measured 20 s
    ok_lat = [x[2] for x in win if x[3]]
    failed = sum(1 for x in win if not x[3])
    # requests still in flight at the end that later timed out also count as failed
    late_fail = sum(1 for x in log if x[1] >= t_end and x[0] < t_end and not x[3])
    failed += late_fail
    total = len(win) + late_fail
    fail_pct = round(100 * failed / total, 2) if total else 0.0
    gs = [u for t, u in gpu_samples if w0 <= t < t_end]
    gpu_util = [round(statistics.mean(col), 1) for col in zip(*gs)] if gs else []
    p95 = pct(ok_lat, 95)
    passed = bool(ok_lat) and p95 <= SLO_P95_SEC and fail_pct < SLO_FAIL_PCT
    row = {"users": n, "requests_measured": total, "images_ok": len(ok_lat), "failed": failed,
           "images_per_sec": round(len(ok_lat) / (t_end - w0), 2),
           "p50_sec": pct(ok_lat, 50), "p95_sec": p95, "p99_sec": pct(ok_lat, 99),
           "failed_pct": fail_pct, "gpu_util_pct": gpu_util,
           "loadgen_cpu_pct_of_one_core": cpu_pct, "loadgen_cpu_pct_of_machine": round(cpu_pct / os.cpu_count(), 2),
           "drain_sec": drain_sec, "slo_pass": passed}
    if args.mode == "hybrid":
        row["avg_images_per_batch"] = mean_batch(w0, t_end)
        row["batches_measured"] = round(sum(1 / b for t, b in batch_events if w0 <= t < t_end))
    print(json.dumps(row), flush=True)
    return row


async def main():
    stop = threading.Event(); threading.Thread(target=gpu_sampler, args=(stop,), daemon=True).start()
    amqp_conn = await watch_batches() if args.mode == "hybrid" else None
    s0 = await stats()
    print(f"API ok, {len(PROMPTS)} prompts, server stats before: {s0}", flush=True)
    rows, last_pass, first_fail = [], None, None
    for n in LEVELS:                                   # 1) climb the ladder
        r = await run_level(n); rows.append(r)
        if r["slo_pass"]: last_pass = n
        else: first_fail = n; break
    lo, hi = last_pass or 0, first_fail
    for _ in range(REFINE_STEPS if hi else 0):         # 2) midpoint twice between last pass and first fail
        mid = (lo + hi) // 2
        if mid in (lo, hi) or mid == 0: break
        r = await run_level(mid); r["refine"] = True; rows.append(r)
        if r["slo_pass"]: lo = mid
        else: hi = mid
    stop.set()
    out = {"api": args.url, "mode": args.mode, "slo": {"p95_sec_max": SLO_P95_SEC, "failed_pct_lt": SLO_FAIL_PCT},
           "user_model": {"think_sec": [THINK_MIN, THINK_MAX], "timeout_sec": TIMEOUT_SEC, "prompts": len(PROMPTS)},
           "level_sec": LEVEL_SEC, "warmup_sec": WARMUP_SEC, "cpu_count": os.cpu_count(),
           "levels": sorted(rows, key=lambda r: r["users"]),
           "max_users_meeting_slo": lo, "first_failing_users": hi,
           "server_stats_after": await stats(), "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
    if amqp_conn: await amqp_conn.close()
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"MAX USERS MEETING SLO = {lo} (first failing = {hi}) -> {args.out}", flush=True)


# ---------- burst: 200 jobs inside 10 s, then wait until the server is empty ----------
async def burst_job(job, t_burst):
    """one user = one job. Fills: first_answer_sec, wait_sec, ok, n_429, gave_up"""
    await asyncio.sleep(max(0, t_burst + job["arrive_sec"] - time.monotonic()))
    t0 = time.monotonic(); job["n_429"] = 0

    def answered():                                     # first HTTP answer of any kind (JPEG, 202, 429)
        if job.get("first_answer_sec") is None:
            job["first_answer_sec"] = round(time.monotonic() - t0, 3)

    async def sync_flow():
        code, payload = await http("POST", "/generate", json.dumps({"prompt": job["prompt"]}).encode(), JSON_HDR)
        answered()
        return code == 200 and payload[:2] == b"\xff\xd8"

    async def hybrid_flow():
        body = json.dumps({"prompt": job["prompt"], "priority": job["priority"]}).encode()
        while True:                                     # submit; on 429 wait as told, then submit again
            code, hdrs, payload = await http_h("POST", "/jobs", body, JSON_HDR)
            answered()
            if code == 202: break
            if code != 429: return False
            job["n_429"] += 1
            retry = float(hdrs.get("retry-after") or json.loads(payload).get("retry_after_seconds", 1))
            job.setdefault("retry_after_told", []).append(retry)
            await asyncio.sleep(retry)
        job["job_id"] = jid = json.loads(payload)["job_id"]
        job["accepted_sec"] = round(time.monotonic() - t0, 3)
        while True:                                     # long poll until done
            code, payload = await http("GET", f"/jobs/{jid}?wait=10", headers={"X-API-Key": API_KEY})
            if code != 200: return False
            st = json.loads(payload)["status"]
            if st == "done": break
            if st not in ("queued", "running"): return False
        code, payload = await http("GET", f"/jobs/{jid}/image", headers={"X-API-Key": API_KEY})
        return code == 200 and payload[:2] == b"\xff\xd8"

    giveup = args.hybrid_giveup if args.mode == "hybrid" else args.sync_giveup
    try:
        job["ok"] = await asyncio.wait_for(hybrid_flow() if args.mode == "hybrid" else sync_flow(), giveup)
        job["gave_up"] = False
    except asyncio.TimeoutError:
        job["ok"], job["gave_up"] = False, True        # connection dropped, user left
    except (OSError, ValueError, IndexError, KeyError) as e:
        job["ok"], job["gave_up"], job["error"] = False, False, type(e).__name__
    job["end_sec"] = round(time.monotonic() - t_burst, 3)
    job["wait_sec"] = round(time.monotonic() - t0, 3)


def wait_summary(jobs):
    w = [j["wait_sec"] for j in jobs if j["ok"]]
    fa = [j["first_answer_sec"] for j in jobs if j.get("first_answer_sec") is not None]
    return {"jobs": len(jobs), "ok": len(w), "ok_pct": round(100 * len(w) / len(jobs), 1) if jobs else None,
            "gave_up": sum(j["gave_up"] for j in jobs), "errors": sum(1 for j in jobs if "error" in j),
            "wait_p50_sec": pct(w, 50), "wait_p95_sec": pct(w, 95), "wait_max_sec": round(max(w), 3) if w else None,
            "first_answer_p50_sec": pct(fa, 50), "first_answer_p95_sec": pct(fa, 95),
            "jobs_got_429": sum(1 for j in jobs if j.get("n_429")), "answers_429": sum(j.get("n_429", 0) for j in jobs)}


def short(s):
    return {k: v for k, v in s.items() if k not in ("workers", "recent_done")}


async def burst_main():
    rnd = random.Random(args.seed)
    n = args.burst_jobs
    arrive = sorted(rnd.uniform(0, args.burst_sec) for _ in range(n))
    express = set(rnd.sample(range(n), round(n * args.express_pct / 100))) if args.mode == "hybrid" else set()
    jobs = [{"n": i, "arrive_sec": round(a, 3), "prompt": next_prompt(),
             "priority": "express" if i in express else "normal"} for i, a in enumerate(arrive)]
    stop = threading.Event(); threading.Thread(target=gpu_sampler, args=(stop,), daemon=True).start()
    amqp_conn = await watch_batches() if args.mode == "hybrid" else None
    s0 = await stats()
    if busy(s0):
        raise SystemExit(f"server not idle before the burst: {short(s0)}")
    print(f"burst {args.mode}: {n} jobs in {args.burst_sec} s ({len(express)} express), stats before: {short(s0)}",
          flush=True)

    backlog = []                                        # every 0.5 s: jobs queued or running on the server
    t_burst = time.monotonic()
    all_users = asyncio.gather(*[asyncio.create_task(burst_job(j, t_burst)) for j in jobs])
    drained_at, k = None, 0
    while True:
        t = round(time.monotonic() - t_burst, 1)
        try:
            s = await stats(); b = busy(s)
            row = {"t": t, "backlog": b}
            if "waiting" in s:
                row |= {"normal": s["waiting"]["normal"], "express": s["waiting"]["express"], "running": s["running"]}
            row["users_waiting"] = sum(1 for j in jobs if j["arrive_sec"] <= t and "end_sec" not in j)
            row["users_done_ok"] = sum(1 for j in jobs if j.get("ok"))
            backlog.append(row)
            if k % 10 == 0:
                print(json.dumps(row), flush=True)
            if all_users.done() and b == 0:
                drained_at = t; break
        except Exception as e:
            print("stats error", type(e).__name__, e, flush=True)
        if t > 1800: break
        k += 1
        await asyncio.sleep(max(0, t_burst + k * 0.5 - time.monotonic()))
    await all_users
    stop.set()
    s1 = await stats()

    done_images = s1["done"] - s0["done"]
    got = sum(j["ok"] for j in jobs)
    oks = sorted(j["end_sec"] for j in jobs if j["ok"])
    fa = sorted(j["arrive_sec"] + j["first_answer_sec"] for j in jobs if j.get("first_answer_sec") is not None)
    out = {"test": "burst", "mode": args.mode, "api": args.url, "seed": args.seed,
           "settings": {"jobs": n, "arrive_within_sec": args.burst_sec,
                        "express_pct": args.express_pct if args.mode == "hybrid" else 0,
                        "user_gives_up_after_sec": args.hybrid_giveup if args.mode == "hybrid" else args.sync_giveup,
                        "on_429": "sleep Retry-After then resubmit" if args.mode == "hybrid" else None},
           "summary": wait_summary(jobs),
           "by_priority": {p: wait_summary([j for j in jobs if j["priority"] == p])
                           for p in ("express", "normal") if any(j["priority"] == p for j in jobs)},
           "first_answer_after_burst_start_sec": round(fa[0], 3) if fa else None,
           "first_image_after_burst_start_sec": oks[0] if oks else None,
           "last_image_after_burst_start_sec": oks[-1] if oks else None,
           "images_drawn_by_server": done_images,
           "images_received_by_users": got,
           "images_wasted": done_images - got,          # drawn for users who had already left
           "server_429_counter_delta": s1.get("rejected_429", 0) - s0.get("rejected_429", 0),
           "peak_backlog": max((r["backlog"] for r in backlog), default=0),
           "drained_after_sec": drained_at,
           "gpu_util_mean_pct": [round(statistics.mean(c), 1) for c in zip(*[u for _, u in gpu_samples])]
                                if gpu_samples else [],
           "backlog_every_0_5s": backlog,
           "jobs": jobs,
           "server_stats_before": short(s0), "server_stats_after": short(s1),
           "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
    if args.mode == "hybrid":
        out["avg_images_per_batch"] = mean_batch(t_burst, time.monotonic())
    if amqp_conn: await amqp_conn.close()
    Path(args.out).write_text(json.dumps(out, indent=2))
    keys = ("summary", "by_priority", "first_answer_after_burst_start_sec", "first_image_after_burst_start_sec",
            "last_image_after_burst_start_sec", "images_drawn_by_server", "images_wasted",
            "server_429_counter_delta", "peak_backlog", "drained_after_sec", "gpu_util_mean_pct")
    print(json.dumps({k: out.get(k) for k in keys} | {"avg_images_per_batch": out.get("avg_images_per_batch")},
                     indent=1), flush=True)
    print(f"-> {args.out}", flush=True)

asyncio.run(burst_main() if args.burst else main())

