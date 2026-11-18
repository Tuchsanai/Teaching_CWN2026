#!/usr/bin/env python
"""LAB 5 · ตัวยิงโหลดแบบ closed-loop: ผู้ใช้ N คนส่งรูปวนไป (ไม่มี think time) ผ่าน NGINX :8080
ไล่ N ตามขั้นบันได หยุดเมื่อไม่ผ่าน SLO 2 ระดับติดกัน แล้วซอยครึ่งหา N ที่พอดีเกณฑ์

    python loadgen.py --name base1            # ผล → /workspace/lab5/results/base1.json

โหมดยิงระดับเดียว (--users) เก็บผลรายวินาที และสั่งคำสั่งตามวินาทีที่กำหนดระหว่างยิงได้ (--at วินาที:คำสั่ง)

    python loadgen.py --name fo_noretry --users 11 --duration 45 \\
        --at "15:bash code/cluster.sh kill 1" --at "30:bash code/cluster.sh start 1" --track gpu1
"""
import argparse, glob, http.client, json, multiprocessing as mp, os, statistics, subprocess, threading, time, uuid

import psutil
import pynvml

BASE = "/workspace/lab5"
LEVELS = [1, 4, 16, 32, 64, 128, 256, 512, 1024]
DURATION, WARMUP, TIMEOUT = 20.0, 5.0, 10.0      # วินาทีต่อระดับ · ช่วงไม่นับ · รอเกินนี้ = error
SLO_P95_MS, SLO_ERR = 500.0, 0.01


def read_key():
    for line in open(os.path.join(BASE, ".env")):
        if line.startswith("API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("ไม่พบ API_KEY ใน .env")


def build_bodies():
    """เตรียม multipart ของรูปตัวอย่างทุกรูปไว้ล่วงหน้า ตัวยิงไม่ต้องอ่านไฟล์ระหว่างยิง"""
    out = []
    for p in sorted(glob.glob(os.path.join(BASE, "samples", "*.jpg"))):
        b = uuid.uuid4().hex
        head = (f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(p)}"\r\n'
                f"Content-Type: image/jpeg\r\n\r\n").encode()
        out.append((head + open(p, "rb").read() + f"\r\n--{b}--\r\n".encode(),
                    f"multipart/form-data; boundary={b}"))
    return out


# ---------- ผู้ใช้ 1 คน = 1 thread ถือ connection ของตัวเอง ----------
def user_loop(uid, host, port, key, bodies, t_end, rec):
    conn, i = None, uid
    while time.time() < t_end:
        body, ctype = bodies[i % len(bodies)]
        i += 1
        t0 = time.time()
        try:
            if conn is None:
                conn = http.client.HTTPConnection(host, port, timeout=TIMEOUT)
            conn.request("POST", "/v1/detect", body, {"Content-Type": ctype, "Authorization": f"Bearer {key}"})
            r = conn.getresponse()
            data = r.read()
            t1 = time.time()
            if r.status == 200:
                j = json.loads(data)
                tm = j["timing_ms"]
                rec.append((t0, t1, True, j["replica"], tm["decode"] + tm["queue"] + tm["inference"],
                            tm["inference"], j["batch_size"]))
            else:
                rec.append((t0, t1, False, f"http{r.status}", 0, 0, 0))
        except Exception as e:  # timeout / connection error → error แล้วเปิด connection ใหม่
            rec.append((t0, time.time(), False, type(e).__name__, 0, 0, 0))
            try:
                conn.close()
            except Exception:
                pass
            conn = None
    if conn:
        conn.close()


def proc_main(uids, host, port, key, t_start, t_end, q):
    bodies = build_bodies()
    rec = []
    while time.time() < t_start:                            # ทุก process เริ่มพร้อมกัน
        time.sleep(0.005)
    ths = [threading.Thread(target=user_loop, args=(u, host, port, key, bodies, t_end, rec), daemon=True)
           for u in uids]
    for t in ths:
        t.start()
    for t in ths:                                           # รอถึงเวลาจบยิง + เผื่อคำขอสุดท้าย (เดิมรอแค่ 15 วินาทีนับจากเริ่ม
        t.join(max(0.0, t_end - time.time()) + TIMEOUT + 5)  # ทำให้ process ที่มีผู้ใช้คนเดียวเลิกยิงก่อนเวลา)
    q.put(rec)


# ---------- ตัววัดฝั่งเครื่อง: GPU ทุกใบ + CPU ของ server / NGINX / ตัวยิงโหลด ----------
def server_pids():
    pids = set()
    for f in glob.glob(os.path.join(BASE, "run", "server_*.pid")):
        try:
            p = psutil.Process(int(open(f).read()))
            pids.add(p.pid)
            pids.update(c.pid for c in p.children(recursive=True))
        except Exception:
            pass
    return pids


def group_pids(loadgen_pids):
    nginx = {p.pid for p in psutil.process_iter(["name"]) if p.info["name"] == "nginx"}
    return {"server": server_pids(), "nginx": nginx, "loadgen": set(loadgen_pids)}


def cpu_seconds(pids):
    s = 0.0
    for pid in pids:
        try:
            t = psutil.Process(pid).cpu_times()
            s += t.user + t.system
        except Exception:
            pass
    return s


class Sampler(threading.Thread):
    """เก็บ GPU util ทุก 0.5 วินาที + จับ CPU time ตอนเริ่ม/จบช่วงนับผล → core ที่ใช้เฉลี่ย"""

    def __init__(self, t_from, t_to, groups):
        super().__init__(daemon=True)
        self.t_from, self.t_to, self.groups = t_from, t_to, groups
        self.h = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(pynvml.nvmlDeviceGetCount())]
        self.util = [[] for _ in self.h]
        self.mem = [0] * len(self.h)

    def run(self):
        while time.time() < self.t_from:
            time.sleep(0.05)
        self.cpu0 = {k: cpu_seconds(v) for k, v in self.groups.items()}
        c0 = time.time()
        while time.time() < self.t_to - 0.5:              # จบก่อน process ตัวยิงเริ่มปิดตัว
            for i, h in enumerate(self.h):
                self.util[i].append(pynvml.nvmlDeviceGetUtilizationRates(h).gpu)
                self.mem[i] = max(self.mem[i], pynvml.nvmlDeviceGetMemoryInfo(h).used // 2**20)
            time.sleep(0.5)
        self.cpu1 = {k: cpu_seconds(v) for k, v in self.groups.items()}
        self.span = time.time() - c0

    def result(self):
        return ({f"gpu{i}": round(statistics.mean(u), 1) if u else 0 for i, u in enumerate(self.util)},
                {f"gpu{i}": m for i, m in enumerate(self.mem)},
                {k: round((self.cpu1[k] - self.cpu0[k]) / self.span, 2) for k in self.cpu0})


def pct(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    f = int(k)
    return xs[f] if f + 1 >= len(xs) else xs[f] + (xs[f + 1] - xs[f]) * (k - f)


def run_level(n, args, key, duration=DURATION, warmup=WARMUP, measure=True):
    nproc = max(1, min(args.procs, n))
    chunks = [list(range(i, n, nproc)) for i in range(nproc)]
    q = mp.Queue()
    t_start = time.time() + 1.0
    t_end = t_start + duration
    ps = [mp.Process(target=proc_main, args=(c, args.host, args.port, key, t_start, t_end, q)) for c in chunks]
    for p in ps:
        p.start()
    smp = None
    if measure:
        smp = Sampler(t_start + warmup, t_end, group_pids([os.getpid()] + [p.pid for p in ps]))
        smp.start()
    recs = []
    for _ in ps:
        recs += q.get()
    for p in ps:
        p.join()
    if not measure:
        return None
    smp.join()
    w0, w1 = t_start + warmup, t_end
    win = [r for r in recs if w0 <= r[1] <= w1]              # นับเฉพาะคำขอที่จบในช่วงวัด
    ok = [r for r in win if r[2]]
    errs = [r for r in win if not r[2]]
    lat = [(r[1] - r[0]) * 1000 for r in ok]
    err_rate = len(errs) / len(win) if win else 1.0
    gpu, gmem, cpu = smp.result()
    per_rep, err_kinds = {}, {}
    for r in ok:
        per_rep[r[3]] = per_rep.get(r[3], 0) + 1
    for r in errs:
        err_kinds[r[3]] = err_kinds.get(r[3], 0) + 1
    res = {
        "users": n, "loadgen_processes": nproc, "window_s": round(w1 - w0, 1),
        "requests": len(win), "ok": len(ok), "errors": len(errs), "error_rate": round(err_rate, 4),
        "error_kinds": err_kinds,
        "throughput_rps": round(len(ok) / (w1 - w0), 2),
        "latency_ms": {k: (round(pct(lat, p), 1) if lat else None)
                       for k, p in (("p50", 50), ("p95", 95), ("p99", 99))},
        "latency_mean_ms": round(statistics.mean(lat), 1) if lat else None,
        "gpu_util_pct": gpu, "gpu_mem_mib": gmem, "cpu_cores": cpu,
        "per_replica": dict(sorted(per_rep.items())),
        "server_ms_mean": round(statistics.mean(r[4] for r in ok), 1) if ok else None,
        "inference_ms_mean": round(statistics.mean(r[5] for r in ok), 1) if ok else None,
        "batch_mean": round(statistics.mean(r[6] for r in ok), 2) if ok else None,
    }
    res["pass"] = bool(lat) and res["latency_ms"]["p95"] <= SLO_P95_MS and err_rate < SLO_ERR
    return res


def show(r, tag=""):
    L = r["latency_ms"]
    f = lambda v: "-" if v is None else f"{v:.0f}"
    gpu = " ".join(f"{k}={v:.0f}%" for k, v in r["gpu_util_pct"].items())
    cpu = " ".join(f"{k}={v:.2f}" for k, v in r["cpu_cores"].items())
    print(f"{tag}N={r['users']:<5} {'PASS' if r['pass'] else 'FAIL'}  thr={r['throughput_rps']:.1f} req/s  "
          f"p50={f(L['p50'])} p95={f(L['p95'])} p99={f(L['p99'])} ms  err={r['error_rate'] * 100:.2f}%  "
          f"| {gpu} | CPU cores {cpu} | replica {r['per_replica']} | server={r['server_ms_mean']} ms "
          f"(infer {r['inference_ms_mean']}) batch={r['batch_mean']}", flush=True)


# ---------- โหมดยิงระดับเดียว: ผลรายวินาที + คำสั่งตามเวลา ----------
def run_events(events, t_start, log):
    """สั่งคำสั่งแต่ละตัวเมื่อถึงวินาทีที่กำหนด (นับจากเริ่มยิง) เก็บเวลาเริ่ม/จบ และผลลัพธ์"""
    def one(sec, cmd):
        while time.time() < t_start + sec:
            time.sleep(0.005)
        t0 = time.time()
        p = subprocess.run(cmd, shell=True, cwd=BASE, capture_output=True, text=True)
        log.append({"at_s": sec, "cmd": cmd, "started_s": round(t0 - t_start, 3), "started_epoch": round(t0, 3),
                    "finished_s": round(time.time() - t_start, 3), "rc": p.returncode,
                    "output": (p.stdout + p.stderr).strip()[-500:]})
        print(f"  [t={t0 - t_start:5.2f}s] {cmd} → rc={p.returncode} {(p.stdout + p.stderr).strip()[-200:]}", flush=True)
    ths = [threading.Thread(target=one, args=e, daemon=True) for e in events]
    for t in ths:
        t.start()
    return ths


class GpuPerSecond(threading.Thread):
    """GPU util ทุก 0.25 วินาที เฉลี่ยเป็นรายวินาที"""

    def __init__(self, t_start, t_end):
        super().__init__(daemon=True)
        self.t_start, self.t_end = t_start, t_end
        self.h = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(pynvml.nvmlDeviceGetCount())]
        self.samples = []                                   # (วินาที, [util ต่อใบ])

    def run(self):
        while time.time() < self.t_start:
            time.sleep(0.01)
        while time.time() < self.t_end:
            s = int(time.time() - self.t_start)
            self.samples.append((s, [pynvml.nvmlDeviceGetUtilizationRates(h).gpu for h in self.h]))
            time.sleep(0.25)

    def per_second(self, sec):
        rows = [u for s, u in self.samples if s == sec]
        return {f"gpu{i}": round(statistics.mean(r[i] for r in rows), 1) for i in range(len(self.h))} if rows else {}


def run_fixed(args, key):
    n, dur = args.users, args.duration
    events = []
    for a in args.at:
        sec, cmd = a.split(":", 1)
        events.append((float(sec), cmd))
    events.sort()
    nproc = max(1, min(args.procs, n))
    chunks = [list(range(i, n, nproc)) for i in range(nproc)]
    q = mp.Queue()
    t_start = time.time() + 1.0
    t_end = t_start + dur
    ps = [mp.Process(target=proc_main, args=(c, args.host, args.port, key, t_start, t_end, q)) for c in chunks]
    for p in ps:
        p.start()
    gpu = GpuPerSecond(t_start, t_end)
    gpu.start()
    ev_log = []
    ev_threads = run_events(events, t_start, ev_log)

    def ticker():                                           # แสดงความคืบหน้าทุก 5 วินาที
        while time.time() < t_end:
            time.sleep(5)
            print(f"  ยิงไปแล้ว {min(dur, time.time() - t_start):.0f}/{dur:.0f} วินาที", flush=True)
    threading.Thread(target=ticker, daemon=True).start()

    recs = []
    for _ in ps:
        recs += q.get()
    for p in ps:
        p.join()
    for t in ev_threads:                                    # คำสั่งแบบรอ (เช่น start --wait) อาจจบหลังหยุดยิง
        t.join(600)
    gpu.join()

    grp = lambda rep: rep.split("-")[0]                     # gpu1-p3 → gpu1
    recs = [(r[0] - t_start, r[1] - t_start) + tuple(r[2:]) for r in recs]   # เวลาเทียบจุดเริ่มยิง
    per_sec = []
    for s in range(int(dur)):
        win = [r for r in recs if s <= r[1] < s + 1]        # นับตามวินาทีที่คำขอจบ
        ok = [r for r in win if r[2]]
        lat = [(r[1] - r[0]) * 1000 for r in ok]
        by_rep, kinds = {}, {}
        for r in ok:
            by_rep[grp(r[3])] = by_rep.get(grp(r[3]), 0) + 1
        for r in win:
            if not r[2]:
                kinds[r[3]] = kinds.get(r[3], 0) + 1
        per_sec.append({"t": s, "ok": len(ok), "ok_by_replica": dict(sorted(by_rep.items())),
                        "errors": len(win) - len(ok), "error_kinds": kinds,
                        "p95_ms": round(pct(lat, 95), 1) if lat else None,
                        "p50_ms": round(pct(lat, 50), 1) if lat else None,
                        "gpu_util_pct": gpu.per_second(s)})

    def phase(a, b):
        rows = [r for r in recs if a <= r[1] < b]
        ok = [r for r in rows if r[2]]
        lat = [(r[1] - r[0]) * 1000 for r in ok]
        return {"from_s": round(a, 2), "to_s": round(b, 2), "requests": len(rows), "ok": len(ok),
                "errors": len(rows) - len(ok), "throughput_rps": round(len(ok) / (b - a), 2) if b > a else None,
                "p95_ms": round(pct(lat, 95), 1) if lat else None}

    cuts = [0.0] + [e[0] for e in events] + [dur]
    names = ["before"] + [f"after_event{i + 1}" for i in range(len(events))]
    if len(events) == 2:
        names = ["before_failure", "during_failure", "after_restart"]
    phases = {names[i]: phase(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)}

    track = {}
    if args.track:
        oks = sorted(r[1] for r in recs if r[2] and grp(r[3]) == args.track)
        for i, ev in enumerate(events):
            before = [t for t in oks if t < ev[0]]
            after = [t for t in oks if t >= ev[0]]
            track[f"event{i + 1}"] = {"cmd": ev[1], "at_s": ev[0],
                                      "last_ok_before_s": round(before[-1], 3) if before else None,
                                      "first_ok_after_s": round(after[0], 3) if after else None}
        if len(events) == 2 and track["event2"]["first_ok_after_s"] is not None:
            rj = track["event2"]["first_ok_after_s"]
            track["rejoin_after_restart_s"] = round(rj - events[1][0], 2)
            phases["after_rejoin"] = phase(rj, dur)
        if len(events) == 2:                                # คำสั่งเปิดคืนแบบ --wait จบเมื่อ replica พร้อม
            e2 = [e for e in ev_log if e["at_s"] == events[1][0]][0]
            track["restart_cmd_took_s"] = round(e2["finished_s"] - e2["started_s"], 2)

    worst = max((r for r in per_sec if r["p95_ms"] is not None), key=lambda r: r["p95_ms"], default=None)
    errs_all = [r for r in recs if not r[2]]
    kinds_all = {}
    for r in errs_all:
        kinds_all[r[3]] = kinds_all.get(r[3], 0) + 1
    return {"users": n, "duration_s": dur, "loadgen_processes": nproc, "events": ev_log,
            "requests_total": len(recs), "ok_total": len(recs) - len(errs_all), "errors_total": len(errs_all),
            "error_kinds_total": kinds_all, "phases": phases, "track": track,
            "worst_second_p95": {"t": worst["t"], "p95_ms": worst["p95_ms"]} if worst else None,
            "per_second": per_sec}


def main_fixed(args, key):
    out = os.path.join(BASE, "results", f"{args.name}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    conf = os.path.join(BASE, "run", "cluster.conf")
    print(f"ยิงระดับเดียว: ผู้ใช้ {args.users} คน นาน {args.duration:.0f} วินาที · คำสั่งตามเวลา {args.at}", flush=True)
    doc = {"name": args.name, "mode": "fixed", "started": time.strftime("%F %T"),
           "cluster_conf": open(conf).read() if os.path.exists(conf) else ""}
    doc.update(run_fixed(args, key))
    doc["finished"] = time.strftime("%F %T")
    json.dump(doc, open(out, "w"), ensure_ascii=False, indent=2)
    print(" t  ok  (" + " ".join(sorted({k for r in doc["per_second"] for k in r["ok_by_replica"]})) + ")  err  p95ms")
    for r in doc["per_second"]:
        print(f"{r['t']:>2} {r['ok']:>4}  {r['ok_by_replica']}  {r['errors']:>4}  {r['p95_ms']}", flush=True)
    print(f"รวม {doc['requests_total']} คำขอ · error {doc['errors_total']} {doc['error_kinds_total']}")
    for k, v in doc["phases"].items():
        print(f"  {k:<15} {v['throughput_rps']} req/s  error {v['errors']}  p95 {v['p95_ms']} ms")
    print(f"p95 แย่สุด {doc['worst_second_p95']} · track {doc['track']} · ผล {out}")
    print("DONE", flush=True)


def capacity(results):
    """N สูงสุดที่ผ่าน โดยทุกระดับที่ต่ำกว่า (ที่วัดแล้ว) ก็ผ่าน"""
    cap = 0
    for r in sorted(results, key=lambda r: r["users"]):
        if not r["pass"]:
            break
        cap = r["users"]
    return cap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="ชื่อผล → results/<name>.json")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--procs", type=int, default=8, help="จำนวน process ของตัวยิงโหลด")
    ap.add_argument("--users", type=int, help="ยิงระดับเดียวด้วยผู้ใช้ N คน (ไม่ไล่ระดับ) เก็บผลรายวินาที")
    ap.add_argument("--duration", type=float, default=45.0, help="วินาทีที่ยิง (โหมด --users)")
    ap.add_argument("--at", action="append", default=[], metavar="วินาที:คำสั่ง",
                    help='สั่งคำสั่ง shell เมื่อถึงวินาทีนั้น (ใส่ซ้ำได้) เช่น --at "15:bash code/cluster.sh kill 1"')
    ap.add_argument("--track", help="ชื่อ replica ที่จะดูเวลาหยุด/กลับมารับงาน เช่น gpu1")
    args = ap.parse_args()
    key = read_key()
    pynvml.nvmlInit()
    if args.users:
        return main_fixed(args, key)
    out_dir = os.path.join(BASE, "results")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{args.name}.json")
    conf = os.path.join(BASE, "run", "cluster.conf")
    doc = {"name": args.name, "started": time.strftime("%F %T"),
           "cluster_conf": open(conf).read() if os.path.exists(conf) else "",
           "slo": {"p95_ms": SLO_P95_MS, "error_rate_lt": SLO_ERR, "timeout_s": TIMEOUT},
           "level_s": DURATION, "warmup_s": WARMUP, "levels": [], "bisect": []}

    def save():
        doc["capacity_users"] = capacity(doc["levels"] + doc["bisect"])
        json.dump(doc, open(out, "w"), ensure_ascii=False, indent=2)

    print("อุ่นระบบ 5 วินาที (N=4 ไม่นับผล)...", flush=True)
    run_level(4, args, key, duration=5, warmup=0, measure=False)

    fails, last_pass, first_fail = 0, 0, None
    for n in LEVELS:
        r = run_level(n, args, key)
        doc["levels"].append(r)
        show(r)
        save()
        if r["pass"]:
            fails, first_fail, last_pass = 0, None, n
        else:
            fails += 1
            first_fail = first_fail or n
            if fails >= 2:
                break

    if fails >= 2:                                          # ซอยครึ่งระหว่าง ผ่าน (lo) กับ ไม่ผ่าน (hi)
        lo, hi = last_pass, first_fail
        for i in range(3):
            mid = (lo + hi) // 2
            if mid <= lo or mid >= hi:
                break
            r = run_level(mid, args, key)
            doc["bisect"].append(r)
            show(r, f"ซอยรอบ {i + 1}: ")
            save()
            lo, hi = (mid, hi) if r["pass"] else (lo, mid)
    doc["finished"] = time.strftime("%F %T")
    save()
    print(f"ความจุ: รองรับผู้ใช้พร้อมกันได้ {doc['capacity_users']} คน ที่ p95 ≤ {SLO_P95_MS:.0f} ms "
          f"และ error < {SLO_ERR * 100:.0f}% · ผล {out}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
