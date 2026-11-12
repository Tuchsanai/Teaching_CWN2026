#!/usr/bin/env python3
"""รันใน container โดย tools/pull.sh: แพ็กผลเป็น tar ส่งออกทาง stdout

runs/<workspace>/...                 workspace ของ WikiSkill (raw/ wiki/ skills/ history/ state.json)
results/runs/<label>/<trial>/...     ผลของทุก Trial: grade.json metrics.json + โค้ดที่ Agent เขียน
results/results.json                 ตารางสรุปของคำสั่ง report (ถ้ามี)

Validation Set: เก็บเฉพาะคะแนนและตัวเลขต้นทุน (ไม่มีผลรายข้อ คำสั่ง และโค้ด) · Training และ Test Set เก็บครบ
"""
import io, json, os, sys, tarfile

W = "/workspace/wklab"
SUITE = os.path.join(W, "suite")
SKIP_DIRS = {"proposer_view", "_wm", "tmp", "__pycache__"}
tar = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")


def add(name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


# ---- workspace ของ WikiSkill
ws_root = os.path.join(W, "ws")
for root, dirs, files in os.walk(ws_root):
    dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
    for f in sorted(files):
        if f.endswith(".stderr"):
            continue
        p = os.path.join(root, f)
        add("runs/" + os.path.relpath(p, ws_root).replace(os.sep, "/"), open(p, "rb").read())

# ---- ผลของทุก Trial
if os.path.isfile(os.path.join(SUITE, "results.json")):
    add("results/results.json", open(os.path.join(SUITE, "results.json"), "rb").read())
runs = os.path.join(SUITE, "runs")
for label in sorted(os.listdir(runs)) if os.path.isdir(runs) else []:
    for trial in sorted(os.listdir(os.path.join(runs, label))):
        d = os.path.join(runs, label, trial)
        try:
            m = json.load(open(os.path.join(d, "metrics.json"), encoding="utf-8"))
            g = json.load(open(os.path.join(d, "grade.json"), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        sealed = m.get("split") == "val"
        if sealed:
            g = {"score": g["score"], "checks": "sealed (Validation Set)"}
            m = {k: v for k, v in m.items() if k not in ("commands", "result")}
        base = "results/runs/%s/%s/" % (label, trial)
        add(base + "grade.json", json.dumps(g, ensure_ascii=False, indent=1).encode("utf-8"))
        add(base + "metrics.json", json.dumps(m, ensure_ascii=False, indent=1).encode("utf-8"))
        for f in ("solve.py", "test_solve.py"):
            p = os.path.join(d, "sandbox", f)
            if not sealed and os.path.isfile(p):
                add(base + "sandbox/" + f, open(p, "rb").read())
tar.close()
