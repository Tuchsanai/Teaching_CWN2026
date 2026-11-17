"""วัดผลบน Test Set ผ่าน AI server (OpenAI-compatible) ทีละใบ ด้วยพรอมต์เดียวกับตอนเทรน
ผล: <out>/pred_<tag>.jsonl (คำตอบรายใบ) และ <out>/metrics_<tag>.json"""
import argparse
import base64
import json
import os
import time
import urllib.request

from receipt_common import PROMPT, parse_output, score_one, summarize

ap = argparse.ArgumentParser()
ap.add_argument("--base-url", default="http://127.0.0.1:8000")
ap.add_argument("--model", required=True, help="ชื่อโมเดลบน server เช่น receipt-base หรือ receipt-ft")
ap.add_argument("--tag", required=True, help="ชื่อชุดผล เช่น base หรือ ft")
ap.add_argument("--data", default="data")
ap.add_argument("--split", default="test")
ap.add_argument("--out", default="out")
ap.add_argument("--limit", type=int, default=0)
args = ap.parse_args()
key = os.environ.get("RECEIPT_API_KEY", "")  # รับ key ทาง environment เท่านั้น


def ask(image_path):
    b64 = base64.b64encode(open(image_path, "rb").read()).decode()
    body = {
        "model": args.model, "temperature": 0, "max_tokens": 1024,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": PROMPT},
        ]}],
    }
    req = urllib.request.Request(
        args.base_url.rstrip("/") + "/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"]


rows = [json.loads(x) for x in open(f"{args.data}/{args.split}.jsonl", encoding="utf-8")]
rows = rows[: args.limit] if args.limit else rows
ask(f"{args.data}/{rows[0]['image']}")  # อุ่นเครื่อง 1 ครั้ง ไม่นับเวลา

scores = []
with open(f"{args.out}/pred_{args.tag}.jsonl", "w", encoding="utf-8") as f:
    for i, r in enumerate(rows, 1):
        t0 = time.time()
        raw = ask(f"{args.data}/{r['image']}")
        sec = time.time() - t0
        pred = parse_output(raw)
        s = score_one(pred, r["target"]) | {"sec": round(sec, 3)}
        scores.append(s)
        f.write(json.dumps({"id": r["id"], "image": r["image"], "raw": raw, "pred": pred,
                            "target": r["target"], "score": s}, ensure_ascii=False) + "\n")
        if i % 20 == 0:
            print(f"{args.tag}: {i}/{len(rows)}", flush=True)

m = summarize(scores) | {"model": args.model, "split": args.split}
json.dump(m, open(f"{args.out}/metrics_{args.tag}.json", "w"), indent=1)
print(json.dumps(m, ensure_ascii=False))
