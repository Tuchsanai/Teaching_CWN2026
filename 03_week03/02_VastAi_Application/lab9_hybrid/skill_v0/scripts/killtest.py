"""LAB 9: kill a GPU worker in the middle of the work and prove no job is lost.

Runs on the rented machine next to gateway.py while 2 workers (gpu0, gpu1) are up.
  1. 90 jobs arrive at the gateway within 3 s; one of them is a bad job (prompt = blank text)
  2. at second 4 the gpu1 worker gets SIGKILL (no clean shutdown, no chance to ack / save anything)
     -> RabbitMQ hands the jobs it held (unacked) to gpu0, marked "redelivered"
  3. every 0.5 s: jobs waiting / running / done / dead + which workers still send heartbeats
  4. waits until every job is done or dead, downloads every image, then starts gpu1 again
     and keeps watching until it is back (heartbeat) -> JSON
Run: python killtest.py [--out killtest.json]
"""
import argparse, asyncio, json, os, signal, subprocess, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--host", default="127.0.0.1")
ap.add_argument("--port", type=int, default=8000)
ap.add_argument("--key-file", default="/workspace/lab9/api_key.txt")
ap.add_argument("--prompts", default=str(Path(__file__).with_name("prompts.txt")))
ap.add_argument("--amqp", default=os.environ.get("AMQP_URL", "amqp://guest:guest@127.0.0.1/"))
ap.add_argument("--jobs", type=int, default=90)
ap.add_argument("--within", type=float, default=3.0, help="all jobs arrive within this many seconds")
ap.add_argument("--bad-index", type=int, default=45, help="which job is the bad one (blank prompt)")
ap.add_argument("--kill-at", type=float, default=4.0)
ap.add_argument("--kill-gpu", type=int, default=1)
ap.add_argument("--restart-cmd", default="cd /workspace/lab9/code && exec /venv/main/bin/python worker.py "
                                         "--gpu {gpu} --name gpu{gpu} >> /workspace/lab9/worker_gpu{gpu}.log 2>&1")
ap.add_argument("--out", default="killtest.json")
args = ap.parse_args()

HOST, PORT = args.host, args.port
KEY = Path(args.key_file).read_text().strip()
PROMPTS = [l.strip() for l in open(args.prompts, encoding="utf-8") if l.strip()]
VICTIM = f"gpu{args.kill_gpu}"
HB_ALIVE = 2.5          # a worker counts as alive if its last heartbeat is younger than this


# ---------- tiny HTTP/1.1 client (stdlib only) ----------
async def http(method, path, body=b""):
    r, w = await asyncio.open_connection(HOST, PORT)
    try:
        h = {"Host": f"{HOST}:{PORT}", "Connection": "close", "Content-Length": str(len(body)),
             "X-API-Key": KEY, "Content-Type": "application/json"}
        w.write((f"{method} {path} HTTP/1.1\r\n" + "".join(f"{k}: {v}\r\n" for k, v in h.items())
                 + "\r\n").encode() + body)
        await w.drain()
        data = await r.read()
        head, _, payload = data.partition(b"\r\n\r\n")
        return int(head.split(b" ", 2)[1]), payload
    finally:
        w.close()

async def stats():
    return json.loads((await http("GET", "/stats"))[1])


# ---------- worker events from RabbitMQ (heartbeat / started / done / failed) ----------
events, last_hb = [], {}
async def watch_events(t0_box):
    import aio_pika
    conn = await aio_pika.connect_robust(args.amqp)
    ch = await conn.channel()
    ex = await ch.declare_exchange("jobs.events", aio_pika.ExchangeType.TOPIC, durable=True)
    q = await ch.declare_queue("", exclusive=True, auto_delete=True)   # private copy of every event
    await q.bind(ex, routing_key="#")
    async def on_msg(m):
        async with m.process():
            e = json.loads(m.body); now = time.time()
            if e["type"] == "heartbeat":
                last_hb[e["worker"]] = (now, e.get("working", 0))
            else:
                events.append({"t": round(now - t0_box[0], 3), **{k: e.get(k) for k in
                               ("type", "worker", "job_id", "redelivered", "requeue", "error", "batch")}})
    await q.consume(on_msg)
    return conn

def worker_pids(gpu):
    out = subprocess.run(["pgrep", "-f", f"worker.py --gpu {gpu} "], capture_output=True, text=True).stdout
    return [int(p) for p in out.split()]


async def main():
    t0 = [time.time()]
    conn = await watch_events(t0)
    await asyncio.sleep(2.5)                                  # collect heartbeats first
    before = await stats()
    alive0 = sorted(w for w, (t, _) in last_hb.items() if time.time() - t < HB_ALIVE)
    assert {"gpu0", VICTIM} <= set(alive0), f"need gpu0 and {VICTIM} alive, got {alive0}"
    victim_pids = worker_pids(args.kill_gpu)
    assert victim_pids, f"no worker process for gpu {args.kill_gpu}"
    print(f"workers alive: {alive0}; {VICTIM} pid {victim_pids}", flush=True)

    jobs = [{"n": i, "bad": i == args.bad_index,
             "prompt": "   " if i == args.bad_index else PROMPTS[i % len(PROMPTS)]} for i in range(args.jobs)]
    timeline, marks = [], {}
    events.clear()
    t0[0] = time.time()
    rel = lambda: round(time.time() - t0[0], 3)
    stop = asyncio.Event()

    async def sampler():                                      # every 0.5 s on a fixed clock
        k = 0
        while not stop.is_set():
            await asyncio.sleep(max(0, t0[0] + 0.5 * k - time.time()))
            s = await stats(); now = time.time()
            alive = {w: now - t < HB_ALIVE for w, (t, _) in last_hb.items()}
            timeline.append({
                "t": round(0.5 * k, 1),
                "waiting": s["waiting"]["normal"] + s["waiting"]["express"],
                "in_rabbitmq": s["waiting"]["in_rabbitmq"],
                "running": s["running"],
                "done": s["done"] - before["done"],
                "dead": s["dead"]["jobs"] - before["dead"]["jobs"],
                "in_dead_letter_queue": s["dead"]["in_dead_letter_queue"],
                "redelivered": s["redelivered"] - before["redelivered"],
                "workers_alive": sorted(w for w, a in alive.items() if a),
                "working": {w: last_hb[w][1] for w, a in alive.items() if a},
            })
            k += 1

    async def submit(job):
        await asyncio.sleep(job["n"] * args.within / args.jobs)
        job["submit_sec"] = rel()
        code, p = await http("POST", "/jobs", json.dumps({"prompt": job["prompt"], "priority": "normal"}).encode())
        job["http"] = code
        job["job_id"] = json.loads(p).get("job_id") if code == 202 else None

    async def killer():
        await asyncio.sleep(max(0, t0[0] + args.kill_at - time.time()))
        hb = last_hb.get(VICTIM, (0, 0))
        for pid in victim_pids:
            os.kill(pid, signal.SIGKILL)                      # no cleanup, no ack, no save
        marks["kill_sec"] = rel()
        marks["victim_working_at_kill"] = hb[1]
        print(f"t={marks['kill_sec']}s SIGKILL {VICTIM} (was drawing {hb[1]} images)", flush=True)

    samp = asyncio.create_task(sampler())
    await asyncio.gather(*(submit(j) for j in jobs), killer())
    marks["last_submit_sec"] = max(j["submit_sec"] for j in jobs)
    print(f"accepted {sum(j['http'] == 202 for j in jobs)}/{len(jobs)}, last at t={marks['last_submit_sec']}s", flush=True)

    async def follow(job):                                    # long-poll until done / dead
        if not job["job_id"]:
            return
        while rel() < 300:
            _, p = await http("GET", f"/jobs/{job['job_id']}?wait=10")
            st = json.loads(p)
            if st["status"] in ("done", "dead"):
                job.update(status=st["status"], worker=st.get("worker"), attempts=st.get("attempts"),
                           error=st.get("error"), end_sec=rel())
                return
        job["status"] = "timeout"
    await asyncio.gather(*(follow(j) for j in jobs))
    marks["all_finished_sec"] = max(j.get("end_sec") or 0 for j in jobs)
    print(f"all jobs finished by t={marks['all_finished_sec']}s", flush=True)

    sem = asyncio.Semaphore(8)                                # every finished image must download
    async def fetch(job):
        if job.get("status") == "done":
            async with sem:
                code, p = await http("GET", f"/jobs/{job['job_id']}/image")
                job["image_ok"] = code == 200 and p[:2] == b"\xff\xd8"
    await asyncio.gather(*(fetch(j) for j in jobs))

    # --- bring the killed worker back ---
    await asyncio.sleep(1.0)
    subprocess.Popen(["bash", "-c", args.restart_cmd.format(gpu=args.kill_gpu)], start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    marks["restart_sec"] = rel()
    print(f"t={marks['restart_sec']}s restarted {VICTIM}", flush=True)
    while rel() < marks["restart_sec"] + 240:
        hb = last_hb.get(VICTIM)
        if hb and hb[0] - t0[0] > marks["restart_sec"]:
            marks["victim_back_sec"] = round(hb[0] - t0[0], 3)
            break
        await asyncio.sleep(0.5)
    print(f"{VICTIM} back at t={marks.get('victim_back_sec')}s", flush=True)
    await asyncio.sleep(2.0)
    stop.set(); await samp
    after = await stats()
    await conn.close()

    good = [j for j in jobs if not j["bad"]]; bad = [j for j in jobs if j["bad"]]
    kill = marks["kill_sec"]
    victim_started = {e["job_id"] for e in events
                      if e["type"] == "started" and e["worker"] == VICTIM and e["t"] <= kill}
    victim_done = {e["job_id"] for e in events if e["type"] == "done" and e["worker"] == VICTIM}
    summary = {
        "jobs_sent": len(jobs), "good_jobs_sent": len(good), "bad_jobs_sent": len(bad),
        "accepted_202": sum(j["http"] == 202 for j in jobs),
        "good_jobs_done": sum(j.get("status") == "done" for j in good),
        "good_jobs_lost": sum(j.get("status") != "done" for j in good),
        "images_downloaded_ok": sum(bool(j.get("image_ok")) for j in good),
        "bad_jobs_dead_lettered": sum(j.get("status") == "dead" for j in bad),
        "redelivered_jobs": sum((j.get("attempts") or 0) > 1 for j in jobs),
        "redelivered_counter_delta": after["redelivered"] - before["redelivered"],
        "dead_letter_queue_delta": after["dead"]["in_dead_letter_queue"] - before["dead"]["in_dead_letter_queue"],
        "victim": VICTIM,
        "victim_jobs_in_hand_at_kill": sorted(victim_started - victim_done),
        "done_by_worker": {w: sum(j.get("worker") == w and j.get("status") == "done" for j in good)
                           for w in ("gpu0", VICTIM)},
        **marks,
        "workers_alive_after": after["live_workers"],
    }
    out = {"test": "kill_worker",
           "settings": {k: v for k, v in vars(args).items() if k not in ("key_file", "amqp")},
           "summary": summary,
           "server_stats_before": {k: before[k] for k in ("done", "redelivered", "dead", "live_workers")},
           "server_stats_after": {k: after[k] for k in ("done", "redelivered", "dead", "live_workers",
                                                       "waiting", "running")},
           "timeline_every_0_5s": timeline, "events": events,
           "jobs": [{k: j.get(k) for k in ("n", "bad", "submit_sec", "http", "job_id", "status", "worker",
                                           "attempts", "error", "end_sec", "image_ok")} for j in jobs],
           "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(summary, indent=1), flush=True)

asyncio.run(main())
