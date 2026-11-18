"""ทดสอบ shop-bot ผ่าน NGINX :8000 — 2 คำถามพร้อมกัน (streaming) + เรียกแบบไม่มี key"""
import json, time, threading, urllib.request, urllib.error
URL = "http://127.0.0.1:8000/v1/chat/completions"
KEY = open("/workspace/lab6/secrets/api_key").read().strip()   # ไม่พิมพ์ค่า
SYSTEM = "คุณคือพนักงานร้านขายของใช้ในบ้าน 'บ้านสบาย' ตอบลูกค้าเป็นภาษาไทยอย่างสุภาพ กระชับ และเป็นประโยชน์"
QUESTIONS = [
    "ไม้ถูพื้นแบบสเปรย์กับแบบถังปั่น ต่างกันอย่างไร บ้านมีแมวควรเลือกแบบไหนคะ",
    "ซื้อกล่องเก็บของพลาสติกไป 3 ใบ ฝาปิดไม่สนิท 1 ใบ เปลี่ยนหรือคืนได้ไหมครับ ต้องทำอย่างไร",
]
results = [None] * len(QUESTIONS)

def ask(i, q):
    body = json.dumps({"model": "shop-bot", "stream": True, "max_tokens": 150,
                       "stream_options": {"include_usage": True},
                       "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}]}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    t0 = time.time(); ttft = None; text = ""; usage = {}
    with urllib.request.urlopen(req, timeout=300) as r:
        backend = r.headers.get("X-vLLM-Backend"); lb = r.headers.get("X-LB-Method")
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data:") or line == "data: [DONE]":
                continue
            d = json.loads(line[5:])
            if d.get("usage"): usage = d["usage"]
            for c in d.get("choices", []):
                piece = c.get("delta", {}).get("content") or ""
                if piece and ttft is None: ttft = time.time() - t0
                text += piece
    total = time.time() - t0
    results[i] = dict(question=q, answer=text, backend=backend, lb=lb, ttft_s=round(ttft, 3), total_s=round(total, 3),
                      prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"),
                      tok_per_s=round(usage.get("completion_tokens", 0) / (total - ttft), 1))

t0 = time.time()
th = [threading.Thread(target=ask, args=(i, q)) for i, q in enumerate(QUESTIONS)]
[t.start() for t in th]; [t.join() for t in th]
wall = round(time.time() - t0, 3)

# เรียกแบบไม่มี key และ key ผิด
neg = {}
for name, hdr in [("no_key", {}), ("wrong_key", {"Authorization": "Bearer sk-wrong"})]:
    req = urllib.request.Request(URL, json.dumps({"model": "shop-bot", "messages": [{"role": "user", "content": "hi"}]}).encode(),
                                 {"Content-Type": "application/json", **hdr})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: neg[name] = {"status": r.status}
    except urllib.error.HTTPError as e:
        neg[name] = {"status": e.code, "body": e.read().decode()[:100]}

out = {"concurrent_wall_s": wall, "answers": results, "rejected": neg}
json.dump(out, open("/workspace/lab6/logs/test_result.json", "w"), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
