#!/usr/bin/env python3
"""รันใน container โดย tools/pull.sh: แพ็กผลของทุกการรันเป็น tar ส่งออกทาง stdout

runs/<ชื่อการรัน>/RUN.json state.json inputs/instruction.md
runs/<ชื่อการรัน>/setup/            benchmark_plugin.py tasks.json freeze.json audit.md
runs/<ชื่อการรัน>/reference/        สิ่งที่ Evolver อ่านได้เกี่ยวกับ benchmark
runs/<ชื่อการรัน>/skills_vK/        ชุดสกิลหลังตาที่ K
runs/<ชื่อการรัน>/turns/            ข้อความที่ส่ง · actions.md · stats.json ของ Benchmark Adaptor และทุกตาของ Evolver
runs/<ชื่อการรัน>/evo/evolver_workspace/   โฟลเดอร์ส่วนตัวของ Evolver (บันทึกและสคริปต์ที่มันเขียนเอง)
runs/<ชื่อการรัน>/evo/scores/              คะแนนของ Training ที่ Evolver เห็น (ตัวเลขอย่างเดียว)
runs/<ชื่อการรัน>/legs/<label>.json        สรุปของแต่ละ leg
runs/<ชื่อการรัน>/legs/runs/<label>/<rollout>/   grade.json metrics.json + โค้ดที่ Solver เขียน

Validation Set: เก็บเฉพาะคะแนนและตัวเลขต้นทุน (ไม่มีผลรายข้อ คำสั่ง และโค้ด) · Training และ Test Set เก็บครบ
transcript ดิบ (.jsonl) ไม่ถูกเก็บลงเครื่อง ดูได้ใน container
"""
import io, json, os, sys, tarfile

W = "/workspace/evlab/ws"
tar = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")
SKIP = {"__pycache__", ".ipynb_checkpoints"}
MAX = 400 * 1024


def add(name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def add_tree(ws, name, sub, skip_ext=(".jsonl", ".stderr", ".pyc")):
    base = os.path.join(W, ws, sub)
    for root, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for f in sorted(files):
            p = os.path.join(root, f)
            try:
                if f.endswith(skip_ext) or os.path.getsize(p) > MAX:
                    continue
                data = open(p, "rb").read()
            except OSError:                              # ไฟล์ของการรันที่ยังเดินอยู่ อาจหายไประหว่างแพ็ก
                continue
            add("runs/%s/%s" % (name, os.path.relpath(p, os.path.join(W, ws)).replace(os.sep, "/")), data)


for ws in sorted(os.listdir(W)) if os.path.isdir(W) else []:
    d = os.path.join(W, ws)
    if not os.path.isfile(os.path.join(d, "state.json")):
        continue
    for f in ("RUN.json", "state.json", "inputs/instruction.md", "setup/benchmark_plugin.py", "setup/tasks.json",
              "setup/freeze.json", "setup/audit.md"):
        p = os.path.join(d, f)
        if os.path.isfile(p):
            add("runs/%s/%s" % (ws, f), open(p, "rb").read())
    for sub in ["reference", "turns", "evo/evolver_workspace", "evo/scores"] + sorted(x for x in os.listdir(d) if x.startswith("skills_v")):
        add_tree(ws, ws, sub)
    legs = os.path.join(d, "legs")
    for f in sorted(os.listdir(legs)) if os.path.isdir(legs) else []:
        if f.endswith(".json"):
            add("runs/%s/legs/%s" % (ws, f), open(os.path.join(legs, f), "rb").read())
    runs = os.path.join(legs, "runs")
    for label in sorted(os.listdir(runs)) if os.path.isdir(runs) else []:
        for trial in sorted(os.listdir(os.path.join(runs, label))):
            t = os.path.join(runs, label, trial)
            try:
                m = json.load(open(os.path.join(t, "metrics.json"), encoding="utf-8"))
                g = json.load(open(os.path.join(t, "grade.json"), encoding="utf-8"))
            except (OSError, ValueError):
                continue
            sealed = m.get("split") == "val"
            if sealed:
                g = {"score": g["score"], "checks": "sealed (Validation Set)"}
                m = {k: v for k, v in m.items() if k not in ("commands", "result")}
            base = "runs/%s/legs/runs/%s/%s/" % (ws, label, trial)
            add(base + "grade.json", json.dumps(g, ensure_ascii=False, indent=1).encode("utf-8"))
            add(base + "metrics.json", json.dumps(m, ensure_ascii=False, indent=1).encode("utf-8"))
            for f in ("solve.py", "test_solve.py"):
                p = os.path.join(t, "sandbox", f)
                try:
                    if not sealed and os.path.isfile(p):
                        add(base + "sandbox/" + f, open(p, "rb").read())
                except OSError:
                    pass
tar.close()
