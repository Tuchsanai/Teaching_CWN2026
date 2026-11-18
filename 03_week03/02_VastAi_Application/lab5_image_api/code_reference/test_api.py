"""ทดสอบ API จากนอกเครื่อง: /health · 6 รูปพร้อม key · ไม่มี key / key ผิด → 401"""
import glob, json, os, sys, time, urllib.request, uuid

BASE = sys.argv[1]
KEY = open(os.path.join(os.path.dirname(__file__), "..", ".api_key")).read().strip()
OUT = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUT, exist_ok=True)


def call(path, img=None, key=None):
    headers = {}
    body = None
    if img:
        b = uuid.uuid4().hex
        data = open(img, "rb").read()
        body = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{os.path.basename(img)}\"\r\n"
                f"Content-Type: image/jpeg\r\n\r\n").encode() + data + f"\r\n--{b}--\r\n".encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={b}"
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method="POST" if img else "GET")
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read()), (time.perf_counter() - t) * 1000
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), (time.perf_counter() - t) * 1000


report = {}
s, h, _ = call("/health")
print("GET /health ->", s, json.dumps(h, ensure_ascii=False))
report["health"] = {"status": s, "body": h}

report["detect"] = []
for img in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "samples", "*.jpg"))):
    s, r, rtt = call("/v1/detect", img, KEY)
    cls = {}
    for d in r.get("detections", []):
        cls[d["class"]] = cls.get(d["class"], 0) + 1
    print(f"{os.path.basename(img)} -> {s}  objs={r.get('count')} {cls}  timing={r.get('timing_ms')} "
          f"batch={r.get('batch_size')} rtt={rtt:.0f}ms")
    report["detect"].append({"file": os.path.basename(img), "status": s, "rtt_ms": round(rtt, 1), "response": r})

s, r, _ = call("/v1/detect", sorted(glob.glob(os.path.join(OUT, "..", "samples", "*.jpg")))[0])
print("no key ->", s, r)
report["no_key"] = {"status": s, "body": r}
s, r, _ = call("/v1/detect", sorted(glob.glob(os.path.join(OUT, "..", "samples", "*.jpg")))[0], "wrong-key")
print("wrong key ->", s, r)
report["wrong_key"] = {"status": s, "body": r}

json.dump(report, open(os.path.join(OUT, "test_single.json"), "w"), ensure_ascii=False, indent=2)
