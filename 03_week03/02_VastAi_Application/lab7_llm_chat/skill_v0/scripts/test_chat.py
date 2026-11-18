# ทดสอบแชทบอท shop-bot ผ่าน NGINX: 2 คำถามพร้อม key (streaming) + เรียกแบบไม่มี key
import json, time, urllib.request, urllib.error
URL = "http://127.0.0.1:8000/v1/chat/completions"
KEY = open("/workspace/lab7/secrets/api_key").read().strip()
SYS = "คุณคือพนักงานร้านขายของใช้ในบ้าน ตอบลูกค้าเป็นภาษาไทย สุภาพ กระชับ"
QS = ["น้ำยาล้างจานแบบไหนอ่อนโยนต่อมือ เหมาะกับคนผิวแพ้ง่ายคะ",
      "ไม้ถูพื้นแบบสเปรย์กับแบบถังปั่น ต่างกันอย่างไร ควรเลือกแบบไหนดีครับ"]
def ask(q, key=KEY):
    body = json.dumps({"model": "shop-bot", "stream": True, "max_tokens": 150,
        "stream_options": {"include_usage": True},
        "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": q}]}).encode()
    h = {"Content-Type": "application/json"}
    if key: h["Authorization"] = "Bearer " + key
    req = urllib.request.Request(URL, body, h)
    t0 = time.time(); ttft = None; text = ""; usage = None
    with urllib.request.urlopen(req, timeout=120) as r:
        backend = r.headers.get("X-Served-By")
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data: ") or line == "data: [DONE]": continue
            d = json.loads(line[6:])
            if d.get("usage"): usage = d["usage"]
            for c in d.get("choices", []):
                t = c["delta"].get("content") or ""
                if t and ttft is None: ttft = time.time() - t0
                text += t
    tot = time.time() - t0
    return dict(q=q, a=text, backend=backend, ttft=round(ttft, 3), total=round(tot, 2),
                prompt_tokens=usage["prompt_tokens"], completion_tokens=usage["completion_tokens"],
                tok_per_s=round(usage["completion_tokens"] / (tot - ttft), 1))
res = [ask(q) for q in QS]
try:
    ask(QS[0], key=None); nokey = "ไม่ถูกปฏิเสธ (ผิด)"
except urllib.error.HTTPError as e:
    nokey = f"HTTP {e.code} {e.read().decode().strip()}"
print(json.dumps({"answers": res, "no_key": nokey}, ensure_ascii=False, indent=1))
