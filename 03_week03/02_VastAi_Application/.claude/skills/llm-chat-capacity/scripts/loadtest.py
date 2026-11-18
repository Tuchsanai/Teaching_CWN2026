#!/usr/bin/env python3
"""loadtest.py — ตัวยิงโหลดแชทบอท shop-bot (ผ่าน NGINX พร้อม API key)

จำลองผู้ใช้ N คน: แต่ละคนสุ่มคำถาม 1 ข้อจาก 40 ข้อ → รอคำตอบแบบ streaming จนจบ → ถามข้อใหม่ทันที
ไล่ N ตาม --levels ระดับละ --duration วินาที ไม่นับ --warmup วินาทีแรก
หยุดเองเมื่อไม่ผ่าน SLO 2 ระดับติดกัน · ระดับที่ผลก้ำกึ่ง (ห่างเส้นเกณฑ์ ≤ 5%) วัดซ้ำอีก 2 ครั้งแล้วใช้ค่ากลาง

SLO: TTFT p95 ≤ 2 s · 95% ของคำถามได้ ≥ 15 token/s (คือ p5 ≥ 15) · error < 1%

ใช้:
  python loadtest.py --levels 1,2,3,4,6,8 --label single_1gpu --out results/
  python loadtest.py --levels 448 --long-frac 0.2 --long-max-tokens 600 --label mix_round_robin --out results/
                                                          # 20% ขอคำตอบละเอียดยาว ≤ 600 token ที่เหลือ ≤ 150
  python loadtest.py --samples 8 --out results/          # ถามทีละข้อ 8 ข้อ เก็บคำตอบจริง (ทำภาพชุดคำขอ)
ต้องมี aiohttp (มีอยู่แล้วใน venv ของ vLLM)
"""
import argparse, asyncio, json, math, multiprocessing as mp, os, random, re, statistics, subprocess
import sys, threading, time, urllib.request

# ---------------- ชุดคำถาม: ลูกค้าร้านขายของใช้ในบ้าน 40 ข้อ ----------------
QUESTIONS = [
    "น้ำยาล้างจานแบบไหนอ่อนโยนต่อมือคะ",
    "ผงซักฟอกกับน้ำยาซักผ้า อันไหนดีกว่ากันครับ",
    "ไม้ถูพื้นแบบสเปรย์กับแบบถังปั่น ต่างกันยังไงคะ",
    "มีถุงขยะแบบย่อยสลายได้ไหมครับ",
    "น้ำยาปรับผ้านุ่มกลิ่นไหนหอมติดทนที่สุดคะ",
    "ทิชชู่ม้วนกับทิชชู่กล่อง แบบไหนคุ้มกว่าครับ",
    "ฟองน้ำล้างจานควรเปลี่ยนบ่อยแค่ไหนคะ",
    "น้ำยาล้างห้องน้ำตัวไหนขจัดคราบหินปูนได้ดีครับ",
    "มีกล่องเก็บอาหารที่เข้าไมโครเวฟได้ไหมคะ",
    "ไม้กวาดดอกหญ้ากับไม้กวาดพลาสติก ใช้ต่างกันยังไงครับ",
    "สเปรย์กันยุงแบบไหนปลอดภัยกับเด็กคะ",
    "ถ่านไฟฉาย AA แบบชาร์จได้ คุ้มไหมครับ",
    "น้ำยาเช็ดกระจกใช้กับกระจกรถได้ไหมคะ",
    "ผ้าไมโครไฟเบอร์ซักเครื่องได้ไหมครับ",
    "หลอดไฟ LED 9 วัตต์ สว่างเท่าหลอดไส้กี่วัตต์คะ",
    "ไม้แขวนเสื้อแบบไหนไม่ทำให้ไหล่เสื้อย้วยครับ",
    "น้ำยาถูพื้นสำหรับบ้านที่เลี้ยงแมวมีไหมคะ",
    "ถุงมือยางล้างจานมีไซซ์อะไรบ้างครับ",
    "กระดาษเช็ดมือแบบแผ่นกับแบบม้วน อันไหนประหยัดกว่าคะ",
    "มีที่ดักฝุ่นสำหรับเครื่องปรับอากาศไหมครับ",
    "ผงล้างเครื่องซักผ้าควรใช้บ่อยแค่ไหนคะ",
    "น้ำยาขจัดคราบไขมันในครัว ตัวไหนแรงสุดครับ",
    "ตะกร้าผ้าแบบพับได้ รับน้ำหนักได้เท่าไหร่คะ",
    "ปลั๊กพ่วงแบบไหนมีระบบกันไฟกระชากครับ",
    "สบู่เหลวล้างมือขวดใหญ่มีแบบเติมไหมคะ",
    "แปรงขัดห้องน้ำแบบด้ามยาวมีขายไหมครับ",
    "ก้อนดับกลิ่นตู้เย็นใช้ได้นานกี่เดือนคะ",
    "น้ำยาล้างจานแบบเข้มข้นต้องผสมน้ำไหมครับ",
    "ถุงซิปล็อกเก็บอาหารแช่แข็งได้ไหมคะ",
    "มีเทปกาวสองหน้าแบบติดผนังไม่ทิ้งคราบไหมครับ",
    "กล่องพลาสติกใส่ของแบบมีล้อ ขนาดไหนขายดีคะ",
    "สเปรย์ปรับอากาศกับเจลหอม อันไหนอยู่ได้นานกว่าครับ",
    "ผ้าขี้ริ้วแบบไหนซับน้ำได้ดีคะ",
    "น้ำยาฆ่าเชื้อใช้เช็ดของเล่นเด็กได้ไหมครับ",
    "ไม้ถูพื้นรีฟิลอะไหล่ใช้กับยี่ห้ออื่นได้ไหมคะ",
    "มีที่คว่ำจานแบบสแตนเลสไม่เป็นสนิมไหมครับ",
    "ผงฟูใช้ทำความสะอาดบ้านได้ไหมคะ",
    "แผ่นกันลื่นในห้องน้ำ ทำความสะอาดยังไงครับ",
    "ถังขยะแบบเหยียบ มีขนาดกี่ลิตรบ้างคะ",
    "ซื้อครบ 500 บาทส่งฟรีไหมครับ",
]
SYSTEM = "คุณคือพนักงานร้านขายของใช้ในบ้าน ตอบลูกค้าเป็นภาษาไทย สุภาพ กระชับ ไม่เกิน 3 ประโยค"
# คำถามแบบ "ขอคำตอบละเอียด" (เปิดด้วย --long-frac): ใช้ system prompt อีกแบบ + ต่อท้ายคำถามให้อธิบายยาว
SYSTEM_LONG = "คุณคือพนักงานร้านขายของใช้ในบ้าน ตอบลูกค้าเป็นภาษาไทย สุภาพ ละเอียด ครบถ้วน"
LONG_SUFFIX = " ขอคำอธิบายละเอียดเป็นข้อๆ อย่างน้อย 10 ข้อ พร้อมเหตุผล ข้อดีข้อเสีย และวิธีใช้ที่ถูกต้องของแต่ละข้อ"

SLO_TTFT_P95 = 2.0      # วินาที (ต้อง ≤)
SLO_SPEED_P5 = 15.0     # token/วินาที (ต้อง ≥)
SLO_ERR = 0.01          # สัดส่วน (ต้อง <)
BORDER = 0.05           # ห่างเส้นเกณฑ์ไม่เกิน 5% = ก้ำกึ่ง


def pct(xs, p):
    """percentile แบบ linear interpolation (p = 0..100)"""
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    f, c = math.floor(k), math.ceil(k)
    return xs[f] if f == c else xs[f] + (xs[c] - xs[f]) * (k - f)


def build_body(q, max_tokens, long=False):
    return {"model": "shop-bot", "stream": True, "max_tokens": max_tokens,
            "stream_options": {"include_usage": True},
            "messages": [{"role": "system", "content": SYSTEM_LONG if long else SYSTEM},
                         {"role": "user", "content": q + LONG_SUFFIX if long else q}]}


def pick_request(rng, mix):
    """mix = (max_tokens ปกติ, สัดส่วนคำถามยาว, max_tokens คำถามยาว) → (คำถาม, max_tokens, ยาวไหม)"""
    short_max, long_frac, long_max = mix
    q = rng.choice(QUESTIONS)
    if long_frac > 0 and rng.random() < long_frac:
        return q, long_max, True
    return q, short_max, False


# ---------------- ผู้ใช้จำลอง (ทำงานใน process ลูก) ----------------
async def one_request(session, url, headers, q, max_tokens, keep_text=False, long=False):
    import aiohttp
    rec = {"q": q, "long": long, "max_tokens": max_tokens, "t0": time.time(), "ttft": None, "t_end": None,
           "tokens": 0, "chunks": [], "backend": None, "err": None}
    text = []
    try:
        async with session.post(url, json=build_body(q, max_tokens, long), headers=headers) as r:
            rec["backend"] = r.headers.get("X-Served-By")
            if r.status != 200:
                rec["err"] = f"HTTP {r.status}"
                await r.read()
                rec["t_end"] = time.time()
                return rec
            buf = b""
            async for raw in r.content:
                buf += raw
                if not buf.endswith(b"\n"):
                    continue
                line, buf = buf.decode("utf-8", "replace").strip(), b""
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                d = json.loads(line[6:])
                if d.get("usage"):
                    rec["tokens"] = d["usage"]["completion_tokens"]
                    rec["prompt_tokens"] = d["usage"]["prompt_tokens"]
                for c in d.get("choices", []):
                    t = (c.get("delta") or {}).get("content") or ""
                    if t:
                        now = time.time()
                        if rec["ttft"] is None:
                            rec["ttft"] = now - rec["t0"]
                        rec["chunks"].append(round(now, 4))
                        if keep_text:
                            text.append(t)
        rec["t_end"] = time.time()
        if rec["ttft"] is None:
            rec["err"] = "no tokens"
    except asyncio.CancelledError:
        rec["err"] = "cancelled"
        rec["t_end"] = time.time()
    except Exception as e:  # timeout, connection reset, ...
        rec["err"] = type(e).__name__
        rec["t_end"] = time.time()
    if keep_text:
        rec["text"] = "".join(text)
    return rec


async def user_loop(uid, session, url, headers, start_at, stop_at, mix, seed, out):
    rng = random.Random(seed * 1000 + uid)
    await asyncio.sleep(max(0, start_at - time.time()))
    while time.time() < stop_at:
        q, mt, long = pick_request(rng, mix)
        rec = await one_request(session, url, headers, q, mt, long=long)
        rec["user"] = uid
        out.append(rec)
        if rec["err"]:
            await asyncio.sleep(0.2)   # กันวนยิงรัวเมื่อ server ตอบ error ทันที


async def worker_main(uids, url, key, start_at, stop_at, grace, mix, seed):
    import aiohttp
    headers = {"Authorization": "Bearer " + key}
    out = []
    conn = aiohttp.TCPConnector(limit=0)
    timeout = aiohttp.ClientTimeout(total=600, sock_read=300)
    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as s:
        tasks = [asyncio.create_task(user_loop(u, s, url, headers, start_at, stop_at, mix, seed, out))
                 for u in uids]
        done, pending = await asyncio.wait(tasks, timeout=max(1, stop_at - time.time() + grace))
        for t in pending:
            t.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    return out


def worker_proc(uids, url, key, start_at, stop_at, warm_at, grace, mix, seed, q):
    c0, w0 = None, None
    async def run():
        return await worker_main(uids, url, key, start_at, stop_at, grace, mix, seed)
    # วัด CPU ของ process นี้เฉพาะช่วงวัดผล (หลัง warm-up ถึงจบระดับ)
    def cpu_mark():
        nonlocal c0, w0
        time.sleep(max(0, warm_at - time.time()))
        c0, w0 = time.process_time(), time.time()
    th = threading.Thread(target=cpu_mark, daemon=True); th.start()
    recs = asyncio.run(run())
    th.join(timeout=1)
    cpu_pct = None
    if c0 is not None:
        cpu_pct = 100 * (time.process_time() - c0) / max(1e-6, time.time() - w0)
    q.put({"recs": recs, "cpu_pct": cpu_pct, "pid": os.getpid(), "users": len(uids)})


# ---------------- ตัวเก็บค่าระบบ (thread ใน process หลัก) ----------------
def parse_prom(text, name):
    tot, seen = 0.0, False
    for line in text.splitlines():
        if line.startswith(name + "{") or line.startswith(name + " "):
            try:
                tot += float(line.rsplit(" ", 1)[1]); seen = True
            except ValueError:
                pass
    return tot if seen else None


class Sampler(threading.Thread):
    """ทุก 1 วินาที: nvidia-smi (util/temp/clock ต่อใบ) + /metrics ของ vLLM แต่ละตัว (running/waiting) + CPU เครื่อง"""
    def __init__(self, vllm_ports, interval=1.0):
        super().__init__(daemon=True)
        self.ports, self.interval, self.rows, self.stop_ev = vllm_ports, interval, [], threading.Event()

    def cpu_times(self):
        with open("/proc/stat") as f:
            v = list(map(int, f.readline().split()[1:]))
        return sum(v), v[3] + v[4]

    def run(self):
        last = self.cpu_times()
        while not self.stop_ev.is_set():
            t = time.time()
            row = {"t": round(t, 3), "gpu": [], "vllm": {}}
            try:
                o = subprocess.run(["nvidia-smi", "--query-gpu=index,utilization.gpu,temperature.gpu,clocks.sm,power.draw",
                                    "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
                for line in o.strip().splitlines():
                    i, u, tp, clk, pw = [x.strip() for x in line.split(",")]
                    row["gpu"].append({"idx": int(i), "util": float(u), "temp": float(tp), "clock_mhz": float(clk),
                                       "power_w": float(pw) if re.match(r"^[\d.]+$", pw) else None})
            except Exception as e:
                row["gpu_err"] = str(e)
            for p in self.ports:
                try:
                    txt = urllib.request.urlopen(f"http://127.0.0.1:{p}/metrics", timeout=3).read().decode()
                    row["vllm"][str(p)] = {"running": parse_prom(txt, "vllm:num_requests_running"),
                                           "waiting": parse_prom(txt, "vllm:num_requests_waiting")}
                except Exception:
                    row["vllm"][str(p)] = None
            cur = self.cpu_times()
            dt, di = cur[0] - last[0], cur[1] - last[1]
            row["host_cpu_pct"] = round(100 * (1 - di / dt), 1) if dt else None
            last = cur
            self.rows.append(row)
            self.stop_ev.wait(max(0, self.interval - (time.time() - t)))


# ---------------- รัน 1 ระดับ ----------------
def run_level(n, a, key, url):
    procs = max(1, min(n, a.procs or max(1, (os.cpu_count() or 2) // 2)))
    groups = [list(range(i, n, procs)) for i in range(procs)]
    start_at = time.time() + 2.0                # ให้ทุก process พร้อมก่อน แล้วเริ่มพร้อมกัน
    warm_at, stop_at = start_at + a.warmup, start_at + a.duration
    q = mp.Queue()
    ps = [mp.Process(target=worker_proc, args=(g, url, key, start_at, stop_at, warm_at, a.grace, a.mix,
                                               a.seed + n, q)) for g in groups]
    for p in ps:                                # เปิด process ลูกก่อน แล้วค่อยเริ่มตัวเก็บค่า (กัน fork ขณะ thread ทำงาน)
        p.start()
    sampler = Sampler(a.vllm_ports)
    sampler.start()
    outs = [q.get() for _ in ps]
    for p in ps:
        p.join()
    sampler.stop_ev.set(); sampler.join()
    recs = [r for o in outs for r in o["recs"]]
    print(f"  ตัวยิง {len(ps)} process · เก็บค่าระบบ {len(sampler.rows)} ครั้ง", flush=True)
    return summarize(n, recs, outs, sampler.rows, warm_at, stop_at)


def summarize(n, recs, outs, samples, warm_at, stop_at):
    win = stop_at - warm_at
    # นับเฉพาะคำถามที่เริ่มหลัง warm-up (คำถามที่เริ่มก่อนหมดเวลาปล่อยให้ตอบจนจบ)
    meas = [r for r in recs if warm_at <= r["t0"] < stop_at and r["err"] != "cancelled"]
    ok = [r for r in meas if not r["err"]]
    errs = [r for r in meas if r["err"]]
    ttft = [r["ttft"] for r in ok]
    speed = []
    for r in ok:
        dec = r["t_end"] - (r["t0"] + r["ttft"])
        if r["tokens"] > 1 and dec > 0:
            speed.append((r["tokens"] - 1) / dec)     # token หลังตัวแรก ÷ เวลาหลังตัวแรก = ความเร็วที่ผู้ใช้เห็น
    # token/วินาทีรวม: นับ token ที่มาถึงภายในหน้าต่างวัดผล (ทุกคำถาม รวมที่เริ่มก่อน warm-up)
    all_ok = [r for r in recs if r["chunks"]]
    tok_per_chunk = (sum(r["tokens"] for r in all_ok) / max(1, sum(len(r["chunks"]) for r in all_ok))) if all_ok else 1
    in_win = sum(1 for r in recs for c in r["chunks"] if warm_at <= c < stop_at)
    agg_tps = in_win * tok_per_chunk / win
    per_backend = {}
    for r in meas:
        per_backend[r["backend"] or "none"] = per_backend.get(r["backend"] or "none", 0) + 1
    # ค่าระบบเฉพาะช่วงวัดผล
    ws = [s for s in samples if warm_at <= s["t"] <= stop_at]
    gpus = {}
    for s in ws:
        for g in s["gpu"]:
            gpus.setdefault(g["idx"], []).append(g)
    gpu_stats = {str(i): {"util_mean": round(statistics.mean(x["util"] for x in v), 1),
                          "temp_max": max(x["temp"] for x in v),
                          "clock_mhz_mean": round(statistics.mean(x["clock_mhz"] for x in v)),
                          "clock_mhz_min": min(x["clock_mhz"] for x in v)} for i, v in sorted(gpus.items())}
    vq = {}
    for s in ws:
        for p, m in s["vllm"].items():
            if m:
                vq.setdefault(p, {"running": [], "waiting": []})
                vq[p]["running"].append(m["running"] or 0); vq[p]["waiting"].append(m["waiting"] or 0)
    queue = {p: {"running_mean": round(statistics.mean(v["running"]), 2), "running_max": max(v["running"]),
                 "waiting_mean": round(statistics.mean(v["waiting"]), 2), "waiting_max": max(v["waiting"])}
             for p, v in vq.items()}
    cpu = [o["cpu_pct"] for o in outs if o["cpu_pct"] is not None]
    host_cpu = [s["host_cpu_pct"] for s in ws if s.get("host_cpu_pct") is not None]
    nreq = len(meas)
    # แยกคำถามสั้น / ยาว
    by_kind = {}
    for kind, sel in (("short", False), ("long", True)):
        ok_k = [r for r in ok if bool(r.get("long")) == sel]
        if not ok_k:
            continue
        sp_k = [(r["tokens"] - 1) / (r["t_end"] - r["t0"] - r["ttft"]) for r in ok_k
                if r["tokens"] > 1 and r["t_end"] - r["t0"] - r["ttft"] > 0]
        by_kind[kind] = {"requests": sum(1 for r in meas if bool(r.get("long")) == sel), "ok": len(ok_k),
                         "ttft_p95": round(pct([r["ttft"] for r in ok_k], 95), 3),
                         "speed_p5": round(pct(sp_k, 5), 3) if sp_k else None,
                         "completion_tokens_mean": round(statistics.mean(r["tokens"] for r in ok_k), 1),
                         "per_backend": {}}
        for r in ok_k:
            b = r["backend"] or "none"
            by_kind[kind]["per_backend"][b] = by_kind[kind]["per_backend"].get(b, 0) + 1
    # คำถามที่ GPU แต่ละใบกำลังทำ / รอคิว ทุกวินาที (ช่วงวัดผล) — ใช้วาดกราฟ
    timeseries = [{"t": round(s["t"] - warm_at, 1),
                   "running": {p: (v["running"] if v else None) for p, v in s["vllm"].items()},
                   "waiting": {p: (v["waiting"] if v else None) for p, v in s["vllm"].items()}} for s in ws]
    m = {
        "N": n, "requests": nreq, "ok": len(ok), "errors": len(errs),
        "error_rate": (len(errs) / nreq) if nreq else 1.0,
        "error_kinds": sorted({e["err"] for e in errs}),
        "ttft_p50": pct(ttft, 50), "ttft_p95": pct(ttft, 95), "ttft_p99": pct(ttft, 99),
        "speed_p50": pct(speed, 50), "speed_p5": pct(speed, 5),
        "agg_tok_s": agg_tps, "completion_tokens_mean": statistics.mean([r["tokens"] for r in ok]) if ok else None,
        "requests_per_backend": per_backend, "gpu": gpu_stats, "queue": queue,
        "waiting_mean": round(sum(v["waiting_mean"] for v in queue.values()), 2) if queue else None,
        "waiting_max": sum(v["waiting_max"] for v in queue.values()) if queue else None,
        "running_mean": round(sum(v["running_mean"] for v in queue.values()), 2) if queue else None,
        "loadgen_procs": len(outs), "loadgen_cpu_pct_per_proc_max": round(max(cpu), 1) if cpu else None,
        "loadgen_cpu_pct_total": round(sum(cpu), 1) if cpu else None,
        "host_cpu_pct_mean": round(statistics.mean(host_cpu), 1) if host_cpu else None,
        "measure_window_s": round(win, 2),
        "by_kind": by_kind, "timeseries": timeseries,
    }
    for k in ("ttft_p50", "ttft_p95", "ttft_p99", "speed_p50", "speed_p5", "agg_tok_s", "completion_tokens_mean"):
        if m[k] is not None:
            m[k] = round(m[k], 3)
    return m


def judge(m):
    c = {"ttft_p95": m["ttft_p95"] is not None and m["ttft_p95"] <= SLO_TTFT_P95,
         "speed_p5": m["speed_p5"] is not None and m["speed_p5"] >= SLO_SPEED_P5,
         "error": m["error_rate"] < SLO_ERR}
    return all(c.values()), c


def borderline(m):
    """ค่าใดค่าหนึ่งห่างเส้นเกณฑ์ไม่เกิน 5% ของเส้น"""
    why = []
    if m["ttft_p95"] is not None and abs(m["ttft_p95"] - SLO_TTFT_P95) <= BORDER * SLO_TTFT_P95:
        why.append("ttft_p95")
    if m["speed_p5"] is not None and abs(m["speed_p5"] - SLO_SPEED_P5) <= BORDER * SLO_SPEED_P5:
        why.append("speed_p5")
    if abs(m["error_rate"] - SLO_ERR) <= BORDER * SLO_ERR:
        why.append("error")
    return why


MEDIAN_KEYS = ["ttft_p50", "ttft_p95", "ttft_p99", "speed_p50", "speed_p5", "agg_tok_s", "error_rate",
               "waiting_mean", "waiting_max", "running_mean", "loadgen_cpu_pct_total", "host_cpu_pct_mean"]


def median_of(runs):
    m = dict(runs[0])
    for k in MEDIAN_KEYS:
        vals = [r[k] for r in runs if r.get(k) is not None]
        m[k] = round(statistics.median(vals), 4) if vals else None
    m["requests"] = int(statistics.median(r["requests"] for r in runs))
    m["errors"] = int(statistics.median(r["errors"] for r in runs))
    m["note"] = "ค่ากลาง (median) ของ 3 รอบ"
    return m


def fmt(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def print_table(levels):
    print()
    hdr = f"{'N':>3} {'req':>4} {'TTFT p50':>9} {'p95':>6} {'p99':>6} {'tok/s p50':>9} {'p5':>6} {'รวม tok/s':>9} " \
          f"{'err%':>5} {'GPU%':>5} {'°C':>4} {'MHz':>5} {'ทำ':>4} {'รอคิว':>6} {'CPUยิง%':>7} {'ผล':>6}"
    print(hdr); print("-" * len(hdr))
    for L in levels:
        m = L["final"]
        g = next(iter(m["gpu"].values()), {}) if m["gpu"] else {}
        print(f"{m['N']:>3} {m['requests']:>4} {fmt(m['ttft_p50']):>9} {fmt(m['ttft_p95']):>6} {fmt(m['ttft_p99']):>6} "
              f"{fmt(m['speed_p50'],1):>9} {fmt(m['speed_p5'],1):>6} {fmt(m['agg_tok_s'],1):>9} "
              f"{100*m['error_rate']:>5.1f} {fmt(g.get('util_mean'),0):>5} {fmt(g.get('temp_max'),0):>4} "
              f"{fmt(g.get('clock_mhz_mean'),0):>5} {fmt(m['running_mean'],1):>4} {fmt(m['waiting_mean'],1):>6} "
              f"{fmt(m['loadgen_cpu_pct_total'],0):>7} {('ผ่าน' if L['pass'] else 'ไม่ผ่าน'):>6}"
              + (" (ซ้ำ 3 รอบ)" if len(L["runs"]) > 1 else ""))


def run_samples(a, key, url):
    """ถามทีละข้อ (ไม่มีโหลดอื่น) เก็บคำตอบจริง token และเวลา — ใช้ทำภาพชุดคำขอ"""
    import aiohttp
    rng = random.Random(a.seed)
    qs = rng.sample(QUESTIONS, a.samples)
    async def go():
        async with aiohttp.ClientSession() as s:
            res = []
            for q in qs:
                r = await one_request(s, url, {"Authorization": "Bearer " + key}, q, a.max_tokens, keep_text=True)
                res.append({"question": q, "answer": r.get("text"), "prompt_tokens": r.get("prompt_tokens"),
                            "completion_tokens": r["tokens"], "ttft_s": round(r["ttft"], 3) if r["ttft"] else None,
                            "total_s": round(r["t_end"] - r["t0"], 2), "backend": r["backend"], "error": r["err"]})
            return res
    res = asyncio.run(go())
    example = {"method": "POST", "url": url, "headers": {"Authorization": "Bearer <API key>",
               "Content-Type": "application/json"}, "body": build_body(qs[0], a.max_tokens)}
    out = {"created": time.strftime("%Y-%m-%d %H:%M:%S"), "system_prompt": SYSTEM, "n_questions_total": len(QUESTIONS),
           "example_request": example, "samples": res}
    path = os.path.join(a.out, "dataset_samples.json")
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    for r in res:
        print(f"[{r['completion_tokens']:>3} tok {r['ttft_s']}s/{r['total_s']}s] {r['question']} → {(r['answer'] or '')[:60]}…")
    print("saved", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000/v1/chat/completions")
    ap.add_argument("--key-file", default="/workspace/lab7/secrets/api_key")
    ap.add_argument("--levels", default="1,2,3,4,6,8")
    ap.add_argument("--duration", type=float, default=30)
    ap.add_argument("--warmup", type=float, default=5)
    ap.add_argument("--grace", type=float, default=120, help="รอคำถามที่ค้างหลังหมดเวลาให้ตอบจนจบ (วินาที)")
    ap.add_argument("--max-tokens", type=int, default=150)
    ap.add_argument("--long-frac", type=float, default=0.0,
                    help="สัดส่วนคำถามที่ขอคำตอบละเอียดยาว (0 = ไม่มี เช่น 0.2 = 20%%)")
    ap.add_argument("--long-max-tokens", type=int, default=600, help="max_tokens ของคำถามยาว")
    ap.add_argument("--procs", type=int, default=0, help="จำนวน process ของตัวยิง (0 = ครึ่งหนึ่งของ CPU)")
    ap.add_argument("--vllm-ports", default="8001", help="พอร์ต vLLM ที่อ่าน /metrics (คั่นด้วย ,)")
    ap.add_argument("--state-file", default="/workspace/lab7/run/state.env")
    ap.add_argument("--label", default="run")
    ap.add_argument("--out", default="results")
    ap.add_argument("--seed", type=int, default=6)
    ap.add_argument("--no-repeat", action="store_true")
    ap.add_argument("--samples", type=int, default=0)
    a = ap.parse_args()
    a.vllm_ports = [int(p) for p in a.vllm_ports.split(",") if p]
    a.mix = (a.max_tokens, a.long_frac, a.long_max_tokens)
    os.makedirs(a.out, exist_ok=True)
    key = open(a.key_file).read().strip()          # ไม่พิมพ์ค่า key ออกจอหรือลงไฟล์
    if a.samples:
        return run_samples(a, key, a.url)

    server = {}
    if os.path.exists(a.state_file):
        for line in open(a.state_file):
            if "=" in line:
                k, v = line.strip().split("=", 1); server[k] = v
    out_path = os.path.join(a.out, f"loadtest_{a.label}.json")
    result = {"label": a.label, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "server": server,
              "config": {"levels": a.levels, "duration_s": a.duration, "warmup_s": a.warmup, "max_tokens": a.max_tokens,
                         "long_frac": a.long_frac, "long_max_tokens": a.long_max_tokens,
                         "system_prompt_long": SYSTEM_LONG if a.long_frac else None,
                         "long_suffix": LONG_SUFFIX if a.long_frac else None,
                         "n_questions": len(QUESTIONS), "system_prompt": SYSTEM, "url": a.url,
                         "slo": {"ttft_p95_max_s": SLO_TTFT_P95, "speed_p5_min_tok_s": SLO_SPEED_P5,
                                 "error_rate_max": SLO_ERR, "borderline": BORDER},
                         "cpu_count": os.cpu_count()},
              "levels": []}
    fails_in_row = 0
    for n in [int(x) for x in a.levels.split(",")]:
        print(f"\n=== N = {n} ผู้ใช้ ({a.duration:.0f} s, warm-up {a.warmup:.0f} s) ===", flush=True)
        runs = [run_level(n, a, key, a.url)]
        ok, checks = judge(runs[0])
        why = borderline(runs[0])
        print(f"  TTFT p95={fmt(runs[0]['ttft_p95'])}s  speed p5={fmt(runs[0]['speed_p5'],1)}  "
              f"err={100*runs[0]['error_rate']:.1f}%  → {'ผ่าน' if ok else 'ไม่ผ่าน'}", flush=True)
        if why and not a.no_repeat:
            print(f"  ก้ำกึ่ง ({', '.join(why)}) → วัดซ้ำอีก 2 ครั้ง", flush=True)
            for i in range(2):
                runs.append(run_level(n, a, key, a.url))
                print(f"  รอบ {i+2}: TTFT p95={fmt(runs[-1]['ttft_p95'])}s speed p5={fmt(runs[-1]['speed_p5'],1)}",
                      flush=True)
            final = median_of(runs)
        else:
            final = runs[0]
        ok, checks = judge(final)
        result["levels"].append({"N": n, "pass": ok, "checks": checks, "borderline": why, "runs": runs, "final": final})
        json.dump(result, open(out_path, "w"), ensure_ascii=False, indent=1)   # บันทึกทุกระดับ เผื่อหลุดกลางทาง
        fails_in_row = 0 if ok else fails_in_row + 1
        if fails_in_row >= 2:
            print("  ไม่ผ่าน SLO 2 ระดับติดกัน → หยุด", flush=True)
            result["stopped_early"] = True
            break
    supported = 0
    for L in result["levels"]:
        if not L["pass"]:
            break
        supported = L["N"]
    result["supported_users"] = supported
    result["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(result, open(out_path, "w"), ensure_ascii=False, indent=1)
    print_table(result["levels"])
    print(f"\nรองรับผู้ใช้พร้อมกันได้ {supported} คน (ระดับสูงสุดที่ผ่าน และทุกระดับที่ต่ำกว่าก็ผ่าน)")
    print("saved", out_path)


if __name__ == "__main__":
    main()
