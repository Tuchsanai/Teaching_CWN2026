#!/usr/bin/env python3
"""precheck2.py — ตรวจ GPU ทั้ง 2 ใบก่อนวัด: อุณหภูมิ/clock ตอนว่างและตอนทำงาน + ความเร็วตอบผู้ใช้ 1 คนของ vLLM แต่ละตัว
ยิงตรงเข้า vLLM แต่ละพอร์ต (ไม่ผ่าน NGINX) เพื่อแยกวัดทีละใบ · บันทึก JSON ไม่มีค่า key"""
import json, statistics, subprocess, sys, threading, time, urllib.request
sys.path.insert(0, "/workspace/lab6")
from loadtest import QUESTIONS, SYSTEM

OUT = sys.argv[1] if len(sys.argv) > 1 else "/workspace/lab6/results/precheck_batch_2gpu.json"
BACKENDS = [("vllm-1", 0, 8001), ("vllm-2", 1, 8002)]
QS = QUESTIONS[:5]

def gpu(i):
    o = subprocess.check_output(["nvidia-smi", "-i", str(i), "--query-gpu=name,temperature.gpu,clocks.sm,clocks.max.sm,utilization.gpu,power.draw",
                                 "--format=csv,noheader,nounits"]).decode().strip()
    n, t, c, m, u, p = [x.strip() for x in o.split(",")]
    return {"name": n, "temp": float(t), "clock_mhz": float(c), "clock_max_mhz": float(m), "util": float(u), "power_w": float(p)}

def ask(port, q):
    body = json.dumps({"model": "shop-bot", "stream": True, "max_tokens": 150, "stream_options": {"include_usage": True},
                       "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}]}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions", body, {"Content-Type": "application/json"})
    t0 = time.time(); first = None; toks = 0
    with urllib.request.urlopen(req, timeout=120) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data:") or line.endswith("[DONE]"):
                continue
            d = json.loads(line[5:])
            if d.get("choices") and (d["choices"][0].get("delta") or {}).get("content") and first is None:
                first = time.time()
            if d.get("usage"):
                toks = d["usage"]["completion_tokens"]
    t1 = time.time()
    return {"q": q, "ttft_s": round(first - t0, 3), "tokens": toks, "speed_tok_s": round((toks - 1) / (t1 - first), 1),
            "total_s": round(t1 - t0, 2)}

res = {"created": time.strftime("%Y-%m-%d %H:%M:%S"), "method": "ผู้ใช้ 1 คน ถามทีละข้อ 5 ข้อ ตรงเข้า vLLM แต่ละตัว (ไม่ผ่าน NGINX) max_tokens 150",
       "gpus": []}
for name, idx, port in BACKENDS:
    idle = gpu(idx)
    ask(port, "สวัสดีครับ")                     # อุ่นเครื่อง 1 ข้อ ไม่นับ
    samples, stop = [], threading.Event()
    def mon():
        while not stop.is_set():
            samples.append(gpu(idx)); stop.wait(0.5)
    th = threading.Thread(target=mon); th.start()
    qs = [ask(port, q) for q in QS]
    stop.set(); th.join()
    busy = [s for s in samples if s["util"] > 50] or samples
    g = {"backend": name, "gpu_index": idx, "port": port, "name": idle["name"],
         "idle": {"temp_c": idle["temp"], "clock_mhz": idle["clock_mhz"], "clock_max_mhz": idle["clock_max_mhz"]},
         "load": {"temp_max_c": max(s["temp"] for s in busy), "clock_mhz_mean": round(statistics.mean(s["clock_mhz"] for s in busy)),
                  "clock_mhz_min": min(s["clock_mhz"] for s in busy), "power_w_mean": round(statistics.mean(s["power_w"] for s in busy), 1)},
         "single_user": {"speed_tok_s_median": statistics.median(x["speed_tok_s"] for x in qs),
                         "ttft_s_median": statistics.median(x["ttft_s"] for x in qs), "questions": qs}}
    res["gpus"].append(g)
    print(f"{name} GPU{idx} {g['name']}: idle {idle['temp']:.0f}C {idle['clock_mhz']:.0f}MHz | load max {g['load']['temp_max_c']:.0f}C "
          f"clock avg {g['load']['clock_mhz_mean']} (min {g['load']['clock_mhz_min']:.0f}, max {idle['clock_max_mhz']:.0f}) MHz | "
          f"1 user {g['single_user']['speed_tok_s_median']} tok/s TTFT {g['single_user']['ttft_s_median']} s", flush=True)
s = [g["single_user"]["speed_tok_s_median"] for g in res["gpus"]]
diff = abs(s[0] - s[1]) / max(s)
res["speed_diff_pct"] = round(100 * diff, 2)
res["speed_diff_over_10pct"] = diff > 0.10
print(f"ความเร็ว 2 ใบต่างกัน {100*diff:.1f}% → {'เกิน 10%' if diff > 0.10 else 'ไม่เกิน 10%'}")
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print("saved", OUT)
