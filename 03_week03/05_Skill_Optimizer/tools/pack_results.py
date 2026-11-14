#!/usr/bin/env python3
"""tools/pull.sh ส่งไฟล์นี้เข้าไปรันใน container ทาง stdin: แพ็กโฟลเดอร์ runs/ เป็น tar ส่งออกทาง stdout

ทุกรุ่น       : skills/ และไฟล์ผลของรุ่น (gate.txt failures.txt null.txt lint.json)
Training Set  : grade.json metrics.json และโค้ดที่ Agent เขียน (sandbox/solve.py test_solve.py)
Validation Set: เฉพาะคะแนนและตัวเลขต้นทุน (ไม่มีผลรายข้อ คำสั่ง และโค้ด) เว้นแต่ใส่ --unseal
"""
import io, json, os, sys, tarfile

RUNS = "/workspace/sklab/runs"
unseal = "--unseal" in sys.argv
tar = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")
SKIP = ("__pycache__", ".ipynb_checkpoints")


def add(name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def add_tree(top, base):
    for root, dirs, files in os.walk(top):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            p = os.path.join(root, f)
            add(base + os.path.relpath(p, top).replace(os.sep, "/"), open(p, "rb").read())


for name in sorted(os.listdir(RUNS)):
    d = os.path.join(RUNS, name)
    if os.path.isfile(d):                                   # ISSUES.md report.md results.json
        add(name, open(d, "rb").read())
        continue
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if os.path.isfile(p):                               # gate.txt failures.txt null.txt lint.json
            add("%s/%s" % (name, f), open(p, "rb").read())
    if os.path.isdir(os.path.join(d, "skills")):
        add_tree(os.path.join(d, "skills"), name + "/skills/")
    trials = os.path.join(d, "trials")
    for trial in sorted(os.listdir(trials)) if os.path.isdir(trials) else []:
        t = os.path.join(trials, trial)
        try:
            m = json.load(open(os.path.join(t, "metrics.json"), encoding="utf-8"))
            g = json.load(open(os.path.join(t, "grade.json"), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        sealed = m.get("split") != "train" and not unseal
        if sealed:
            g = {"score": g["score"], "checks": "sealed (Validation Set)"}
            m = {k: v for k, v in m.items() if k not in ("commands", "result")}
        base = "%s/trials/%s/" % (name, trial)
        add(base + "grade.json", json.dumps(g, ensure_ascii=False, indent=1).encode("utf-8"))
        add(base + "metrics.json", json.dumps(m, ensure_ascii=False, indent=1).encode("utf-8"))
        for f in ("solve.py", "test_solve.py"):
            p = os.path.join(t, "sandbox", f)
            if not sealed and os.path.isfile(p):
                add(base + "sandbox/" + f, open(p, "rb").read())
tar.close()
