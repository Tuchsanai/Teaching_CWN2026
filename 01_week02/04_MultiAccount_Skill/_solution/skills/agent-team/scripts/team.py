#!/usr/bin/env python3
"""team.py - multi-agent teamwork across Claude (yoloN) and Codex (cyoloN) accounts.

Run a task graph (relay, fan-out/fan-in, DAG, review loop, board, debate, best-of-N, router,
failover, human gate) or a self-healing leader. Everything lives in the run directory
/workspace/.agent-team/<run_id>/ (graph.json, state.json, board.md, handoff.md, msgs/, out/,
ledger.jsonl) so a new leader or a human can pick up at any time.

  team.py run GRAPH.json|- [--run ID] [--detach] [options]   run a graph to the end
  team.py status [--run ID]            accounts | role | running | queued | tokens | quota | state
  team.py stats  [--run ID] [--json]   totals by account / model / run from the ledger
  team.py quota  [ACCOUNT ...]         latest quota of every account, with the time of the data
  team.py check  [ACCOUNT ...] [--recheck]   readiness by a real call (cached 10 min)
  team.py approve NODE --run ID        open a human gate
  team.py note "TEXT" --run ID [--by X]       append to board.md
  team.py lead --goal "..." [options]  supervisor: leader episodes + leader handoff
  leader tools: add / dispatch / wait / checkpoint / finish  (see references/leader.md)

Options of run/lead: --accounts a,b  --per-account 3  --max 8  --timeout 600
  --worker-token-budget N|acct=N,...  --quota-threshold 80  --recheck
"""
import argparse
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait as fwait

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
for _d in ("cyolo", "yolo"):
    sys.path.insert(0, os.path.join(SKILLS, _d, "scripts"))
import macore as M  # noqa: E402
import yolo as Y  # noqa: E402
import cyolo as C  # noqa: E402

TEAM = os.path.realpath(__file__)
TERMINAL = ("done", "failed", "blocked")
ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
TPL_RE = re.compile(r"\{\{(file:)?([A-Za-z0-9_.-]+)\}\}")
SHORT_LIMIT = 2000           # {{node}} longer than this must go through {{file:node}}
OPTS = {"per_account": 3, "max_total": 8, "timeout": 600, "quota_threshold": 80.0,
        "worker_token_budget": {}, "gate_timeout": 3600, "accounts": None}


# =============================================================== run directory
class Run:
    def __init__(self, run_id):
        if not ID_RE.match(run_id or ""):
            raise SystemExit(f"run id ไม่ถูกต้อง: {run_id!r}")
        self.id = run_id
        self.dir = os.path.join(M.TEAM_DIR, run_id)

    def p(self, *parts):
        return os.path.join(self.dir, *parts)

    def exists(self):
        return os.path.isfile(self.p("state.json"))

    def read(self):
        with open(self.p("state.json"), encoding="utf-8") as f:
            return json.load(f)

    @contextlib.contextmanager
    def tx(self):
        """Exclusive read-modify-write of state.json (threads and processes)."""
        with open(self.p(".lock"), "a") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            st = self.read()
            yield st
            st["updated"] = M.now_iso()
            tmp = self.p("state.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(st, f, ensure_ascii=False, indent=1)
            os.replace(tmp, self.p("state.json"))

    def board(self, by, text):
        with open(self.p("board.md"), "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(f"- [{M.now_iso()[11:19]}] **{by}**: {text.strip()}\n")

    def board_text(self):
        try:
            with open(self.p("board.md"), encoding="utf-8") as f:
                return f.read()
        except OSError:
            return ""

    def msg(self, frm, to, text, append=False):
        with open(self.p("msgs", f"{frm}__{to}.md"), "a" if append else "w", encoding="utf-8") as f:
            f.write(text.rstrip() + "\n")

    def event(self, st, kind, text, **kw):
        """worker_switch / worker_pause / lead_switch ...: state.json + board.md + ledger."""
        ev = {"ts": M.now_iso(), "event": kind, "text": text, **kw}
        st.setdefault("events", []).append(ev)
        self.board("ระบบ", f"[{kind}] {text}")
        M.ledger_append({"ts_start": ev["ts"], "ts_end": ev["ts"], "run_id": self.id, **kw,
                         "event": kind, "error": text[:200]}, self.dir)


def new_run(run_id, goal, nodes, opts, mode):
    run = Run(run_id or time.strftime("%Y%m%d-%H%M%S") + f"-{os.getpid() % 1000:03d}")
    if run.exists():
        raise SystemExit(f"run {run.id} มีอยู่แล้ว")
    for d in ("msgs", "out", "approvals", "work"):
        os.makedirs(run.p(d), exist_ok=True)
    st = {"run_id": run.id, "goal": goal, "mode": mode, "created": M.now_iso(), "updated": None,
          "options": opts, "accounts": {}, "nodes": {}, "order": [], "events": [],
          "sched_pid": None, "lead": None, "final": None}
    for n in nodes:
        add_node(st, n)
    with open(run.p("state.json"), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    with open(run.p("graph.json"), "w", encoding="utf-8") as f:
        json.dump({"goal": goal, "nodes": nodes}, f, ensure_ascii=False, indent=1)
    with open(run.p("board.md"), "w", encoding="utf-8") as f:
        f.write(f"# board — run {run.id}\n\nกระดานความรู้กลาง: ทุก agent อ่านก่อนเริ่ม เพิ่มได้อย่างเดียว\n\n")
    write_handoff(run, st)
    return run


def latest_run():
    try:
        runs = [d for d in os.listdir(M.TEAM_DIR) if os.path.isfile(os.path.join(M.TEAM_DIR, d, "state.json"))]
    except OSError:
        runs = []
    if not runs:
        raise SystemExit("ยังไม่มี run")
    return Run(max(runs, key=lambda d: os.path.getmtime(os.path.join(M.TEAM_DIR, d, "state.json"))))


# =============================================================== nodes
def add_node(st, spec):
    n = dict(spec)
    nid = n.get("id")
    if not ID_RE.match(str(nid or "")):
        raise ValueError(f"node id ไม่ถูกต้อง: {nid!r}")
    if nid in st["nodes"]:
        raise ValueError(f"node {nid} มีอยู่แล้ว")
    n.setdefault("type", "task")
    if n["type"] not in ("task", "review", "debate", "best_of"):
        raise ValueError(f"{nid}: type ไม่รู้จัก {n['type']!r}")
    if not n.get("prompt"):
        raise ValueError(f"{nid}: ไม่มี prompt")
    n.setdefault("account", "any")
    acct = n["account"]
    if not (M.is_account(acct) or acct in ("yolo", "cyolo", "any")):
        raise ValueError(f"{nid}: account ต้องเป็น yoloN/cyoloN/yolo/cyolo/any")
    if n.get("image") and (acct == "yolo" or (M.is_account(acct) and M.side_of(acct) == "yolo")):
        raise ValueError(f"{nid}: งานภาพทำได้เฉพาะ cyolo")
    deps = list(n.get("depends_on") or [])
    for _, ref in TPL_RE.findall(n["prompt"]):          # a template reference implies a dependency
        if ref not in deps:
            deps.append(ref)
    for d in deps:
        if d not in st["nodes"]:
            raise ValueError(f"{nid}: depends_on {d!r} ไม่มีในกราฟ (ต้องประกาศก่อน)")
    n["depends_on"] = deps
    if n.get("difficulty") is not None and int(n["difficulty"]) not in range(1, 7):
        raise ValueError(f"{nid}: difficulty ต้องเป็น 1-6")
    n.update(status="pending", planned=None, assigned=None, attempts=[], value=None, error="",
             added=M.now_iso())
    st["nodes"][nid] = n
    st["order"].append(nid)
    return n


def pinned(n):
    return M.is_account(n["account"])


def bound_side(n):
    """Side a node is tied to: named account/side, image -> cyolo; None = free to cross."""
    a = n["account"]
    if M.is_account(a):
        return M.side_of(a)
    if a in ("yolo", "cyolo"):
        return a
    if n.get("image"):
        return "cyolo"
    return None


IMG_RE = re.compile(r"สร้างภาพ|วาดภาพ|รูปภาพ|image generation|generate an image|\.png\b", re.I)
REVIEW_RE = re.compile(r"ตรวจโค้ด|รีวิวโค้ด|review (the |this )?code|code review|หาบั๊ก|find bugs?", re.I)
DOC_RE = re.compile(r"เอกสารยาว|สรุปเอกสาร|สรุปรายงาน|long document|summari[sz]e (the |this )?document", re.I)


def route(st, n):
    """Router for account 'any': image -> cyolo, code review -> Codex, long document -> Claude,
    otherwise the side with more quota left. -> (side, reason)"""
    if n.get("image") or n.get("kind") == "image" or IMG_RE.search(n["prompt"]):
        return "cyolo", "งานภาพ → cyolo (สร้างภาพได้เฉพาะ Codex)"
    if n.get("kind") == "code_review" or REVIEW_RE.search(n["prompt"]):
        return "cyolo", "ตรวจโค้ด → Codex"
    big = any(os.path.getsize(f) > 20000 for f in re.findall(r"(/[^\s'\"]+)", n["prompt"])
              if os.path.isfile(f))
    if n.get("kind") == "long_doc" or DOC_RE.search(n["prompt"]) or big or len(n["prompt"]) > 4000:
        return "yolo", "เอกสารยาว → Claude"
    best = {}
    for s in M.SIDES:
        c = eligible(st, s)
        if c:
            best[s] = min(quota_pct(a) for a in c)
    if not best:
        return "yolo", "ไม่มีบัญชีพร้อม"
    s = min(best, key=lambda k: (best[k], k))
    return s, f"งานทั่วไป → ฝั่งที่โควตาเหลือมากกว่า ({s} ใช้ไป {best[s]:g}%)"


# =============================================================== accounts, quota, budgets
def readiness(accts, recheck=False, run_dir=None):
    cache = M.cache_load(M.READINESS_FILE)
    todo = [a for a in accts if recheck or M.age_s((cache.get(a) or {}).get("ts")) > 600]
    if todo:
        with ThreadPoolExecutor(len(todo)) as ex:
            for a, s in zip(todo, ex.map(lambda x: (Y if M.side_of(x) == "yolo" else C).check(x, run_dir), todo)):
                cache[a] = s
    return {a: cache[a] for a in accts}


def refresh_quota(accts, max_age=600):
    cache = M.cache_load(M.QUOTA_FILE)
    todo = [a for a in accts if M.age_s((cache.get(a) or {}).get("fetched")) > max_age]
    if todo:
        def one(a):
            q = Y.quota(a) if M.side_of(a) == "yolo" else C.quota(a)
            q["fetched"] = M.now_iso()
            M.cache_update(M.QUOTA_FILE, a, q)
        with ThreadPoolExecutor(len(todo)) as ex:
            list(ex.map(one, todo))


def quota_pct(acct):
    q = M.cache_load(M.QUOTA_FILE).get(acct) or {}
    return max([w["used_percent"] for w in q.get("windows") or []] or [0.0])


def quota_text(acct):
    q = M.cache_load(M.QUOTA_FILE).get(acct)
    return (Y if M.side_of(acct) == "yolo" else C).quota_text(q)


def run_tokens(run, role=None):
    """{account: tokens used in this run} from the run ledger (role filter: 'lead' / 'worker')."""
    out = {}
    for r in M.ledger_read(run.p("ledger.jsonl")):
        if r.get("event") != "call" or not r.get("account"):
            continue
        if role == "lead" and r.get("role") != "lead":
            continue
        if role == "worker" and r.get("role") in ("lead", "check"):   # budget = work, not probes
            continue
        out[r["account"]] = out.get(r["account"], 0) + M.tokens_used(r)
    return out


def budget_of(opts, acct):
    b = opts.get("worker_token_budget") or {}
    return b.get(acct, b.get("*"))


def eligible(st, side=None, paused_ok=False):
    out = []
    for a, s in st["accounts"].items():
        if side and M.side_of(a) != side:
            continue
        if s.get("ready") != "ready" or s.get("unavailable") or (s.get("paused") and not paused_ok):
            continue
        out.append(a)
    return out


def load(st, acct):
    return sum(1 for n in st["nodes"].values()
               if (n["status"] == "running" and n.get("assigned") == acct)
               or (n["status"] in ("pending", "waiting_approval") and n.get("planned") == acct))


def running_on(st, acct):
    return sum(1 for n in st["nodes"].values() if n["status"] == "running" and n.get("assigned") == acct)


def update_pauses(run, st):
    """Proactive switch: quota >= threshold or worker budget spent -> no new work for that account."""
    used = run_tokens(run, "worker")
    th = float(st["options"].get("quota_threshold") or 80)
    for a, s in st["accounts"].items():
        s["tokens"] = used.get(a, 0)
        if s.get("paused") or s.get("ready") != "ready":
            continue
        b = budget_of(st["options"], a)
        why = None
        if b is not None and s["tokens"] >= int(b):
            why = f"ใช้โทเค็นใน run นี้ {s['tokens']} ≥ งบ {b}"
        elif quota_pct(a) >= th:
            why = f"โควตา {quota_pct(a):g}% ≥ {th:g}%"
        if why:
            s["paused"] = why
            run.event(st, "worker_pause", f"{a} หยุดรับงานใหม่: {why} (งานที่รันอยู่ปล่อยให้จบ)", account=a)


def plan(run, st):
    """Give every waiting non-pinned node a planned account (balanced by quota, load, tokens).
    A node whose planned account is paused/unavailable moves - logged as worker_switch."""
    for nid in st["order"]:
        n = st["nodes"][nid]
        if n["status"] not in ("pending", "waiting_approval") or pinned(n):
            continue
        if n["account"] == "any" and not n.get("route"):
            side, why = route(st, n)
            n["route"] = {"side": side, "reason": why}
            run.board("router", f"{nid}: {why}")
        if n.get("planned") in eligible(st):
            continue
        side = bound_side(n) or n["route"]["side"]
        cands = eligible(st, side)
        crossed = False
        if not cands and not bound_side(n):
            cands, crossed = eligible(st, "cyolo" if side == "yolo" else "yolo"), True
        old = n.get("planned") or (n.get("moved_from") or {}).get("account")
        # score: queued/running jobs + quota used (every 25% used counts like one more queued job)
        new = min(cands, key=lambda a: (load(st, a) + quota_pct(a) / 25, st["accounts"][a].get("tokens", 0),
                                        a)) if cands else None
        if old and old != new:
            reason = (n.get("moved_from") or {}).get("reason") or \
                st["accounts"].get(old, {}).get("paused") or st["accounts"].get(old, {}).get("unavailable") or "ไม่พร้อม"
            run.event(st, "worker_switch", f"{nid}: ย้ายจาก {old} ไป {new or '— (ไม่มีบัญชีให้ย้าย)'}"
                      f"{' ข้ามฝั่ง' if crossed and new else ''} เพราะ {reason}", node=nid, account=old,
                      to=new)
        n["planned"] = new
        n.pop("moved_from", None)
        if new is None and n["status"] == "pending":
            n.update(status="failed", error=f"ไม่มีบัญชีที่พร้อมสำหรับฝั่ง {side}")


def choose(st, n):
    """-> (account or None, fail_reason or None). None/None = wait for a free slot."""
    cap = int(st["options"]["per_account"])
    if pinned(n):
        a, s = n["account"], st["accounts"].get(n["account"], {})
        if s.get("ready") != "ready" or s.get("unavailable") or s.get("paused"):
            why = s.get("unavailable") or s.get("paused") or M.READY_LABEL.get(s.get("ready"), "ไม่ได้ตรวจ")
            return None, f"บัญชีที่ผู้ใช้ระบุ ({a}) ใช้ไม่ได้: {why} — ไม่ย้ายอัตโนมัติ"
        return (a, None) if running_on(st, a) < cap else (None, None)
    a = n.get("planned")
    if not a:
        return None, None
    if running_on(st, a) < cap:
        return a, None
    side = M.side_of(a)
    free = [x for x in eligible(st, side) if running_on(st, x) < cap]   # plain load balancing
    if free:
        return min(free, key=lambda x: (load(st, x), x)), None
    return None, None


# =============================================================== templates, prompts, results
def render(run, st, nid, text):
    def sub(m):
        is_file, ref = m.group(1), m.group(2)
        dep = st["nodes"].get(ref)
        if not dep or dep["status"] != "done":
            raise ValueError(f"{{{{{ref}}}}} ยังไม่มีผล")
        if is_file:
            val = run.p("out", f"{ref}.md")
        else:
            val = str(dep["value"])
            if len(val) > SHORT_LIMIT:
                raise ValueError(f"ผลของ {ref} ยาว {len(val)} ตัวอักษร ใช้ {{{{file:{ref}}}}} แทน {{{{{ref}}}}}")
        run.msg(ref, nid, f"# จาก {ref} ({dep.get('assigned')}) ถึง {nid}\n\n"
                + (f"ไฟล์ผล: {val}\n" if is_file else f"ค่า: {val}\n"))
        return val
    return TPL_RE.sub(sub, text)


def preamble(run, nid, acct, n):
    board = run.board_text()
    entries = [l for l in board.splitlines() if l.startswith("- [")]
    lines = [f"[agent-team · run {run.id} · งาน {nid} · บัญชี {acct}]"]
    if entries:
        if len(board) <= 3000:
            lines += ["ข้อค้นพบบนกระดานกลาง (board.md) ใช้ข้อมูลนี้ได้:", *entries[-40:]]
        else:
            lines.append(f"อ่านกระดานกลาง {run.p('board.md')} ก่อนเริ่ม")
    lines.append("ถ้าพบข้อเท็จจริงที่งานอื่นในทีมควรรู้ ให้เพิ่มบรรทัดท้ายคำตอบที่ขึ้นต้นด้วย `BOARD: `")
    prog = run.p("msgs", f"{nid}__progress.md")
    if int(n.get("difficulty") or 2) >= 3 or n.get("progress"):
        lines.append(f"งานนี้ยาว: ระหว่างทำให้บันทึกความคืบหน้าต่อท้ายไฟล์ {prog}")
    if os.path.exists(prog):
        lines.append(f"มีความคืบหน้าจากผู้ทำก่อนหน้าใน {prog} อ่านก่อนแล้วทำต่อ ไม่ต้องเริ่มใหม่")
    return "\n".join(lines) + "\n---\n"


EXPECT_HINT = {"int": "(ตอบผลลัพธ์สุดท้ายเป็นจำนวนเต็มล้วน ไม่มีข้อความอื่น)",
               "number": "(ตอบผลลัพธ์สุดท้ายเป็นตัวเลขล้วน ไม่มีข้อความอื่น)",
               "json": "(ตอบเป็น JSON ล้วน ไม่มีข้อความอื่น)"}


def split_board(text):
    keep, notes = [], []
    for line in (text or "").splitlines():
        m = re.match(r"^\s*`?BOARD:\s*(.+?)`?\s*$", line)
        (notes.append(m.group(1)) if m else keep.append(line))
    return "\n".join(keep).strip(), notes


def validate(text, expect):
    """Check the format the next node needs before passing it on. -> (ok, value, error)"""
    t = (text or "").strip()
    if not expect or expect == "text":
        return bool(t), t, "" if t else "ผลว่าง"
    eq = re.fullmatch(r"[\d\s.,+\-−*×/÷()^]+=\s*(-?[\d,]+(?:\.\d+)?)", t)
    if expect in ("int", "number") and eq:          # "50 - 8 = 42" -> "42" (one-line equation only)
        t = eq.group(1)
    if expect == "int":
        v = t.replace(",", "").strip("` ")
        return (True, v, "") if re.fullmatch(r"-?\d+", v) else (False, t, f"ไม่ใช่จำนวนเต็มล้วน: {t[:60]!r}")
    if expect == "number":
        try:
            float(t.replace(",", "").strip("` "))
            return True, t.replace(",", "").strip("` "), ""
        except ValueError:
            return False, t, f"ไม่ใช่ตัวเลข: {t[:60]!r}"
    if expect == "json":
        body = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
        try:
            json.loads(body)
            return True, body, ""
        except ValueError:
            return False, t, "ไม่ใช่ JSON"
    if expect.startswith("regex:"):
        return (True, t, "") if re.fullmatch(expect[6:], t, re.S) else (False, t, f"ไม่ตรง {expect}")
    return False, t, f"expect ไม่รู้จัก {expect!r}"


def do_call(run, n, acct, prompt, node_tag, role="worker", schema=None, timeout=None):
    """One model call on either CLI, with the node's difficulty/model/effort for that side."""
    side = M.side_of(acct)
    ctx = {"run_id": run.id, "node": node_tag, "role": role, "run_dir": run.dir}
    timeout = int(timeout or n.get("timeout") or run.read()["options"]["timeout"])
    cwd = n.get("cwd") or run.p("work")
    model = n.get("model")
    claude_model = bool(model) and (model in M.CLAUDE_MODELS or model.startswith("claude"))
    if side == "yolo":
        mdl, eff = Y.pick(n.get("difficulty"), model if claude_model else None, n.get("effort"))
        return Y.call(acct, prompt, mdl, eff, schema, cwd, timeout, ctx)
    if n.get("image"):
        return C.image(acct, prompt, n["image"], None if claude_model else model, timeout, ctx)
    mdl, eff, note = C.pick(acct, n.get("difficulty"), None if claude_model else model, n.get("effort"))
    return C.call(acct, prompt, mdl, eff, schema, cwd, timeout, ctx, effort_note=note)


def resolve(run, want, exclude=()):
    """Account for a role inside a composite node (review/debate/best_of)."""
    st = run.read()
    if M.is_account(want):
        return want
    side = None if want == "any" else want
    cands = eligible(st, side) or eligible(st, side, paused_ok=True)
    pref = [a for a in cands if a not in exclude] or cands
    if not pref:
        raise RuntimeError(f"ไม่มีบัญชีที่พร้อมสำหรับ {want}")
    return min(pref, key=lambda a: (load(st, a), quota_pct(a), a))


JUDGE_DEBATE = {"type": "object", "additionalProperties": False,
                "properties": {"answer": {"type": "string"}, "winner": {"type": "string"},
                               "agree": {"type": "boolean"}, "reason": {"type": "string"}},
                "required": ["answer", "winner", "agree", "reason"]}
JUDGE_BEST = {"type": "object", "additionalProperties": False,
              "properties": {"scores": {"type": "array", "items": {
                  "type": "object", "additionalProperties": False,
                  "properties": {"candidate": {"type": "string"}, "score": {"type": "number"},
                                 "note": {"type": "string"}},
                  "required": ["candidate", "score", "note"]}},
                  "best": {"type": "string"}, "reason": {"type": "string"}},
              "required": ["scores", "best", "reason"]}


def _parallel(fn, items):
    with ThreadPoolExecutor(max(1, len(items))) as ex:
        return list(ex.map(fn, items))


def exec_node(run, nid, acct):
    """Runs in a worker thread. -> outcome dict for finish_node()."""
    st = run.read()
    n = st["nodes"][nid]
    pre = preamble(run, nid, acct, n)
    body = render(run, st, nid, n["prompt"])
    t = n["type"]
    if t == "task":
        hint = EXPECT_HINT.get(n.get("expect") or "")
        prompt = body if n.get("image") else pre + body + (f"\n\n{hint}" if hint else "")
        r = do_call(run, n, acct, prompt, nid, schema=n.get("schema"))
        return {"ok": r["ok"], "status": r["status"], "text": r["result"], "error": r["error"],
                "account": acct, "model": r["model"], "effort": r["effort"]}

    if t == "review":
        worker, reviewer = acct, resolve(run, n.get("reviewer", "any"), exclude=(acct,))
        criteria = n.get("criteria") or "ถูกต้องและครบตามโจทย์"
        draft, feedback, log = None, "", []
        for rnd in range(1, int(n.get("max_rounds") or 3) + 1):
            wp = pre + body
            if draft:
                wp += (f"\n\nร่างก่อนหน้าอยู่ที่ {draft}\nผู้ตรวจให้แก้ดังนี้:\n{feedback}\n"
                       "แก้ตามความเห็นแล้วส่งงานฉบับเต็มใหม่ทั้งหมด")
            w = do_call(run, n, worker, wp, f"{nid}.w{rnd}")
            if not w["ok"]:
                return {"ok": False, "status": w["status"], "error": f"ผู้ทำรอบ {rnd}: {w['error']}", "account": worker}
            draft = run.p("out", f"{nid}.r{rnd}.md")
            with open(draft, "w", encoding="utf-8") as f:
                f.write(split_board(w["result"])[0] + "\n")
            run.msg(f"{nid}.worker", f"{nid}.reviewer", f"## รอบ {rnd} ({worker})\nร่าง: {draft}\n", append=True)
            rp = (f"[agent-team · run {run.id} · ผู้ตรวจงาน {nid} · บัญชี {reviewer}]\n"
                  f"ตรวจงานในไฟล์ {draft} (อ่านไฟล์เอง)\nโจทย์เดิม: {body}\nเกณฑ์: {criteria}\n"
                  "ถ้าผ่านทุกเกณฑ์ ตอบคำเดียวว่า APPROVED\n"
                  "ถ้าไม่ผ่าน ตอบเป็นรายการสั้น ๆ ว่าต้องแก้อะไร และห้ามมีคำว่า APPROVED")
            rv = do_call(run, dict(n, difficulty=n.get("review_difficulty", n.get("difficulty"))),
                         reviewer, rp, f"{nid}.r{rnd}", role="reviewer")
            if not rv["ok"]:
                return {"ok": False, "status": rv["status"], "error": f"ผู้ตรวจรอบ {rnd}: {rv['error']}", "account": worker}
            verdict = rv["result"].strip()
            run.msg(f"{nid}.reviewer", f"{nid}.worker", f"## รอบ {rnd} ({reviewer})\n{verdict}\n", append=True)
            log.append(f"รอบ {rnd}: ผู้ทำ {worker} · ผู้ตรวจ {reviewer} → {verdict[:200]}")
            if re.fullmatch(r"\W*APPROVED\W*", verdict, re.I):
                with open(draft, encoding="utf-8") as f:
                    final = f.read()
                return {"ok": True, "status": "ok", "account": worker, "text": final,
                        "extra": {"rounds": rnd, "reviewer": reviewer, "log": log}}
            feedback = verdict
        return {"ok": False, "status": "error", "account": worker,
                "error": f"ไม่ได้ APPROVED ภายใน {n.get('max_rounds') or 3} รอบ", "extra": {"log": log}}

    # debate / best_of: candidates answer the same prompt, a judge decides
    if t == "debate":
        wants = n.get("candidates") or ["yolo", "cyolo"]
    else:
        wants = n.get("candidates") or [n.get("candidate_account", "any")] * int(n.get("n") or 3)
    cands, used = [], []
    for w in wants:
        a = resolve(run, w, exclude=used)
        cands.append(a)
        used.append(a)

    def answer(i_a):
        i, a = i_a
        r = do_call(run, n, a, pre + body, f"{nid}.c{i}", role="candidate")
        path = run.p("out", f"{nid}.c{i}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(split_board(r["result"])[0] + "\n")
        return {"label": f"c{i}", "account": a, "cli": M.CLI[M.side_of(a)], "ok": r["ok"],
                "path": path, "result": split_board(r["result"])[0], "error": r["error"]}
    answers = _parallel(answer, list(enumerate(cands, 1)))
    good = [x for x in answers if x["ok"]]
    if len(good) < 2:
        return {"ok": False, "status": "error", "account": acct,
                "error": "ผู้ตอบสำเร็จไม่ถึง 2 คน: " + "; ".join(x["error"] for x in answers if not x["ok"])}
    judge = resolve(run, n.get("judge", "any"), exclude=[x["account"] for x in good])
    listing = "\n".join(f"- {x['label']} ({x['account']}, {x['cli']}): ไฟล์ {x['path']}" for x in good)
    if t == "debate":
        jp = (f"[agent-team · run {run.id} · ผู้ตัดสิน {nid}]\nโจทย์: {body}\nคำตอบของแต่ละฝ่าย (อ่านจากไฟล์):\n"
              f"{listing}\nตรวจโจทย์ด้วยตัวเองอย่างอิสระ เทียบคำตอบ แล้วสรุปคำตอบที่ถูก "
              "ตอบ JSON: answer = คำตอบที่ถูก (สั้น), winner = label ของฝ่ายที่ถูก หรือ 'both'/'none', "
              "agree = ทั้งสองฝ่ายตอบตรงกันหรือไม่, reason = เหตุผลสั้น ๆ")
        schema = JUDGE_DEBATE
    else:
        jp = (f"[agent-team · run {run.id} · ผู้ตัดสิน {nid}]\nโจทย์: {body}\nเกณฑ์ให้คะแนน (0-10): "
              f"{n.get('criteria') or 'ถูกต้อง ครบถ้วน กระชับ'}\nผลงานของผู้สมัคร (อ่านจากไฟล์):\n{listing}\n"
              "ให้คะแนนทุกคนตามเกณฑ์ แล้วเลือกคนที่ดีที่สุด ตอบ JSON: scores = [{candidate: label, score, note}], "
              "best = label ที่ดีที่สุด, reason = เหตุผลที่เลือก")
        schema = JUDGE_BEST
    j = do_call(run, dict(n, difficulty=n.get("judge_difficulty", n.get("difficulty"))), judge, jp,
                f"{nid}.judge", role="judge", schema=schema)
    if not j["ok"]:
        return {"ok": False, "status": j["status"], "account": acct, "error": f"ผู้ตัดสิน: {j['error']}"}
    v = j["structured"] or {}
    with open(run.p("out", f"{nid}.judge.json"), "w", encoding="utf-8") as f:
        json.dump({"judge": judge, "candidates": answers, "verdict": v}, f, ensure_ascii=False, indent=1)
    if t == "debate":
        value = str(v.get("answer", "")).strip()
        text = (f"คำตอบ: {value}\nผู้ชนะ: {v.get('winner')} · ตรงกัน: {v.get('agree')}\n"
                f"ผู้ตัดสิน: {judge}\nเหตุผล: {v.get('reason')}\n\n"
                + "\n".join(f"- {x['label']} {x['account']}: {x['result'][:300]}" for x in good))
    else:
        best = next((x for x in good if x["label"] == v.get("best")), good[0])
        value = best["result"]
        text = (f"{best['result']}\n\n---\nผู้ชนะ: {best['label']} ({best['account']}) · ผู้ตัดสิน {judge}\n"
                f"เหตุผล: {v.get('reason')}\nคะแนน: "
                + ", ".join(f"{s.get('candidate')}={s.get('score')}" for s in v.get("scores") or []))
    return {"ok": True, "status": "ok", "account": acct, "text": text, "value": value,
            "extra": {"judge": judge, "candidates": [x["account"] for x in answers], "verdict": v}}


def finish_node(run, nid, acct, oc):
    """Write the result, share board notes, or decide failover (only for failures that
    burned no tokens: quota/limit or expired login, and only when the node is not pinned)."""
    with run.tx() as st:
        n = st["nodes"][nid]
        n["ended"] = M.now_iso()
        n["attempts"].append({"account": acct, "status": oc.get("status"), "error": oc.get("error", "")[:200],
                              "ts": n["ended"]})
        if oc.get("ok"):
            text, notes = split_board(oc.get("text", ""))
            ok, value, err = validate(oc.get("value", text), n.get("expect")) if n["type"] == "task" \
                else (True, oc.get("value", text), "")
            for note in notes:
                run.board(f"{nid} ({acct})", note)
            with open(run.p("out", f"{nid}.md"), "w", encoding="utf-8") as f:
                f.write(text + "\n")
            n.update(extra=oc.get("extra"), model=oc.get("model"), effort=oc.get("effort"))
            if ok:
                n.update(status="done", value=value, error="")
            else:
                n.update(status="failed", error=f"รูปแบบผลไม่ผ่าน: {err}")
            return
        kind = oc.get("status")
        if kind in ("limit", "auth") and n["type"] == "task":
            s = st["accounts"].setdefault(acct, {})
            if not s.get("unavailable"):
                s["unavailable"] = f"{kind}: {oc.get('error', '')[:80]}"
                run.event(st, "account_down", f"{acct} ใช้ไม่ได้ระหว่าง run ({s['unavailable']})", account=acct)
            if pinned(n):
                n.update(status="failed", error=f"บัญชีที่ผู้ใช้ระบุ ({acct}) ล้ม: {oc.get('error')} — ไม่ย้ายอัตโนมัติ")
                run.board("ระบบ", f"{nid}: หยุด — {n['error']}")
                return
            n.update(status="pending", assigned=None, planned=None,
                     moved_from={"account": acct, "reason": f"{kind} ({oc.get('error', '')[:60]})"})
            return
        n.update(status="failed", error=f"{kind}: {oc.get('error', '')[:300]}")


class Scheduler:
    """Starts every ready node on a fitting account within the caps; loops until nothing is left."""

    def __init__(self, run):
        self.run = run
        st = run.read()
        self.opts = st["options"]
        self.ex = ThreadPoolExecutor(int(self.opts["max_total"]))
        self.futs = {}
        self.t_quota = time.time()

    def _job(self, nid, acct):
        try:
            oc = exec_node(self.run, nid, acct)
        except Exception as e:  # template/resolve errors, crashes - never retried
            oc = {"ok": False, "status": "error", "error": f"{type(e).__name__}: {e}", "account": acct}
        finish_node(self.run, nid, acct, oc)

    def tick(self):
        """-> 'busy' | 'idle' | 'gate' (only human gates left)."""
        run = self.run
        with run.tx() as st:
            update_pauses(run, st)
            gates = False
            for nid in st["order"]:
                n = st["nodes"][nid]
                if n["status"] not in ("pending", "waiting_approval"):
                    continue
                deps = [st["nodes"][d] for d in n["depends_on"]]
                bad = [d["id"] for d in deps if d["status"] in ("failed", "blocked")]
                if bad:
                    n.update(status="blocked", error=f"หยุดเพราะงานที่ขึ้นด้วยล้ม: {', '.join(bad)}")
                    run.board("ระบบ", f"{nid}: {n['error']}")
                    continue
                if any(d["status"] != "done" for d in deps):
                    continue
                if n.get("approve") and not os.path.exists(run.p("approvals", f"{nid}.ok")):
                    if n["status"] != "waiting_approval":
                        n["status"] = "waiting_approval"
                        run.msg(nid, "human", f"# {nid} รออนุมัติ\n\nงาน: {n['prompt'][:500]}\n\n"
                                f"อนุมัติ: python3 {TEAM} approve {nid} --run {run.id}\n"
                                f"(หรือสร้างไฟล์ {run.p('approvals', nid + '.ok')})\n")
                        run.board("ระบบ", f"{nid}: หยุดรออนุมัติจากคน (human gate)")
                    gates = True
                    continue
                if n["status"] == "waiting_approval":
                    n["status"] = "pending"
                    run.board("ระบบ", f"{nid}: ได้รับอนุมัติแล้ว รันต่อ")
            plan(run, st)
            total = sum(1 for n in st["nodes"].values() if n["status"] == "running")
            started = 0
            for nid in st["order"]:
                n = st["nodes"][nid]
                if n["status"] != "pending" or total >= int(self.opts["max_total"]):
                    continue
                if any(st["nodes"][d]["status"] != "done" for d in n["depends_on"]):
                    continue
                acct, fail = choose(st, n)
                if fail:
                    n.update(status="failed", error=fail)
                    run.board("ระบบ", f"{nid}: {fail}")
                    continue
                if not acct:
                    continue
                n.update(status="running", assigned=acct, started=M.now_iso())
                total += 1
                started += 1
                self.futs[nid] = self.ex.submit(self._job, nid, acct)
            if started or self.futs or any(n["status"] == "running" for n in st["nodes"].values()):
                return "busy"
            if gates:
                return "gate"
            for n in st["nodes"].values():          # nothing can move any more
                if n["status"] == "pending":
                    n.update(status="blocked", error="ค้าง: ไม่มีทางเริ่มได้")
            st["sched_pid"] = None
            return "idle"

    def loop(self):
        gate_since = None
        with self.run.tx() as st:
            st["sched_pid"] = os.getpid()
        while True:
            if time.time() - self.t_quota > 600:
                refresh_quota(eligible(self.run.read()))
                self.t_quota = time.time()
            state = self.tick()
            if state == "idle":
                break
            if state == "gate":
                gate_since = gate_since or time.time()
                if time.time() - gate_since > float(self.opts.get("gate_timeout") or 3600):
                    with self.run.tx() as st:
                        for n in st["nodes"].values():
                            if n["status"] == "waiting_approval":
                                n.update(status="blocked", error="human gate หมดเวลารอ")
                        st["sched_pid"] = None
                    break
            else:
                gate_since = None
            for k in [k for k, f in self.futs.items() if f.done()]:
                self.futs.pop(k)
            if self.futs:
                fwait(list(self.futs.values()), timeout=2, return_when=FIRST_COMPLETED)
            else:
                time.sleep(2)
            for k in [k for k, f in self.futs.items() if f.done()]:
                self.futs.pop(k)
        self.ex.shutdown(wait=True)


def setup_accounts(run, accts, recheck):
    rd = readiness(accts, recheck, run.dir)
    ready = [a for a in accts if rd[a]["state"] == "ready"]
    refresh_quota(ready)
    with run.tx() as st:
        for a in accts:
            st["accounts"][a] = {"ready": rd[a]["state"], "detail": rd[a].get("detail"), "checked": rd[a].get("ts"),
                                 "paused": None, "unavailable": None, "tokens": 0}
        skipped = [f"{a} ({M.READY_LABEL[rd[a]['state']]})" for a in accts if a not in ready]
        if skipped:
            run.board("ระบบ", "ข้ามบัญชีที่ใช้ไม่ได้: " + ", ".join(skipped))
    return ready


# =============================================================== handoff (leader state)
def write_handoff(run, st):
    lead = st.get("lead") or {}
    rows = []
    for nid in st["order"]:
        n = st["nodes"][nid]
        val = (str(n.get("value")) if n["status"] == "done" else n.get("error") or "")[:80].replace("\n", " ")
        rows.append((nid, n["status"], n.get("assigned") or n.get("planned") or n["account"],
                     ",".join(n["depends_on"]) or "-", val,
                     run.p("out", nid + ".md") if n["status"] == "done" else ""))
    cps = lead.get("checkpoints") or []
    hist = lead.get("history") or []
    txt = [f"# handoff — run {run.id}", "", f"เป้าหมาย: {st.get('goal') or '-'}",
           f"หัวหน้าปัจจุบัน: {lead.get('current') or '-'} · รอบที่ {lead.get('episode', 0)} · "
           f"อัปเดต {M.now_iso()}", "",
           "## งานทั้งหมด (สด จาก state.json)", "",
           M.table(rows, ["id", "สถานะ", "บัญชี", "ขึ้นกับ", "ค่า/ข้อผิดพลาด", "ไฟล์ผล"]) if rows else "(ยังไม่มีงาน)",
           "", "## บันทึก checkpoint ของหัวหน้า (ล่าสุดอยู่ล่าง)", ""]
    txt += [f"- [{c['ts'][11:19]}] {c['by']} รอบ {c['episode']}: ทำแล้ว: {c['done']} | ต่อไป: {c['next']}"
            + (f" | ตัดสินใจ: {c['decision']}" if c.get("decision") else "") for c in cps] or ["(ยังไม่มี)"]
    txt += ["", "## ประวัติการสลับหัวหน้า", ""]
    txt += [f"- [{h['ts'][11:19]}] {h['from']} → {h['to']} ({h['type']}): {h['reason']}" for h in hist] or ["(ไม่มี)"]
    if cps:
        txt += ["", "## ขั้นต่อไป (จาก checkpoint ล่าสุด)", "", cps[-1]["next"]]
    if st.get("final"):
        txt += ["", "## จบแล้ว", "", f"คำตอบสุดท้าย: {st['final']['answer']}"]
    tmp = run.p("handoff.md.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(txt) + "\n")
    os.replace(tmp, run.p("handoff.md"))


LEAD_PROMPT = """คุณคือหัวหน้าทีม (leader) ของงานทีม agent-team · run @RUN · รอบ (episode) ที่ @EP · บัญชีของคุณ @ACCT
เป้าหมายของทีม: @GOAL

สถานะทั้งหมดอยู่ในไฟล์ ไม่ได้อยู่ในความจำของคุณ เริ่มด้วยการอ่าน: cat @HANDOFF

คำสั่งของทีม (T หมายถึง python3 @TEAM --run @RUN):
- T add <id> --account <yolo|cyolo|any|yoloN|cyoloN> --prompt "<งานของลูกทีม>" [--depends <id,id>] [--expect int|number|json|text] [--difficulty 1-6]
  ส่งผลของงานก่อนหน้า: ใส่ {{<id>}} ใน --prompt (ค่าสั้น) หรือ {{file:<id>}} (path ของไฟล์ผลยาว)
- T dispatch          สั่งลูกทีมรันงานที่พร้อม (รันเบื้องหลัง คำสั่งนี้จบทันที)
- T wait [<id> ...]   รอจนงานเสร็จแล้วแสดงผล
- T checkpoint --done "<ทำอะไรไปแล้ว>" --next "<ขั้นต่อไป>" [--decision "<การตัดสินใจสำคัญ>"]
- T finish --answer "<คำตอบสุดท้าย>"

ขั้นตอนของรอบนี้ ทำตามลำดับแล้วจบรอบ:
1. cat handoff.md
2. ถ้าตาราง "งานทั้งหมด" ยังว่าง: แตกเป้าหมายเป็นงานย่อยให้ลูกทีมด้วย T add (ทุกงาน) → T dispatch → T checkpoint → จบรอบทันที ไม่ต้อง wait
3. ถ้ามีงานแล้ว: ห้าม add งานที่มีอยู่แล้วซ้ำ → T dispatch → T wait
   - ผลครบตามเป้าหมาย: ตรวจผลของลูกทีม แล้ว T finish --answer "<คำตอบ>" และจบรอบ
   - มีงานล้มหรือยังต้องทำต่อ: T add งานใหม่ที่จำเป็น → T dispatch → T checkpoint แล้วจบรอบ
ห้ามคำนวณหรือทำงานของลูกทีมเอง ห้ามแก้ไฟล์ใน @DIR ด้วยมือ ตอบกลับหนึ่งบรรทัดว่ารอบนี้ทำอะไร"""


def lead_tool_touch(run, dispatched=False):
    """Leader commands refresh the heartbeat that the supervisor watches."""
    with run.tx() as st:
        lead = st.get("lead")
        if lead:
            lead["heartbeat"] = M.now_iso()
            if dispatched:
                lead["dispatches_ep"] = lead.get("dispatches_ep", 0) + 1


def pick_successor(run, st, exclude):
    lead = st["lead"]
    cand = [a for a in eligible(st, paused_ok=True) if a not in exclude and a not in lead["forbid"]]
    if lead.get("succession"):
        for a in lead["succession"]:
            if a in cand:
                return a
        return None
    cur_side = M.side_of(lead["current"])
    used = run_tokens(run, "lead")
    return min(cand, key=lambda a: (M.side_of(a) != cur_side, quota_pct(a), used.get(a, 0), a)) if cand else None


def switch_lead(run, kind, reason):
    with run.tx() as st:
        lead = st["lead"]
        old = lead["current"]
        if kind == "reactive":
            lead.setdefault("failed", []).append(old)
        new = pick_successor(run, st, exclude=[old] + lead.get("failed", []))
        lead["history"].append({"ts": M.now_iso(), "from": old, "to": new, "type": kind, "reason": reason})
        run.event(st, "lead_switch", f"หัวหน้า {old} → {new or '— (ไม่มีผู้สืบทอด)'} ({kind}): {reason}",
                  account=old, to=new)
        lead["current"] = new
        write_handoff(run, st)
        return new


def cmd_lead(a):
    accts = [x for x in (a.accounts.split(",") if a.accounts else M.accounts()) if x]
    opts = build_opts(a, accts)
    run = new_run(a.run, a.goal, [], opts, "lead")
    print(f"run {run.id} · {run.dir}")
    ready = setup_accounts(run, accts, a.recheck)
    forbid = [x for x in (a.forbid or "").split(",") if x]
    succ = [x for x in (a.succession or "").split(",") if x]
    with run.tx() as st:
        st["lead"] = {"current": None, "episode": 0, "heartbeat": None, "history": [], "checkpoints": [],
                      "forbid": forbid, "succession": succ, "failed": [], "budget": a.lead_token_budget}
        first = a.leader if a.leader and a.leader != "auto" else None
        if first and first not in ready:
            raise SystemExit(f"หัวหน้าที่ระบุ {first} ไม่พร้อม: {st['accounts'].get(first)}")
        if not first:
            st["lead"]["current"] = (succ or ready)[0] if (succ or ready) else None
            st["lead"]["current"] = pick_successor(run, st, exclude=[]) or st["lead"]["current"]
        else:
            st["lead"]["current"] = first
        write_handoff(run, st)
    sim_crash = os.environ.get("MA_SIMULATE_CRASH", "")
    status = "incomplete"
    for ep in range(1, a.max_episodes + 1):
        with run.tx() as st:
            lead = st["lead"]
            acct = lead["current"]
            if not acct:
                status = "stalled: ไม่มีหัวหน้าที่ใช้ได้"
                break
            lead.update(episode=ep, heartbeat=M.now_iso(), dispatches_ep=0, cp_ep=0)
            write_handoff(run, st)
        print(f"-- รอบ {ep}: หัวหน้า {acct}", flush=True)
        prompt = LEAD_PROMPT
        for k, v in {"@RUN": run.id, "@EP": str(ep), "@ACCT": acct, "@GOAL": a.goal, "@TEAM": TEAM,
                     "@HANDOFF": run.p("handoff.md"), "@DIR": run.dir}.items():
            prompt = prompt.replace(k, v)

        def watch():
            st = run.read()
            lead = st["lead"]
            if M.age_s(lead.get("heartbeat")) > a.heartbeat_timeout:
                return f"heartbeat ไม่อัปเดตเกิน {a.heartbeat_timeout}s"
            if sim_crash == "lead_after_dispatch" and lead.get("dispatches_ep") and not lead.get("sim_crashed"):
                with run.tx() as s2:
                    s2["lead"]["sim_crashed"] = True
                return "simulated crash (MA_SIMULATE_CRASH=lead_after_dispatch) หลังสั่งงานลูกทีม"
            return None
        lp = {"difficulty": a.lead_difficulty, "model": a.lead_model, "effort": a.lead_effort}
        ctx = {"run_id": run.id, "node": f"_lead.ep{ep}", "role": "lead", "run_dir": run.dir}
        env = {"MA_RUN": run.id, "MA_ROLE": "lead", "MA_ACCOUNT": acct}
        if M.side_of(acct) == "yolo":
            mdl, eff = Y.pick(lp["difficulty"], lp["model"] if (lp["model"] or "") in M.CLAUDE_MODELS else None,
                              lp["effort"])
            r = Y.call(acct, prompt, mdl, eff, cwd=run.dir, timeout=a.episode_timeout, ctx=ctx, watch=watch,
                       env_extra=env)
        else:
            mdl, eff, note = C.pick(acct, lp["difficulty"], None, lp["effort"])
            r = C.call(acct, prompt, mdl, eff, cwd=run.dir, timeout=a.episode_timeout, ctx=ctx, watch=watch,
                       env_extra=env, effort_note=note)
        print(f"   {acct}: {r['status']} · {r['duration_s']}s · {(r['result'] or r['error'])[:160]}", flush=True)
        st = run.read()
        if st.get("final"):
            status = "finished"
            break
        if not r["ok"]:
            kind = r["status"]
            new = switch_lead(run, "reactive", f"รอบ {ep} ล้ม ({kind}: {(r['error'] or '')[:100]}) "
                                               "→ ย้อนไป checkpoint ล่าสุด")
            print(f"   สลับหัวหน้าเชิงรับ → {new}", flush=True)
            continue
        if not st["lead"].get("cp_ep"):
            run.board("ระบบ", f"หัวหน้า {acct} จบรอบ {ep} โดยไม่ได้ checkpoint")
        used = run_tokens(run, "lead").get(acct, 0)
        refresh_quota([acct], max_age=300)
        why = None
        if a.lead_token_budget and used >= a.lead_token_budget:
            why = f"หัวหน้าใช้โทเค็น {used} ≥ งบ {a.lead_token_budget}"
        elif quota_pct(acct) >= opts["quota_threshold"]:
            why = f"โควตาหัวหน้า {quota_pct(acct):g}% ≥ {opts['quota_threshold']:g}%"
        if why:
            new = switch_lead(run, "proactive", why + " → ส่งไม้ต่อพร้อม checkpoint")
            print(f"   สลับหัวหน้าเชิงรุก → {new}", flush=True)
    with run.tx() as st:
        st["lead"]["status"] = status
        write_handoff(run, st)
    st = run.read()
    print(f"\nสถานะ: {status}")
    if st.get("final"):
        print(f"คำตอบสุดท้าย: {st['final']['answer']} (โดย {st['final']['by']})")
    for h in st["lead"]["history"]:
        print(f"สลับหัวหน้า: {h['from']} → {h['to']} ({h['type']}) {h['reason']}")
    print(f"handoff: {run.p('handoff.md')}")
    return 0 if status == "finished" else 1


# =============================================================== leader tools
def get_run(a):
    rid = a.run or os.environ.get("MA_RUN")
    return Run(rid) if rid else latest_run()


def cmd_add(a):
    run = get_run(a)
    spec = {"id": a.id, "prompt": a.prompt, "account": a.account,
            "depends_on": [x for x in (a.depends or "").split(",") if x]}
    for k in ("expect", "difficulty", "model", "effort", "image", "kind"):
        if getattr(a, k, None) is not None:
            spec[k] = getattr(a, k)
    with run.tx() as st:
        if a.id in st["nodes"]:
            print(f"{a.id} มีอยู่แล้ว (สถานะ {st['nodes'][a.id]['status']}) ไม่เพิ่มซ้ำ")
            return 0
        add_node(st, spec)
        write_handoff(run, st)
    lead_tool_touch(run)
    print(f"เพิ่มงาน {a.id} ({a.account}) แล้ว · อย่าลืม dispatch")
    return 0


def ensure_scheduler(run):
    with run.tx() as st:
        pid = st.get("sched_pid")
        alive = False
        if pid:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        if alive:
            return pid, False
        log = open(run.p("scheduler.log"), "a")
        p = subprocess.Popen([sys.executable, TEAM, "--run", run.id, "_sched"], stdin=subprocess.DEVNULL,
                             stdout=log, stderr=log, start_new_session=True, cwd=run.dir)
        st["sched_pid"] = p.pid
        return p.pid, True


def cmd_dispatch(a):
    run = get_run(a)
    pid, started = ensure_scheduler(run)
    lead_tool_touch(run, dispatched=True)
    st = run.read()
    pend = [n for n in st["order"] if st["nodes"][n]["status"] in ("pending", "running", "waiting_approval")]
    print(f"ลูกทีมกำลังทำ: {', '.join(pend) or '-'} (scheduler pid {pid}{' เริ่มใหม่' if started else ''})")
    return 0


def cmd_wait(a):
    run = get_run(a)
    t0, last = time.time(), 0
    while True:
        st = run.read()
        ids = a.ids or st["order"]
        missing = [i for i in ids if i not in st["nodes"]]
        if missing:
            print(f"ไม่มีงาน: {', '.join(missing)}")
            return 2
        pend = [i for i in ids if st["nodes"][i]["status"] not in TERMINAL]
        if not pend or time.time() - t0 > a.timeout:
            break
        if time.time() - last > 20:
            lead_tool_touch(run)
            last = time.time()
        time.sleep(2)
    for i in ids:
        n = st["nodes"][i]
        v = n.get("value") if n["status"] == "done" else n.get("error")
        print(f"{i}: {n['status']} ({n.get('assigned') or '-'}) → {str(v)[:300]}"
              + (f" · ไฟล์ {run.p('out', i + '.md')}" if n["status"] == "done" else ""))
    if pend:
        print(f"ยังไม่เสร็จ (หมดเวลารอ {a.timeout}s): {', '.join(pend)}")
    lead_tool_touch(run)
    return 0 if not pend else 3


def cmd_checkpoint(a):
    run = get_run(a)
    with run.tx() as st:
        lead = st.get("lead") or {}
        lead.setdefault("checkpoints", []).append({"ts": M.now_iso(), "by": lead.get("current") or a.by,
                                                   "episode": lead.get("episode", 0), "done": a.done,
                                                   "next": a.next, "decision": a.decision})
        lead["cp_ep"] = lead.get("cp_ep", 0) + 1
        lead["heartbeat"] = M.now_iso()
        st["lead"] = lead
        write_handoff(run, st)
    print(f"checkpoint บันทึกแล้ว: {run.p('handoff.md')}")
    return 0


def cmd_finish(a):
    run = get_run(a)
    with run.tx() as st:
        by = (st.get("lead") or {}).get("current") or a.by
        st["final"] = {"answer": a.answer, "by": by, "ts": M.now_iso()}
        if st.get("lead"):
            st["lead"]["heartbeat"] = M.now_iso()
        write_handoff(run, st)
    run.board(by or "leader", f"จบงาน: {a.answer}")
    print("บันทึกคำตอบสุดท้ายแล้ว")
    return 0


# =============================================================== run / status / stats / quota
def build_opts(a, accts):
    opts = dict(OPTS)
    opts.update(per_account=a.per_account, max_total=a.max, timeout=a.timeout,
                quota_threshold=a.quota_threshold, accounts=accts)
    b = {}
    for part in [x for x in (a.worker_token_budget or "").split(",") if x]:
        k, _, v = part.rpartition("=")
        b[k or "*"] = int(v)
    opts["worker_token_budget"] = b
    return opts


def cmd_run(a):
    data = json.load(sys.stdin if a.graph == "-" else open(a.graph, encoding="utf-8"))
    nodes = data["nodes"] if isinstance(data, dict) else data
    goal = data.get("goal", "") if isinstance(data, dict) else ""
    defaults = data.get("defaults", {}) if isinstance(data, dict) else {}
    for n in nodes:
        for k, v in defaults.items():
            n.setdefault(k, v)
    accts = [x for x in (a.accounts.split(",") if a.accounts else M.accounts()) if x]
    run = new_run(a.run, goal, nodes, build_opts(a, accts), "graph")
    print(f"run {run.id} · {run.dir}", flush=True)
    ready = setup_accounts(run, accts, a.recheck)
    print("บัญชีพร้อม: " + (", ".join(ready) or "ไม่มี"), flush=True)
    if a.detach:
        pid, _ = ensure_scheduler(run)
        print(f"รันเบื้องหลัง (scheduler pid {pid}) ดูสถานะ: team.py status --run {run.id}")
        return 0
    t0 = time.time()
    Scheduler(run).loop()
    st = run.read()
    with run.tx() as s2:
        write_handoff(run, s2)
    return report(run, st, time.time() - t0, a.json)


def report(run, st, secs, as_json=False):
    nodes = [st["nodes"][i] for i in st["order"]]
    ok = all(n["status"] == "done" for n in nodes)
    if as_json:
        print(json.dumps({"run_id": run.id, "ok": ok, "wall_s": round(secs, 1),
                          "nodes": {n["id"]: {k: n.get(k) for k in ("status", "assigned", "value", "error",
                                                                     "route", "attempts", "extra")}
                                    for n in nodes},
                          "events": st.get("events")}, ensure_ascii=False))
    else:
        rows = [(n["id"], n["type"], n["status"], n.get("assigned") or "-",
                 f"{n.get('model') or ''}/{n.get('effort') or ''}".strip("/") or "-",
                 str(n.get("value") if n["status"] == "done" else n.get("error"))[:70].replace("\n", " "))
                for n in nodes]
        print(M.table(rows, ["งาน", "ชนิด", "สถานะ", "บัญชี", "รุ่น/effort", "ค่า/ข้อผิดพลาด"]))
        for e in st.get("events") or []:
            print(f"* {e['event']}: {e['text']}")
        print(f"-- {sum(n['status'] == 'done' for n in nodes)}/{len(nodes)} สำเร็จ · {secs:.1f}s · {run.dir}")
    return 0 if ok else 1


def acct_state(st, a):
    s = st["accounts"][a]
    if s.get("ready") != "ready" or s.get("unavailable"):
        return "ใช้ไม่ได้"
    if s.get("paused"):
        return "หยุดรับงาน"
    b = budget_of(st["options"], a)
    th = float(st["options"].get("quota_threshold") or 80)
    if quota_pct(a) >= th - 15 or (b and s.get("tokens", 0) >= 0.7 * int(b)):
        return "ใกล้หมด"
    return "พร้อม"


def cmd_status(a):
    run = get_run(a)
    st = run.read()
    used = run_tokens(run)
    lead = (st.get("lead") or {}).get("current")
    rows = []
    for acct in st["accounts"]:
        nodes = st["nodes"].values()
        running = [n["id"] for n in nodes if n["status"] == "running" and n.get("assigned") == acct]
        queued = [n["id"] for n in nodes if n["status"] in ("pending", "waiting_approval")
                  and (n.get("planned") == acct or n["account"] == acct)]
        worker = any(n.get("assigned") == acct or n.get("planned") == acct for n in nodes)
        role = "หัวหน้า" if acct == lead else ("ลูกทีม" if worker else "-")
        s = st["accounts"][acct]
        state = acct_state(st, acct)
        why = s.get("paused") or s.get("unavailable") or (M.READY_LABEL.get(s.get("ready")) if s.get("ready") != "ready" else "")
        rows.append((acct, role, ",".join(running) or "-", ",".join(queued) or "-", used.get(acct, 0),
                     quota_text(acct), state + (f" ({why})" if why else "")))
    print(f"run {run.id} · {st.get('goal') or ''} · โหมด {st.get('mode')} · อัปเดต {st.get('updated')}")
    print(M.table(rows, ["บัญชี", "บทบาท", "งานที่รัน", "งานในคิว", "tokens ใน run", "โควตาล่าสุด", "สถานะ"]))
    print()
    print(M.table([(i, st["nodes"][i]["status"], st["nodes"][i].get("assigned") or st["nodes"][i].get("planned") or "-",
                    str(st["nodes"][i].get("value") if st["nodes"][i]["status"] == "done"
                        else st["nodes"][i].get("error") or "")[:60].replace("\n", " "))
                   for i in st["order"]], ["งาน", "สถานะ", "บัญชี", "ค่า/ข้อผิดพลาด"]))
    if st.get("final"):
        print(f"\nคำตอบสุดท้าย: {st['final']['answer']}")
    return 0


def aggregate(rows, key):
    g = {}
    for r in rows:
        k = key(r)
        x = g.setdefault(k, {"calls": 0, "ok": 0, "fail": 0, "input_tokens": 0, "cached_input_tokens": 0,
                             "cache_write_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0,
                             "cost_usd": 0.0, "secs": 0.0})
        x["calls"] += 1
        x["ok" if r.get("status") == "ok" else "fail"] += 1
        for f in ("input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens"):
            x[f] += int(r.get(f) or 0)
        x["cost_usd"] += float(r.get("cost_usd") or 0)
        x["secs"] += float(r.get("duration_s") or 0)
    for x in g.values():
        x["avg_secs"] = round(x["secs"] / x["calls"], 2) if x["calls"] else 0
        x["secs"] = round(x["secs"], 2)
        x["cost_usd"] = round(x["cost_usd"], 6)
    return g


def cmd_stats(a):
    path = Run(a.run).p("ledger.jsonl") if a.run else M.GLOBAL_LEDGER
    rows = [r for r in M.ledger_read(path) if r.get("event") == "call"]
    groups = {"by_account": aggregate(rows, lambda r: r.get("account")),
              "by_model": aggregate(rows, lambda r: f"{r.get('cli')}:{r.get('model')}"),
              "by_run": aggregate(rows, lambda r: r.get("run_id") or "(เรียกเดี่ยว)"),
              "total": aggregate(rows, lambda r: "total").get("total", {})}
    if a.json:
        print(json.dumps({"ledger": path, **groups}, ensure_ascii=False))
        return 0
    hdr = ["", "ครั้ง", "สำเร็จ", "ล้ม", "input", "cache read", "cache write", "output", "reasoning",
           "$ list", "เวลารวม s", "เฉลี่ย s"]
    cols = ("calls", "ok", "fail", "input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens",
            "reasoning_tokens", "cost_usd", "secs", "avg_secs")
    print(f"ledger: {path} ({len(rows)} calls)")
    for title, key in (("ตามบัญชี", "by_account"), ("ตามรุ่น", "by_model"), ("ตาม run", "by_run")):
        print(f"\n### {title}")
        print(M.table([[k] + [v[c] for c in cols] for k, v in sorted(groups[key].items(), key=lambda kv: str(kv[0]))],
                      [title] + hdr[1:]))
    t = groups["total"]
    if t:
        print("\nรวม: " + " · ".join(f"{c} {t[c]}" for c in cols))
    print("(cost = ราคาตามรายการของ Claude ไม่ใช่ยอดจ่ายจริง · Codex ไม่มีข้อมูลค่าใช้จ่าย)")
    return 0


def cmd_quota(a):
    accts = a.accounts or M.accounts()
    refresh_quota(accts, max_age=0 if a.fresh else 600)
    cache = M.cache_load(M.QUOTA_FILE)
    print(M.table([(x, quota_text(x), (cache.get(x) or {}).get("source", "")) for x in accts],
                  ["บัญชี", "โควตาที่ใช้ไป (เวลาของข้อมูล)", "แหล่ง"]))
    return 0


def cmd_check(a):
    accts = a.accounts or M.accounts()
    rd = readiness(accts, a.recheck)
    print(M.table([(x, M.READY_LABEL[rd[x]["state"]], rd[x].get("detail"), rd[x].get("ts"))
                   for x in accts], ["บัญชี", "สถานะ", "รายละเอียด", "ตรวจเมื่อ"]))
    return 0


def cmd_approve(a):
    run = get_run(a)
    with open(run.p("approvals", f"{a.node}.ok"), "w", encoding="utf-8") as f:
        f.write(f"approved {M.now_iso()} by {a.by}\n")
    print(f"อนุมัติ {a.node} แล้ว")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", help="run id (default: $MA_RUN or the newest run)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--accounts", help="comma list (default: every account dir)")
        p.add_argument("--per-account", type=int, default=3)
        p.add_argument("--max", type=int, default=8)
        p.add_argument("--timeout", type=int, default=600)
        p.add_argument("--worker-token-budget", help="N (every account) or acct=N,acct=N")
        p.add_argument("--quota-threshold", type=float, default=80.0)
        p.add_argument("--recheck", action="store_true", help="ignore the 10-min readiness cache")
    r = sub.add_parser("run")
    r.add_argument("graph")
    r.add_argument("--detach", action="store_true")
    r.add_argument("--json", action="store_true")
    common(r)
    ld = sub.add_parser("lead")
    ld.add_argument("--goal", required=True)
    ld.add_argument("--leader", default="auto")
    ld.add_argument("--succession")
    ld.add_argument("--forbid")
    ld.add_argument("--lead-token-budget", type=int, default=0)
    ld.add_argument("--lead-difficulty", type=int, default=2)
    ld.add_argument("--lead-model")
    ld.add_argument("--lead-effort")
    ld.add_argument("--max-episodes", type=int, default=8)
    ld.add_argument("--episode-timeout", type=int, default=1200)
    ld.add_argument("--heartbeat-timeout", type=int, default=900)
    common(ld)
    sub.add_parser("status")
    s = sub.add_parser("stats")
    s.add_argument("--json", action="store_true")
    q = sub.add_parser("quota")
    q.add_argument("accounts", nargs="*")
    q.add_argument("--fresh", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("accounts", nargs="*")
    c.add_argument("--recheck", action="store_true")
    ad = sub.add_parser("add")
    ad.add_argument("id")
    ad.add_argument("--prompt", required=True)
    ad.add_argument("--account", default="any")
    ad.add_argument("--depends")
    ad.add_argument("--expect")
    ad.add_argument("--difficulty", type=int, choices=range(1, 7))
    ad.add_argument("--model")
    ad.add_argument("--effort")
    ad.add_argument("--image")
    ad.add_argument("--kind")
    sub.add_parser("dispatch")
    w = sub.add_parser("wait")
    w.add_argument("ids", nargs="*")
    w.add_argument("--timeout", type=int, default=900)
    cp = sub.add_parser("checkpoint")
    cp.add_argument("--done", required=True)
    cp.add_argument("--next", required=True)
    cp.add_argument("--decision")
    cp.add_argument("--by", default="leader")
    fi = sub.add_parser("finish")
    fi.add_argument("--answer", required=True)
    fi.add_argument("--by", default="leader")
    apv = sub.add_parser("approve")
    apv.add_argument("node")
    apv.add_argument("--by", default="human")
    nt = sub.add_parser("note")
    nt.add_argument("text")
    nt.add_argument("--by", default="human")
    sub.add_parser("_sched")
    for p in sub.choices.values():          # --run may also come after the subcommand
        p.add_argument("--run", default=argparse.SUPPRESS)
    a = ap.parse_args()

    if a.cmd == "stats":
        return cmd_stats(a)
    if a.cmd == "note":
        get_run(a).board(a.by, a.text)
        return 0
    if a.cmd == "_sched":
        Scheduler(get_run(a)).loop()
        return 0
    return {"run": cmd_run, "lead": cmd_lead, "status": cmd_status, "quota": cmd_quota, "check": cmd_check,
            "add": cmd_add, "dispatch": cmd_dispatch, "wait": cmd_wait, "checkpoint": cmd_checkpoint,
            "finish": cmd_finish, "approve": cmd_approve}[a.cmd](a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError) as e:
        sys.exit(f"team.py: {e}")
