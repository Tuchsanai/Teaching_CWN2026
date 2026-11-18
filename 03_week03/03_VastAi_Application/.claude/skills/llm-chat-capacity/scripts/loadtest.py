#!/usr/bin/env python3
"""loadtest.py — ตัวยิงโหลดแชทบอท shop-bot (closed-loop: ผู้ใช้ N คน ถาม → รอ stream จนจบ → ถามใหม่ทันที)

  python loadtest.py --label single_1gpu --levels 1,2,3,4,6,8
  python loadtest.py --label batch_1gpu  --levels 1,8,16,32,64 --duration 30 --warmup 5
  python loadtest.py --label lb_round_robin --levels 448 --duration 120 --warmup 30 --long-frac 0.2 --long-max-tokens 600
      (--long-frac: สัดส่วนคำถามที่ขอคำตอบละเอียดยาว ได้ถึง --long-max-tokens token · ที่เหลือใช้ --max-tokens)

ยิงผ่าน NGINX (:8000) พร้อม API key จากไฟล์ (ไม่พิมพ์ค่า key)
ต่อระดับ N: วิ่ง --duration วินาที นับเฉพาะคำถามที่ "เริ่ม" หลัง --warmup วินาทีแรก
คำถามที่นับแล้วแต่ยังไม่จบตอนหมดเวลา ระบบยังคงโหลด N คนไว้จนคำถามเหล่านั้นจบ
หยุดเองเมื่อไม่ผ่าน SLO 2 ระดับติดกัน · ผลชุดละ 1 ไฟล์ JSON (เขียนทับทุกระดับ เผื่อหลุดกลางทาง)
"""
import argparse, asyncio, json, multiprocessing as mp, os, random, re, subprocess, sys, time
import urllib.request

import aiohttp

SYSTEM = "คุณคือพนักงานร้านขายของใช้ในบ้าน 'บ้านสบาย' ตอบลูกค้าเป็นภาษาไทยอย่างสุภาพ กระชับ และเป็นประโยชน์"

QUESTIONS = [
    "น้ำยาล้างจานขวดใหญ่ราคาเท่าไหร่คะ",
    "ไม้ถูพื้นแบบถังปั่นมีกี่สีครับ",
    "ผ้าไมโครไฟเบอร์เช็ดกระจกได้ไหม",
    "น้ำยาถูพื้นกลิ่นไหนปลอดภัยกับแมว",
    "ถุงขยะแบบหนาขนาด 30x40 มีไหมคะ",
    "กล่องพลาสติกฝาล็อกใส่ตู้เย็นได้ไหม",
    "ไม้กวาดดอกหญ้ากับไม้กวาดพลาสติกต่างกันยังไง",
    "ซื้อของครบเท่าไหร่ส่งฟรีครับ",
    "สั่งวันนี้ได้ของกี่วันคะ",
    "สินค้าชำรุดขอเปลี่ยนได้ภายในกี่วัน",
    "ถังขยะแบบเท้าเหยียบมีขนาด 20 ลิตรไหม",
    "ชั้นวางของเหล็ก 4 ชั้นรับน้ำหนักได้กี่กิโล",
    "น้ำยาล้างห้องน้ำขจัดคราบหินปูนตัวไหนดี",
    "แปรงขัดห้องน้ำด้ามยาวมีขายไหมคะ",
    "ผงซักฟอกกับน้ำยาซักผ้าแบบไหนประหยัดกว่า",
    "น้ำยาปรับผ้านุ่มสำหรับเด็กอ่อนมีไหม",
    "ราวตากผ้าสแตนเลสพับได้ราคาเท่าไหร่",
    "ไม้แขวนเสื้อแพ็ก 10 อันมีสีอะไรบ้าง",
    "ตะกร้าผ้าแบบมีฝาปิดมีไหมครับ",
    "ฟองน้ำล้างจานควรเปลี่ยนบ่อยแค่ไหน",
    "ถุงมือยางล้างจานมีไซซ์ L ไหมคะ",
    "สเปรย์กำจัดยุงใช้ในห้องเด็กได้ไหม",
    "กับดักแมลงสาบแบบไหนได้ผลดี",
    "ที่ดักฝุ่นไฟฟ้าสถิตใช้ซ้ำได้ไหม",
    "เครื่องดูดฝุ่นมือถือแบตอยู่ได้นานแค่ไหน",
    "หลอดไฟ LED ขั้ว E27 แสงขาวมีกี่วัตต์",
    "ปลั๊กพ่วง 4 ช่องมีมาตรฐาน มอก. ไหม",
    "ผ้าม่านกันแสงยาว 2 เมตรมีสีเทาไหม",
    "พรมเช็ดเท้ากันลื่นซักเครื่องได้ไหมคะ",
    "กล่องสุญญากาศเก็บผ้าห่มมีขนาดไหนบ้าง",
    "ขวดโหลแก้วฝาไม้ใส่น้ำตาลได้ไหม",
    "หม้อหุงข้าว 1 ลิตรเหมาะกับกี่คน",
    "กระทะเคลือบล้างด้วยฝอยเหล็กได้ไหม",
    "เขียงไม้กับเขียงพลาสติกแบบไหนดีกว่า",
    "จ่ายเงินปลายทางได้ไหมครับ",
    "มีโปรโมชันซื้อ 1 แถม 1 อะไรบ้าง",
    "สะสมแต้มสมาชิกแลกอะไรได้บ้าง",
    "ขอใบกำกับภาษีเต็มรูปได้ไหมคะ",
    "สินค้าหมดจะเข้าเมื่อไหร่",
    "ร้านเปิดกี่โมงถึงกี่โมงครับ",
]

# ต่อท้ายคำถามกลุ่ม "ขอคำตอบยาว" ให้โมเดลตอบละเอียดจริง (ไม่ใช่แค่เพิ่มเพดาน max_tokens)
LONG_SUFFIX = " ช่วยอธิบายอย่างละเอียดทุกแง่มุม พร้อมตัวอย่าง ข้อดีข้อเสีย และคำแนะนำการใช้งานทีละขั้นตอน"

SLO = {"ttft_p95_max_s": 2.0, "speed_p5_min_tok_s": 15.0, "error_rate_max": 0.01}


def pct(xs, p):
    """percentile แบบ linear interpolation (p = 0..100)"""
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


# ---------------------------------------------------------------- worker process
async def _user(uid, session, cfg, t_warm, t_end, t_hard, inflight, recs, seed):
    rng = random.Random(seed)
    while True:
        now = time.time()
        if now >= t_hard:
            break
        if now >= t_end and inflight.value == 0:      # ไม่มีคำถามที่นับค้างอยู่แล้ว → เลิก
            break
        qi = rng.randrange(len(QUESTIONS))
        is_long = rng.random() < cfg["long_frac"]
        counted = t_warm <= now < t_end
        if counted:
            with inflight.get_lock():
                inflight.value += 1
        body = {"model": cfg["model"], "stream": True,
                "max_tokens": cfg["long_max_tokens"] if is_long else cfg["max_tokens"],
                "stream_options": {"include_usage": True},
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": QUESTIONS[qi] + (LONG_SUFFIX if is_long else "")}]}
        r = {"user": uid, "q": qi, "long": is_long, "counted": counted, "start": now, "ttft": None, "end": None,
             "tokens": 0, "prompt_tokens": None, "backend": None, "status": None, "error": None, "answer": ""}
        try:
            async with session.post(cfg["url"], json=body, headers=cfg["headers"]) as resp:
                r["status"] = resp.status
                r["backend"] = resp.headers.get("X-vLLM-Backend")
                if resp.status != 200:
                    r["error"] = f"HTTP {resp.status}"
                    await resp.read()
                else:
                    async for raw in resp.content:
                        line = raw.decode("utf-8", "ignore").strip()
                        if not line.startswith("data:") or line == "data: [DONE]":
                            continue
                        d = json.loads(line[5:])
                        if d.get("usage"):
                            r["tokens"] = d["usage"].get("completion_tokens", 0)
                            r["prompt_tokens"] = d["usage"].get("prompt_tokens")
                        for c in d.get("choices", []):
                            piece = (c.get("delta") or {}).get("content") or ""
                            if piece:
                                if r["ttft"] is None:
                                    r["ttft"] = time.time() - now
                                r["answer"] += piece
                    if r["tokens"] == 0:
                        r["error"] = "empty answer"
        except Exception as e:  # timeout / connection error
            r["error"] = f"{type(e).__name__}: {e}"[:200]
        r["end"] = time.time()
        if counted:
            with inflight.get_lock():
                inflight.value -= 1
        recs.append(r)


def worker(n_users, uid0, cfg, t_warm, t_end, t_hard, inflight, q, seed):
    async def main():
        recs = []
        conn = aiohttp.TCPConnector(limit=0)
        to = aiohttp.ClientTimeout(total=cfg["timeout"])
        async with aiohttp.ClientSession(connector=conn, timeout=to) as s:
            cpu0 = None
            async def cpu_mark():
                nonlocal cpu0
                await asyncio.sleep(max(0, t_warm - time.time()))
                cpu0 = time.process_time()
            marker = asyncio.create_task(cpu_mark())
            await asyncio.gather(*[_user(uid0 + i, s, cfg, t_warm, t_end, t_hard, inflight, recs, seed + uid0 + i)
                                   for i in range(n_users)])
            await marker
        cpu_s = time.process_time() - (cpu0 or 0)
        return recs, cpu_s
    recs, cpu_s = asyncio.run(main())
    q.put({"pid": os.getpid(), "records": recs, "cpu_s": cpu_s, "end": time.time()})


# ---------------------------------------------------------------- monitoring (main process)
METRIC_RE = re.compile(r'^(vllm:num_requests_(?:running|waiting))\{[^}]*\}\s+([0-9.eE+-]+)', re.M)


def scrape_vllm(port):
    try:
        txt = urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics", timeout=2).read().decode()
    except Exception:
        return None
    out = {"running": 0.0, "waiting": 0.0}
    for name, val in METRIC_RE.findall(txt):
        out[name.rsplit("_", 1)[1]] += float(val)
    return out


def gpu_stats():
    """{gpu: (util %, SM clock MHz, temp C)}"""
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=index,utilization.gpu,clocks.sm,temperature.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
        return {int(a): (float(b), float(c), float(d)) for a, b, c, d in (l.split(",") for l in o.strip().splitlines())}
    except Exception:
        return {}


def run_level(n, cfg, args):
    procs = max(1, min(n, args.procs))
    t0 = time.time() + 1.0                       # เผื่อเวลา fork ให้ทุก process เริ่มพร้อมกัน
    t_warm, t_end = t0 + args.warmup, t0 + args.duration
    t_hard = t_end + args.tail_max
    inflight = mp.Value("i", 0)
    q = mp.Queue()
    ps, uid = [], 0
    for i in range(procs):
        k = n // procs + (1 if i < n % procs else 0)
        p = mp.Process(target=worker, args=(k, uid, cfg, t_warm, t_end, t_hard, inflight, q, args.seed * 1000 + n * 100))
        p.start(); ps.append(p); uid += k
    main_cpu0 = None
    gpu_samples, vllm_samples = {}, {port: [] for port in cfg["backend_ports"]}
    gpu_clock, gpu_temp = {}, {}
    timeseries = []          # ทุก ~1 วินาทีในช่วงวัด: เวลา (วินาทีหลังเริ่มนับ) + คำถามที่แต่ละ vLLM กำลังทำ/รอคิว
    results, done = [], 0
    while done < procs:
        now = time.time()
        if t_warm <= now < t_end:
            if main_cpu0 is None:
                main_cpu0 = time.process_time()
            for g, (u, clk, tmp) in gpu_stats().items():
                gpu_samples.setdefault(g, []).append(u)
                gpu_clock.setdefault(g, []).append(clk)
                gpu_temp.setdefault(g, []).append(tmp)
            point = {"t": round(now - t_warm, 2)}
            for port in cfg["backend_ports"]:
                m = scrape_vllm(port)
                if m:
                    vllm_samples[port].append(m)
                    point[f"port{port}"] = {"running": m["running"], "waiting": m["waiting"]}
            timeseries.append(point)
        try:
            results.append(q.get(timeout=args.sample_every)); done += 1
        except Exception:
            pass
    main_cpu = time.process_time() - (main_cpu0 or time.process_time())
    for p in ps:
        p.join()

    window = args.duration - args.warmup
    recs = [r for res in results for r in res["records"]]
    cnt = [r for r in recs if r["counted"]]
    ok = [r for r in cnt if not r["error"]]
    errs = [r for r in cnt if r["error"]]
    ttfts = [r["ttft"] for r in ok if r["ttft"] is not None]
    speeds = [r["tokens"] / (r["end"] - r["start"] - r["ttft"]) for r in ok
              if r["ttft"] is not None and r["tokens"] > 1 and r["end"] - r["start"] - r["ttft"] > 0]
    # token/วินาทีรวม = token ของคำถามที่จบภายในช่วงวัด ÷ ความยาวช่วงวัด
    tok_window = sum(r["tokens"] for r in recs if not r["error"] and t_warm <= r["end"] < t_end)
    per_backend = {}
    for r in cnt:
        per_backend[r["backend"] or "none"] = per_backend.get(r["backend"] or "none", 0) + 1
    err_rate = len(errs) / len(cnt) if cnt else 1.0
    lvl = {
        "users": n,
        "load_processes": procs,
        "requests_counted": len(cnt),
        "requests_ok": len(ok),
        "errors": len(errs),
        "error_rate": round(err_rate, 4),
        "error_examples": sorted({r["error"] for r in errs})[:5],
        "ttft_s": {"p50": pct(ttfts, 50), "p95": pct(ttfts, 95), "p99": pct(ttfts, 99)},
        "speed_tok_s_per_user": {"p50": pct(speeds, 50), "p5": pct(speeds, 5)},
        "total_tok_s": tok_window / window,
        "latency_s_p50": pct([r["end"] - r["start"] for r in ok], 50),
        "completion_tokens_mean": (sum(r["tokens"] for r in ok) / len(ok)) if ok else None,
        "gpu_util_pct": {str(g): round(sum(v) / len(v), 1) for g, v in sorted(gpu_samples.items()) if v},
        "vllm_queue": {
            f"port{port}": {
                "running_avg": round(sum(s["running"] for s in v) / len(v), 2) if v else None,
                "running_max": max((s["running"] for s in v), default=None),
                "waiting_avg": round(sum(s["waiting"] for s in v) / len(v), 2) if v else None,
                "waiting_max": max((s["waiting"] for s in v), default=None),
            } for port, v in vllm_samples.items()},
        "requests_per_backend": per_backend,
        "loadgen_cpu_pct": {
            "per_process": [round(res["cpu_s"] / window * 100, 1) for res in results],
            "main_monitor": round(main_cpu / window * 100, 1),
            "max_process": round(max(res["cpu_s"] / window * 100 for res in results), 1),
        },
    }
    lvl["gpu_sm_clock_mhz_avg"] = {str(g): round(sum(v) / len(v)) for g, v in sorted(gpu_clock.items()) if v}
    lvl["gpu_temp_c_max"] = {str(g): max(v) for g, v in sorted(gpu_temp.items()) if v}
    lvl["vllm_timeseries"] = timeseries
    # แยกผลคำถามสั้น / ยาว (เมื่อใช้ --long-frac)
    by_kind = {}
    for kind, flag in (("short", False), ("long", True)):
        ks = [r for r in ok if r.get("long", False) == flag]
        if not ks:
            continue
        kt = [r["ttft"] for r in ks if r["ttft"] is not None]
        kspd = [r["tokens"] / (r["end"] - r["start"] - r["ttft"]) for r in ks
                if r["ttft"] is not None and r["tokens"] > 1 and r["end"] - r["start"] - r["ttft"] > 0]
        per_b = {}
        for r in ks:
            per_b[r["backend"] or "none"] = per_b.get(r["backend"] or "none", 0) + 1
        by_kind[kind] = {"requests_ok": len(ks), "completion_tokens_mean": sum(r["tokens"] for r in ks) / len(ks),
                         "ttft_s": {"p50": pct(kt, 50), "p95": pct(kt, 95)},
                         "speed_tok_s_per_user": {"p50": pct(kspd, 50), "p5": pct(kspd, 5)},
                         "requests_per_backend": per_b}
    lvl["by_kind"] = by_kind
    lvl["running_avg_total"] =round(sum(v["running_avg"] or 0 for v in lvl["vllm_queue"].values()), 2)
    lvl["waiting_avg_total"] = round(sum(v["waiting_avg"] or 0 for v in lvl["vllm_queue"].values()), 2)
    lvl["waiting_max_total"] = sum(v["waiting_max"] or 0 for v in lvl["vllm_queue"].values())
    t95, s5 = lvl["ttft_s"]["p95"], lvl["speed_tok_s_per_user"]["p5"]
    lvl["slo"] = {
        "ttft_p95_ok": t95 is not None and t95 <= SLO["ttft_p95_max_s"],
        "speed_p5_ok": s5 is not None and s5 >= SLO["speed_p5_min_tok_s"],
        "error_ok": err_rate < SLO["error_rate_max"],
    }
    lvl["slo"]["pass"] = all(lvl["slo"].values())
    # ตัวอย่างคำตอบจริง (ข้อละ 1 คำตอบ) ไว้ทำภาพชุดคำขอ
    samples = {}
    for r in sorted(ok, key=lambda r: r["start"]):
        samples.setdefault(r["q"], {"q": r["q"], "question": QUESTIONS[r["q"]], "answer": r["answer"],
                                    "prompt_tokens": r["prompt_tokens"], "completion_tokens": r["tokens"],
                                    "ttft_s": round(r["ttft"], 3), "total_s": round(r["end"] - r["start"], 3),
                                    "backend": r["backend"], "users": n})
    return lvl, samples


def fmt(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def print_table(run):
    print(f"\n== {run['label']}  (mode={run['server'].get('mode')}, gpus={run['server'].get('gpus')}) ==")
    hdr = f"{'N':>3} {'req':>4} {'TTFTp50':>8} {'TTFTp95':>8} {'TTFTp99':>8} {'spd p50':>8} {'spd p5':>7} " \
          f"{'tok/s':>7} {'err%':>5} {'GPU%':>5} {'run':>5} {'wait':>5} {'cpu%max':>7}  SLO"
    print(hdr); print("-" * len(hdr))
    for l in run["levels"]:
        gpu = max(l["gpu_util_pct"].values()) if l["gpu_util_pct"] else None
        print(f"{l['users']:>3} {l['requests_counted']:>4} {fmt(l['ttft_s']['p50']):>8} {fmt(l['ttft_s']['p95']):>8} "
              f"{fmt(l['ttft_s']['p99']):>8} {fmt(l['speed_tok_s_per_user']['p50'],1):>8} "
              f"{fmt(l['speed_tok_s_per_user']['p5'],1):>7} {fmt(l['total_tok_s'],1):>7} "
              f"{l['error_rate']*100:>5.1f} {fmt(gpu,0):>5} {fmt(l['running_avg_total'],1):>5} "
              f"{fmt(l['waiting_avg_total'],1):>5} {l['loadgen_cpu_pct']['max_process']:>7}  "
              f"{'ผ่าน' if l['slo']['pass'] else 'ไม่ผ่าน'}")
    print(f"\nรองรับผู้ใช้พร้อมกันได้ (N สูงสุดที่ผ่าน SLO): {run['max_users_pass_slo']}")
    print(f"ไฟล์ผล: {run['_path']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="ชื่อชุดทดสอบ เช่น single_1gpu")
    ap.add_argument("--levels", default="1,2,3,4,6,8")
    ap.add_argument("--duration", type=float, default=30)
    ap.add_argument("--warmup", type=float, default=5)
    ap.add_argument("--tail-max", type=float, default=120, help="เวลาสูงสุดที่รอคำถามที่นับแล้วให้จบหลังหมดเวลา")
    ap.add_argument("--url", default="http://127.0.0.1:8000/v1/chat/completions")
    ap.add_argument("--key-file", default="/workspace/lab6/secrets/api_key")
    ap.add_argument("--model", default="shop-bot")
    ap.add_argument("--max-tokens", type=int, default=150)
    ap.add_argument("--long-frac", type=float, default=0.0, help="สัดส่วนคำถามที่ขอคำตอบละเอียดยาว (0–1)")
    ap.add_argument("--long-max-tokens", type=int, default=600, help="เพดาน token ของคำถามกลุ่มคำตอบยาว")
    ap.add_argument("--procs", type=int, default=min(8, os.cpu_count() or 4), help="จำนวน process สูงสุดของตัวยิง")
    ap.add_argument("--backend-ports", default="", help="พอร์ต vLLM ที่อ่าน /metrics (ว่าง = อ่านจาก state ของ cluster.sh)")
    ap.add_argument("--state", default="/workspace/lab6/run/state.env")
    ap.add_argument("--fail-stop", type=int, default=2, help="หยุดเมื่อไม่ผ่าน SLO กี่ระดับติดกัน")
    ap.add_argument("--sample-every", type=float, default=1.0)
    ap.add_argument("--timeout", type=float, default=300)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out-dir", default="/workspace/lab6/results")
    args = ap.parse_args()

    server = {}
    if os.path.exists(args.state):
        for line in open(args.state):
            if "=" in line:
                k, v = line.strip().split("=", 1); server[k.lower()] = v
    gpus = int(server.get("gpus", 1))
    ports = [int(p) for p in args.backend_ports.split(",") if p] or [8001 + i for i in range(gpus)]
    key = open(args.key_file).read().strip()            # ไม่พิมพ์ค่า key
    cfg = {"url": args.url, "model": args.model, "max_tokens": args.max_tokens, "timeout": args.timeout,
           "long_frac": args.long_frac, "long_max_tokens": args.long_max_tokens,
           "headers": {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
           "backend_ports": ports}

    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, f"loadtest_{args.label}.json")
    run = {"label": args.label, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "server": server,
           "config": {"levels": args.levels, "duration_s": args.duration, "warmup_s": args.warmup,
                      "max_tokens": args.max_tokens, "long_frac": args.long_frac,
                      "long_max_tokens": args.long_max_tokens, "long_suffix": LONG_SUFFIX if args.long_frac else "",
                      "url": args.url, "model": args.model,
                      "load_processes_max": args.procs, "questions": len(QUESTIONS), "cpu_count": os.cpu_count()},
           "slo": SLO, "questions": QUESTIONS, "levels": [], "samples": {}, "max_users_pass_slo": 0,
           "stopped_reason": "all levels done"}
    fails = 0
    for n in [int(x) for x in args.levels.split(",")]:
        print(f"[loadtest] N={n} ...", flush=True)
        lvl, samples = run_level(n, cfg, args)
        run["levels"].append(lvl)
        for qi, s in samples.items():
            run["samples"].setdefault(str(qi), s)
        if lvl["slo"]["pass"]:
            fails = 0
            run["max_users_pass_slo"] = max(run["max_users_pass_slo"], n)
        else:
            fails += 1
        print(f"[loadtest] N={n} req={lvl['requests_counted']} TTFTp95={fmt(lvl['ttft_s']['p95'])}s "
              f"spd_p5={fmt(lvl['speed_tok_s_per_user']['p5'],1)} tok/s={fmt(lvl['total_tok_s'],1)} "
              f"err={lvl['error_rate']*100:.1f}% SLO={'PASS' if lvl['slo']['pass'] else 'FAIL'} "
              f"running_avg/max={ {p: (v['running_avg'], v['running_max']) for p, v in lvl['vllm_queue'].items()} } "
              f"waiting_avg={lvl['waiting_avg_total']}", flush=True)
        run["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        json.dump(run, open(path, "w"), ensure_ascii=False, indent=2)
        if fails >= args.fail_stop:
            run["stopped_reason"] = f"ไม่ผ่าน SLO {fails} ระดับติดกัน (หยุดที่ N={n})"
            break
    run["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(run, open(path, "w"), ensure_ascii=False, indent=2)
    run["_path"] = path
    print_table(run)
    print(f"สถานะ: {run['stopped_reason']}")


if __name__ == "__main__":
    mp.set_start_method("fork")
    main()
