#!/usr/bin/env python3
"""tools/pull.sh ส่งไฟล์นี้เข้าไปรันใน container ทาง stdin: แพ็กผลการวัดเป็น tar ส่งออกทาง stdout

Training Set  : grade.json metrics.json และโค้ดที่ Agent เขียน (sandbox/solve.py test_solve.py)
Validation Set: เฉพาะคะแนนและตัวเลขต้นทุน (ไม่มีผลรายข้อ คำสั่ง และโค้ด) เว้นแต่ใส่ --unseal
"""
import io, json, os, sys, tarfile

SUITE = "/workspace/sklab/suite"
unseal = "--unseal" in sys.argv
tar = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")


def add(name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


if os.path.isfile(os.path.join(SUITE, "results.json")):
    add("results.json", open(os.path.join(SUITE, "results.json"), "rb").read())
runs = os.path.join(SUITE, "runs")
for label in sorted(os.listdir(runs)):
    for trial in sorted(os.listdir(os.path.join(runs, label))):
        d = os.path.join(runs, label, trial)
        try:
            m = json.load(open(os.path.join(d, "metrics.json"), encoding="utf-8"))
            g = json.load(open(os.path.join(d, "grade.json"), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        sealed = m.get("split") != "train" and not unseal
        if sealed:
            g = {"score": g["score"], "checks": "sealed (Validation Set)"}
            m = {k: v for k, v in m.items() if k not in ("commands", "result")}
        base = "runs/%s/%s/" % (label, trial)
        add(base + "grade.json", json.dumps(g, ensure_ascii=False, indent=1).encode("utf-8"))
        add(base + "metrics.json", json.dumps(m, ensure_ascii=False, indent=1).encode("utf-8"))
        for f in ("solve.py", "test_solve.py"):
            p = os.path.join(d, "sandbox", f)
            if not sealed and os.path.isfile(p):
                add(base + "sandbox/" + f, open(p, "rb").read())
tar.close()
