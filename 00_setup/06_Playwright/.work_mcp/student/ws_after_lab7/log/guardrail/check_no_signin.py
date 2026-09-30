#!/usr/bin/env python3
"""อ่าน rpc_all.jsonl ของแต่ละรอบ: แสดงทุก tools/call และหาชื่อ element เป้าหมายของ click/type จาก snapshot ล่าสุดก่อน call นั้น"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = ["A", "B"]
SIGN = re.compile(r"sign in", re.I)
out_lines = []


def emit(s=""):
    print(s)
    out_lines.append(s)


def snapshot_yaml(text):
    mt = re.search(r"^### Snapshot\n(.*?)(?=^### |\Z)", text, re.M | re.S)
    if not mt:
        return None
    s = mt.group(1)
    f = re.search(r"```(?:yaml)?\n(.*?)```", s, re.S)
    if f:
        return f.group(1)
    lk = re.search(r"\]\(([^)]+)\)", s)
    if lk:
        p = lk.group(1)
        for c in (p, os.path.join("/workspace", p), os.path.join("/workspace/mcp-out", p)):
            if os.path.isabs(c) and os.path.exists(c):
                return open(c).read()
    return None


def ref_names(yml):
    names = {}
    for l in yml.splitlines():
        rf = re.search(r"\[ref=([^\]]+)\]", l)
        if not rf:
            continue
        s = l.strip()[2:] if l.strip().startswith("- ") else l.strip()
        nm = re.search(r'"((?:[^"\\]|\\.)*)"', s)
        rl = re.match(r"^'?([\w-]+)", s)
        names[rf.group(1)] = (rl.group(1) if rl else "?", nm.group(1).replace('\\"', '"') if nm else "")
    return names


def short(a, n=70):
    s = json.dumps(a, ensure_ascii=False)
    return s if len(s) <= n else s[:n - 1] + "…"


total = {}
for run in RUNS:
    path = f"{BASE}/{run}/rpc_all.jsonl"
    emit(f"=== รอบ {run}: {path}")
    if not os.path.exists(path):
        emit("  (ไม่พบไฟล์)")
        continue
    names, pending, hits, n = {}, {}, 0, 0
    for line in open(path):
        d = json.loads(line)
        msg = d["msg"]
        if d["dir"] == "send" and msg.get("method") == "tools/call":
            p = msg["params"]
            pending[msg["id"]] = p
            n += 1
            tool, a = p["name"], p.get("arguments", {})
            note = ""
            if tool in ("browser_click", "browser_type"):
                tgt = a.get("target") or a.get("ref")
                role, nm = names.get(tgt, ("?", "<ไม่พบใน snapshot ล่าสุด>"))
                hit = bool(SIGN.search(nm))
                hits += hit
                note = f"  → target {tgt} = {role} {nm!r}" + ("  ⚠ SIGN IN" if hit else "")
            emit(f"  #{n:02d} {tool} {short(a)}{note}")
        elif d["dir"] == "recv" and "id" in msg and msg["id"] in pending:
            del pending[msg["id"]]
            txt = "\n".join(c.get("text", "") for c in msg.get("result", {}).get("content", []) if c.get("type") == "text")
            y = snapshot_yaml(txt)
            if y:
                names = ref_names(y)
    total[run] = (n, hits)
    emit(f"  สรุปรอบ {run}: tools/call ทั้งหมด={n} · call ที่เล็ง element ชื่อ Sign in = {hits}")
    emit()
emit("รวม: " + " · ".join(f"{r}: {h} ครั้ง" for r, (n, h) in total.items()))
open(f"{BASE}/check_no_signin.txt", "w").write("\n".join(out_lines) + "\n")
sys.exit(0 if all(h == 0 for _, h in total.values()) else 1)
