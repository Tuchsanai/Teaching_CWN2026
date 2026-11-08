#!/usr/bin/env python3
"""team.py - ให้หลายบัญชี (yoloN = Claude Code, cyoloN = Codex) ทำงานร่วมกันแบบ multi-agent

คำสั่งหลัก (ดู --help ของแต่ละคำสั่ง):
  check            ตรวจความพร้อมทุกบัญชีด้วยการเรียกจริง
  quota            โควตาล่าสุดทุกบัญชี (พร้อมเวลาของข้อมูล)
  run <graph|->    รันกราฟงาน (relay / fan-out / DAG / review / debate / best_of / image / gate)
  status [--run]   ภาพรวม run: บัญชี | บทบาท | งานที่รัน | คิว | tokens | โควตา | สถานะ
  stats            สถิติจาก ledger แยกตามบัญชี / รุ่น / run
  approve          อนุมัติงานที่มี "approve": true
  lead             หัวหน้าทีมเป็นรอบสั้น + สลับหัวหน้าอัตโนมัติ (--demo สาธิตครบในคำสั่งเดียว)
  dispatch/wait/combine/checkpoint/finish   คำสั่งที่หัวหน้าทีมใช้ระหว่างรอบ
  board            อ่าน/เพิ่มข้อค้นพบบน board.md
"""
import argparse
import collections
import datetime as _dt
import fcntl
import json
import os
import random
import re
import shutil
import signal
import sys
import threading
import time

sys.dont_write_bytecode = True  # ไม่ทิ้ง __pycache__ ในโฟลเดอร์สกิล
HERE = os.path.dirname(os.path.realpath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
for _s in ("yolo", "cyolo"):
    _p = os.path.join(SKILLS, _s, "scripts")
    if _p not in sys.path:
        sys.path.insert(0, _p)
try:
    import yolo as Y
    import cyolo as C
except ImportError as _e:  # pragma: no cover
    sys.stderr.write("team.py: ต้องมีสกิล yolo และ cyolo อยู่ในโฟลเดอร์ skills เดียวกัน (%s)\n" % _e)
    sys.exit(2)

TEAM_PY = os.path.realpath(__file__)
ROOT = Y.LEDGER_DIR
FAIL = {"failed", "bad_format", "blocked", "timeout", "not_approved"}
TERMINAL = FAIL | {"ok"}
STATUS_TH = {"ok": "สำเร็จ", "failed": "ล้ม", "bad_format": "รูปแบบไม่ผ่าน", "blocked": "ถูกบล็อก",
             "timeout": "หมดเวลา", "not_approved": "ไม่ผ่านการตรวจ", "waiting_approval": "รออนุมัติ",
             "pending": "รอคิว", "running": "กำลังรัน"}
DEMO_GOAL = ("สร้างตารางสูตรคูณแม่ 2 ถึง 9 (แต่ละแม่คูณ 1 ถึง 12 บรรทัดละ 'a x b = c') "
             "แบ่งให้ลูกทีมทำคนละแม่ แล้วรวมเป็นไฟล์เดียวเรียงแม่ 2 ถึง 9")
_tlock = threading.RLock()
_qlock = threading.Lock()
QUIET = {"on": False}


# ================================================================ utils
def now_iso():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def hhmmss():
    return _dt.datetime.now().strftime("%H:%M:%S")


def log(msg):
    stream = sys.stderr if QUIET["on"] else sys.stdout
    stream.write("[%s] %s\n" % (hhmmss(), msg))
    stream.flush()


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.tmp.%d.%d" % (path, os.getpid(), threading.get_ident())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read_text(path, default=""):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return default


def par(fn, items):
    from concurrent.futures import ThreadPoolExecutor
    items = list(items)
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=min(16, len(items))) as ex:
        return list(ex.map(fn, items))


def side(acct):
    return "claude" if acct.startswith("yolo") else "codex"


def mod(acct):
    return Y if side(acct) == "claude" else C


def all_accounts():
    return Y.list_accounts() + C.list_accounts()


def parse_budget(values):
    """['30000', 'yolo2=1'] -> {'*': 30000, 'yolo2': 1}"""
    out = {}
    for v in values or []:
        for part in str(v).split(","):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                k, n = part.split("=", 1)
                out[k.strip()] = int(n)
            else:
                out["*"] = int(part)
    return out


def budget_of(budgets, acct):
    if not budgets:
        return None
    if acct in budgets:
        return budgets[acct]
    return budgets.get("*")


# ================================================================ run dir / state
def run_path(run_id):
    return os.path.join(ROOT, run_id)


def list_runs():
    if not os.path.isdir(ROOT):
        return []
    out = []
    for n in os.listdir(ROOT):
        p = os.path.join(ROOT, n)
        if n.startswith(".") or not os.path.isdir(p) or not os.path.isfile(os.path.join(p, "state.json")):
            continue
        out.append((os.path.getmtime(os.path.join(p, "state.json")), n))
    return [n for _, n in sorted(out)]


def resolve_run(run_id):
    if run_id:
        p = run_path(run_id)
        return p if os.path.isfile(os.path.join(p, "state.json")) else None
    runs = list_runs()
    return run_path(runs[-1]) if runs else None


class locked(object):
    """อ่าน-แก้-เขียน state.json แบบ atomic ข้าม process (flock) - ห้ามซ้อนกัน"""

    def __init__(self, run_dir):
        self.run_dir = run_dir

    def __enter__(self):
        _tlock.acquire()
        self.f = open(os.path.join(self.run_dir, "state.lock"), "a+")
        fcntl.flock(self.f, fcntl.LOCK_EX)
        self.st = load_json(os.path.join(self.run_dir, "state.json"), {})
        self.orig = json.dumps(self.st, sort_keys=True, ensure_ascii=False)
        return self.st

    def __exit__(self, et, ev, tb):
        try:
            if et is None:
                s = json.dumps(self.st, sort_keys=True, ensure_ascii=False)
                if s != self.orig:
                    self.st["updated"] = now_iso()
                    save_json(os.path.join(self.run_dir, "state.json"), self.st)
        finally:
            fcntl.flock(self.f, fcntl.LOCK_UN)
            self.f.close()
            _tlock.release()
        return False


def read_state(run_dir):
    return load_json(os.path.join(run_dir, "state.json"), {})


def board_path(run_dir):
    return os.path.join(run_dir, "board.md")


def board_append(run_dir, author, text, node=None):
    line = "- [%s] **%s**%s: %s\n" % (now_iso(), author, (" (%s)" % node) if node else "",
                                       text.strip().replace("\n", " "))
    with open(board_path(run_dir), "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line)


def board_body(run_dir):
    txt = read_text(board_path(run_dir))
    return "\n".join(l for l in txt.splitlines() if l.startswith("- ["))


def ledger_event(run_dir, st, event, **kw):
    row = Y.ledger_row(ts_start=now_iso(), ts_end=now_iso(), run_id=st.get("run_id"),
                       event=event, status="ok", **kw)
    Y.ledger_append(row, run_dir)


def new_run_dir(mode, goal, run_id=None):
    rid = run_id or "%s-%04x" % (_dt.datetime.now().strftime("%Y%m%d-%H%M%S"), random.randint(0, 0xffff))
    rd = run_path(rid)
    for d in ("msgs", "out", "approvals", "tmp"):
        os.makedirs(os.path.join(rd, d), exist_ok=True)
    if not os.path.exists(board_path(rd)):
        write_text(board_path(rd), "# board ของ run %s\nกระดานความรู้กลาง: ทุก agent อ่านก่อนเริ่ม · "
                                   "เพิ่มแบบต่อท้าย (ผู้เขียน + เวลา)\n\n" % rid)
    return rid, rd


# ================================================================ accounts: readiness + quota
def check_accounts(accs, fresh=False, max_age=900):
    cache_f = os.path.join(ROOT, "accounts.json")
    cache = load_json(cache_f, {})
    t = time.time()
    need = [a for a in accs if fresh or not cache.get(a) or t - cache[a].get("epoch", 0) > max_age]
    if need:
        for r in par(lambda a: mod(a).check_account(a), need):
            r["epoch"] = time.time()
            cache[r["account"]] = r
        with _qlock:
            cur = load_json(cache_f, {})
            cur.update({a: cache[a] for a in need})
            save_json(cache_f, cur)
    return {a: cache[a] for a in accs if a in cache}


def get_quota(acct, refresh=False):
    info = Y.quota(acct) if side(acct) == "claude" else C.quota(acct, refresh=refresh)
    info["pct"] = Y.quota_pct(info)
    with _qlock:
        f = os.path.join(ROOT, "quota.json")
        cur = load_json(f, {})
        cur[acct] = info
        try:
            save_json(f, cur)
        except OSError:
            pass
    return info


def cached_quota(acct):
    return load_json(os.path.join(ROOT, "quota.json"), {}).get(acct)


def quota_text(q):
    if not q or not q.get("available"):
        return "ไม่มีข้อมูล"
    if q.get("cli") == "claude":
        parts = []
        if q.get("session_pct") is not None:
            parts.append("session %g%%" % q["session_pct"])
        if q.get("week_pct") is not None:
            parts.append("week %g%%" % q["week_pct"])
        return "%s (ณ %s)" % (" · ".join(parts) or "-", (q.get("ts") or "")[11:19])
    parts = []
    if q.get("primary_pct") is not None:
        parts.append("primary %g%%" % q["primary_pct"])
    if q.get("secondary_pct") is not None:
        parts.append("secondary %g%%" % q["secondary_pct"])
    return "%s (ณ %s)" % (" · ".join(parts) or "-", (q.get("ts") or "")[:16].replace("T", " "))


# ================================================================ graph
PH = re.compile(r"\{\{\s*(file:|account:)?([A-Za-z0-9_.\-]+)\s*\}\}")
SPECIAL = {"run_dir", "board"}


def placeholders(text):
    return [m.group(2) for m in PH.finditer(text or "") if m.group(2) not in SPECIAL]


def expand(nodes):
    """debate / best_of -> งานย่อย + ผู้ตัดสิน"""
    out = []
    for n in nodes:
        t = n.get("type", "task")
        if t not in ("debate", "best_of"):
            out.append(n)
            continue
        nid = n["id"]
        if t == "debate":
            accs = n.get("accounts") or ["yolo", "cyolo"]
        else:
            k = int(n.get("n") or len(n.get("accounts") or []) or 3)
            base = n.get("accounts") or ["any"]
            accs = [base[i % len(base)] for i in range(k)]
        subs = []
        for i, a in enumerate(accs, 1):
            s = {kk: vv for kk, vv in n.items() if kk in ("prompt", "difficulty", "cwd", "kind",
                                                       "timeout", "depends_on", "effort", "model")}
            s.update(id="%s.%d" % (nid, i), account=a, type="task", expect=n.get("candidate_expect", "text"))
            out.append(s)
            subs.append(s["id"])
        letters = "ABCDEFGHIJKLMNOP"
        answers = "\n\n".join("คำตอบ %s (จาก {{account:%s}}):\n{{%s}}" % (letters[i], sid, sid)
                              for i, sid in enumerate(subs))
        if t == "debate":
            jp = ("คุณเป็นผู้ตัดสินที่เป็นกลาง โจทย์:\n" + n["prompt"] + "\n\n" + answers +
                  "\n\nตรวจแต่ละคำตอบอย่างอิสระ (คำนวณหรือทดสอบเองถ้าทำได้) แล้วตอบ JSON บรรทัดเดียวเท่านั้น: "
                  '{"final": "<คำตอบที่ถูกที่สุด>", "winner": "<ตัวอักษรของคำตอบที่ดีที่สุด หรือ tie หรือ none>", '
                  '"reason": "<เหตุผลสั้น ๆ>"}')
        else:
            crit = n.get("criteria") or "ความถูกต้อง ความครบถ้วน ความชัดเจน"
            jp = ("คุณเป็นผู้ตัดสิน ให้คะแนนผลงานแต่ละชิ้นของโจทย์นี้:\n" + n["prompt"] + "\n\nเกณฑ์: " + crit +
                  "\n\n" + answers.replace("คำตอบ ", "ผลงาน ") +
                  "\n\nให้คะแนน 0-10 ตามเกณฑ์ แล้วตอบ JSON บรรทัดเดียวเท่านั้น: "
                  '{"best": "<ตัวอักษรของผลงานที่ดีที่สุด>", "scores": {"A": <คะแนน>, ...}, "reason": "<เหตุผลสั้น ๆ>"}')
        j = {"id": nid, "type": "task", "prompt": jp, "account": n.get("judge") or "any",
             "expect": "json", "depends_on": subs, "post": t, "candidates": subs,
             "difficulty": n.get("judge_difficulty") or n.get("difficulty"),
             "approve": n.get("approve", False)}
        out.append(j)
    return out


def normalize_nodes(raw, defaults):
    if isinstance(raw, dict):
        nodes = raw.get("nodes") or raw.get("tasks") or []
    else:
        nodes = raw
    out = []
    for n in nodes:
        n = dict(n)
        for k, v in (defaults or {}).items():
            n.setdefault(k, v)
        coerce(n)
        if "id" not in n:
            raise ValueError("ทุกงานต้องมี id")
        n["id"] = str(n["id"])
        if not n.get("prompt") and n.get("type") != "review":
            raise ValueError("งาน %s ไม่มี prompt" % n["id"])
        out.append(n)
    out = expand(out)
    ids = [n["id"] for n in out]
    dup = [i for i, c in collections.Counter(ids).items() if c > 1]
    if dup:
        raise ValueError("id ซ้ำ: %s" % ", ".join(dup))
    for n in out:
        deps = list(n.get("depends_on") or [])
        for p in placeholders(n.get("prompt", "")) + placeholders(n.get("review_prompt", "")):
            if p not in deps:
                deps.append(p)
        n["depends_on"] = deps
        bad = [d for d in deps if d not in ids]
        if bad:
            raise ValueError("งาน %s อ้างงานที่ไม่มี: %s" % (n["id"], ", ".join(bad)))
        if n.get("kind") == "image" or n.get("type") == "image":
            n["kind"] = "image"
            n.setdefault("expect", "png")
    # ตรวจวงจร
    g = {n["id"]: n["depends_on"] for n in out}
    seen, stack = set(), set()

    def visit(x):
        if x in stack:
            raise ValueError("กราฟมีวงจรที่ %s" % x)
        if x in seen:
            return
        stack.add(x)
        for d in g[x]:
            visit(d)
        stack.discard(x)
        seen.add(x)
    for x in g:
        visit(x)
    return out


# ================================================================ planning / router
def route(n):
    kind = (n.get("kind") or "").lower()
    p = n.get("prompt") or ""
    if kind == "image" or (not kind and re.search(r"สร้างภาพ|image generation", p, re.I)):
        return "codex", "งานภาพ → cyolo (สร้างภาพได้ฝั่ง Codex เท่านั้น)", True
    if kind in ("code_review", "review_code") or (not kind and re.search(r"ตรวจโค้ด|code review|review (the )?code", p, re.I)):
        return "codex", "ตรวจโค้ด → Codex", False
    if kind in ("doc", "long", "summary", "writing") or len(p) > 4000 or \
            (not kind and re.search(r"เอกสารยาว|long document", p, re.I)):
        return "claude", "เอกสาร/ข้อความยาว → Claude", False
    return None, "เลือกบัญชีที่โควตาเหลือมากสุด/งานน้อยสุด", False


def model_side(n):
    m = n.get("model")
    if not m:
        return None
    return "claude" if m in Y.MODELS else "codex"


def usable(st, want=None, exclude=()):
    out = []
    for a, info in sorted(st.get("accounts", {}).items()):
        if not info.get("ready") or info.get("stopped") or info.get("unavailable"):
            continue
        if a in exclude or a in (st.get("settings", {}).get("exclude") or []):
            continue
        if want and side(a) != want:
            continue
        out.append(a)
    return out


def load_of(st, a):
    return sum(1 for n in st["nodes"].values()
               if n.get("planned") == a and n.get("status") in ("pending", "running", "waiting_approval"))


def tokens_of(st, a):
    tot = 0
    for n in st["nodes"].values():
        for at in n.get("attempts") or []:
            if at.get("account") == a:
                tot += int(at.get("in") or 0) + int(at.get("out") or 0)
    return tot


def plan(st, n, exclude=(), prefer=None, spec_override=None):
    """คืน (account, เหตุผล, pinned)"""
    spec = spec_override or n.get("account") or "any"
    if re.fullmatch(r"c?yolo\d+", spec):
        return spec, "ผู้ใช้ระบุบัญชี", True
    bound = model_side(n)
    if spec in ("yolo", "claude"):
        want, reason, cli_bound = "claude", "ระบุฝั่ง yolo", True
    elif spec in ("cyolo", "codex"):
        want, reason, cli_bound = "codex", "ระบุฝั่ง cyolo", True
    else:
        want, reason, cli_bound = route(n)
        if bound:
            want, cli_bound = bound, True
            reason = "รุ่น %s → ฝั่ง %s" % (n.get("model"), bound)
    cands = usable(st, want, exclude)
    if not cands and want and not cli_bound:
        cands = usable(st, None, exclude)
        reason += " (ฝั่งที่ต้องการไม่ว่าง → ข้ามฝั่ง)"
    if not cands:
        return None, reason + ": ไม่มีบัญชีที่พร้อม", False
    q = st.get("quota", {})
    prefer = prefer if prefer else None
    dw = st.get("settings", {}).get("demo_worker")  # --demo: ลูกทีมงบต่ำรับ 2 งานแรก จึงมีงานในคิวให้ย้ายแน่นอน

    def key(a):
        return (0 if (a == dw and load_of(st, a) < 2) else 1,
                0 if (prefer is None or side(a) == prefer) else 1, load_of(st, a),
                q.get(a) if q.get(a) is not None else 50.0, tokens_of(st, a), a)
    return min(cands, key=key), reason, False


def worker_switch(st, run_dir, nid, frm, to, reason):
    ev = {"ts": now_iso(), "node": nid, "from": frm, "to": to, "reason": reason}
    st.setdefault("worker_switches", []).append(ev)
    board_append(run_dir, "team.py", "ย้ายงาน %s จาก %s ไป %s: %s" % (nid, frm, to or "-", reason))
    ledger_event(run_dir, st, "worker_switch", node=nid, account=to, error=reason[:160],
                 **{"from": frm})
    log("⇄ ย้ายงาน %s: %s → %s (%s)" % (nid, frm, to or "-", reason))


def stop_account(st, run_dir, a, reason):
    info = st["accounts"].setdefault(a, {})
    if info.get("stopped"):
        return
    info["stopped"] = True
    info["stop_reason"] = reason
    board_append(run_dir, "team.py", "%s หยุดรับงานใหม่: %s" % (a, reason))
    log("⏸ %s หยุดรับงานใหม่: %s (งานที่กำลังรันปล่อยให้จบ)" % (a, reason))
    replan_queued(st, run_dir, a, reason)


def replan_queued(st, run_dir, a, reason):
    for nid in st["order"]:
        n = st["nodes"][nid]
        if n.get("planned") != a or n.get("status") not in ("pending", "waiting_approval"):
            continue
        if n.get("pinned"):
            continue  # ผู้ใช้ระบุบัญชีเอง: ไม่ย้ายเงียบ - จะหยุดและรายงานตอนถึงคิว
        new, why, _ = plan(st, n, exclude=(a,), prefer=side(a))
        n["planned"] = new
        worker_switch(st, run_dir, nid, a, new, reason)


WORD_DIFF = {"easy": 1, "low": 1, "ง่าย": 1, "medium": 2, "normal": 2, "กลาง": 2, "hard": 3, "high": 3,
             "ยาก": 3, "xhigh": 4, "max": 5}


def coerce(n):
    """แก้ค่าที่ชนิดผิดให้ใช้ได้ (เช่น difficulty "easy" หรือ "2") แทนการล้มกลางทาง"""
    d = n.get("difficulty")
    if d not in (None, ""):
        try:
            n["difficulty"] = min(max(int(float(d)), 1), 6)
        except (TypeError, ValueError):
            n["difficulty"] = WORD_DIFF.get(str(d).strip().lower(), 2)
    for k, dv in (("timeout", 600), ("max_rounds", 3), ("n", 3)):
        if n.get(k) not in (None, ""):
            try:
                n[k] = int(float(n[k]))
            except (TypeError, ValueError):
                n[k] = dv
    if isinstance(n.get("depends_on"), str):
        n["depends_on"] = [x.strip() for x in n["depends_on"].split(",") if x.strip()]
    return n


def add_nodes(st, nodes):
    for n in nodes:
        n = coerce(dict(n))
        n.setdefault("type", "task")
        n.update(status="pending", attempts=[], error=None, value=None)
        acct, reason, pinned = plan(st, n)
        n["planned"], n["route"], n["pinned"] = acct, reason, pinned
        if n.get("type") == "review":
            r_spec = n.get("reviewer") or "any"
            racct, rreason, rpinned = plan(st, n, spec_override=r_spec,
                                           prefer=("codex" if acct and side(acct) == "claude" else "claude"))
            n["reviewer_planned"] = racct
        st["nodes"][n["id"]] = n
        if n["id"] not in st["order"]:
            st["order"].append(n["id"])
    write_graph(st)


def write_graph(st):
    keys = ("id", "type", "kind", "account", "planned", "depends_on", "expect", "difficulty", "approve",
            "reviewer", "max_rounds", "cwd", "post", "candidates")
    g = {"run_id": st["run_id"], "goal": st.get("goal"),
         "nodes": [{k: st["nodes"][i].get(k) for k in keys if st["nodes"][i].get(k) not in (None, [], False)}
                   for i in st["order"]],
         "edges": [[d, i] for i in st["order"] for d in st["nodes"][i].get("depends_on") or []]}
    save_json(os.path.join(st["run_dir"], "graph.json"), g)


def init_state(rid, rd, mode, goal, settings, accounts_info, quotas):
    st = {"run_id": rid, "run_dir": rd, "mode": mode, "goal": goal, "created": now_iso(),
          "status": "running", "settings": settings, "nodes": {}, "order": [],
          "accounts": {}, "quota": {}, "worker_switches": [], "lead_history": [], "leader": None}
    for a, info in accounts_info.items():
        st["accounts"][a] = {"ready": info.get("state") == "ready", "check": info.get("state"),
                             "checked": info.get("ts")}
    for a, q in quotas.items():
        st["quota"][a] = q.get("pct")
    return st


def apply_quota_threshold(st, run_dir, quotas):
    thr = st["settings"].get("quota_threshold", 80)
    for a, q in quotas.items():
        pct = q.get("pct")
        st["quota"][a] = pct
        if pct is not None and pct >= thr and st["accounts"].get(a, {}).get("ready"):
            stop_account(st, run_dir, a, "โควตา %g%% ≥ เกณฑ์ %g%%" % (pct, thr))


# ================================================================ prompts / validation
FORMAT_HINT = {"int": "\n\n(รูปแบบคำตอบ: จำนวนเต็มอย่างเดียว)",
               "number": "\n\n(รูปแบบคำตอบ: ตัวเลขอย่างเดียว)",
               "json": "\n\n(รูปแบบคำตอบ: JSON อย่างเดียว ไม่มีข้อความอื่น)"}


def value_of(st, run_dir, nid, limit=1500):
    n = st["nodes"].get(nid) or {}
    path = os.path.join(run_dir, "out", nid + ".md")
    v = n.get("value")
    if v is None:
        v = read_text(path).strip()
    if len(v) > limit:
        return "(ข้อมูลยาว %d ตัวอักษร อ่านจากไฟล์ %s)" % (len(v), path)
    return v


def render(st, run_dir, text):
    def rep(m):
        kind, key = m.group(1), m.group(2)
        if key == "run_dir":
            return run_dir
        if key == "board":
            return board_path(run_dir)
        if kind == "file:":
            return os.path.join(run_dir, "out", key + ".md")
        if kind == "account:":
            return (st["nodes"].get(key) or {}).get("assigned") or "?"
        return value_of(st, run_dir, key)
    return PH.sub(rep, text or "")


def build_prompt(st, run_dir, n, acct, body=None):
    parts = ["[ทีม %s · งาน %s · บัญชี %s]" % (st["run_id"], n["id"], acct)]
    if n.get("cwd"):
        parts.append("โฟลเดอร์ทำงาน (absolute path): %s" % n["cwd"])
    if st["settings"].get("board", True):
        b = board_body(run_dir)
        if b and len(b) <= 1500:
            parts.append("กระดานความรู้กลาง (%s):\n%s" % (board_path(run_dir), b))
        elif b:
            parts.append("อ่านกระดานความรู้กลางก่อนเริ่ม: %s" % board_path(run_dir))
        parts.append("(ถ้าพบข้อเท็จจริงที่งานอื่นควรรู้ เพิ่มบรรทัด BOARD: <ข้อเท็จจริง> ต่อท้ายคำตอบได้ ไม่ใช่แทนคำตอบ)")
    prev = [at["account"] for at in n.get("attempts") or [] if at.get("account") != acct]
    for pa in prev[-1:]:
        pf = os.path.join(run_dir, "msgs", "%s__%s.progress.md" % (pa, n["id"]))
        if os.path.isfile(pf):
            parts.append("งานนี้ย้ายมาจาก %s ความคืบหน้าเดิมอยู่ที่ %s อ่านก่อนแล้วทำต่อ" % (pa, pf))
    if int(n.get("difficulty") or 0) >= 3 or n.get("kind") == "code":
        parts.append("งานยาว: เขียนความคืบหน้าสั้น ๆ ลง %s เป็นระยะ" %
                     os.path.join(run_dir, "msgs", "%s__%s.progress.md" % (acct, n["id"])))
    parts.append("---")
    parts.append(render(st, run_dir, body if body is not None else n.get("prompt", "")))
    hint = FORMAT_HINT.get((n.get("expect") or "text").split(":")[0])
    return "\n".join(parts) + (hint or "")


BOARD_LINE = re.compile(r"^\s*\**BOARD:\**\s*(.+)$", re.M)


def split_board(text):
    facts = [m.group(1).strip() for m in BOARD_LINE.finditer(text or "")]
    clean = BOARD_LINE.sub("", text or "").strip()
    if not clean and facts:
        clean = "\n".join(facts)  # ตอบมาเป็นบรรทัด BOARD: อย่างเดียว: ใช้เป็นคำตอบด้วย ไม่ทิ้ง
    return clean, facts


def _strip_fences(t):
    t = t.strip()
    m = re.match(r"^```[a-zA-Z0-9]*\s*\n(.*?)\n?```\s*$", t, re.S)
    return m.group(1).strip() if m else t


def validate(expect, text, n=None):
    """คืน (ok, value, เหตุผลเมื่อไม่ผ่าน)"""
    e = expect or "text"
    t = (text or "").strip()
    if e == "text":
        return (bool(t), t, None if t else "คำตอบว่าง")
    if e in ("int", "number"):
        pat = r"[-−]?\d[\d,]*" if e == "int" else r"[-−]?\d[\d,]*(?:\.\d+)?"
        lines = [l.strip().strip("`*_ ").strip() for l in _strip_fences(t).splitlines() if l.strip()]
        for cand in lines[-1:]:
            m = re.fullmatch(pat, cand) or re.search(r"=\s*(" + pat + r")\s*\.?$", cand)
            if m:
                v = (m.group(1) if m.groups() else m.group(0)).replace(",", "").replace("−", "-")
                return True, v, None
        return False, None, ("expect %s: ต้องเป็นค่าล้วนหรือสมการบรรทัดเดียวที่ลงท้าย '= N' (ได้: %r)"
                             % (e, t[:80]))
    if e == "json":
        s = _strip_fences(t)
        try:
            obj = json.loads(s)
        except ValueError:
            m = re.search(r"(\{.*\}|\[.*\])", s, re.S)
            try:
                obj = json.loads(m.group(1)) if m else None
            except ValueError:
                obj = None
            if obj is None:
                return False, None, "expect json: แปลงเป็น JSON ไม่ได้"
        return True, json.dumps(obj, ensure_ascii=False), None
    if e.startswith("regex:"):
        m = re.search(e[6:], t, re.S | re.M)
        if not m:
            return False, None, "expect %s: ไม่ตรงรูปแบบ" % e
        return True, (m.group(1) if m.groups() else t), None
    if e.startswith("contains:"):
        ok = e[9:] in t
        return ok, t, None if ok else "expect %s: ไม่พบข้อความ" % e
    if e == "approved":
        ok = t.lstrip("*# ").upper().startswith("APPROVED")
        return ok, t, None if ok else "ผู้ตรวจไม่ตอบ APPROVED"
    if e == "png":
        p = (n or {}).get("output")
        if p and C.is_png(p):
            return True, p, None
        return False, None, "expect png: ไม่พบไฟล์ PNG ที่ %s" % p
    return bool(t), t, None


# ================================================================ execution
def exec_on(st, run_dir, n, acct, prompt, role="worker", popen_cb=None):
    s = side(acct)
    model = n.get("model") if model_side(n) == s else None
    eff = n.get("effort")
    diff = n.get("difficulty") or st["settings"].get("difficulty") or 2
    timeout = int(n.get("timeout") or st["settings"].get("timeout") or 600)
    common = dict(timeout=timeout, run_id=st["run_id"], node=n["id"] if role == "worker" else n["id"] + "." + role,
                  run_dir=run_dir, cwd=n.get("cwd"), popen_cb=popen_cb)
    if s == "claude":
        if eff == "ultra":
            eff = "max"
        if eff and eff not in Y.EFFORTS:
            eff = None
        schema = json.dumps(n["schema"]) if n.get("schema") else None
        return Y.call(acct, prompt, model, eff, diff, json_schema=schema, **common)
    if eff and eff not in C.LEVELS:
        eff = None
    if n.get("kind") == "image" and role == "worker":
        common["cwd"] = common["cwd"] or os.path.dirname(n["output"])
        return C.image(acct, render(st, run_dir, n.get("prompt", "")), n["output"], **common)
    schema = None
    if n.get("schema"):
        schema = os.path.join(run_dir, "tmp", n["id"] + ".schema.json")
        save_json(schema, n["schema"])
    return C.call(acct, prompt, model, eff, diff, output_schema=schema, **common)


def attempt_of(r, role):
    return {"account": r["account"], "role": role, "model": r["model"], "effort": r["effort"],
            "in": r["input_tokens"], "out": r["output_tokens"], "duration_s": r["duration_s"],
            "ok": r["ok"], "error": (r["error"] or "")[:160] or None, "ts": now_iso(),
            "effort_note": r.get("effort_note")}


class Engine(object):
    def __init__(self, run_dir, keep_alive=False, wait_approval=0):
        self.run_dir = run_dir
        self.keep_alive = keep_alive
        self.wait_approval = wait_approval
        self.threads = {}
        self.stop = threading.Event()
        self.announced = set()
        self.last_q = {}

    # ---------------------------------------------------------- scheduling
    def schedule(self, st, launches):
        s = st["settings"]
        per, mx = int(s.get("per_account", 3)), int(s.get("max_parallel", 8))
        running = collections.Counter(n.get("assigned") for n in st["nodes"].values() if n["status"] == "running")
        total = sum(running.values())
        order = sorted(st["order"], key=lambda i: 0 if st["nodes"][i].get("kind") == "image" else 1)
        for nid in order:
            n = st["nodes"][nid]
            if n["status"] not in ("pending", "waiting_approval"):
                continue
            deps = [st["nodes"][d]["status"] for d in n.get("depends_on") or [] if d in st["nodes"]]
            bad = [d for d in n.get("depends_on") or [] if st["nodes"].get(d, {}).get("status") in FAIL]
            if bad:
                n["status"] = "blocked"
                n["error"] = "งานที่ขึ้นกับล้ม: %s" % ", ".join(bad)
                log("⊘ %s ถูกบล็อก (%s)" % (nid, n["error"]))
                continue
            if any(x != "ok" for x in deps):
                continue
            if n.get("approve") and not os.path.exists(os.path.join(self.run_dir, "approvals", nid)):
                if n["status"] != "waiting_approval":
                    n["status"] = "waiting_approval"
                    log("✋ %s รออนุมัติ: python3 %s approve --run %s %s" % (nid, TEAM_PY, st["run_id"], nid))
                continue
            if n["status"] == "waiting_approval":
                n["status"] = "pending"
                log("✔ %s ได้รับอนุมัติแล้ว" % nid)
            acct = n.get("planned")
            info = st["accounts"].get(acct or "", {})
            blocked = (not acct) or (not info.get("ready")) or info.get("stopped") or info.get("unavailable")
            if blocked:
                why = (info.get("stop_reason") or info.get("unavailable") or
                       ("ไม่พร้อม (%s)" % info.get("check")) if acct else "ยังไม่มีบัญชี")
                if n.get("pinned"):
                    n["status"] = "failed"
                    n["error"] = "บัญชีที่ผู้ใช้ระบุ %s ใช้ไม่ได้/หยุดรับงาน: %s (ไม่ย้ายอัตโนมัติ)" % (acct, why)
                    log("✗ %s: %s" % (nid, n["error"]))
                    continue
                new, reason, _ = plan(st, n, exclude=(acct,) if acct else ())
                if not new:
                    n["status"] = "failed"
                    n["error"] = "ไม่มีบัญชีที่พร้อม (%s)" % reason
                    log("✗ %s: %s" % (nid, n["error"]))
                    continue
                if acct:
                    worker_switch(st, self.run_dir, nid, acct, new, why)
                n["planned"] = acct = new
            if total >= mx:
                break
            if running[acct] >= per:
                continue
            n["status"] = "running"
            n["assigned"] = acct
            n["started"] = now_iso()
            launches.append(nid)
            running[acct] += 1
            total += 1

    def loop(self):
        wait_start = None
        stuck = 0
        while True:
            launches = []
            with locked(self.run_dir) as st:
                self.schedule(st, launches)
                pend = [i for i in st["order"] if st["nodes"][i]["status"] == "pending"]
                waiting = [i for i in st["order"] if st["nodes"][i]["status"] == "waiting_approval"]
            for nid in launches:
                th = threading.Thread(target=self.run_node, args=(nid,), daemon=True)
                self.threads[nid] = th
                th.start()
            alive = [i for i, th in self.threads.items() if th.is_alive()]
            if not alive and not launches:
                if self.keep_alive and not self.stop.is_set():
                    stuck = 0
                elif waiting:
                    wait_start = wait_start or time.time()
                    if time.time() - wait_start >= self.wait_approval:
                        return "waiting_approval"
                elif not pend:
                    return "done"
                else:
                    stuck += 1
                    if stuck > 15:  # ไม่มีงานรันและจัดคิวไม่ได้: รายงานแทนการวนไม่จบ
                        with locked(self.run_dir) as st:
                            for i in st["order"]:
                                if st["nodes"][i]["status"] == "pending":
                                    st["nodes"][i]["status"] = "failed"
                                    st["nodes"][i]["error"] = "จัดคิวไม่ได้ (ไม่มีบัญชีว่าง/ค้าง)"
                        return "done"
            else:
                stuck = 0
            time.sleep(0.4)

    # ---------------------------------------------------------- node
    def run_node(self, nid):
        try:
            self._run_node(nid)
        except Exception as e:  # ไม่ให้ thread ตายเงียบ
            with locked(self.run_dir) as st:
                n = st["nodes"][nid]
                n["status"] = "failed"
                n["error"] = "ข้อผิดพลาดในสคริปต์: %s" % e
            log("✗ %s ข้อผิดพลาดในสคริปต์: %s" % (nid, e))

    def _run_node(self, nid):
        rd = self.run_dir
        with locked(rd) as st:
            n = json.loads(json.dumps(st["nodes"][nid]))
            acct = n["assigned"]
            if n.get("kind") == "image" and not n.get("output"):
                n["output"] = st["nodes"][nid]["output"] = os.path.join(rd, "out", nid + ".png")
            if n.get("cwd"):
                os.makedirs(n["cwd"], exist_ok=True)
            for d in n.get("depends_on") or []:
                dn = st["nodes"].get(d) or {}
                write_text(os.path.join(rd, "msgs", "%s__%s.md" % (d, nid)),
                           "จาก %s (งาน %s) ถึง %s (งาน %s) · %s\nผลอยู่ที่ %s\nค่า: %s\n" % (
                               dn.get("assigned"), d, acct, nid, now_iso(),
                               os.path.join(rd, "out", d + ".md"), value_of(st, rd, d, 300)))
            snap = json.loads(json.dumps(st))
        mdl = "%s/%s" % (n.get("model") or "auto", n.get("effort") or "auto")
        log("▶ %s → %s%s" % (nid, acct, " (review loop)" if n.get("type") == "review" else ""))
        if n.get("type") == "review":
            out = self.review_loop(snap, n, acct)
        else:
            prompt = build_prompt(snap, rd, n, acct)
            r = exec_on(snap, rd, n, acct, prompt)
            out = {"results": [(r, "worker")], "final": r}
        self.finish_node(nid, n, acct, out)

    def review_loop(self, st, n, acct):
        rd = self.run_dir
        racct = n.get("reviewer_planned") or acct
        rounds = int(n.get("max_rounds") or 3)
        feedback, results, log_lines = None, [], []
        draft_path = os.path.join(rd, "out", n["id"] + ".md")
        for rnd in range(1, rounds + 1):
            body = n.get("prompt", "")
            if feedback:
                body += ("\n\nรอบที่ %d: แก้งานตามความเห็นผู้ตรวจด้านล่าง แล้วส่งงานฉบับเต็มใหม่ทั้งหมด\n"
                         "งานเดิม: %s\nความเห็นผู้ตรวจ:\n%s" % (rnd, draft_path, feedback))
            r = exec_on(st, rd, n, acct, build_prompt(st, rd, n, acct, body))
            results.append((r, "worker"))
            if not r["ok"]:
                return {"results": results, "final": r}
            draft, facts = split_board(r["result"])
            for f in facts:
                board_append(rd, acct, f, n["id"])
            write_text(os.path.join(rd, "out", "%s.r%d.md" % (n["id"], rnd)), draft)
            write_text(draft_path, draft)
            shown = draft if len(draft) <= 2500 else "(อ่านจากไฟล์ %s)" % draft_path
            rp = ((n.get("review_prompt") or "ตรวจงานนี้ว่าถูกต้องและครบตามโจทย์") +
                  "\n\nโจทย์ของผู้ทำ:\n" + render(st, rd, n.get("prompt", "")) +
                  "\n\nงานที่ต้องตรวจ (%s):\n%s\n\nบรรทัดแรกตอบ APPROVED ถ้าผ่านทุกเกณฑ์ หรือ CHANGES ถ้าไม่ผ่าน "
                  "แล้วบรรทัดถัดไปบอกสิ่งที่ต้องแก้ให้ชัด" % (draft_path, shown))
            rv = exec_on(st, rd, n, racct, "[ทีม %s · ผู้ตรวจงาน %s · บัญชี %s]\n%s" % (
                st["run_id"], n["id"], racct, render(st, rd, rp)), role="review%d" % rnd)
            results.append((rv, "review%d" % rnd))
            text = (rv["result"] or "").strip()
            log_lines.append("## รอบ %d (%s ตรวจงานของ %s)\n%s\n" % (rnd, racct, acct, text or rv["error"]))
            write_text(os.path.join(rd, "out", n["id"] + ".review.md"), "\n".join(log_lines))
            if not rv["ok"]:
                return {"results": results, "final": rv}
            if text.lstrip("*# ").upper().startswith("APPROVED"):
                log("  %s รอบ %d: ผู้ตรวจ %s ตอบ APPROVED" % (n["id"], rnd, racct))
                return {"results": results, "final": r, "approved": True, "rounds": rnd, "draft": draft}
            log("  %s รอบ %d: ผู้ตรวจ %s ขอแก้" % (n["id"], rnd, racct))
            feedback = text
        return {"results": results, "final": r, "approved": False, "rounds": rounds, "draft": draft}

    def finish_node(self, nid, n, acct, out):
        rd = self.run_dir
        final = out["final"]
        quota_after = None
        if final.get("ok") and side(acct) == "claude":
            quota_after = get_quota(acct)  # /usage ไม่เสียโทเค็น
        with locked(rd) as st:
            sn = st["nodes"][nid]
            if "output" in n:
                sn["output"] = n["output"]
            for r, role in out["results"]:
                sn.setdefault("attempts", []).append(attempt_of(r, role))
            sn["model"], sn["effort"] = final.get("model"), final.get("effort")
            sn["ended"] = now_iso()
            ok = all(r["ok"] for r, _ in out["results"])
            if not ok:
                bad = [r for r, _ in out["results"] if not r["ok"]][-1]
                kind = bad.get("error_kind")
                tok = bad["input_tokens"] + bad["output_tokens"]
                if kind in ("quota", "auth") and tok == 0:
                    st["accounts"].setdefault(bad["account"], {})["unavailable"] = \
                        "%s: %s" % ("โควตาหมด/rate limit" if kind == "quota" else "ล็อกอินหมดอายุ", bad["error"][:80])
                    if sn.get("pinned"):
                        sn["status"] = "failed"
                        sn["error"] = "บัญชีที่ผู้ใช้ระบุ %s ล้ม (%s) - ไม่ย้ายอัตโนมัติ" % (bad["account"], bad["error"][:100])
                        log("✗ %s %s" % (nid, sn["error"]))
                    else:
                        new, why, _ = plan(st, sn, exclude=(bad["account"],), prefer=side(bad["account"]))
                        reason = "ล้มเพราะ%s (%s)" % ("โควตาหมด/rate limit" if kind == "quota" else "ล็อกอินหมดอายุ",
                                                      bad["error"][:60])
                        worker_switch(st, rd, nid, bad["account"], new, reason)
                        if new:
                            sn["status"], sn["planned"], sn["assigned"] = "pending", new, None
                        else:
                            sn["status"], sn["error"] = "failed", reason + " และไม่มีบัญชีอื่นที่พร้อม"
                    replan_queued(st, rd, bad["account"], "บัญชีใช้ไม่ได้: " + reason_short(kind))
                else:
                    sn["status"] = "timeout" if kind == "timeout" else "failed"
                    sn["error"] = (bad["error"] or "")[:300]
                    log("✗ %s %s (%s) %s" % (nid, STATUS_TH[sn["status"]], bad["account"], sn["error"][:120]))
            else:
                text = final.get("result") or ""
                clean, facts = split_board(text)
                for f in facts:
                    board_append(rd, acct, f, nid)
                if n.get("type") == "review":
                    clean = out.get("draft", clean)
                    sn["rounds"] = out.get("rounds")
                write_text(os.path.join(rd, "out", nid + ".md"), clean)
                if n.get("type") == "review" and not out.get("approved"):
                    vok, val, why = False, None, "ครบ max_rounds=%s แล้วผู้ตรวจยังไม่ตอบ APPROVED" % out.get("rounds")
                    sn["status"] = "not_approved"
                else:
                    vok, val, why = validate(n.get("expect"), clean, sn)
                    if vok and n.get("post") in ("best_of", "debate"):
                        vok, why = self.post_judge(st, sn, val)
                    sn["status"] = "ok" if vok else "bad_format"
                sn["value"], sn["error"] = val, why
                tin = sum(a["in"] for a in sn["attempts"])
                tout = sum(a["out"] for a in sn["attempts"])
                dur = sum(a["duration_s"] for a in sn["attempts"])
                log("%s %s %s (%s %s/%s) %.1fs in=%d out=%d%s" % (
                    "✓" if vok else "✗", nid, STATUS_TH[sn["status"]], acct, sn["model"], sn["effort"], dur,
                    tin, tout, (" ค่า=%s" % val[:60]) if (vok and val and len(val) < 60) else
                    ((" · " + why) if why else "")))
            # งบโทเค็นลูกทีม: ตรวจทันทีที่งานจบ (งานที่รันอยู่ปล่อยให้จบ)
            for a in {r["account"] for r, _ in out["results"]}:
                b = budget_of(st["settings"].get("worker_budget"), a)
                used = tokens_of(st, a)
                if b is not None and used > b:
                    stop_account(st, rd, a, "เกินงบโทเค็นลูกทีม %d > %d" % (used, b))
            if quota_after is not None:
                apply_quota_threshold(st, rd, {acct: quota_after})

    def post_judge(self, st, sn, val):
        try:
            obj = json.loads(val)
        except ValueError:
            return False, "ผู้ตัดสินไม่ได้ตอบ JSON"
        cands = sn.get("candidates") or []
        key = obj.get("best") if sn.get("post") == "best_of" else obj.get("winner")
        letters = "ABCDEFGHIJKLMNOP"
        idx = None
        if isinstance(key, int) or (isinstance(key, str) and key.strip().isdigit()):
            idx = int(key) - 1
        elif isinstance(key, str) and key.strip()[:1].upper() in letters:
            idx = letters.index(key.strip()[:1].upper())
        if not obj.get("reason"):
            return False, "ผู้ตัดสินไม่ได้ให้เหตุผล (reason)"
        if sn.get("post") == "best_of":
            if idx is None or not (0 <= idx < len(cands)):
                return False, "ผู้ตัดสินเลือกผลงานไม่ถูกต้อง: %r" % key
        if idx is not None and 0 <= idx < len(cands):
            src = os.path.join(self.run_dir, "out", cands[idx] + ".md")
            if os.path.isfile(src):
                shutil.copyfile(src, os.path.join(self.run_dir, "out", sn["id"] + ".best.md"))
                sn["best"] = cands[idx]
        return True, None


def reason_short(kind):
    return "โควตาหมด/rate limit" if kind == "quota" else "ล็อกอินหมดอายุ"


# ================================================================ summaries
def node_row(st, nid):
    n = st["nodes"][nid]
    ats = n.get("attempts") or []
    accts = []
    for a in ats:
        lab = a["account"] + ("" if a["role"] == "worker" else "(ตรวจ)")
        if lab not in accts:
            accts.append(lab)
    me = "%s/%s" % (n.get("model") or "-", n.get("effort") or "-")
    return {"node": nid, "accounts": ",".join(accts) or (n.get("planned") or "-"), "model_effort": me,
            "duration_s": round(sum(a["duration_s"] for a in ats), 1),
            "input_tokens": sum(a["in"] for a in ats), "output_tokens": sum(a["out"] for a in ats),
            "status": n["status"], "note": n.get("error") or "", "value": n.get("value")}


def summary_data(st, quotas):
    rows = [node_row(st, i) for i in st["order"]]
    tot = {"duration_s": round(sum(r["duration_s"] for r in rows), 1),
           "input_tokens": sum(r["input_tokens"] for r in rows),
           "output_tokens": sum(r["output_tokens"] for r in rows),
           "ok": sum(1 for r in rows if r["status"] == "ok"), "count": len(rows)}
    return {"run_id": st["run_id"], "run_dir": st["run_dir"], "status": st.get("status"),
            "nodes": rows, "totals": tot, "worker_switches": st.get("worker_switches", []),
            "lead_history": st.get("lead_history", []),
            "quota": [{"account": a, "text": quota_text(q), "ts": q.get("ts"), "lines": q.get("lines")}
                      for a, q in sorted(quotas.items())]}


def print_summary(st, quotas, title="สรุป run"):
    d = summary_data(st, quotas)
    print("\n## %s %s (%s)" % (title, d["run_id"], STATUS_TH.get(d["status"], d["status"])))
    print("| งาน | บัญชี | รุ่น/effort | เวลา (s) | input tokens | output tokens | สถานะ |")
    print("|---|---|---|---|---|---|---|")
    for r in d["nodes"]:
        note = (" · " + r["note"][:70].replace("|", "/").replace("\n", " ")) if r["note"] and r["status"] != "ok" else ""
        print("| %s | %s | %s | %.1f | %d | %d | %s%s |" % (
            r["node"], r["accounts"], r["model_effort"], r["duration_s"], r["input_tokens"],
            r["output_tokens"], STATUS_TH.get(r["status"], r["status"]), note))
    t = d["totals"]
    print("| **รวม** | | | %.1f | %d | %d | สำเร็จ %d/%d |" % (t["duration_s"], t["input_tokens"],
                                                            t["output_tokens"], t["ok"], t["count"]))
    if d["worker_switches"]:
        print("\nการย้ายงานลูกทีม:\n| งาน | จาก | ไป | เหตุผล |\n|---|---|---|---|")
        for w in d["worker_switches"]:
            print("| %s | %s | %s | %s |" % (w["node"], w["from"], w["to"] or "-", w["reason"]))
    if quotas:
        print("\nโควตาบัญชีที่ใช้ (ข้อมูลจริง ณ เวลาที่ระบุ):")
        for q in d["quota"]:
            print("- %s: %s" % (q["account"], q["text"]))
    print("\nผลแต่ละงาน: %s/out/<งาน>.md · ledger: %s/ledger.jsonl" % (d["run_dir"], d["run_dir"]))


def used_accounts(st):
    s = set()
    for n in st["nodes"].values():
        for a in n.get("attempts") or []:
            s.add(a["account"])
    if st.get("leader"):
        for h in st.get("lead_history", []):
            for k in ("from", "to"):
                if h.get(k):
                    s.add(h[k])
    return sorted(s)


def final_quotas(st):
    accs = used_accounts(st)
    return dict(zip(accs, par(get_quota, accs)))


# ================================================================ setup helper
def prepare(args, mode, goal):
    accs = all_accounts()
    log("ตรวจความพร้อม %d บัญชี (เรียกจริง, ใช้ผลที่ตรวจภายใน 15 นาทีซ้ำได้) ..." % len(accs))
    info = check_accounts(accs, fresh=getattr(args, "recheck", False))
    ready = [a for a in accs if info.get(a, {}).get("state") == "ready"]
    notready = ["%s=%s" % (a, Y.STATE_TH.get(info.get(a, {}).get("state"), "?")) for a in accs if a not in ready]
    log("พร้อม: %s%s" % (", ".join(ready) or "-", (" · ข้าม: " + ", ".join(notready)) if notready else ""))
    quotas = dict(zip(ready, par(get_quota, ready)))
    return info, ready, quotas


def settings_from(args):
    return {"per_account": args.per_account, "max_parallel": args.max_parallel,
            "timeout": args.timeout, "worker_budget": parse_budget(args.worker_token_budget),
            "quota_threshold": args.quota_threshold,
            "exclude": [x for x in (args.exclude or "").split(",") if x], "board": True,
            "difficulty": getattr(args, "difficulty", None) or 2}


# ================================================================ commands
def cmd_check(args):
    accs = args.accounts or all_accounts()
    info = check_accounts(accs, fresh=not args.cached)
    rows = [info[a] for a in accs if a in info]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    print("| บัญชี | CLI | สถานะ | เวลา (s) | ตรวจเมื่อ | หมายเหตุ |\n|---|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s | %.1f | %s | %s |" % (r["account"], r["cli"], Y.STATE_TH.get(r["state"], r["state"]),
              r.get("duration_s") or 0, (r.get("ts") or "")[11:19], (r.get("error") or "")[:60]))
    print("\nพร้อม %d/%d บัญชี" % (sum(1 for r in rows if r["state"] == "ready"), len(rows)))
    return 0


def cmd_quota(args):
    accs = args.accounts or all_accounts()
    rows = par(lambda a: (C.quota(a, refresh=args.refresh) if side(a) == "codex" else Y.quota(a)), accs)
    for r in rows:
        r["pct"] = Y.quota_pct(r)
    with _qlock:
        f = os.path.join(ROOT, "quota.json")
        cur = load_json(f, {})
        cur.update({r["account"]: r for r in rows})
        save_json(f, cur)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    print("| บัญชี | โควตาที่ใช้ไปแล้ว | เวลาของข้อมูล |\n|---|---|---|")
    for r in rows:
        print("| %s | %s | %s |" % (r["account"], " · ".join(r["lines"]) if r["lines"] else "ไม่มีข้อมูล: %s" % r["error"],
                                     r.get("ts") or "-"))
    return 0


def read_graph_arg(path):
    if path == "-":
        data = sys.stdin.buffer.read().decode("utf-8-sig")
    else:
        with open(path, encoding="utf-8-sig") as f:
            data = f.read()
    return json.loads(data)


def cmd_run(args):
    QUIET["on"] = args.json
    if args.resume:
        return resume_run(args)
    if not args.graph:
        print("ต้องระบุไฟล์กราฟ (หรือ - เพื่ออ่านจาก stdin) หรือ --resume <run_id>", file=sys.stderr)
        return 2
    try:
        g = read_graph_arg(args.graph)
        defaults = g.get("defaults", {}) if isinstance(g, dict) else {}
        nodes = normalize_nodes(g, defaults)
    except (ValueError, OSError) as e:
        print("กราฟไม่ถูกต้อง: %s" % e, file=sys.stderr)
        return 2
    goal = g.get("goal") if isinstance(g, dict) else None
    info, ready, quotas = prepare(args, "graph", goal)
    probs = pinned_problems(nodes, info)
    if probs:
        print("ไม่เริ่ม run (ยังไม่เสียโทเค็น): งานที่ระบุบัญชีเองแต่บัญชีนั้นใช้ไม่ได้ — %s\n"
              "แก้ account เป็นบัญชีที่พร้อม (%s) หรือใช้ฝั่ง yolo / cyolo / any ให้ระบบเลือก" % (
                  "; ".join(probs), ", ".join(ready) or "-"), file=sys.stderr)
        return 2
    rid, rd = new_run_dir("graph", goal, args.run_id)
    st = init_state(rid, rd, "graph", goal, settings_from(args), info, quotas)
    if isinstance(g, dict) and g.get("board") is False:
        st["settings"]["board"] = False
    with locked(rd) as s2:
        s2.update(st)
        apply_quota_threshold(s2, rd, quotas)
        add_nodes(s2, nodes)
        for nid in s2["order"]:
            n = s2["nodes"][nid]
            log("  %s → %s (%s)" % (nid, n["planned"] or "ไม่มีบัญชี", n["route"]))
    log("run %s เริ่ม · %d งาน · โฟลเดอร์ %s" % (rid, len(nodes), rd))
    return finish_run(args, rd)


def pinned_problems(nodes, info):
    """งานที่ผู้ใช้ระบุบัญชีเอง (account / reviewer / judge) แต่บัญชีนั้นไม่พร้อม"""
    out = []
    for n in nodes:
        for f in ("account", "reviewer"):
            a = n.get(f)
            if a and re.fullmatch(r"c?yolo\d+", a):
                stt = (info.get(a) or {}).get("state")
                if stt != "ready":
                    out.append("%s.%s=%s (%s)" % (n["id"], f, a, Y.STATE_TH.get(stt, "ไม่มีบัญชีนี้")))
    return out


def finish_run(args, rd):
    eng = Engine(rd, wait_approval=args.wait_approval)
    res = eng.loop()
    with locked(rd) as st:
        sts = [st["nodes"][i]["status"] for i in st["order"]]
        if res == "waiting_approval":
            st["status"] = "waiting_approval"
        else:
            st["status"] = "done" if all(s == "ok" for s in sts) else "failed"
        bad = [i for i in st["order"] if st["nodes"][i]["status"] != "ok"]
        write_handoff(rd, st, "team.py run", "สำเร็จ %d/%d งาน" % (len(sts) - len(bad), len(sts)),
                      ("รันต่อ: team.py run --resume %s (งานที่ยังไม่สำเร็จ: %s)" % (st["run_id"], ", ".join(bad)))
                      if bad else "ไม่มี (จบแล้ว)", "-")
        final = json.loads(json.dumps(st))
    quotas = final_quotas(final)
    if args.json:
        print(json.dumps(summary_data(final, quotas), ensure_ascii=False, indent=1))
    else:
        print_summary(final, quotas)
        if res == "waiting_approval":
            w = [i for i in final["order"] if final["nodes"][i]["status"] == "waiting_approval"]
            print("\n✋ รออนุมัติ: %s\n   อนุมัติ: python3 %s approve --run %s <งาน>\n   แล้วรันต่อ: python3 %s run --resume %s"
                  % (", ".join(w), TEAM_PY, final["run_id"], TEAM_PY, final["run_id"]))
        elif final["status"] != "done":
            print("\nแก้แล้วรันต่อเฉพาะงานที่ล้ม: python3 %s run --resume %s [graph.json] [--set <งาน>.expect=text]"
                  % (TEAM_PY, final["run_id"]))
    return 0 if final["status"] in ("done", "waiting_approval") else 1


def resume_run(args):
    rd = resolve_run(args.resume)
    if not rd:
        print("ไม่พบ run %s" % args.resume, file=sys.stderr)
        return 2
    overrides = {}
    if args.graph:
        try:
            g = read_graph_arg(args.graph)
            for n in normalize_nodes(g, g.get("defaults", {}) if isinstance(g, dict) else {}):
                overrides[n["id"]] = n
        except (ValueError, OSError) as e:
            print("กราฟไม่ถูกต้อง: %s" % e, file=sys.stderr)
            return 2
    for s in args.set or []:
        m = re.match(r"^([^=]+)\.(prompt|expect|account|model|effort|difficulty|timeout|cwd)=(.*)$", s, re.S)
        if not m:
            print("--set ต้องเป็นรูป <งาน>.<field>=<ค่า>: %s" % s, file=sys.stderr)
            return 2
        overrides.setdefault(m.group(1), {})[m.group(2)] = m.group(3)
    info, ready, quotas = prepare(args, "graph", None)
    with locked(rd) as st:
        for a, i in info.items():
            st["accounts"][a] = {"ready": i.get("state") == "ready", "check": i.get("state"), "checked": i.get("ts")}
        if args.worker_token_budget:
            st["settings"]["worker_budget"] = parse_budget(args.worker_token_budget)
        st["quota"] = {}
        apply_quota_threshold(st, rd, quotas)
        new_nodes = [o for k, o in overrides.items() if k not in st["nodes"] and o.get("prompt")]
        rerun, revalid = [], []
        for nid in st["order"]:
            n = st["nodes"][nid]
            if n["status"] == "ok":
                continue
            ov = overrides.get(nid, {})
            prompt_changed = "prompt" in ov and ov["prompt"] != n.get("prompt")
            for k in ("prompt", "expect", "account", "model", "effort", "difficulty", "timeout", "cwd",
                      "review_prompt", "max_rounds", "reviewer"):
                if k in ov:
                    n[k] = int(ov[k]) if k in ("difficulty", "timeout", "max_rounds") else ov[k]
            outf = os.path.join(rd, "out", nid + ".md")
            if n["status"] == "bad_format" and not prompt_changed and os.path.isfile(outf):
                vok, val, why = validate(n.get("expect"), read_text(outf), n)
                if vok:
                    n.update(status="ok", value=val, error=None, revalidated=now_iso())
                    revalid.append(nid)
                    continue
            n.update(status="pending", error=None, assigned=None)
            acct, reason, pinned = plan(st, n)
            n["planned"], n["route"], n["pinned"] = acct, reason, pinned
            rerun.append(nid)
        if new_nodes:
            add_nodes(st, new_nodes)
        st["status"] = "running"
    log("resume %s · ตรวจรูปแบบใหม่ผ่านโดยไม่เรียกซ้ำ: %s · รันใหม่: %s" % (
        os.path.basename(rd), ", ".join(revalid) or "-", ", ".join(rerun) or "-"))
    return finish_run(args, rd)


def cmd_approve(args):
    rd = resolve_run(args.run)
    if not rd:
        print("ไม่พบ run", file=sys.stderr)
        return 2
    st = read_state(rd)
    if args.node not in st.get("nodes", {}):
        print("ไม่มีงาน %s ใน run %s" % (args.node, st.get("run_id")), file=sys.stderr)
        return 2
    write_text(os.path.join(rd, "approvals", args.node), "approved %s by %s\n" % (now_iso(), args.by))
    board_append(rd, args.by, "อนุมัติงาน %s" % args.node)
    print("อนุมัติ %s แล้ว (%s) · ถ้า run หยุดอยู่ให้รัน: python3 %s run --resume %s" % (
        args.node, os.path.join(rd, "approvals", args.node), TEAM_PY, st["run_id"]))
    return 0


def account_status_rows(st, refresh=False):
    accs = sorted(st.get("accounts", {}).keys(), key=lambda a: (side(a), int(re.sub(r"\D", "", a) or 0)))
    leader = (st.get("leader") or {}).get("account")
    past = {h.get("from") for h in st.get("lead_history", [])}
    thr = st.get("settings", {}).get("quota_threshold", 80)
    rows = []
    for a in accs:
        info = st["accounts"][a]
        running = [i for i in st["order"] if st["nodes"][i]["status"] == "running" and st["nodes"][i].get("assigned") == a]
        queued = [i for i in st["order"] if st["nodes"][i]["status"] in ("pending", "waiting_approval")
                  and st["nodes"][i].get("planned") == a]
        q = get_quota(a) if (refresh and info.get("ready")) else cached_quota(a)
        pct = Y.quota_pct(q) if q else None
        b = budget_of(st.get("settings", {}).get("worker_budget"), a)
        used = tokens_of(st, a)
        if not info.get("ready") or info.get("unavailable"):
            stt = "ใช้ไม่ได้ (%s)" % (info.get("unavailable") or Y.STATE_TH.get(info.get("check"), info.get("check")))
        elif info.get("stopped"):
            stt = "หยุดรับงาน (%s)" % info.get("stop_reason")
        elif (pct is not None and pct >= thr - 20) or (b and used >= 0.8 * b):
            stt = "ใกล้หมด"
        else:
            stt = "พร้อม"
        role = "หัวหน้า" if a == leader and st.get("status") == "running" else \
            ("อดีตหัวหน้า" if a in past else "ลูกทีม")
        rows.append({"account": a, "role": role, "running": running, "queued": queued, "tokens": used,
                     "budget": b, "quota": quota_text(q), "status": stt})
    return rows


def cmd_status(args):
    rd = resolve_run(args.run)
    if not rd:
        print("ยังไม่มี run%s (เริ่มด้วย team.py run <graph.json> หรือ team.py lead --demo)" %
              ((" ชื่อ " + args.run) if args.run else ""))
        return 0
    st = read_state(rd)
    rows = account_status_rows(st, refresh=args.refresh)
    if args.json:
        print(json.dumps({"run_id": st["run_id"], "status": st.get("status"), "accounts": rows,
                          "nodes": [node_row(st, i) for i in st["order"]],
                          "leader": st.get("leader"), "lead_history": st.get("lead_history")},
                         ensure_ascii=False, indent=1))
        return 0
    print("run %s · โหมด %s · สถานะ %s · %s" % (st["run_id"], st.get("mode"), STATUS_TH.get(st.get("status"), st.get("status")), rd))
    if st.get("goal"):
        print("เป้าหมาย: %s" % st["goal"])
    print("\n| บัญชี | บทบาท | งานที่รัน | งานในคิว | tokens ที่ใช้ใน run | โควตาล่าสุด (เวลาของข้อมูล) | สถานะ |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s | %s | %d%s | %s | %s |" % (
            r["account"], r["role"], ",".join(r["running"]) or "-", ",".join(r["queued"]) or "-", r["tokens"],
            (" / งบ %d" % r["budget"]) if r["budget"] is not None else "", r["quota"], r["status"]))
    if not args.brief:
        print("\n| งาน | บัญชี | สถานะ | ค่า/หมายเหตุ |\n|---|---|---|---|")
        for i in st["order"]:
            r = node_row(st, i)
            v = r["value"] if r["status"] == "ok" else r["note"]
            print("| %s | %s | %s | %s |" % (i, r["accounts"], STATUS_TH.get(r["status"], r["status"]), (v or "")[:70]))
    else:
        for i in st["order"]:
            r = node_row(st, i)
            print("- %s: %s (%s)%s" % (i, STATUS_TH.get(r["status"]), r["accounts"],
                                       (" ค่า=" + r["value"][:50]) if r["status"] == "ok" and r["value"] and len(r["value"]) < 50 else ""))
    return 0


def read_ledger(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for ln in f:
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return rows


def agg(rows, key):
    out = collections.OrderedDict()
    for r in rows:
        k = key(r)
        a = out.setdefault(k, collections.Counter())
        a["calls"] += 1
        a["ok"] += 1 if r.get("status") == "ok" else 0
        a["fail"] += 0 if r.get("status") == "ok" else 1
        for f in ("input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens"):
            a[f] += int(r.get(f) or 0)
        a["cost_usd"] += float(r.get("cost_usd") or 0)
        a["duration_s"] += float(r.get("duration_s") or 0)
    return out


def cmd_stats(args):
    if args.run:
        rd = resolve_run(args.run)
        if not rd:
            print("ไม่พบ run %s" % args.run)
            return 0
        path = os.path.join(rd, "ledger.jsonl")
    else:
        path = os.path.join(ROOT, "ledger.jsonl")
    rows = [r for r in read_ledger(path) if r.get("cli") and r.get("event") not in ("worker_switch", "lead_switch")]
    if args.event:
        rows = [r for r in rows if r.get("event") in args.event.split(",")]
    if args.since:
        rows = [r for r in rows if (r.get("ts_start") or "") >= args.since]
    if not rows:
        print("ยังไม่มีสถิติใน %s" % path)
        return 0
    groups = [("บัญชี", agg(rows, lambda r: r.get("account"))),
              ("รุ่น", agg(rows, lambda r: "%s/%s" % (r.get("cli"), r.get("model")))),
              ("run", agg(rows, lambda r: r.get("run_id") or "(ไม่มี run)")),
              ("ชนิดการเรียก", agg(rows, lambda r: r.get("event") or "call"))]
    tot = agg(rows, lambda r: "รวม")["รวม"]
    if args.json:
        print(json.dumps({"ledger": path, "rows": len(rows),
                          "by": {g: {k: dict(v) for k, v in d.items()} for g, d in groups},
                          "total": dict(tot)}, ensure_ascii=False, indent=1))
        return 0
    print("สถิติจาก %s (%d แถว)" % (path, len(rows)))
    for title, d in groups:
        print("\n### ตาม%s\n| %s | ครั้ง | สำเร็จ | ล้ม | input | cached | cache write | output | reasoning | ค่าใช้จ่ายตามรายการ ($) | เวลารวม (s) | เฉลี่ย (s) |" % (title, title))
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for k, a in list(d.items()) + [("**รวม**", tot)]:
            print("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %.4f | %.1f | %.1f |" % (
                k, a["calls"], a["ok"], a["fail"], a["input_tokens"], a["cached_input_tokens"],
                a["cache_write_tokens"], a["output_tokens"], a["reasoning_tokens"], a["cost_usd"],
                a["duration_s"], a["duration_s"] / max(1, a["calls"])))
    print("\n(ค่าใช้จ่ายเป็นราคาตามรายการของ Claude ไม่ใช่ยอดจ่ายจริง · Codex ไม่มีข้อมูลราคา)")
    return 0


def cmd_board(args):
    rd = resolve_run(args.run)
    if not rd:
        print("ยังไม่มี run")
        return 0
    if args.add:
        board_append(rd, args.author, args.add)
    print(read_text(board_path(rd)))
    return 0


# ================================================================ leader mode
def lead_env():
    return os.environ.get("MA_RUN_DIR"), os.environ.get("MA_LEAD_ACCOUNT")


def lead_over_budget(st):
    ld = st.get("leader") or {}
    b = budget_of(st["settings"].get("lead_budget"), ld.get("account"))
    if b is not None and int(ld.get("tokens") or 0) > b:
        return "งบโทเค็นหัวหน้า %s ใช้ %d > งบ %d" % (ld.get("account"), ld.get("tokens"), b)
    mx = st["settings"].get("max_dispatch_per_episode")
    if mx and int(ld.get("dispatches") or 0) >= mx:
        return "ครบจำนวนการแจกงานต่อรอบ (%d)" % mx
    return None


OVER_MSG = ("⚠ งบหัวหน้าหมด (%s): ส่งไม้ต่อเดี๋ยวนี้ - รัน checkpoint (บอกสิ่งที่ทำแล้วและขั้นต่อไป) "
            "แล้วจบรอบทันที ห้ามสั่งงานเพิ่ม")


def _leader_run(args):
    rd = resolve_run(args.run) if args.run else (lead_env()[0] or resolve_run(None))
    if not rd:
        print("ไม่พบ run (ใส่ --run <run_id>)")
        return None
    return rd


def heartbeat(st):
    if st.get("leader"):
        st["leader"]["heartbeat"] = time.time()


def cmd_dispatch(args):
    rd = _leader_run(args)
    if not rd:
        return 2
    tasks = []
    if args.tasks_file:
        try:
            with open(args.tasks_file, encoding="utf-8-sig") as f:
                tasks = json.load(f)
            if isinstance(tasks, dict):
                tasks = tasks.get("tasks") or tasks.get("nodes") or []
        except (OSError, ValueError) as e:
            print("อ่าน --tasks-file ไม่ได้: %s" % e)
            return 2
    if args.id:
        if not args.prompt:
            print("ต้องมี --prompt คู่กับ --id")
            return 2
        tasks.append({"id": args.id, "prompt": args.prompt, "expect": args.expect, "account": args.account,
                      "difficulty": args.difficulty, "kind": args.kind, "depends_on": args.depends_on.split(",") if args.depends_on else []})
    if not tasks:
        print("ไม่มีงานให้แจก (ใช้ --id/--prompt หรือ --tasks-file)")
        return 2
    crash = False
    with locked(rd) as st:
        heartbeat(st)
        over = lead_over_budget(st)
        if over:
            print(OVER_MSG % over)
            return 0
        known = set(st["nodes"])
        fresh, dup = [], []
        for t in tasks:
            t = {k: v for k, v in t.items() if v not in (None, "", [])}
            t["id"] = str(t["id"])
            if t["id"] in known:
                dup.append(t["id"])
                continue
            t.setdefault("difficulty", st["settings"].get("difficulty") or 2)
            t.setdefault("account", "any")
            fresh.append(t)
            known.add(t["id"])
        try:
            for t in fresh:
                for d in t.get("depends_on") or []:
                    if d not in known:
                        raise ValueError("งาน %s อ้างงานที่ไม่มี: %s" % (t["id"], d))
            fresh = normalize_nodes_partial(fresh, known)
        except ValueError as e:
            print("แจกงานไม่ได้: %s" % e)
            return 2
        add_nodes(st, fresh)
        ld = st.get("leader") or {}
        acct = ld.get("account") or "?"
        ld["dispatches"] = int(ld.get("dispatches") or 0) + len(fresh)
        for t in fresh:
            write_text(os.path.join(rd, "msgs", "%s__%s.md" % (acct, t["id"])),
                       "จาก หัวหน้า %s ถึง ลูกทีม (%s) · %s\n\n%s\n" % (acct, st["nodes"][t["id"]]["planned"], now_iso(), t["prompt"]))
        sim = st["settings"].get("simulate_crash")
        if sim and sim == acct and not st.get("sim_crash_done") and fresh:
            st["sim_crash_done"] = True
            crash = True
        pg = ld.get("pgid")
        lines = ["แจกแล้ว %d งาน: %s" % (len(fresh), ", ".join("%s→%s" % (t["id"], st["nodes"][t["id"]]["planned"]) for t in fresh))]
        if dup:
            lines.append("มีอยู่แล้ว (ไม่แจกซ้ำ): %s" % ", ".join(dup))
        over = lead_over_budget(st)
    print("\n".join(lines))
    if crash and pg:
        log("💥 จำลองหัวหน้า %s ล้มกะทันหันหลังแจกงาน (--simulate-crash)" % acct)
        sys.stdout.flush()
        try:
            os.killpg(int(pg), signal.SIGKILL)
        except Exception:
            pass
    if over:
        print(OVER_MSG % over)
    else:
        print("รอผลด้วย: python3 %s wait --run %s" % (TEAM_PY, os.path.basename(rd)))
    return 0


def normalize_nodes_partial(nodes, known):
    out = []
    for n in expand([coerce(dict(x)) for x in nodes]):
        deps = list(n.get("depends_on") or [])
        for p in placeholders(n.get("prompt", "")):
            if p not in deps:
                deps.append(p)
        n["depends_on"] = deps
        if n.get("kind") == "image":
            n.setdefault("expect", "png")
        out.append(n)
    ids = known | {n["id"] for n in out}
    for n in out:
        bad = [d for d in n["depends_on"] if d not in ids]
        if bad:
            raise ValueError("งาน %s อ้างงานที่ไม่มี: %s" % (n["id"], ", ".join(bad)))
    return out


def cmd_wait(args):
    rd = _leader_run(args)
    if not rd:
        return 2
    t0 = time.time()
    while True:
        with locked(rd) as st:
            heartbeat(st)
            over = lead_over_budget(st) if st.get("mode") == "lead" else None
            ids = args.ids.split(",") if args.ids else list(st["order"])
            missing = [i for i in ids if i not in st["nodes"]]
            sts = {i: st["nodes"][i]["status"] for i in ids if i in st["nodes"]}
            snap = {i: node_row(st, i) for i in sts}
        if missing:
            print("ไม่มีงาน: %s" % ", ".join(missing))
            return 2
        done = all(s in TERMINAL for s in sts.values())
        if done or over or time.time() - t0 > args.timeout:
            break
        time.sleep(2)
    for i, r in snap.items():
        v = r["value"] if r["status"] == "ok" else r["note"]
        print("- %s: %s (%s) %s · ผล: %s" % (i, STATUS_TH.get(r["status"], r["status"]), r["accounts"],
                                             (v or "")[:80].replace("\n", " "), os.path.join(rd, "out", i + ".md")))
    if over:
        print(OVER_MSG % over)
    elif not done:
        print("ยังไม่ครบ (หมดเวลารอ %ss) เรียก wait อีกครั้ง" % args.timeout)
    return 0


def cmd_combine(args):
    rd = _leader_run(args)
    if not rd:
        return 2
    st = read_state(rd)
    ids = args.ids.split(",")
    notok = [i for i in ids if st["nodes"].get(i, {}).get("status") != "ok"]
    if notok:
        print("รวมไม่ได้: งานยังไม่สำเร็จ %s (ใช้ wait ก่อน)" % ", ".join(notok))
        return 2
    parts = []
    if args.title:
        parts.append("# %s\n" % args.title)
    for i in ids:
        txt = read_text(os.path.join(rd, "out", i + ".md")).strip()
        parts.append(("## %s\n\n%s\n" % (i, txt)) if args.headings else txt + "\n")
    out = os.path.abspath(args.output or os.path.join(rd, "final.md"))
    write_text(out, "\n".join(parts))
    with locked(rd) as s2:
        heartbeat(s2)
        s2["combined"] = {"output": out, "ids": ids, "ts": now_iso()}
        over = lead_over_budget(s2) if s2.get("mode") == "lead" else None
    print("รวม %d งานเป็น %s (%d ตัวอักษร)" % (len(ids), out, sum(len(p) for p in parts)))
    if over:
        print(OVER_MSG % over)
    return 0


def write_handoff(rd, st, who, done, nxt, decisions):
    rows = ["- %s: %s%s" % (i, STATUS_TH.get(st["nodes"][i]["status"]), (" ค่า=" + (st["nodes"][i].get("value") or "")[:40])
            if st["nodes"][i]["status"] == "ok" else "") for i in st["order"]]
    txt = ("# handoff · run %s\nเขียนโดย %s · %s\n\n## เป้าหมาย\n%s\n\n## ทำไปแล้ว\n%s\n\n## งานทั้งหมดตอนนี้\n%s\n\n"
           "## ขั้นต่อไป\n%s\n\n## การตัดสินใจสำคัญ\n%s\n" % (
               st["run_id"], who, now_iso(), st.get("goal"), done or "-", "\n".join(rows) or "- (ยังไม่มีงาน)",
               nxt or "-", decisions or "-"))
    write_text(os.path.join(rd, "handoff.md"), txt)


def cmd_checkpoint(args):
    rd = _leader_run(args)
    if not rd:
        return 2
    with locked(rd) as st:
        heartbeat(st)
        who = (st.get("leader") or {}).get("account") or args.by
        write_handoff(rd, st, who, args.done, args.next, args.decisions)
        st.setdefault("checkpoints", []).append({"ts": now_iso(), "by": who})
        if st.get("leader"):
            st["leader"]["checkpointed"] = True
        over = lead_over_budget(st) if st.get("mode") == "lead" else None
    board_append(rd, who, "checkpoint: %s | ต่อไป: %s" % ((args.done or "-")[:120], (args.next or "-")[:120]))
    print("บันทึก checkpoint แล้ว: %s" % os.path.join(rd, "handoff.md"))
    if over:
        print("งบหัวหน้าหมด (%s): จบรอบได้เลย หัวหน้าคนถัดไปจะทำต่อจาก handoff.md" % over)
    return 0


def cmd_finish(args):
    rd = _leader_run(args)
    if not rd:
        return 2
    res = os.path.abspath(args.result) if args.result else None
    if res and not os.path.isfile(res):
        print("ไม่พบไฟล์ผลลัพธ์ %s" % res)
        return 2
    with locked(rd) as st:
        heartbeat(st)
        st["goal_done"] = {"ts": now_iso(), "by": (st.get("leader") or {}).get("account"), "result": res,
                           "summary": args.summary}
        write_handoff(rd, st, (st.get("leader") or {}).get("account") or "?", "งานเสร็จ: %s" % (args.summary or res),
                      "ไม่มี (จบแล้ว)", "-")
    print("บันทึกว่าเป้าหมายเสร็จแล้ว (ผล: %s) จบรอบได้เลย" % res)
    return 0


def leader_prompt(st, rd, acct, episode, out_path):
    t = "python3 " + TEAM_PY
    r = st["run_id"]
    handoff = read_text(os.path.join(rd, "handoff.md")).strip()
    tasks = "\n".join("- %s: %s (%s)" % (i, STATUS_TH.get(st["nodes"][i]["status"]), st["nodes"][i].get("planned") or "-")
                      for i in st["order"]) or "- (ยังไม่มีงาน)"
    ready = ", ".join(usable(st)) or "-"
    return ("คุณคือหัวหน้าทีม บัญชี %s รอบที่ %d ของ run %s\nเป้าหมาย: %s\n\n"
            "สถานะอยู่ในไฟล์ ไม่อยู่ในความจำ หัวหน้าคนก่อนอาจถูกสลับออก ทำต่อจาก handoff ด้านล่าง ห้ามแจกงานที่มี id อยู่แล้วซ้ำ\n"
            "งานในระบบตอนนี้:\n%s\nลูกทีมที่พร้อม: %s (ระบบเลือกบัญชีให้เองเมื่อใช้ account any)\n\n"
            "=== handoff.md ===\n%s\n=== จบ handoff ===\n\n"
            "คำสั่ง (รันด้วยเชลล์ แต่ละคำสั่งตอบเร็ว):\n"
            "1. แจกงานหลายชิ้นในคำสั่งเดียว: เขียนไฟล์ JSON รายการงาน [{\"id\":\"t1\",\"prompt\":\"<คำสั่งงานครบในตัว>\",\"expect\":\"text\",\"difficulty\":1}, ...] (difficulty เป็นตัวเลข 1-6) "
            "ลง %s/tmp/tasks.json แล้วรัน: %s dispatch --run %s --tasks-file %s/tmp/tasks.json\n"
            "   (หรือทีละงาน: %s dispatch --run %s --id t1 --prompt \"...\" [--expect int|number|text|json])\n"
            "2. รอผล: %s wait --run %s\n"
            "3. รวมผลเป็นไฟล์เดียว (สคริปต์ต่อไฟล์ให้ ไม่เสียโทเค็น): %s combine --run %s --ids t1,t2,... --output %s\n"
            "4. บันทึก checkpoint (ทำก่อนจบรอบทุกครั้ง): %s checkpoint --run %s --done \"...\" --next \"...\" --decisions \"...\"\n"
            "5. เมื่อไฟล์ผลรวมเสร็จ: %s finish --run %s --result %s --summary \"...\"\n\n"
            "กฎ: แบ่งเป้าหมายเป็นงานย่อยอิสระให้ลูกทีม (คุณไม่ทำงานเอง) · prompt ของงานย่อยต้องครบในตัวและสั่งรูปแบบคำตอบให้ชัด "
            "(งานคำนวณให้สั่งลูกทีมใช้เชลล์คำนวณ) · ถ้าคำสั่งใดตอบว่า \"งบหัวหน้าหมด\" ให้รัน checkpoint แล้วจบรอบทันที · "
            "ถ้างานใดล้ม ให้แจกงานใหม่ด้วย id ใหม่ · จบด้วยข้อความสั้น ๆ" % (
                acct, episode, r, st.get("goal"), tasks, ready, handoff or "(ยังไม่มี)",
                rd, t, r, rd, t, r, t, r, t, r, out_path, t, r, t, r, out_path))


def choose_successor(st, current, banned, succession, prefer_side):
    pool = [a for a in (succession or []) if a not in banned]
    ready = usable(st, exclude=banned)
    if pool:
        for a in pool:
            if a in ready:
                return a, "ตามรายชื่อสืบทอด"
    q = st.get("quota", {})
    cands = [a for a in ready if a != current]
    if not cands:
        return None, "ไม่มีบัญชีที่พร้อม"
    cands.sort(key=lambda a: (0 if side(a) == prefer_side else 1, q.get(a) if q.get(a) is not None else 50.0, a))
    return cands[0], "อัตโนมัติ: พร้อม โควตาเหลือมากสุด ฝั่งเดียวกันก่อน"


def verify_demo(path):
    txt = read_text(path)
    got = {}
    for a, b, c in re.findall(r"(\d+)\s*[x×*]\s*(\d+)\s*=\s*(\d+)", txt):
        got[(int(a), int(b))] = int(c)
    need = [(a, b) for a in range(2, 10) for b in range(1, 13)]
    ok = sum(1 for k in need if got.get(k) == k[0] * k[1])
    wrong = [k for k in need if k in got and got[k] != k[0] * k[1]]
    return ok, len(need), wrong


def cmd_lead(args):
    goal = args.goal or (DEMO_GOAL if args.demo else None)
    if not goal:
        print("ต้องมี --goal \"...\" หรือ --demo", file=sys.stderr)
        return 2
    info, ready, quotas = prepare(args, "lead", goal)
    excl = [x for x in (args.exclude or "").split(",") if x]
    leaders_pool = [a for a in ready if a not in excl]
    if not leaders_pool:
        print("ไม่มีบัญชีที่พร้อมเป็นหัวหน้า", file=sys.stderr)
        return 1
    succession = [x for x in (args.succession or "").split(",") if x]
    claude_first = sorted(leaders_pool, key=lambda a: (0 if side(a) == "claude" else 1,
                                                       quotas.get(a, {}).get("pct") or 0, a))
    first = (succession[0] if succession and succession[0] in leaders_pool else claude_first[0])
    lead_budget = parse_budget(args.lead_token_budget)
    worker_budget = parse_budget(args.worker_token_budget)
    sim_crash, sim_limit = args.simulate_crash, args.simulate_limit
    per_account = args.per_account
    difficulty = args.worker_difficulty
    demo_worker = None
    if args.demo:
        order = [first] + [a for a in claude_first if a != first]
        if not sim_crash:
            sim_crash = first
        second = order[1] if len(order) > 1 else None
        if second and not lead_budget:
            lead_budget = {second: 1}
        if not worker_budget:
            workers = [a for a in ready if a not in excl]
            wb = workers[-1] if workers else None
            if wb:
                worker_budget = {wb: 1}
                demo_worker = wb
        if per_account == 3:
            per_account = 1
        difficulty = difficulty or 1
        log("โหมดสาธิต: หัวหน้า %s ล้มกะทันหันหลังแจกงานครั้งแรก (เชิงรับ) · งบหัวหน้า %s · งบลูกทีม %s · "
            "per-account %d (งานเข้าคิวจึงย้ายได้)" % (sim_crash, json.dumps(lead_budget), json.dumps(worker_budget), per_account))
    rid, rd = new_run_dir("lead", goal, args.run_id)
    out_path = os.path.abspath(args.output or os.path.join(rd, "final.md"))
    settings = {"per_account": per_account, "max_parallel": args.max_parallel, "timeout": args.timeout,
                "worker_budget": worker_budget, "lead_budget": lead_budget, "quota_threshold": args.quota_threshold,
                "exclude": excl, "board": True, "difficulty": difficulty or 2, "simulate_crash": sim_crash,
                "max_dispatch_per_episode": args.max_dispatch_per_episode,
                "demo_worker": demo_worker}
    st0 = init_state(rid, rd, "lead", goal, settings, info, quotas)
    with locked(rd) as st:
        st.update(st0)
        apply_quota_threshold(st, rd, quotas)
        write_handoff(rd, st, "team.py (เริ่มต้น)", "-", "แบ่งเป้าหมายเป็นงานย่อยแล้วแจกให้ลูกทีม แล้วรวมผลเป็น %s" % out_path, "-")
    log("run %s (หัวหน้าทีม) · เป้าหมาย: %s" % (rid, goal))
    log("โฟลเดอร์ %s · ผลรวมจะอยู่ที่ %s" % (rd, out_path))
    env_sim = {}
    if sim_limit:
        os.environ["MA_SIMULATE_LIMIT"] = ",".join(x for x in [os.environ.get("MA_SIMULATE_LIMIT"), sim_limit] if x)
        log("จำลอง: บัญชี %s ล้มเหมือนโควตาหมดทุกครั้งที่เรียก (MA_SIMULATE_LIMIT)" % sim_limit)
    eng = Engine(rd, keep_alive=True)
    eth = threading.Thread(target=eng.loop, daemon=True)
    eth.start()
    leader, banned, episode = first, set(), 0
    t_start = time.time()
    while leader and episode < args.max_episodes:
        episode += 1
        with locked(rd) as st:
            st["leader"] = {"account": leader, "episode": episode, "started": now_iso(), "tokens": 0,
                            "dispatches": 0, "heartbeat": time.time(), "pgid": None, "checkpointed": False}
            prompt = leader_prompt(st, rd, leader, episode, out_path)
        log("👑 หัวหน้า %s เริ่มรอบที่ %d" % (leader, episode))
        outcome = run_leader_episode(args, rd, leader, episode, prompt, env_sim)
        with locked(rd) as st:
            ld = st.get("leader") or {}
            tokens = int(ld.get("tokens") or 0)
            done = bool(st.get("goal_done"))
            over = lead_over_budget(st)
            checkpointed = ld.get("checkpointed")
        r = outcome["result"]
        log("   รอบ %d ของ %s จบ: %s · tokens %d%s" % (episode, leader, outcome["how"], tokens,
                                                  (" · " + over) if over else ""))
        if done:
            break
        kind = reason = None
        if outcome["how"] in ("crash", "timeout", "stale") or not r["ok"]:
            kind = "เชิงรับ"
            reason = {"crash": "หัวหน้าหยุดกะทันหัน (process ถูก kill%s)" % (" · จำลอง --simulate-crash" if leader == sim_crash else ""),
                      "timeout": "รอบเกินเวลา %ss" % args.episode_timeout,
                      "stale": "heartbeat ไม่อัปเดตเกิน %ss" % args.heartbeat_timeout}.get(
                outcome["how"], "รอบล้ม: %s" % (r.get("error") or "")[:100])
            banned.add(leader)
        elif over:
            kind, reason = "เชิงรุก", over
            banned.add(leader)
        else:
            q = get_quota(leader)
            pct = q.get("pct")
            if pct is not None and pct >= args.quota_threshold:
                kind, reason = "เชิงรุก", "โควตา %s %g%% ≥ %g%%" % (leader, pct, args.quota_threshold)
                banned.add(leader)
        if not kind:
            continue  # หัวหน้าคนเดิมทำรอบต่อไป
        nxt, why = choose_successor(read_state(rd), leader, banned | set(excl), succession, side(leader))
        ev = {"ts": now_iso(), "from": leader, "to": nxt, "type": kind, "reason": reason, "episode": episode,
              "tokens": tokens, "checkpoint": bool(checkpointed), "choice": why}
        with locked(rd) as st:
            st["lead_history"].append(ev)
            if kind == "เชิงรับ" and not checkpointed:
                hf = os.path.join(rd, "handoff.md")
                with open(hf, "a", encoding="utf-8") as f:
                    f.write("\n## หมายเหตุจาก team.py (%s)\nหัวหน้า %s ล้มก่อนเขียน checkpoint: ย้อนไป checkpoint ล่าสุดด้านบน "
                            "และใช้รายการงานใน state.json เป็นหลัก (งานที่แจกไปแล้วยังรันอยู่ ไม่ต้องแจกซ้ำ)\n" % (now_iso(), leader))
        board_append(rd, "team.py", "สลับหัวหน้า%s %s → %s: %s" % (kind, leader, nxt or "-", reason))
        ledger_event(rd, read_state(rd), "lead_switch", account=nxt, error=reason[:160],
                     **{"from": leader, "switch_type": kind})
        log("🔁 สลับหัวหน้า%s: %s → %s (%s)" % (kind, leader, nxt or "-", reason))
        leader = nxt
    # รอให้งานลูกทีมที่ค้างจบ
    log("รองานลูกทีมที่ค้างให้จบ ...")
    t1 = time.time()
    while time.time() - t1 < args.timeout:
        st = read_state(rd)
        if all(st["nodes"][i]["status"] in TERMINAL or st["nodes"][i]["status"] == "waiting_approval" for i in st["order"]):
            break
        time.sleep(1)
    eng.stop.set()
    with locked(rd) as st:
        st["status"] = "done" if st.get("goal_done") and all(
            st["nodes"][i]["status"] == "ok" for i in st["order"]) else "failed"
        if st.get("leader"):
            st["leader"]["ended"] = now_iso()
        final = json.loads(json.dumps(st))
    quotas = final_quotas(final)
    print_lead_summary(final, rd, quotas, out_path, goal == DEMO_GOAL, time.time() - t_start, args.json)
    return 0 if final["status"] == "done" else 1


def run_leader_episode(args, rd, leader, episode, prompt, env_sim):
    holder = {"p": None}
    seen_msgs = set()
    state_box = {"tokens": 0, "last": time.time()}

    def popen_cb(p):
        holder["p"] = p
        with locked(rd) as st:
            st["leader"]["pgid"] = p.pid

    def on_event(ev):
        state_box["last"] = time.time()
        if ev.get("type") == "assistant":
            msg = ev.get("message") or {}
            mid = msg.get("id")
            u = msg.get("usage") or {}
            if mid and mid not in seen_msgs:
                seen_msgs.add(mid)
                state_box["tokens"] += int(u.get("input_tokens") or 0) + int(u.get("cache_read_input_tokens") or 0) + \
                    int(u.get("cache_creation_input_tokens") or 0) + int(u.get("output_tokens") or 0)
                with locked(rd) as st:
                    st["leader"]["tokens"] = state_box["tokens"]
                    st["leader"]["heartbeat"] = time.time()

    env = {"MA_RUN_DIR": rd, "MA_LEAD_ACCOUNT": leader}
    env.update(env_sim)
    how = {"v": "normal"}
    stop = threading.Event()

    def watchdog():
        t0 = time.time()
        over_since = None
        while not stop.wait(1.0):
            p = holder["p"]
            if not p:
                continue
            st = read_state(rd)
            hb = max(state_box["last"], float((st.get("leader") or {}).get("heartbeat") or 0))
            if time.time() - t0 > args.episode_timeout:
                how["v"] = "timeout"
                Y._kill(p)
                return
            if time.time() - hb > args.heartbeat_timeout:
                how["v"] = "stale"
                Y._kill(p)
                return
            if lead_over_budget(st):
                over_since = over_since or time.time()
                if time.time() - over_since > args.over_budget_grace:
                    how["v"] = "forced"
                    Y._kill(p)
                    return
    wd = threading.Thread(target=watchdog, daemon=True)
    wd.start()
    node = "_lead.e%d" % episode
    st = read_state(rd)
    if side(leader) == "claude":
        r = Y.call(leader, prompt, model=args.lead_model, effort=args.lead_effort, cwd=rd,
                   timeout=args.episode_timeout + 30, run_id=st["run_id"], node=node, run_dir=rd, event="lead",
                   stream_cb=on_event, popen_cb=popen_cb, env_extra=env)
    else:
        r = C.call(leader, prompt, effort=args.lead_effort_codex, cwd=rd, timeout=args.episode_timeout + 30,
                   run_id=st["run_id"], node=node, run_dir=rd, event="lead", popen_cb=popen_cb, env_extra=env,
                   stream_cb=lambda ev: state_box.__setitem__("last", time.time()))
    stop.set()
    p = holder["p"]
    if how["v"] == "normal" and p is not None and p.returncode is not None and p.returncode < 0:
        how["v"] = "crash"
    with locked(rd) as st2:
        tok = r["input_tokens"] + r["output_tokens"]
        if tok > int(st2["leader"].get("tokens") or 0):
            st2["leader"]["tokens"] = tok
        st2["leader"]["ended"] = now_iso()
        st2["leader"]["outcome"] = how["v"]
        if how["v"] == "forced":
            how["v"] = "normal"
    return {"how": how["v"], "result": r}


def print_lead_summary(st, rd, quotas, out_path, is_demo_goal, elapsed, as_json):
    stats = agg([r for r in read_ledger(os.path.join(rd, "ledger.jsonl"))
                 if r.get("cli") and r.get("event") not in ("worker_switch", "lead_switch")],
                lambda r: r.get("account"))
    roles = {}
    for r in read_ledger(os.path.join(rd, "ledger.jsonl")):
        if r.get("cli"):
            roles.setdefault(r["account"], set()).add({"lead": "หัวหน้า", "check": "ตรวจความพร้อม"}.get(r.get("event"), "ลูกทีม"))
    verify = verify_demo(out_path) if (is_demo_goal and os.path.isfile(out_path)) else None
    if as_json:
        d = summary_data(st, quotas)
        d.update(stats_by_account={k: dict(v) for k, v in stats.items()}, output=out_path,
                 elapsed_s=round(elapsed, 1), verify=verify and {"ok": verify[0], "total": verify[1]})
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return
    print("\n## สรุปงานหัวหน้าทีม run %s (%s · %.0f วินาที)" % (st["run_id"], STATUS_TH.get(st["status"], st["status"]), elapsed))
    print("เป้าหมาย: %s" % st.get("goal"))
    print("\n### ประวัติการสลับหัวหน้า\n| # | จาก | ไป | ชนิด | เหตุผล | checkpoint ก่อนสลับ |\n|---|---|---|---|---|---|")
    for i, h in enumerate(st.get("lead_history", []), 1):
        print("| %d | %s | %s | %s | %s | %s |" % (i, h["from"], h["to"] or "-", h["type"], h["reason"],
                                                 "มี" if h.get("checkpoint") else "ไม่มี (ใช้ state.json)"))
    if not st.get("lead_history"):
        print("| - | - | - | - | ไม่มีการสลับ | - |")
    gd = st.get("goal_done") or {}
    print("หัวหน้าที่ปิดงาน: %s" % (gd.get("by") or "-"))
    print("\n### การย้ายงานลูกทีม\n| งาน | จาก | ไป | เหตุผล |\n|---|---|---|---|")
    for w in st.get("worker_switches", []):
        print("| %s | %s | %s | %s |" % (w["node"], w["from"], w["to"] or "-", w["reason"]))
    if not st.get("worker_switches"):
        print("| - | - | - | ไม่มีการย้าย |")
    d = summary_data(st, quotas)
    print("\n### ผลของแต่ละงาน\n| งาน | บัญชี | รุ่น/effort | เวลา (s) | input tokens | output tokens | สถานะ | ค่า/หมายเหตุ |")
    print("|---|---|---|---|---|---|---|---|")
    for r in d["nodes"]:
        v = r["value"] if r["status"] == "ok" else r["note"]
        print("| %s | %s | %s | %.1f | %d | %d | %s | %s |" % (r["node"], r["accounts"], r["model_effort"], r["duration_s"],
              r["input_tokens"], r["output_tokens"], STATUS_TH.get(r["status"], r["status"]),
              (v or "").replace("\n", " ").replace("|", "/")[:50]))
    print("\n### สถิติแยกตามบัญชี (จาก ledger ของ run)\n| บัญชี | บทบาท | ครั้ง | สำเร็จ/ล้ม | input | output | ค่าใช้จ่ายตามรายการ ($) | เวลารวม (s) | โควตาล่าสุด |")
    print("|---|---|---|---|---|---|---|---|---|")
    for a, s in stats.items():
        print("| %s | %s | %d | %d/%d | %d | %d | %.4f | %.1f | %s |" % (
            a, ",".join(sorted(roles.get(a, []))), s["calls"], s["ok"], s["fail"], s["input_tokens"], s["output_tokens"],
            s["cost_usd"], s["duration_s"], quota_text(quotas.get(a))))
    print("\nไฟล์ผลรวม: %s%s" % (out_path, "" if os.path.isfile(out_path) else " (ยังไม่มี)"))
    if verify:
        print("ตรวจผลอิสระ (คำนวณ a×b เอง): ถูก %d/%d บรรทัด%s" % (verify[0], verify[1],
              (" · ผิด: %s" % verify[2][:5]) if verify[2] else ""))
    print("state: %s/state.json · handoff: %s/handoff.md · board: %s/board.md" % (rd, rd, rd))


# ================================================================ main
def add_run_opts(p):
    p.add_argument("--per-account", type=int, default=3, help="งานพร้อมกันต่อบัญชี (ค่าเริ่มต้น 3)")
    p.add_argument("--max-parallel", type=int, default=8, help="งานพร้อมกันรวม (ค่าเริ่มต้น 8)")
    p.add_argument("--timeout", type=int, default=600, help="timeout ต่องาน วินาที (ค่าเริ่มต้น 600)")
    p.add_argument("--worker-token-budget", action="append",
                   help="งบโทเค็นลูกทีมใน run: N (ทุกบัญชี) หรือ บัญชี=N เช่น yolo2=30000 · เกินแล้วหยุดรับงานใหม่")
    p.add_argument("--quota-threshold", type=float, default=80, help="โควตา ≥ ค่านี้ (%%) หยุดรับงานใหม่ (ค่าเริ่มต้น 80)")
    p.add_argument("--exclude", help="บัญชีที่ห้ามใช้ คั่นด้วย ,")
    p.add_argument("--recheck", action="store_true", help="ตรวจความพร้อมใหม่ทุกบัญชี (ไม่ใช้ผลภายใน 15 นาที)")
    p.add_argument("--run-id", help="ตั้งชื่อ run เอง")
    p.add_argument("--json", action="store_true", help="พิมพ์สรุปเป็น JSON (ความคืบหน้าไป stderr)")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="team.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("check", help="ตรวจความพร้อมทุกบัญชีด้วยการเรียกจริง")
    p.add_argument("accounts", nargs="*")
    p.add_argument("--cached", action="store_true", help="ใช้ผลที่ตรวจภายใน 15 นาที")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("quota", help="โควตาล่าสุด (Claude: /usage · Codex: rate_limits) พร้อมเวลาของข้อมูล")
    p.add_argument("accounts", nargs="*")
    p.add_argument("--refresh", action="store_true", help="Codex: เรียกสั้น 1 ครั้งแบบไม่ ephemeral เพื่ออัปเดต")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_quota)

    p = sub.add_parser("run", help="รันกราฟงานจากไฟล์ JSON (หรือ - = stdin)")
    p.add_argument("graph", nargs="?")
    p.add_argument("--resume", metavar="RUN_ID", help="รันต่อ: งานที่สำเร็จไม่รันซ้ำ รันเฉพาะงานที่ล้ม/ถูกบล็อก")
    p.add_argument("--set", action="append", metavar="งาน.field=ค่า", help="แก้ prompt/expect/... ของงานก่อน resume")
    p.add_argument("--wait-approval", type=int, default=0, metavar="S",
                   help="รอไฟล์อนุมัตินานสุด S วินาที (0 = หยุดแล้วให้ resume ภายหลัง)")
    p.add_argument("--difficulty", type=int, help="ความยากเริ่มต้นของงานที่ไม่ระบุ (ค่าเริ่มต้น 2)")
    add_run_opts(p)
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("status", help="ภาพรวม run สำหรับหัวหน้าทีม")
    p.add_argument("--run")
    p.add_argument("--refresh", action="store_true", help="อ่านโควตาใหม่")
    p.add_argument("--brief", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("stats", help="สถิติจาก ledger ตามบัญชี/รุ่น/run")
    p.add_argument("--run", help="เฉพาะ run นี้")
    p.add_argument("--event", help="กรองชนิด เช่น call หรือ call,lead")
    p.add_argument("--since", help="ตั้งแต่เวลา ISO เช่น 2026-11-08T10:00")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_stats)

    p = sub.add_parser("approve", help="อนุมัติงานที่มี approve: true")
    p.add_argument("node")
    p.add_argument("--run")
    p.add_argument("--by", default="human")
    p.set_defaults(fn=cmd_approve)

    p = sub.add_parser("board", help="อ่าน/เพิ่มข้อค้นพบบน board.md")
    p.add_argument("--run")
    p.add_argument("--add")
    p.add_argument("--author", default="human")
    p.set_defaults(fn=cmd_board)

    p = sub.add_parser("lead", help="หัวหน้าทีมเป็นรอบสั้น + สลับหัวหน้า/ย้ายงานลูกทีมอัตโนมัติ",
                       description="รัน foreground พิมพ์ความคืบหน้าทีละบรรทัด จบด้วยตารางสรุป · "
                                   "--demo = เปิดตัวจำลองครบชุด (หัวหน้าคนแรกล้มหลังแจกงาน, งบหัวหน้าคนที่สอง=1, "
                                   "งบลูกทีมหนึ่งคน=1, per-account 1) ใช้กับ --goal ของตัวเองได้")
    p.add_argument("--goal", help="เป้าหมาย (ไม่ใส่ + --demo = ตารางสูตรคูณแม่ 2-9)")
    p.add_argument("--demo", action="store_true", help="สาธิต: เกิดสลับหัวหน้าเชิงรับ + เชิงรุก + ย้ายงานลูกทีม ในรันเดียว")
    p.add_argument("--output", help="ไฟล์ผลรวม (ค่าเริ่มต้น <run>/final.md)")
    p.add_argument("--lead-model", default="sonnet", choices=Y.MODELS, help="รุ่นของหัวหน้าฝั่ง Claude (ค่าเริ่มต้น sonnet)")
    p.add_argument("--lead-effort", default="low", choices=Y.EFFORTS)
    p.add_argument("--lead-effort-codex", default="low", choices=C.LEVELS)
    p.add_argument("--succession", help="รายชื่อหัวหน้าตามลำดับ เช่น yolo1,yolo2,cyolo1")
    p.add_argument("--lead-token-budget", action="append", help="งบโทเค็นต่อหัวหน้า: N หรือ บัญชี=N (ตรวจระหว่างรอบ)")
    p.add_argument("--max-dispatch-per-episode", type=int, default=0, help="จำกัดจำนวนงานที่แจกต่อรอบ (0 = ไม่จำกัด)")
    p.add_argument("--simulate-crash", metavar="บัญชี", help="จำลองหัวหน้าบัญชีนี้ล้มกะทันหันหลังแจกงานครั้งแรก")
    p.add_argument("--simulate-limit", metavar="บัญชี", help="จำลองบัญชีนี้โควตาหมด (= MA_SIMULATE_LIMIT) ทั้งหัวหน้าและลูกทีม")
    p.add_argument("--worker-difficulty", type=int, help="ความยากเริ่มต้นของงานลูกทีม (ค่าเริ่มต้น 2, demo 1)")
    p.add_argument("--episode-timeout", type=int, default=900)
    p.add_argument("--heartbeat-timeout", type=int, default=420)
    p.add_argument("--over-budget-grace", type=int, default=120, help="วินาทีที่ให้หัวหน้าเขียน checkpoint หลังงบหมด")
    p.add_argument("--max-episodes", type=int, default=8)
    add_run_opts(p)
    p.set_defaults(fn=cmd_lead)

    p = sub.add_parser("dispatch", help="(หัวหน้า) แจกงานให้ลูกทีม")
    p.add_argument("--run")
    p.add_argument("--id")
    p.add_argument("--prompt")
    p.add_argument("--expect")
    p.add_argument("--account")
    p.add_argument("--difficulty", type=int)
    p.add_argument("--kind")
    p.add_argument("--depends-on")
    p.add_argument("--tasks-file", help="ไฟล์ JSON รายการงาน [{id, prompt, expect?, account?, difficulty?, depends_on?}]")
    p.set_defaults(fn=cmd_dispatch)

    p = sub.add_parser("wait", help="(หัวหน้า) รอผลงาน")
    p.add_argument("--run")
    p.add_argument("--ids")
    p.add_argument("--timeout", type=int, default=300)
    p.set_defaults(fn=cmd_wait)

    p = sub.add_parser("combine", help="(หัวหน้า) รวม out/<id>.md เป็นไฟล์เดียว (ไม่เสียโทเค็น)")
    p.add_argument("--run")
    p.add_argument("--ids", required=True)
    p.add_argument("--output")
    p.add_argument("--title")
    p.add_argument("--headings", action="store_true", help="ใส่หัวข้อ ## <id> ก่อนแต่ละส่วน")
    p.set_defaults(fn=cmd_combine)

    p = sub.add_parser("checkpoint", help="(หัวหน้า) เขียน handoff.md สำหรับหัวหน้าคนถัดไป")
    p.add_argument("--run")
    p.add_argument("--done")
    p.add_argument("--next")
    p.add_argument("--decisions")
    p.add_argument("--by", default="leader")
    p.set_defaults(fn=cmd_checkpoint)

    p = sub.add_parser("finish", help="(หัวหน้า) บันทึกว่าเป้าหมายเสร็จ")
    p.add_argument("--run")
    p.add_argument("--result")
    p.add_argument("--summary")
    p.set_defaults(fn=cmd_finish)

    args = ap.parse_args(argv)
    if not getattr(args, "fn", None):
        ap.print_help()
        return 0
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
