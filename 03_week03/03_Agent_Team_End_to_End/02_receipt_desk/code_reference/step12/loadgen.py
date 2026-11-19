#!/usr/bin/env python3
"""ReceiptDesk load generator (step 12 · capacity tests against the live API gateway).

Runs ON the GPU machine (label e2e-receipt) and calls the gateway API exactly as the web
dispatcher does (G2 POST /v1/receipts, G4 GET /v1/jobs, G5 urgent, G6 queue, G7 delete).
The API key is read from secrets.env and never printed.

usage: loadgen.py prep                      extract Test Set receipts (CORD-v2 test split) + 2 broken files
       loadgen.py capacity --workers 1|2    100 normal receipts, time until all have a result
       loadgen.py urgent                    100 normal pending + 10 urgent (G5), time + BR-10 order
       loadgen.py queuefull                 submit past the 400 cap, check 429 body, nothing lost
       loadgen.py crash                     40 receipts, kill -9 one worker mid-run, restart it
       loadgen.py dlq                       2 broken files + 20 good: DLQ after 3 attempts, others not blocked
       loadgen.py state                     queue + workers (normal-state check)
Every test writes results/<test>.json next to this script.
"""
import argparse, asyncio, io, json, math, os, random, sqlite3, subprocess, sys, time, uuid
from datetime import datetime
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
S = Path("/workspace/e2e_receipt/step11")
DATA = Path("/workspace/e2e_receipt/data/cord-v2/data")
IMG = HERE / "images"; BAD = HERE / "bad"; OUT = HERE / "results"
GW = os.environ.get("GW_URL", "http://127.0.0.1:8000")
DB = S / "gateway-data" / "gateway.db"


def api_key() -> str:
    for line in (S / "secrets.env").read_text().splitlines():
        if line.startswith("GATEWAY_API_KEYS=") or line.startswith("GATEWAY_API_KEY="):
            return line.split("=", 1)[1].split(",")[0].strip().strip('"')
    sys.exit("no gateway key in secrets.env")


H = {"X-API-Key": api_key()}


def ts(iso: str | None) -> float | None:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp() if iso else None


def save(name: str, obj) -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False))
    print(f"saved results/{name}.json")


def svc(action: str, name: str) -> None:
    subprocess.run(["bash", str(S / "svc.sh"), action, name], check=False)


def kill9(name: str) -> int:
    pane = subprocess.check_output(["tmux", "list-panes", "-t", name, "-F", "#{pane_pid}"], text=True).split()[0]
    pid = int(subprocess.check_output(["pgrep", "-P", pane], text=True).split()[0])
    os.kill(pid, 9)
    return pid


def db_rows(refs: list[str]) -> dict[str, dict]:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    out = {}
    for i in range(0, len(refs), 500):
        part = refs[i:i + 500]
        q = f"SELECT receipt_ref,priority,status,attempts,worker_id,claimed_at,claim_seq,finished_at,error FROM gw_receipts WHERE receipt_ref IN ({','.join('?'*len(part))})"
        for r in con.execute(q, part):
            out[r["receipt_ref"]] = dict(r)
    con.close()
    return out


def stored_by(refs) -> dict[str, list[str]]:
    """receipt_ref -> workers whose log says '-> done (stored)' (the DB clears worker_id when done)."""
    want, out = set(refs), {}
    for w in ("worker0", "worker1"):
        for line in (S / "logs" / f"{w}.log").read_text(errors="ignore").splitlines():
            if "(stored)" in line and "receipt=" in line:
                ref = line.split("receipt=", 1)[1].split()[0]
                if ref in want:
                    out.setdefault(ref, []).append(w)
    return out


def images(n: int) -> list[Path]:
    files = sorted(IMG.glob("te*.jpg"))
    return [files[i % len(files)] for i in range(n)]


class Gate:
    def __init__(self, conc: int = 8):
        self.c = httpx.AsyncClient(base_url=GW, headers=H, timeout=60)
        self.sem = asyncio.Semaphore(conc)

    async def submit(self, path: Path, job: str, prio: str = "normal") -> dict:
        ref = str(uuid.uuid4())
        async with self.sem:
            t = time.time()
            r = await self.c.post("/v1/receipts", data={"receipt_ref": ref, "job_ref": job, "priority": prio},
                                  files={"file": (path.name, path.read_bytes())})
            rec = {"ref": ref, "job": job, "file": path.name, "code": r.status_code, "t_sent": t, "t_resp": time.time()}
            if r.status_code != 202:
                rec["body"] = r.json()
                rec["retry_after_header"] = r.headers.get("Retry-After")
            return rec

    async def batch(self, paths, job, prio="normal"):
        return await asyncio.gather(*(self.submit(p, job, prio) for p in paths))

    async def job(self, job: str) -> dict:
        return (await self.c.get(f"/v1/jobs/{job}")).json()

    async def queue(self) -> dict:
        return (await self.c.get("/v1/queue")).json()

    async def wait_job(self, job: str, n: int, limit_s: float = 1800, log_every: float = 10) -> dict:
        t0, last = time.time(), 0
        while True:
            j = await self.job(job)
            c = j.get("counts", {})
            fin = c.get("done", 0) + c.get("dead", 0)
            if time.time() - last > log_every:
                print(f"  job {job[:8]} {c}", flush=True); last = time.time()
            if fin >= n or time.time() - t0 > limit_s:
                return j
            await asyncio.sleep(0.5)

    async def wait_workers(self, n: int, limit_s: float = 60) -> float:
        t0 = time.time()
        while time.time() - t0 < limit_s:
            if (await self.queue()).get("workers_alive") == n:
                return time.time() - t0
            await asyncio.sleep(0.5)
        return -1

    async def delete(self, refs):
        async def one(ref):
            async with self.sem:
                await self.c.delete(f"/v1/receipts/{ref}")
        await asyncio.gather(*(one(r) for r in refs))


def finish_times(j: dict) -> dict[str, float]:
    return {r["receipt_ref"]: ts(r.get("finished_at")) for r in j["receipts"] if r.get("finished_at")}


# ---------------------------------------------------------------- tests
def prep(_):
    import pyarrow.parquet as pq
    IMG.mkdir(exist_ok=True); BAD.mkdir(exist_ok=True)
    f = next(DATA.glob("test-*.parquet"))
    t = pq.read_table(f, columns=["image"])
    for i, cell in enumerate(t.column("image").to_pylist()):
        (IMG / f"te{i:04d}.jpg").write_bytes(cell["bytes"])
    # the gateway (and the web, BR-03) refuse files over 10 MB: re-encode the few big CORD photos
    from PIL import Image
    for f in IMG.glob("te*.jpg"):
        if f.stat().st_size > 9_500_000:
            im = Image.open(f).convert("RGB"); im.save(f, "JPEG", quality=85)
            print(f"re-encoded {f.name} -> {f.stat().st_size} bytes")
    good = (IMG / "te0000.jpg").read_bytes()
    rnd = random.Random(12)
    # passes the gateway's file-type check (JPEG / PNG magic bytes) but cannot be decoded
    (BAD / "broken_truncated.jpg").write_bytes(good[:600])
    (BAD / "broken_garbage.png").write_bytes(b"\x89PNG\r\n\x1a\n" + bytes(rnd.getrandbits(8) for _ in range(4000)))
    print(f"{len(list(IMG.glob('te*.jpg')))} test images, 2 broken files")


async def capacity(a):
    g = Gate()
    if a.workers == 1:
        svc("stop", "worker1")
    else:
        svc("start", "worker1")
    print("workers_alive ->", a.workers, "after", round(await g.wait_workers(a.workers), 1), "s")
    q0 = await g.queue()
    job = str(uuid.uuid4()); paths = images(100)
    t0 = time.time()
    subs = await g.batch(paths, job)
    t_acc = max(s["t_resp"] for s in subs)
    j = await g.wait_job(job, sum(s["code"] == 202 for s in subs))
    fin = finish_times(j); rows = db_rows([s["ref"] for s in subs])
    lat = [fin[s["ref"]] - s["t_resp"] for s in subs if s["ref"] in fin]
    t_end = max(fin.values())
    res = {
        "test": f"capacity_{a.workers}w{a.tag}", "workers": a.workers, "queue_before": q0, "n": 100,
        "accepted_202": sum(s["code"] == 202 for s in subs), "accept_all_s": round(t_acc - t0, 2),
        "makespan_s": round(t_end - t0, 2), "max_latency_s": round(max(lat), 2),
        "rate_per_min": round(100 / (t_end - t0) * 60, 1),
        "counts": j["counts"], "by_worker": {},
        "slo_s": 1800,
        "curve": sorted(round(f - t0, 2) for f in fin.values()),
    }
    for ws in stored_by([s["ref"] for s in subs]).values():
        for w in ws:
            res["by_worker"][w] = res["by_worker"].get(w, 0) + 1
    res["pass"] = res["counts"].get("done", 0) + res["counts"].get("dead", 0) == 100 and res["max_latency_s"] <= 1800
    await g.delete([s["ref"] for s in subs])
    if a.workers == 1:
        svc("start", "worker1"); await g.wait_workers(2)
    print(json.dumps({k: v for k, v in res.items() if k != "curve"}, ensure_ascii=False))
    save(res["test"], res)


async def urgent(_):
    g = Gate()
    await g.wait_workers(2)
    A, B = str(uuid.uuid4()), str(uuid.uuid4())
    t0 = time.time()
    subA = await g.batch(images(100), A)
    subB = await g.batch(images(110)[100:], B)          # 10 more receipts, queued behind A as normal
    j = await g.job(A); print("normal job before urgent:", j["counts"])
    t_u = time.time()
    r = await g.c.post(f"/v1/jobs/{B}/urgent"); urg = r.json(); t_u_resp = time.time()
    print("G5 urgent ->", r.status_code, urg)
    jb = await g.wait_job(B, sum(s["code"] == 202 for s in subB), log_every=2)
    ja = await g.wait_job(A, sum(s["code"] == 202 for s in subA))
    finB, finA = finish_times(jb), finish_times(ja)
    refsA, refsB = [s["ref"] for s in subA], [s["ref"] for s in subB]
    rows = db_rows(refsA + refsB)
    # claim order (system-wide claim_seq) while urgent receipts existed
    seq = sorted(rows.values(), key=lambda r: r["claim_seq"] or 0)
    order = [("U" if r["receipt_ref"] in refsB else "N", r["claim_seq"], round((r["claimed_at"] or 0) - t0, 2),
              r["worker_id"]) for r in seq]
    first_u = min(i for i, o in enumerate(order) if o[0] == "U")
    last_u = max(i for i, o in enumerate(order) if o[0] == "U")
    window = order[first_u:last_u + 1]
    run, max_run = 0, 0
    for o in window:
        run = run + 1 if o[0] == "U" else 0
        max_run = max(max_run, run)
    res = {
        "test": "urgent", "g5_response": urg, "g5_code": r.status_code,
        "normal_done_before_urgent": j["counts"],
        "urgent_all_done_s": round(max(finB.values()) - t_u, 2), "slo_s": 300,
        "urgent_finish_s": sorted(round(f - t_u, 2) for f in finB.values()),
        "normal_all_done_s": round(max(finA.values()) - t0, 2),
        "claim_window": "".join(o[0] for o in window),
        "max_urgent_in_a_row": max_run, "normals_in_window": sum(o[0] == "N" for o in window),
        "order": order, "t_urgent_rel": round(t_u - t0, 2),
        "curve_normal": sorted(round(f - t0, 2) for f in finA.values()),
        "curve_urgent": sorted(round(f - t0, 2) for f in finB.values()),
        "countsA": ja["counts"], "countsB": jb["counts"],
    }
    res["pass_time"] = res["urgent_all_done_s"] <= 300
    res["pass_order"] = max_run <= 4 and res["normals_in_window"] >= 1
    await g.delete(refsA + refsB)
    print(json.dumps({k: v for k, v in res.items() if k not in ("order", "curve_normal", "curve_urgent")}, ensure_ascii=False))
    save("urgent", res)


async def queuefull(a):
    g = Gate(conc=16)
    await g.wait_workers(2)
    q0 = await g.queue()
    subs, rejected, peak = [], [], 0
    t0 = time.time(); jobs = []
    for k in range(a.max_batches):                      # batches of 100 like the web sends
        job = str(uuid.uuid4()); jobs.append(job)
        part = await g.batch(images(100), job)
        subs += part
        rej = [s for s in part if s["code"] == 429]
        rejected += rej
        q = await g.queue(); peak = max(peak, q["normal"]["pending"])
        print(f"  batch {k+1}: 202={sum(s['code']==202 for s in part)} 429={len(rej)} pending={q['normal']['pending']}", flush=True)
        if len(rejected) >= 10:
            break
    # urgent work is not counted in the 400 cap (BR-11): one urgent receipt while full
    uj = str(uuid.uuid4())
    u = await g.submit(images(1)[0], uj, "urgent")
    qfull = await g.queue()
    first = rejected[0] if rejected else None
    accepted = [s for s in subs if s["code"] == 202] + ([u] if u["code"] == 202 else [])
    # rejected receipts must not exist on the gateway (not stored, no status)
    rej_lookup = [(await g.c.get(f"/v1/receipts/{s['ref']}")).status_code for s in rejected[:20]]
    # wait until every accepted receipt has a result
    t_w = time.time()
    while True:
        rows = db_rows([s["ref"] for s in accepted])
        fin = sum(r["status"] in ("done", "dead") for r in rows.values())
        if fin >= len(accepted) or time.time() - t_w > 1500:
            break
        print(f"  finished {fin}/{len(accepted)}", flush=True); await asyncio.sleep(10)
    rows = db_rows([s["ref"] for s in accepted])
    st = {}
    for r in rows.values():
        st[r["status"]] = st.get(r["status"], 0) + 1
    body = first["body"] if first else {}
    res = {
        "test": "queuefull", "queue_before": q0, "submitted": len(subs), "accepted_202": len(accepted) - (u["code"] == 202),
        "rejected_429": len(rejected), "other_codes": sorted({s["code"] for s in subs} - {202, 429}),
        "first_429_body": body, "first_429_retry_after_header": first and first["retry_after_header"],
        "first_429_at_submission": subs.index(first) + 1 if first else None,
        "peak_pending": peak, "queue_when_full": qfull,
        "urgent_while_full_code": u["code"],
        "rejected_lookup_codes": sorted(set(rej_lookup)),
        "accepted_rows_found": len(rows), "accepted_final_status": st,
        "lost": len(accepted) - len(rows), "drain_s": round(time.time() - t_w, 1),
        "total_s": round(time.time() - t0, 1),
    }
    ok_body = (body.get("error") == "queue_full" and body.get("queue") == "normal" and body.get("limit") == 400
               and str(body.get("retry_after_seconds")) == str(first["retry_after_header"]))
    res["pass"] = bool(rejected) and ok_body and res["lost"] == 0 and st.get("done", 0) + st.get("dead", 0) == len(accepted) \
        and res["rejected_lookup_codes"] == [404] and u["code"] == 202
    await g.delete([s["ref"] for s in accepted])
    print(json.dumps(res, ensure_ascii=False))
    save("queuefull", res)


async def crash(_):
    g = Gate()
    await g.wait_workers(2)
    job = str(uuid.uuid4())
    t0 = time.time()
    subs = await g.batch(images(40), job)
    while True:
        c = (await g.job(job))["counts"]
        if c.get("done", 0) >= 10:
            break
        await asyncio.sleep(0.3)
    held = [r for r in db_rows([s["ref"] for s in subs]).values() if r["status"] == "processing" and r["worker_id"] == "worker0"]
    t_k = time.time(); pid = kill9("worker0")
    print(f"kill -9 worker0 (pid {pid}) at done={c.get('done')} holding={len(held)}", flush=True)
    detect = await g.wait_workers(1, 60)
    j = await g.wait_job(job, sum(s["code"] == 202 for s in subs))
    rows = db_rows([s["ref"] for s in subs])
    after = [r["receipt_ref"] for r in rows.values() if (r["finished_at"] or 0) > t_k]
    sb = stored_by([s["ref"] for s in subs])
    by_after = {}
    for ref in after:
        for w in sb.get(ref, ["?"]):
            by_after[w] = by_after.get(w, 0) + 1
    dup = sum(1 for ws in sb.values() if len(ws) > 1)       # a receipt stored twice = duplicate result
    held_ref = held[0]["receipt_ref"] if held else None
    res = {
        "test": "crash", "n": 40, "killed": "worker0", "done_at_kill": c.get("done", 0),
        "kill_at_s": round(t_k - t0, 2), "workers_alive_1_after_s": round(detect, 1),
        "counts": j["counts"], "finished_after_kill_by_worker": by_after,
        "held_by_killed": held_ref and {"attempts": rows[held_ref]["attempts"], "status": rows[held_ref]["status"],
                                        "worker": rows[held_ref]["worker_id"]},
        "lost": 40 - len(rows), "duplicate_results": dup,
        "all_done_s": round(max(r["finished_at"] for r in rows.values()) - t0, 2),
    }
    res["pass"] = j["counts"].get("done", 0) == 40 and res["lost"] == 0 and dup == 0 and set(by_after) == {"worker1"} \
        and 0 <= detect <= 15 + 5
    svc("start", "worker0")
    res["restart_workers_alive_2_after_s"] = round(await g.wait_workers(2, 120), 1)
    await g.delete([s["ref"] for s in subs])
    print(json.dumps(res, ensure_ascii=False))
    save("crash", res)


async def dlq(_):
    g = Gate()
    await g.wait_workers(2)
    q0 = await g.queue()
    dlq0 = rabbit_dlq()
    job = str(uuid.uuid4())
    bad = sorted(BAD.iterdir())
    paths = [bad[0]] + images(10) + [bad[1]] + images(20)[10:]
    t0 = time.time()
    subs = await g.batch(paths, job)
    j = await g.wait_job(job, sum(s["code"] == 202 for s in subs), log_every=3)
    rows = db_rows([s["ref"] for s in subs])
    badrefs = [s["ref"] for s in subs if s["file"].startswith("broken")]
    good = [s for s in subs if not s["file"].startswith("broken")]
    fin = finish_times(j)
    q1 = await g.queue(); dlq1 = rabbit_dlq()
    res = {
        "test": "dlq", "submitted": len(subs), "codes": sorted({s["code"] for s in subs}),
        "broken": [{"file": s["file"], "status": rows[s["ref"]]["status"], "attempts": rows[s["ref"]]["attempts"],
                    "error": rows[s["ref"]]["error"], "finished_s": round(fin[s["ref"]] - t0, 2)} for s in subs if s["ref"] in badrefs],
        "good_done": sum(rows[s["ref"]]["status"] == "done" for s in good), "good_n": len(good),
        "good_all_done_s": round(max(fin[s["ref"]] for s in good) - t0, 2),
        "dead_letter_count_before_after": [q0["dead_letter"]["count"], q1["dead_letter"]["count"]],
        "rabbit_receipts_dlq_before_after": [dlq0, dlq1],
    }
    res["pass"] = all(b["status"] == "dead" and b["attempts"] == 3 for b in res["broken"]) and \
        res["good_done"] == len(good) and (dlq1 - dlq0 == 2 if None not in (dlq0, dlq1) else True)
    await g.delete([s["ref"] for s in subs])
    print(json.dumps(res, ensure_ascii=False))
    save("dlq", res)


def rabbit_dlq():
    try:
        out = subprocess.check_output(["runuser", "-u", "rabbitmq", "--", "env", "HOME=/var/lib/rabbitmq",
                                       "rabbitmqctl", "-q", "list_queues", "name", "messages"], text=True)
        for line in out.splitlines():
            p = line.split()
            if p and p[0] == "receipts.dlq":
                return int(p[1])
    except Exception:
        return None


async def state(_):
    g = Gate()
    print(json.dumps(await g.queue()))
    out = subprocess.check_output(["runuser", "-u", "rabbitmq", "--", "env", "HOME=/var/lib/rabbitmq",
                                   "rabbitmqctl", "-q", "list_queues", "name", "messages"], text=True)
    print(out.strip())


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("prep")
    c = sp.add_parser("capacity"); c.add_argument("--workers", type=int, choices=(1, 2), required=True); c.add_argument("--tag", default="")
    sp.add_parser("urgent")
    qf = sp.add_parser("queuefull"); qf.add_argument("--max-batches", type=int, default=8)
    sp.add_parser("crash"); sp.add_parser("dlq"); sp.add_parser("state")
    a = p.parse_args()
    if a.cmd == "prep":
        return prep(a)
    asyncio.run(globals()[a.cmd](a))


if __name__ == "__main__":
    main()
