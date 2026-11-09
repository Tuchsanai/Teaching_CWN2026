#!/usr/bin/env python3
"""agent-team: ให้หลายบัญชี Claude/Codex ทำงานร่วมกันด้วยกราฟงาน + หัวหน้าทีมที่สลับตัวได้"""
import sys
sys.dont_write_bytecode = True
import argparse
import contextlib
import copy
import fcntl
import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid

HERE = os.path.dirname(os.path.realpath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILLS, "yolo", "scripts"))
sys.path.insert(0, os.path.join(SKILLS, "cyolo", "scripts"))
import ma_common as mc  # noqa: E402
import yolo  # noqa: E402
import cyolo  # noqa: E402

TERMINAL = ("done", "failed", "blocked")
QUOTA_STOP = 80.0
QUOTA_WARN = 60.0
PLACEHOLDER = re.compile(r"\{\{\s*(file:)?([A-Za-z0-9_.-]+)\s*\}\}")
READY_CACHE = os.path.join(mc.TEAM_ROOT, "readiness.json")
SHORT_VALUE_LIMIT = 2000
BOARD_INLINE_LIMIT = 1500
GATE_POLL = 1.0


class GraphError(Exception):
    pass


# ---------- run directory & state ----------

def run_path(run_id):
    return os.path.join(mc.TEAM_ROOT, run_id)


def latest_run():
    try:
        with open(os.path.join(mc.TEAM_ROOT, "latest"), encoding="utf-8") as handle:
            return handle.read().strip() or None
    except OSError:
        return None


def resolve_run(run):
    run = run or os.environ.get("MA_TEAM_RUN") or latest_run()
    if not run or not os.path.exists(os.path.join(run_path(run), "state.json")):
        return None
    return run


def read_state(rd):
    # /workspace เป็น bind mount: เห็นไฟล์หาย/ค้างครึ่งชั่วขณะได้ ต้องอ่านซ้ำ ห้ามให้เธรดตาย
    last = None
    for _ in range(100):
        try:
            with open(os.path.join(rd, "state.json"), encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, ValueError) as exc:
            last = exc
            time.sleep(0.05)
    raise last


def write_state(rd, state):
    tmp = os.path.join(rd, "state.json.%s.tmp" % uuid.uuid4().hex[:6])
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=1)
    for attempt in range(50):
        try:
            os.replace(tmp, os.path.join(rd, "state.json"))
            return
        except OSError:
            if attempt == 49:
                raise
            time.sleep(0.05)


def lock_path(rd):
    # flock บน bind mount ไม่น่าเชื่อถือ จึงเก็บ lock ไว้ใน filesystem ของ container
    directory = "/tmp/agent-team-locks"
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, os.path.basename(rd.rstrip("/")) + ".lock")


@contextlib.contextmanager
def locked(rd):
    with open(lock_path(rd), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = read_state(rd)
        yield state
        write_state(rd, state)


def read_graph(rd):
    with open(os.path.join(rd, "graph.json"), encoding="utf-8") as handle:
        return json.load(handle)


def write_graph(rd, graph):
    tmp = os.path.join(rd, "graph.json.tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(graph, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(rd, "graph.json"))


def new_run(goal, mode):
    run_id = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]
    rd = run_path(run_id)
    for sub in ("msgs", "out", "approvals", "logs"):
        os.makedirs(os.path.join(rd, sub))
    with open(os.path.join(rd, "board.md"), "w", encoding="utf-8") as handle:
        handle.write("# Board ของ run %s\n\n" % run_id)
    with open(os.path.join(mc.TEAM_ROOT, "latest"), "w", encoding="utf-8") as handle:
        handle.write(run_id)
    state = dict(run_id=run_id, goal=goal, mode=mode, status="running", created=mc.now_iso(), nodes={},
                 accounts={}, stopped={}, quota={}, worker_switches=[], options={}, leader=None, finished=False)
    write_state(rd, state)
    return run_id, rd


def board_append(rd, author, text):
    path = os.path.join(rd, "board.md")
    with open(path, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.write("- [%s] %s: %s\n" % (mc.now_iso(), author, text.strip()))


def event(rd, name, run_id, **fields):
    row = dict(event=name, ts=mc.now_iso(), run_id=run_id, status="event")
    row.update(fields)
    mc.ledger_append(row, rd)


# ---------- readiness & quota ----------

def check_one(account):
    return (yolo.check if mc.cli_of(account) == "claude" else cyolo.check)(account)


def parallel_map(func, items):
    results = {}

    def work(item):
        try:
            results[item] = func(item)
        except Exception as exc:  # รายงานต่อบัญชีแทนการล้มทั้งคำสั่ง
            results[item] = exc

    threads = [threading.Thread(target=work, args=(item,)) for item in items]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return results


def all_accounts():
    return mc.accounts("yolo") + mc.accounts("cyolo")


def readiness(fresh=False, ttl=300):
    """ตรวจด้วยการเรียกจริง ใช้ผลซ้ำได้ไม่เกิน ttl วินาทีเพื่อประหยัดโควตา"""
    cached = {}
    if not fresh:
        try:
            with open(READY_CACHE, encoding="utf-8") as handle:
                data = json.load(handle)
            if time.time() - data["ts"] < ttl:
                cached = data["accounts"]
        except (OSError, ValueError, KeyError):
            cached = {}
    names = all_accounts()
    missing = [n for n in names if n not in cached]
    if missing:
        for name, res in parallel_map(check_one, missing).items():
            cached[name] = res if isinstance(res, dict) else dict(
                account=name, cli=mc.cli_of(name), status="error", label=mc.STATUS_TH["error"],
                detail=mc.short(res), checked_at=mc.now_iso(), duration_s=0)
        os.makedirs(mc.TEAM_ROOT, exist_ok=True)
        with open(READY_CACHE, "w", encoding="utf-8") as handle:
            json.dump({"ts": time.time(), "accounts": cached}, handle, ensure_ascii=False)
    return {n: cached[n] for n in names}


def quota_one(account):
    return (yolo.quota if mc.cli_of(account) == "claude" else cyolo.quota)(account)


def quota_of(names):
    out = {}
    for name, res in parallel_map(quota_one, list(names)).items():
        out[name] = res if isinstance(res, dict) else dict(account=name, has_data=False, as_of=None)
    return out


def quota_label(row):
    return (yolo.quota_cell if row.get("cli") != "codex" else cyolo.quota_cell)(row)


def effective_used(row):
    if not row or not row.get("has_data"):
        return None
    values = [v for v in (row.get("session_pct"), row.get("week_pct")) if v is not None]
    return max(values) if values else None


def refresh_quota(rd, names, max_age=120):
    with locked(rd) as state:
        known = copy.deepcopy(state["quota"])
    stale = [n for n in names if time.time() - known.get(n, {}).get("_fetched", 0) > max_age]
    if not stale:
        return
    fresh = quota_of(stale)
    with locked(rd) as state:
        for name, row in fresh.items():
            row["_fetched"] = time.time()
            state["quota"][name] = row
            used = effective_used(row)
            if used is not None and used >= state["options"].get("quota_stop", QUOTA_STOP):
                state["stopped"].setdefault(name, dict(reason="โควตาเกินเกณฑ์ (%g%%)" % used, ts=mc.now_iso()))


def account_tokens(state, name):
    total = 0
    for node in state["nodes"].values():
        for attempt in node.get("attempts", []):
            if attempt.get("account") == name:
                total += attempt.get("tokens", 0)
    return total


# ---------- graph normalization ----------

IMAGE_RE = re.compile(r"สร้างภาพ|วาดภาพ|image generation|generate (an? )?image|\.png\b", re.I)
CODE_REVIEW_RE = re.compile(r"ตรวจโค้ด|รีวิวโค้ด|code review|review (the )?code", re.I)
LONG_DOC_RE = re.compile(r"เอกสารยาว|long document|สรุปเอกสาร|summari[sz]e .*document", re.I)


def detect_kind(prompt):
    for kind, regex in (("image", IMAGE_RE), ("code_review", CODE_REVIEW_RE), ("long_doc", LONG_DOC_RE)):
        if regex.search(prompt or ""):
            return kind
    return "general"


def route_of(node):
    kind = node.get("kind") or detect_kind(node.get("prompt"))
    side = {"image": "cyolo", "code_review": "cyolo", "long_doc": "yolo"}.get(kind)
    return kind, side


def expand_macros(nodes):
    out = []
    for node in nodes:
        kind = node.get("type", "task")
        common = {k: node[k] for k in ("difficulty", "model", "effort", "timeout", "cwd") if k in node}
        deps = list(node.get("depends_on", []))
        if kind == "debate":
            sides = node.get("sides") or ["yolo", "cyolo"]
            if len(sides) != 2:
                raise GraphError("debate '%s': sides ต้องมี 2 ค่า" % node["id"])
            ids = [node["id"] + "__a", node["id"] + "__b"]
            for child, side in zip(ids, sides):
                out.append(dict(common, id=child, account=side, depends_on=deps,
                                prompt="%s\n\n(ตอบอย่างเป็นอิสระ ให้เหตุผลสั้น ๆ)" % node["prompt"]))
            judge = dict(common, id=node["id"], account=node.get("judge", "any"), depends_on=ids,
                         expect="contains:REASON:", difficulty=node.get("judge_difficulty", node.get("difficulty", 2)),
                         prompt=("คุณคือผู้ตัดสิน โจทย์: %s\nอ่านคำตอบ A จาก {{file:%s}} และคำตอบ B จาก {{file:%s}}\n"
                                 "เทียบแล้วตอบสามบรรทัดตามนี้เท่านั้น\nWINNER: A หรือ B\nANSWER: คำตอบที่ถูก\nREASON: เหตุผลสั้น ๆ")
                                % (node["prompt"], ids[0], ids[1]))
            out.append(judge)
        elif kind == "best_of":
            accounts = node.get("accounts") or []
            if len(accounts) < 2:
                raise GraphError("best_of '%s': accounts ต้องมีอย่างน้อย 2" % node["id"])
            ids = []
            for index, account in enumerate(accounts, 1):
                child = "%s__%d" % (node["id"], index)
                ids.append(child)
                out.append(dict(common, id=child, account=account, depends_on=deps, prompt=node["prompt"]))
            listing = "\n".join("%d: {{file:%s}}" % (i, c) for i, c in enumerate(ids, 1))
            judge = dict(common, id=node["id"], account=node.get("judge", "any"), depends_on=ids,
                         expect="regex:WINNER:\\s*\\d+", winner_of=ids,
                         difficulty=node.get("judge_difficulty", node.get("difficulty", 2)),
                         prompt=("คุณคือผู้ตัดสิน โจทย์: %s\nเกณฑ์ให้คะแนน: %s\nผลงานแต่ละหมายเลข อ่านจากไฟล์:\n%s\n"
                                 "ตอบตามนี้เท่านั้น\nSCORES: หมายเลข=คะแนน คั่นด้วยจุลภาค\nWINNER: หมายเลข\nREASON: เหตุผลสั้น ๆ")
                                % (node["prompt"], node.get("criteria", "ถูกต้องและกระชับ"), listing))
            out.append(judge)
        else:
            out.append(node)
    return out


def normalize(graph):
    if isinstance(graph, list):
        graph = dict(nodes=graph)
    if not isinstance(graph, dict) or not isinstance(graph.get("nodes"), list) or not graph["nodes"]:
        raise GraphError("กราฟต้องเป็น JSON ที่มี nodes เป็น list ที่ไม่ว่าง")
    nodes = expand_macros(graph["nodes"])
    ids = [node.get("id") for node in nodes]
    for node in nodes:
        nid = node.get("id")
        if not nid or not re.fullmatch(r"[A-Za-z0-9_.-]+", str(nid)):
            raise GraphError("id ไม่ถูกต้อง: %r (ใช้ A-Z a-z 0-9 _ . - เท่านั้น)" % nid)
        if node.get("type", "task") not in ("task", "review") and "prompt" not in node:
            raise GraphError("node '%s': ไม่มี prompt" % nid)
    if len(set(ids)) != len(ids):
        raise GraphError("id ซ้ำในกราฟ")
    known = set(ids)
    for node in nodes:
        node.setdefault("account", "any")
        node.setdefault("difficulty", 2)
        deps = list(node.get("depends_on", []))
        texts = [node.get("prompt", "")]
        for part in ("worker", "reviewer"):
            if isinstance(node.get(part), dict):
                texts.append(node[part].get("prompt", ""))
        for text in texts:
            for _, ref in PLACEHOLDER.findall(text or ""):
                if ref not in deps:
                    deps.append(ref)
        unknown = [d for d in deps if d not in known]
        if unknown:
            raise GraphError("node '%s' อ้างงานที่ไม่มี: %s" % (node["id"], ", ".join(unknown)))
        node["depends_on"] = deps
        if node.get("type") == "review":
            for part in ("worker", "reviewer"):
                if not isinstance(node.get(part), dict) or not node[part].get("prompt"):
                    raise GraphError("review '%s': ต้องมี %s.prompt" % (node["id"], part))
        kind, side = route_of(node)
        node["kind"] = kind
        if kind == "image":
            bad = node["account"] == "yolo" or re.fullmatch(r"yolo\d+", node["account"])
            if bad:
                raise GraphError("node '%s': สร้างภาพทำได้ฝั่ง Codex เท่านั้น" % node["id"])
    # ตรวจวงจร
    order = {node["id"]: set(node["depends_on"]) for node in nodes}
    done = set()
    while len(done) < len(order):
        ready = [k for k, deps in order.items() if k not in done and deps <= done]
        if not ready:
            raise GraphError("กราฟมีวงจร: %s" % ", ".join(sorted(set(order) - done)))
        done.update(ready)
    graph["nodes"] = nodes
    return graph


def is_pinned(account):
    return bool(re.fullmatch(r"c?yolo\d+", account or ""))


def bound_side(node):
    account = node.get("account")
    if account in ("yolo", "cyolo"):
        return account
    if node.get("kind") == "image":
        return "cyolo"
    return None


def side_of(account):
    return "cyolo" if account.startswith("cyolo") else "yolo"


def score(state, name):
    used = effective_used(state["quota"].get(name))
    used = 50.0 if used is None else used
    load = sum(1 for n in state["nodes"].values()
               if n.get("status") == "running" and n.get("account") == name)
    load += sum(1 for n in state["nodes"].values()
                if n.get("status") not in TERMINAL and n.get("status") != "running" and n.get("planned") == name)
    return (used, load, account_tokens(state, name), name)


def candidates(state, node, exclude=()):
    account = node.get("account")
    ready = [a for a, v in state["accounts"].items()
             if v.get("status") == "ready" and a not in state["stopped"] and a not in exclude]
    if is_pinned(account):
        return [a for a in ready if a == account]
    bound = bound_side(node)
    pool = [a for a in ready if side_of(a) == bound] if bound else list(ready)
    prefer = node.get("prefer")
    _, routed = route_of(node)
    if routed and not bound:
        same = [a for a in pool if side_of(a) == routed]
        pool = same or pool
    ranked = sorted(pool, key=lambda a: score(state, a))
    if prefer in ranked:
        ranked.remove(prefer)
        ranked.insert(0, prefer)
    return ranked


def plan_nodes(rd):
    with locked(rd) as state:
        graph = read_graph(rd)
        for node in graph["nodes"]:
            rec = state["nodes"][node["id"]]
            if rec["status"] in ("pending",) and not rec.get("planned"):
                ranked = candidates(state, node)
                rec["planned"] = ranked[0] if ranked else None


# ---------- prompts & expect ----------

def out_file(rd, nid):
    return os.path.join(rd, "out", nid + ".md")


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def render(rd, text):
    def sub(match):
        ref = match.group(2)
        if match.group(1):
            return out_file(rd, ref)
        value = strip_board(read_text(out_file(rd, ref))).strip()
        if len(value) > SHORT_VALUE_LIMIT:
            return "[ค่ายาว ให้อ่านจากไฟล์ %s]" % out_file(rd, ref)
        return value
    return PLACEHOLDER.sub(sub, text or "")


def strip_board(text):
    return "\n".join(line for line in text.splitlines() if not re.match(r"\s*BOARD:", line))


def harvest_board(rd, text, author):
    for line in text.splitlines():
        match = re.match(r"\s*BOARD:\s*(.+)$", line)
        if match:
            board_append(rd, author, match.group(1))


EXPECT_HINTS = {"number": "ตอบเป็นตัวเลขล้วนเท่านั้น ไม่มีข้อความอื่น", "integer": "ตอบเป็นจำนวนเต็มล้วนเท่านั้น ไม่มีข้อความอื่น",
                "json": "ตอบเป็น JSON ที่ถูกต้องเท่านั้น ไม่มี markdown"}


def check_expect(expect, text):
    if not expect:
        return True, None
    value = text.strip()
    if expect == "number":
        return (bool(re.fullmatch(r"-?\d+(\.\d+)?", value)), "ต้องเป็นตัวเลขล้วน")
    if expect == "integer":
        return (bool(re.fullmatch(r"-?\d+", value)), "ต้องเป็นจำนวนเต็มล้วน")
    if expect == "json":
        try:
            json.loads(value)
            return True, None
        except ValueError:
            return False, "ไม่ใช่ JSON"
    if expect.startswith("regex:"):
        return (bool(re.search(expect[6:], value)), "ไม่ตรง regex %s" % expect[6:])
    if expect.startswith("contains:"):
        return (expect[9:] in value, "ไม่มีข้อความ %s" % expect[9:])
    if expect == "nonempty":
        return bool(value), "คำตอบว่าง"
    return False, "expect ไม่รู้จัก: %s" % expect


def compose_prompt(rd, node, base=None):
    """ประกอบ prompt ของงานจริง: ค่าที่แทรก กระดาน โฟลเดอร์ทำงาน รูปแบบคำตอบ"""
    parts = []
    board = read_text(os.path.join(rd, "board.md"))
    entries = board.split("\n", 2)[2].strip() if board.count("\n") >= 2 else ""
    if entries:
        if len(entries) <= BOARD_INLINE_LIMIT:
            parts.append("ความรู้กลางจากทีม (board.md) อ่านก่อนเริ่ม:\n%s" % entries)
        else:
            parts.append("อ่านความรู้กลางจากไฟล์ %s ก่อนเริ่มงาน" % os.path.join(rd, "board.md"))
    if node.get("cwd"):
        parts.append("โฟลเดอร์ทำงาน: %s ใช้ absolute path เมื่ออ่านเขียนไฟล์" % node["cwd"])
    progress = os.path.join(rd, "msgs", node["id"] + "__progress.md")
    if os.path.exists(progress):
        parts.append("มีความคืบหน้าจากผู้ทำก่อนหน้าที่ %s อ่านแล้วทำต่อ ไม่ต้องเริ่มใหม่" % progress)
    elif int(node.get("difficulty", 2)) >= 3:
        parts.append("งานยาว: เขียนความคืบหน้าต่อท้ายไฟล์ %s เป็นระยะ" % progress)
    parts.append(render(rd, base if base is not None else node.get("prompt", "")))
    if node.get("expect") in EXPECT_HINTS:
        parts.append(EXPECT_HINTS[node["expect"]])
    if node.get("board"):
        parts.append("ข้อเท็จจริงสำคัญที่ agent อื่นควรรู้ ให้ใส่เป็นบรรทัดขึ้นต้นด้วย BOARD: ถ้าไม่มีไม่ต้องกล่าวถึง")
    return "\n\n".join(parts)


def invoke_for(rd, run_id, label, account, node, prompt, simulate):
    difficulty = int(node.get("difficulty", 2))
    timeout = int(node.get("timeout") or read_state(rd)["options"].get("timeout", 600))
    cwd = node.get("cwd")
    if cwd:
        os.makedirs(cwd, exist_ok=True)
    if mc.cli_of(account) == "claude":
        model, effort = yolo.resolve(difficulty, node.get("model"), node.get("effort"))
        return yolo.invoke(account, prompt, model, effort, cwd=cwd, timeout=timeout, run_id=run_id,
                           node=label, run_dir=rd, simulate=simulate)
    model, effort = cyolo.resolve(account, difficulty, node.get("model"), node.get("effort"))
    if node.get("kind") == "image":
        path = node.get("out") or os.path.join(rd, "out", node["id"] + ".png")
        res = cyolo.make_image(account, prompt, path, cwd=cwd, timeout=timeout, run_id=run_id,
                               node=label, run_dir=rd, simulate=simulate)
        if res["ok"]:
            res["result"] = path
        return res
    return cyolo.invoke(account, prompt, model, effort, cwd=cwd, timeout=timeout, run_id=run_id,
                        node=label, run_dir=rd, simulate=simulate)


# ---------- execution ----------

def should_simulate(rd, account):
    with locked(rd) as state:
        opts = state["options"]
        if account in opts.get("sim_limit", []):
            return True
        if opts.get("sim_once") and not opts.get("sim_once_used") and side_of(account):
            opts["sim_once_used"] = True
            opts["sim_once_account"] = account
            return True
    return False


def record_attempt(rd, nid, res):
    row = res["row"]
    attempt = dict(account=res["account"], model=row["model"], effort=row["effort"], status=row["status"],
                   tokens=mc.total_tokens(row), input=row["input_tokens"], output=row["output_tokens"],
                   duration=row["duration_s"], error=row["error"])
    with locked(rd) as state:
        rec = state["nodes"][nid]
        rec.setdefault("attempts", []).append(attempt)
        budget = state["options"].get("worker_token_budget")
        name = res["account"]
        if budget and account_tokens(state, name) >= budget and name not in state["stopped"]:
            state["stopped"][name] = dict(reason="เกินงบโทเค็นต่อบัญชี (%d)" % budget, ts=mc.now_iso())


def switch_event(rd, run_id, nid, frm, to, reason, kind):
    with locked(rd) as state:
        state["worker_switches"].append(dict(node=nid, frm=frm, to=to, reason=reason, kind=kind, ts=mc.now_iso()))
    board_append(rd, "team", "ย้ายงาน %s จาก %s ไป %s (%s)" % (nid, frm, to, reason))
    event(rd, "worker_switch", run_id, node=nid, frm=frm, to=to, reason=reason, kind=kind)
    print("[worker_switch] %s: %s -> %s (%s)" % (nid, frm, to, reason), flush=True)


def claim(rd, node, exclude, run_id):
    """พยายามจองบัญชี คืน ('run', account) / ('wait', None) / ('fail', เหตุผล)"""
    with locked(rd) as state:
        ranked = candidates(state, node, exclude)
        planned = state["nodes"][node["id"]].get("planned")
        if not ranked:
            account = node.get("account")
            if is_pinned(account):
                info = state["accounts"].get(account, {})
                stop = state["stopped"].get(account, {})
                reason = stop.get("reason") or info.get("label") or "ไม่พบบัญชี"
                return "fail", "บัญชีที่ระบุ %s ใช้ไม่ได้ (%s) ไม่ย้ายให้โดยอัตโนมัติ" % (account, reason)
            return "fail", "ไม่มีบัญชีที่พร้อมสำหรับงานนี้"
        total = sum(1 for n in state["nodes"].values() if n.get("status") == "running")
        if total >= state["options"].get("max_total", 8):
            return "wait", None
        per = state["options"].get("max_per_account", 3)
        chosen = None
        for name in ranked:
            running = sum(1 for n in state["nodes"].values() if n.get("status") == "running" and n.get("account") == name)
            if running < per:
                chosen = name
                break
        if not chosen:
            return "wait", None
        rec = state["nodes"][node["id"]]
        rec.update(status="running", account=chosen, started=rec.get("started") or mc.now_iso())
        stopped_reason = state["stopped"].get(planned, {}).get("reason") if planned else None
    if planned and planned != chosen and stopped_reason and not exclude:
        switch_event(rd, run_id, node["id"], planned, chosen, stopped_reason, "proactive")
    return "run", chosen


def run_attempts(rd, run_id, node, prompt, label):
    """รันหนึ่งงานพร้อมย้ายบัญชีเมื่อโควตา/ล็อกอินล้ม คืนผล invoke หรือ dict(ok=False, ...)"""
    exclude = []
    pending = None
    while True:
        verdict, account = claim(rd, node, exclude, run_id)
        if verdict == "wait":
            time.sleep(0.3)
            continue
        if verdict == "fail":
            reason = account if not pending else "%s; ย้ายต่อไม่ได้: %s" % (pending[1], account)
            return dict(ok=False, error=reason, error_kind="no_account", result="")
        if pending:
            switch_event(rd, run_id, node["id"], pending[0], account, pending[1], "reactive")
            pending = None
        simulate = should_simulate(rd, account)
        res = invoke_for(rd, run_id, label, account, node, prompt, simulate)
        res["account"] = account
        record_attempt(rd, node["id"], res)
        if res["ok"] or res.get("error_kind") not in ("quota", "rate_limit", "auth"):
            with locked(rd) as state:
                state["nodes"][node["id"]]["status"] = "running"
            return res
        reason = "%s: %s" % (res["error_kind"], res["error"])
        with locked(rd) as state:
            state["stopped"].setdefault(account, dict(reason=reason, ts=mc.now_iso()))
            state["nodes"][node["id"]]["account"] = None
            state["nodes"][node["id"]]["status"] = "pending"
        if is_pinned(node.get("account")):
            return dict(res, error="บัญชีที่ระบุ %s ล้ม (%s) ไม่ย้ายให้โดยอัตโนมัติ" % (account, res["error"]))
        exclude.append(account)
        pending = (account, reason)


def finish_node(rd, nid, status, error=None):
    with locked(rd) as state:
        rec = state["nodes"][nid]
        rec.update(status=status, ended=mc.now_iso())
        if error:
            rec["error"] = error


def write_out(rd, nid, text):
    with open(out_file(rd, nid), "w", encoding="utf-8") as handle:
        handle.write(text)


def notify_dependents(rd, nid, author):
    graph = read_graph(rd)
    for node in graph["nodes"]:
        if nid in node.get("depends_on", []):
            path = os.path.join(rd, "msgs", "%s__%s.md" % (nid, node["id"]))
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("from: %s (%s)\nto: %s\nout: %s\ntime: %s\n" % (nid, author, node["id"], out_file(rd, nid), mc.now_iso()))


def run_simple(rd, run_id, node):
    res = run_attempts(rd, run_id, node, compose_prompt(rd, node), node["id"])
    text = res.get("result") or ""
    if res.get("structured") is not None and not text:
        text = json.dumps(res["structured"], ensure_ascii=False)
    author = res.get("account") or "-"
    if text:
        harvest_board(rd, text, "%s/%s" % (author, node["id"]))
        write_out(rd, node["id"], text)
    if not res.get("ok"):
        finish_node(rd, node["id"], "failed", res.get("error"))
        return
    ok, reason = check_expect(node.get("expect"), strip_board(text))
    if not ok:
        finish_node(rd, node["id"], "failed", "ผลไม่ตรงรูปแบบ expect=%s: %s (เก็บคำตอบไว้ใน out/%s.md)" % (node["expect"], reason, node["id"]))
        return
    if node.get("winner_of"):
        match = re.search(r"WINNER:\s*(\d+)", text)
        index = int(match.group(1)) if match else 0
        if 1 <= index <= len(node["winner_of"]):
            shutil.copyfile(out_file(rd, node["winner_of"][index - 1]), os.path.join(rd, "out", node["id"] + ".winner.md"))
    notify_dependents(rd, node["id"], author)
    finish_node(rd, node["id"], "done")


def run_review(rd, run_id, node):
    max_rounds = int(node.get("max_rounds", 3))
    worker = dict({k: v for k, v in node.items() if k in ("difficulty", "model", "effort", "timeout", "cwd")}, id=node["id"], account=node.get("worker", {}).get("account", node.get("account", "any")))
    worker.update(node["worker"])
    reviewer = dict(worker)
    reviewer.update(node["reviewer"])
    work_path, feedback = out_file(rd, node["id"]), None
    for round_no in range(1, max_rounds + 1):
        base = worker["prompt"]
        if feedback:
            base = ("%s\n\nผลงานรอบก่อนอยู่ที่ %s\nแก้ตามความเห็นผู้ตรวจในไฟล์ %s\n"
                    "ตอบผลงานฉบับเต็มเป็นคำตอบนี้เท่านั้น ไม่ต้องอธิบาย ไม่ต้องแก้ไฟล์เหล่านั้นเอง") % (base, work_path, feedback)
        spec = dict(worker, id=node["id"])
        res = run_attempts(rd, run_id, spec, compose_prompt(rd, spec, base), "%s.r%d.work" % (node["id"], round_no))
        if not res.get("ok"):
            finish_node(rd, node["id"], "failed", res.get("error"))
            return
        write_out(rd, node["id"], strip_board(res["result"]))
        with open(os.path.join(rd, "out", "%s.r%d.work.md" % (node["id"], round_no)), "w", encoding="utf-8") as handle:
            handle.write(res["result"])
        review_prompt = "%s\n\nผลงานที่ต้องตรวจอยู่ที่ %s\nบรรทัดแรกตอบ APPROVED ถ้าผ่านทุกข้อ ไม่เช่นนั้นตอบ CHANGES แล้วตามด้วยสิ่งที่ต้องแก้" % (reviewer["prompt"], work_path)
        spec = dict(reviewer, id=node["id"])
        res = run_attempts(rd, run_id, spec, compose_prompt(rd, spec, review_prompt), "%s.r%d.review" % (node["id"], round_no))
        if not res.get("ok"):
            finish_node(rd, node["id"], "failed", res.get("error"))
            return
        feedback = os.path.join(rd, "out", "%s.r%d.review.md" % (node["id"], round_no))
        with open(feedback, "w", encoding="utf-8") as handle:
            handle.write(res["result"])
        harvest_board(rd, res["result"], "%s/%s" % (res["account"], node["id"]))
        first = strip_board(res["result"]).strip().splitlines()[0] if strip_board(res["result"]).strip() else ""
        if re.match(r"\s*\**APPROVED", first):
            with locked(rd) as state:
                state["nodes"][node["id"]]["rounds"] = round_no
            notify_dependents(rd, node["id"], res["account"])
            finish_node(rd, node["id"], "done")
            return
    finish_node(rd, node["id"], "failed", "ผู้ตรวจไม่ APPROVED ภายใน max_rounds=%d (ผลล่าสุดใน out/%s.md)" % (max_rounds, node["id"]))


def wait_gate(rd, nid, gate_timeout):
    path = os.path.join(rd, "approvals", nid + ".ok")
    with locked(rd) as state:
        state["nodes"][nid]["status"] = "waiting_approval"
    print("[gate] %s รออนุมัติ: team.py approve %s %s" % (nid, os.path.basename(rd), nid), flush=True)
    started = time.time()
    while not os.path.exists(path):
        if gate_timeout and time.time() - started > gate_timeout:
            return False
        time.sleep(GATE_POLL)
    with locked(rd) as state:
        state["nodes"][nid]["status"] = "pending"
    return True


def execute(rd, run_id, nid, gate_timeout=3600):
    try:
        _execute(rd, run_id, nid, gate_timeout)
    except Exception as exc:  # เธรด/โปรเซสลูกตายเงียบไม่ได้ งานต้องไม่ค้างสถานะ pending
        try:
            finish_node(rd, nid, "failed", "ตัวรันล้ม: %s" % mc.short(repr(exc)))
        except Exception:
            pass
        print("[failed] %s: %r" % (nid, exc), flush=True)


def _execute(rd, run_id, nid, gate_timeout):
    """รัน node จนจบ: รอ deps → human gate → จองบัญชี → เรียก"""
    graph = read_graph(rd)
    node = next(n for n in graph["nodes"] if n["id"] == nid)
    while True:
        state = read_state(rd)
        statuses = [state["nodes"].get(d, {}).get("status") for d in node.get("depends_on", [])]
        if any(s in ("failed", "blocked") for s in statuses):
            bad = [d for d in node["depends_on"] if state["nodes"][d]["status"] in ("failed", "blocked")]
            finish_node(rd, nid, "blocked", "งานก่อนหน้าไม่สำเร็จ: %s" % ", ".join(bad))
            print("[blocked] %s" % nid, flush=True)
            return
        if all(s == "done" for s in statuses):
            break
        time.sleep(0.3)
    if node.get("approve") and not os.path.exists(os.path.join(rd, "approvals", nid + ".ok")):
        if not wait_gate(rd, nid, gate_timeout):
            finish_node(rd, nid, "waiting_approval", "ยังไม่อนุมัติภายในเวลา")
            return
    print("[start] %s" % nid, flush=True)
    try:
        if node.get("type") == "review":
            run_review(rd, run_id, node)
        else:
            run_simple(rd, run_id, node)
    except Exception as exc:
        finish_node(rd, nid, "failed", "ข้อผิดพลาดในตัวรัน: %s" % mc.short(repr(exc)))
    status = read_state(rd)["nodes"][nid]["status"]
    print("[%s] %s" % (status, nid), flush=True)
    names = [a["account"] for a in read_state(rd)["nodes"][nid].get("attempts", [])]
    if names:
        refresh_quota(rd, set(names[-1:]))


def init_nodes(rd, state, nodes):
    for node in nodes:
        state["nodes"].setdefault(node["id"], dict(status="pending", account=None, planned=None, attempts=[], kind=node.get("kind")))


def node_row(rd, nid, rec):
    attempts = rec.get("attempts", [])
    last = attempts[-1] if attempts else {}
    return dict(node=nid, account=rec.get("account") or last.get("account"),
                model=last.get("model"), effort=last.get("effort"),
                duration=round(sum(a.get("duration", 0) for a in attempts), 1),
                input=sum(a.get("input", 0) for a in attempts), output=sum(a.get("output", 0) for a in attempts),
                status=rec.get("status"), error=rec.get("error"), out=out_file(rd, nid))


def result_table(rd, state):
    rows = [node_row(rd, nid, rec) for nid, rec in state["nodes"].items()]
    table = mc.md_table(["งาน", "บัญชี", "รุ่น/effort", "เวลา s", "input tokens", "output tokens", "สถานะ"],
                        [[r["node"], r["account"], "%s/%s" % (r["model"], r["effort"]) if r["model"] else "-",
                          r["duration"], r["input"], r["output"],
                          r["status"] + (" — " + mc.short(r["error"], 90) if r["error"] else "")] for r in rows])
    return rows, table


def used_accounts(state):
    used = []
    for rec in state["nodes"].values():
        for attempt in rec.get("attempts", []):
            if attempt.get("account") not in used:
                used.append(attempt["account"])
    leader = state.get("leader") or {}
    for item in leader.get("episodes", []):
        if item.get("account") not in used:
            used.append(item["account"])
    return used


def quota_section(rd, state):
    used = used_accounts(state)
    rows = quota_of(used)
    table = mc.md_table(["บัญชี", "โควตาล่าสุด", "เวลาของข้อมูล"],
                        [[n, quota_label(rows[n]), rows[n].get("as_of") or "ไม่มีข้อมูล"] for n in used])
    return rows, table


def execute_graph(rd, run_id, nids, gate_timeout):
    threads = [threading.Thread(target=execute, args=(rd, run_id, nid, gate_timeout)) for nid in nids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def set_field(graph, expression):
    if "=" not in expression or "." not in expression.split("=", 1)[0]:
        raise GraphError("--set ต้องเป็น node.field=value")
    target, value = expression.split("=", 1)
    nid, field = target.rsplit(".", 1)
    for node in graph["nodes"]:
        if node["id"] == nid:
            if value == "":
                node.pop(field, None)
            else:
                node[field] = value
            return
    raise GraphError("ไม่พบ node: %s" % nid)


def repair_text(raw):
    """stdin จาก PowerShell 5.1 มีทั้ง BOM และ UTF-8 ที่ถูกอ่านเป็น ANSI: ซ่อมก่อน parse"""
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    text = raw.decode("utf-8", "replace")
    for encoding in ("cp874", "cp1252"):
        try:
            fixed = text.encode(encoding).decode("utf-8")
        except (UnicodeError, ValueError):
            continue
        if fixed != text and len(fixed) < len(text):
            return fixed
    return text


def load_graph(source):
    if source == "-":
        raw = sys.stdin.buffer.read()
    else:
        with open(source, "rb") as handle:
            raw = handle.read()
    if not raw.strip():
        raise GraphError("กราฟว่าง")
    text = repair_text(raw)
    if re.search(r"\?{4,}", text) and all(ord(c) < 128 for c in text):
        raise GraphError("ข้อความภาษาไทยหายระหว่างส่งผ่าน stdin (เหลือ ????): ใช้ docker cp แล้วส่ง path แทน")
    try:
        return json.loads(text)
    except ValueError as exc:
        raise GraphError("JSON ไม่ถูกต้อง: %s" % exc)


def cmd_run(args):
    os.makedirs(mc.TEAM_ROOT, exist_ok=True)
    if args.resume:
        run_id = args.resume
        rd = run_path(run_id)
        if not os.path.exists(os.path.join(rd, "state.json")):
            print("ไม่พบ run: %s" % run_id, file=sys.stderr)
            return 2
        graph = read_graph(rd)
        for expression in args.set or []:
            set_field(graph, expression)
        write_graph(rd, normalize(graph))
        rerun = []
        with locked(rd) as state:
            for node in graph["nodes"]:
                rec = state["nodes"].setdefault(node["id"], dict(status="pending", attempts=[]))
                if rec["status"] != "done":
                    rerun.append(node["id"])
                    rec.update(status="pending", account=None, planned=None, attempts=[], error=None, ended=None)
            state["status"] = "running"
    else:
        graph = normalize(load_graph(args.graph))
        run_id, rd = new_run(graph.get("goal", ""), "run")
        write_graph(rd, graph)
        rerun = [n["id"] for n in graph["nodes"]]
        with locked(rd) as state:
            init_nodes(rd, state, graph["nodes"])
    with locked(rd) as state:
        state["options"].update(max_total=args.max_total, max_per_account=args.max_per_account,
                                timeout=args.timeout, worker_token_budget=args.worker_token_budget,
                                quota_stop=args.quota_stop)
        state["options"]["sim_limit"] = [x for x in (args.simulate_limit or "").split(",") if x]
    ready = readiness(fresh=args.fresh_check)
    names = [n for n, v in ready.items() if v["status"] == "ready"]
    quota = quota_of(names)
    with locked(rd) as state:
        state["accounts"] = ready
        for name, row in quota.items():
            row["_fetched"] = time.time()
            state["quota"][name] = row
    plan_nodes(rd)
    print("run_id: %s\nrun dir: %s\nบัญชีพร้อม: %s" % (run_id, rd, ", ".join(names) or "ไม่มี"), flush=True)
    skipped = ["%s (%s)" % (n, v["label"]) for n, v in ready.items() if v["status"] != "ready"]
    if skipped:
        print("ข้ามบัญชี: " + ", ".join(skipped), flush=True)
    if not names:
        print("ไม่มีบัญชีที่พร้อม", file=sys.stderr)
        return 1
    execute_graph(rd, run_id, rerun, args.gate_timeout)
    state = read_state(rd)
    state["status"] = "done"
    rows, table = result_table(rd, state)
    stuck = [r["node"] for r in rows if r["status"] not in TERMINAL and r["status"] != "waiting_approval"]
    for nid in stuck:
        finish_node(rd, nid, "failed", "ตัวรันหยุดก่อนงานจบ")
    if stuck:
        state = read_state(rd)
        rows, table = result_table(rd, state)
    waiting = [r["node"] for r in rows if r["status"] == "waiting_approval"]
    failed = [r["node"] for r in rows if r["status"] in ("failed", "blocked")]
    with locked(rd) as locked_state:
        locked_state["status"] = "failed" if failed else "waiting" if waiting else "done"
    qrows, qtable = quota_section(rd, state)
    if args.json:
        print(json.dumps(dict(run_id=run_id, status="failed" if failed else "waiting" if waiting else "done",
                              run_dir=rd, nodes=rows, quota=[qrows[n] for n in qrows],
                              worker_switches=state["worker_switches"]), ensure_ascii=False))
    else:
        print("\n## สรุป run %s\n%s\n\n## โควตาของบัญชีที่ใช้\n%s" % (run_id, table, qtable))
        if state["worker_switches"]:
            print("\n## การย้ายงาน\n%s" % switch_table(state))
        if failed:
            print("\nงานไม่สำเร็จ: %s\nแก้แล้วรันต่อ: team.py run --resume %s" % (", ".join(failed), run_id))
        if waiting:
            print("\nรออนุมัติ: %s\nอนุมัติแล้วรันต่อ: team.py approve %s <node> แล้ว team.py run --resume %s" % (", ".join(waiting), run_id, run_id))
    if failed:
        return 1
    return 3 if waiting else 0


def switch_table(state):
    return mc.md_table(["งาน", "จาก", "ไป", "ชนิด", "เหตุผล"],
                       [[s["node"], s["frm"], s["to"], s["kind"], mc.short(s["reason"], 120)] for s in state["worker_switches"]])


# ---------- status / simple commands ----------

def account_rows(state):
    leader = (state.get("leader") or {}).get("current")
    rows = []
    ledger = [r for r in mc.read_ledger(os.path.join(run_path(state["run_id"]), "ledger.jsonl")) if not r.get("event")]
    for name, info in sorted(state["accounts"].items()):
        running = sum(1 for n in state["nodes"].values() if n.get("status") == "running" and n.get("account") == name)
        queued = sum(1 for n in state["nodes"].values() if n.get("status") == "pending" and n.get("planned") == name)
        tokens = sum(mc.total_tokens(r) for r in ledger if r.get("account") == name)  # รวมโทเค็นของหัวหน้าด้วย
        quota = state["quota"].get(name, {})
        used = effective_used(quota)
        if info.get("status") != "ready":
            status = "ใช้ไม่ได้ (%s)" % info.get("label")
        elif name in state["stopped"]:
            status = "หยุดรับงาน (%s)" % mc.short(state["stopped"][name].get("reason"), 60)
        elif used is not None and used >= QUOTA_WARN:
            status = "ใกล้หมด"
        else:
            status = "พร้อม"
        role = "หัวหน้า" if name == leader else "ลูกทีม" if tokens or running or queued else "-"
        qtext = "%s (ข้อมูล %s)" % (quota_label(quota), quota.get("as_of")) if quota.get("has_data") else "ไม่มีข้อมูล"
        rows.append([name, role, running, queued, tokens, qtext, status])
    return rows


def cmd_status(args):
    run = resolve_run(args.run)
    if not run:
        print("ยังไม่มี run ใน %s" % mc.TEAM_ROOT)
        return 0
    rd = run_path(run)
    state = read_state(rd)
    rows, table = result_table(rd, state)
    if args.json:
        print(json.dumps(dict(run_id=run, status=state["status"], accounts=account_rows(state), nodes=rows,
                              leader=state.get("leader"), worker_switches=state["worker_switches"]), ensure_ascii=False))
        return 0
    print("run %s · สถานะ %s · %s\n" % (run, state["status"], rd))
    print(mc.md_table(["บัญชี", "บทบาท", "งานที่รัน", "งานในคิว", "tokens ที่ใช้ใน run", "โควตาล่าสุด", "สถานะ"], account_rows(state)))
    print("\n" + table)
    if state["worker_switches"]:
        print("\n## การย้ายงาน\n" + switch_table(state))
    return 0


def cmd_check(args):
    ready = readiness(fresh=not args.cached)
    rows = list(ready.values())
    if args.json:
        print(json.dumps(rows, ensure_ascii=False))
    else:
        print(mc.md_table(["บัญชี", "สถานะ", "รายละเอียด", "เวลาเรียก s", "ตรวจเมื่อ"],
                          [[r["account"], r["label"], r["detail"], r["duration_s"], r["checked_at"]] for r in rows]))
    return 0


def cmd_quota(args):
    rows = quota_of(all_accounts())
    if args.json:
        print(json.dumps(list(rows.values()), ensure_ascii=False))
    else:
        print(mc.md_table(["บัญชี", "โควตาล่าสุด", "เวลาของข้อมูล"],
                          [[n, quota_label(rows[n]), rows[n].get("as_of") or "ไม่มีข้อมูล"] for n in sorted(rows)]))
    return 0


def cmd_approve(args):
    rd = run_path(args.run)
    if not os.path.isdir(rd):
        print("ไม่พบ run: %s" % args.run, file=sys.stderr)
        return 2
    with open(os.path.join(rd, "approvals", args.node + ".ok"), "w", encoding="utf-8") as handle:
        handle.write(mc.now_iso() + "\n")
    print("อนุมัติ %s แล้ว" % args.node)
    return 0


def cmd_board(args):
    run = resolve_run(args.run)
    if not run:
        print("ยังไม่มี run ใน %s" % mc.TEAM_ROOT)
        return 0
    rd = run_path(run)
    if args.add:
        board_append(rd, args.author or os.environ.get("MA_LEAD_ACCOUNT", "user"), args.add)
    print(read_text(os.path.join(rd, "board.md")), end="")
    return 0


# ---------- leader tools (เรียกโดยหัวหน้าทีมระหว่างรอบ) ----------

def lead_budget_exceeded(state):
    leader = state.get("leader") or {}
    budget = leader.get("budget")
    return bool(budget and leader.get("tokens_live", 0) >= budget)


def over_budget_msg(state):
    return ("BUDGET_EXCEEDED: หัวหน้าใช้โทเค็นถึงงบแล้ว ให้เรียก checkpoint แล้วจบรอบทันที")


def cmd_dispatch(args):
    run = resolve_run(args.run)
    if not run:
        print("ไม่พบ run", file=sys.stderr)
        return 2
    rd = run_path(run)
    gate = read_state(rd)
    if (gate.get("leader") or {}).get("handoff_requested"):
        # งบหมดแล้ว: งานชิ้นใหม่ต้องเป็นของหัวหน้าคนถัดไป ไม่พึ่งให้โมเดลหยุดเอง
        print("REFUSED: " + over_budget_msg(gate))
        return 3
    prompt = mc.read_prompt(args)
    node = dict(id=args.node, account=args.account or "any", prompt=prompt, difficulty=args.difficulty)
    for field in ("model", "effort", "expect", "cwd", "kind", "prefer"):
        if getattr(args, field, None):
            node[field] = getattr(args, field)
    if args.depends:
        node["depends_on"] = [x for x in args.depends.split(",") if x]
    with locked(rd) as state:
        cap = state["options"].get("worker_max_difficulty")
        if cap:
            node["difficulty"] = min(int(node["difficulty"]), int(cap))
        graph = read_graph(rd)
        if any(n["id"] == node["id"] for n in graph["nodes"]):
            print("ERROR: มี node ชื่อ %s แล้ว" % node["id"], file=sys.stderr)
            return 2
        graph["nodes"].append(node)
        try:
            write_graph(rd, normalize(graph))
        except GraphError as exc:
            print("ERROR: %s" % exc, file=sys.stderr)
            return 2
        graph = read_graph(rd)
        node = next(n for n in graph["nodes"] if n["id"] == node["id"])
        rec = dict(status="pending", account=None, planned=None, attempts=[], kind=node.get("kind"))
        state["nodes"][node["id"]] = rec
        ranked = candidates(state, node)
        rec["planned"] = ranked[0] if ranked else None
        leader = state.get("leader") or {}
        leader["dispatches"] = leader.get("dispatches", 0) + 1
        over = lead_budget_exceeded(state)
        if over:
            leader["handoff_requested"] = "งบโทเค็นหัวหน้า"
        limit = leader.get("max_dispatch") and leader["dispatches"] >= leader["max_dispatch"]
        planned = rec["planned"]
    log = open(os.path.join(rd, "logs", node["id"] + ".log"), "ab")
    subprocess.Popen([sys.executable, os.path.realpath(__file__), "_worker", "--run", run, "--node", node["id"]],
                     stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True, env=mc.clean_env("CLAUDE_CODE_"))
    log.close()
    print("OK dispatched %s planned=%s out=%s" % (node["id"], planned, out_file(rd, node["id"])))
    if over:
        print(over_budget_msg(state))
    elif limit:
        print("EPISODE_LIMIT: สั่งงานครบจำนวนต่อรอบแล้ว ให้ checkpoint แล้วจบรอบ หัวหน้ารอบถัดไปจะทำต่อ")
    return 0


def cmd_worker(args):
    rd = run_path(args.run)
    execute(rd, args.run, args.node, gate_timeout=args.gate_timeout)
    return 0


def cmd_wait(args):
    run = resolve_run(args.run)
    if not run:
        print("ไม่พบ run", file=sys.stderr)
        return 2
    rd = run_path(run)
    wanted = [x for x in args.nodes.split(",") if x]
    deadline = time.time() + min(args.timeout, 600)
    beat = 0
    while True:
        state = read_state(rd)
        unknown = [n for n in wanted if n not in state["nodes"]]
        if unknown:
            print("ไม่พบ node: %s" % ", ".join(unknown), file=sys.stderr)
            return 2
        if time.time() - beat > 5:
            with locked(rd) as locked_state:
                if locked_state.get("leader"):
                    locked_state["leader"]["heartbeat"] = time.time()
            beat = time.time()
        if all(state["nodes"][n]["status"] in TERMINAL for n in wanted):
            break
        if time.time() > deadline:
            print("TIMEOUT: ยังไม่จบ ใช้ wait ซ้ำได้")
            break
        time.sleep(1)
    state = read_state(rd)
    for nid in wanted:
        rec = state["nodes"][nid]
        print("%s\t%s\t%s\t%s" % (nid, rec["status"], out_file(rd, nid), rec.get("error") or ""))
    return 0


def digest(rd, state):
    lines = ["เป้าหมาย: %s" % state.get("goal", "")]
    if not state["nodes"]:
        lines.append("ยังไม่มีงาน")
    for nid, rec in state["nodes"].items():
        lines.append("- %s: %s (บัญชี %s) ผล %s%s" % (nid, rec.get("status"), rec.get("account") or rec.get("planned") or "-",
                                                     out_file(rd, nid) if rec.get("status") == "done" else "-",
                                                     " error: " + mc.short(rec.get("error"), 100) if rec.get("error") else ""))
    return "\n".join(lines)


NOTES_MARK = "\n<!-- notes -->\n"


def write_handoff(rd, state, note=None):
    path = os.path.join(rd, "handoff.md")
    previous = read_text(path)
    notes = previous.split(NOTES_MARK, 1)[1] if NOTES_MARK in previous else ""
    if note:
        notes += note
    head = "# Handoff ของ run %s\nอัปเดต: %s\n\n%s\n" % (state["run_id"], mc.now_iso(), digest(rd, state))
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(head + NOTES_MARK + notes)


def cmd_checkpoint(args):
    run = resolve_run(args.run)
    if not run:
        print("ไม่พบ run", file=sys.stderr)
        return 2
    rd = run_path(run)
    state = read_state(rd)
    leader = state.get("leader") or {}
    note = "\n## รอบ %s โดย %s (%s)\n- ทำแล้ว: %s\n- กำลังรัน: %s\n- ขั้นต่อไป: %s\n- การตัดสินใจ: %s\n" % (
        leader.get("episode", "?"), leader.get("current", "?"), mc.now_iso(),
        args.done or "-", args.running or "-", args.next or "-", args.decision or "-")
    write_handoff(rd, state, note)
    with locked(rd) as locked_state:
        if locked_state.get("leader"):
            locked_state["leader"]["last_checkpoint"] = mc.now_iso()
            locked_state["leader"]["heartbeat"] = time.time()
    print("CHECKPOINT OK %s" % os.path.join(rd, "handoff.md"))
    fresh = read_state(rd)
    if lead_budget_exceeded(fresh) or (fresh.get("leader") or {}).get("handoff_requested"):
        print(over_budget_msg(fresh))
    return 0


def cmd_assemble(args):
    run = resolve_run(args.run)
    if not run:
        print("ไม่พบ run", file=sys.stderr)
        return 2
    rd = run_path(run)
    target = args.out if os.path.isabs(args.out) else os.path.join(rd, "out", args.out)
    parts = []
    for nid in [x for x in args.nodes.split(",") if x]:
        if not os.path.exists(out_file(rd, nid)):
            print("ERROR: ไม่มีผลของ %s" % nid, file=sys.stderr)
            return 1
        body = strip_board(read_text(out_file(rd, nid))).strip()
        parts.append("## %s\n\n%s" % (nid, body) if args.headings else body)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("\n\n".join(parts) + "\n")
    print("ASSEMBLED %s" % target)
    return 0


def cmd_finish(args):
    run = resolve_run(args.run)
    if not run:
        print("ไม่พบ run", file=sys.stderr)
        return 2
    rd = run_path(run)
    gate = read_state(rd)
    if (gate.get("leader") or {}).get("handoff_requested"):
        print("REFUSED: " + over_budget_msg(gate) + " หัวหน้าคนถัดไปจะเป็นผู้จบงาน")
        return 3
    with locked(rd) as state:
        state["finished"] = True
        state["result"] = args.result
    print("FINISHED %s" % (args.result or ""))
    return 0


# ---------- supervisor ----------

DEMO_GOAL = ("แบ่งงานให้ลูกทีม 3 ชิ้น แต่ละชิ้นเขียนประโยคภาษาไทย 1 ประโยคอธิบายเรื่องหนึ่ง: "
             "(1) การหมุนของโลก (2) ประโยชน์ของการนอน (3) การรีไซเคิล แล้วรวมเป็นไฟล์เดียว")


def lead_prompt(rd, run_id, state, account, episode):
    team = os.path.realpath(__file__)
    handoff = read_text(os.path.join(rd, "handoff.md"))
    return (
        "คุณคือหัวหน้าทีมรอบที่ %d (บัญชี %s) ของ run %s ทำงานเป็นรอบสั้น ๆ แผนทั้งหมดอยู่ในไฟล์ ไม่ใช่ในความจำของคุณ\n"
        "เป้าหมาย: %s\n\n"
        "จุดพักงาน (อ่านแล้วทำต่อจากที่ค้าง อย่าสั่งงานซ้ำกับงานที่มีอยู่แล้ว):\n%s\n\n"
        "ใช้ shell รันคำสั่งเหล่านี้เท่านั้น (T=\"python3 %s\"):\n"
        "$T dispatch --run %s --node <id> --account any --difficulty 1 --prompt \"<งานของลูกทีม>\" [--depends a,b]\n"
        "   id ใช้ a-z0-9_ เท่านั้น prompt ต้องบอกชัดว่าตอบอะไร\n"
        "$T wait --run %s --nodes a,b --timeout 300   # รอให้งานจบ แล้วเห็น path ผลลัพธ์\n"
        "$T assemble --run %s --nodes a,b,c --out final.md --headings   # รวมผลเป็น out/final.md\n"
        "$T checkpoint --run %s --done \"...\" --running \"...\" --next \"...\" --decision \"...\"\n"
        "$T finish --run %s --result out/final.md   # เรียกเมื่อทั้งเป้าหมายเสร็จจริงเท่านั้น\n\n"
        "กฎ: ห้ามลงมือทำงานเนื้อหาเอง สั่งลูกทีมทุกชิ้น · ทำเฉพาะช่วงสั้น ๆ แล้วเรียก checkpoint ก่อนจบรอบเสมอ · "
        "ถ้าผลคำสั่งมีคำว่า BUDGET_EXCEEDED หรือ EPISODE_LIMIT ให้ checkpoint แล้วหยุดทันที (ไม่ต้อง finish) · "
        "ห้าม retry งานที่ล้มเอง ให้บันทึกใน checkpoint · เมื่อทำเสร็จตอบว่าเสร็จสั้น ๆ\n"
    ) % (episode, account, run_id, state.get("goal", ""), handoff, team, run_id, run_id, run_id, run_id, run_id)


def lead_cmd(account, prompt, model, effort):
    if mc.cli_of(account) == "claude":
        return [account, "-p", prompt, "--model", model, "--effort", effort, "--output-format", "stream-json",
                "--verbose", "--no-session-persistence", "--strict-mcp-config"]
    cmd = [account, "exec", "--skip-git-repo-check", "--ephemeral"]
    if model:
        cmd += ["-m", model]
    return cmd + ["-c", "model_reasoning_effort=%s" % effort, "--json", prompt]


def next_leader(rd, opts, current, used):
    state = read_state(rd)
    forbidden = set(opts.get("forbid", [])) | {current}
    ready = [a for a, v in state["accounts"].items() if v.get("status") == "ready" and a not in forbidden]
    if opts.get("succession"):
        order = [a for a in opts["succession"] if a in ready]
    else:
        same = side_of(current) if current else "yolo"
        order = sorted(ready, key=lambda a: (side_of(a) != same, score(state, a)))
    fresh = [a for a in order if a not in used]
    if fresh:
        return fresh[0], True  # ยังมีผู้สืบทอดที่ยังไม่เคยเป็นหัวหน้า
    return (order[0], False) if order else (None, False)


def leader_switch(rd, run_id, frm, to, kind, reason):
    with locked(rd) as state:
        state["leader"].setdefault("history", []).append(dict(frm=frm, to=to, kind=kind, reason=reason, ts=mc.now_iso()))
        write_handoff(rd, state)
    board_append(rd, "supervisor", "สลับหัวหน้า %s -> %s (%s: %s)" % (frm, to, kind, reason))
    event(rd, "lead_switch", run_id, frm=frm, to=to, kind=kind, reason=reason)
    print("[lead_switch] %s -> %s (%s: %s)" % (frm, to, kind, reason), flush=True)


def run_episode(rd, run_id, account, episode, opts, model, effort):
    """รันหัวหน้าหนึ่งรอบ คืน (outcome, reason, tokens) outcome: ok / limit / failed / crash"""
    state = read_state(rd)
    with locked(rd) as locked_state:
        write_handoff(rd, locked_state)
        leader = locked_state["leader"]
        leader.update(current=account, episode=episode, tokens_live=0, dispatches=0, handoff_requested=None,
                      heartbeat=time.time(), budget=opts.get("episode_budget"), max_dispatch=opts.get("max_dispatch"))
        leader.setdefault("episodes", []).append(dict(episode=episode, account=account, ts=mc.now_iso()))
        state = copy.deepcopy(locked_state)
    prompt = lead_prompt(rd, run_id, state, account, episode)
    started = mc.now_iso()
    print("[lead] รอบ %d: %s" % (episode, account), flush=True)
    if account in opts.get("sim_limit", []):
        message = "simulated limit: usage limit reached"
        row = mc.make_row(started, account, model or "-", effort, "error", error=message, run_id=run_id, node="lead.e%d" % episode, prompt_chars=len(prompt), cost=0 if mc.cli_of(account) == "claude" else None)
        mc.ledger_append(row, rd)
        return "limit", "จำลองโควตาหมด", 0
    crash = account in opts.get("sim_crash", []) and account not in opts.get("crashed", [])
    usage_live = {"tokens": 0, "seen": {}, "final": None, "model": model}

    def on_line(line):
        try:
            event_data = json.loads(line)
        except ValueError:
            return
        if not isinstance(event_data, dict):
            return
        kind = event_data.get("type")
        now = time.time()
        added = 0
        if kind == "assistant":
            msg = event_data.get("message") or {}
            usage = msg.get("usage") or {}
            total = sum((usage.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            prev = usage_live["seen"].get(msg.get("id"), 0)
            usage_live["seen"][msg.get("id")] = max(prev, total)
            added = max(0, total - prev)
            if msg.get("model"):
                usage_live["model"] = msg["model"]
        elif kind == "turn.completed":
            usage = event_data.get("usage") or {}
            usage_live["final"] = usage
            added = (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)
        elif kind == "item.completed":
            added = len(json.dumps(event_data.get("item", {}), ensure_ascii=False)) // 4
        elif kind == "result" or (kind is None and "total_cost_usd" in event_data):
            usage_live["final"] = event_data
        usage_live["tokens"] += added
        with locked(rd) as locked_state:
            locked_state["leader"]["tokens_live"] = usage_live["tokens"]
            locked_state["leader"]["heartbeat"] = now
            if lead_budget_exceeded(locked_state):
                locked_state["leader"]["handoff_requested"] = "งบโทเค็นหัวหน้า"

    def should_stop():
        leader = read_state(rd)["leader"]
        if crash and leader.get("dispatches", 0) >= 1:
            with locked(rd) as locked_state:
                locked_state["options"].setdefault("crashed", []).append(account)
            return True
        if time.time() - leader.get("heartbeat", 0) > opts.get("heartbeat_timeout", 240):
            return True
        return False

    env = mc.clean_env("CLAUDE_CODE_")
    env.update(MA_TEAM_RUN=run_id, MA_LEAD_ACCOUNT=account)
    proc = mc.run_process(lead_cmd(account, prompt, model, effort), timeout=opts.get("episode_timeout", 900), cwd=rd, env=env, on_line=on_line, should_stop=should_stop)
    final = usage_live["final"] or {}
    if mc.cli_of(account) == "claude":
        usage = yolo.usage_of(final) if final else {}
    else:
        usage = {"input": final.get("input_tokens", 0), "cached": final.get("cached_input_tokens", 0), "cache_write": final.get("cache_write_input_tokens", 0), "output": final.get("output_tokens", 0), "reasoning": final.get("reasoning_output_tokens", 0)} if final else {}
    tokens = mc.total_tokens({"cli": mc.cli_of(account), "input_tokens": usage.get("input", 0), "cached_input_tokens": usage.get("cached", 0), "cache_write_tokens": usage.get("cache_write", 0), "output_tokens": usage.get("output", 0)}) or usage_live["tokens"]
    if proc["stopped"] and crash:
        status, kind, reason = "error", "crash", "จำลองหัวหน้าล้มกลางคัน (SIGKILL หลังสั่งงานชิ้นแรก)"
    elif proc["stopped"]:
        status, kind, reason = "error", "failed", "heartbeat ไม่อัปเดต"
    elif proc["timed_out"]:
        status, kind, reason = "timeout", "failed", "หัวหน้า timeout"
    elif mc.cli_of(account) == "claude" and final.get("is_error"):
        message = final.get("result") or "is_error"
        status, kind, reason = "error", "limit" if mc.classify_error(message) in ("quota", "rate_limit", "auth") else "failed", mc.short(message)
    elif proc["rc"] != 0:
        message = proc["stderr"] or proc["stdout"][-200:]
        status, kind, reason = "error", "limit" if mc.classify_error(message) in ("quota", "rate_limit", "auth") else "failed", mc.short(message)
    else:
        status, kind, reason = "ok", "ok", None
    row = mc.make_row(started, account, usage_live.get("model") or model or "default", effort, status, usage=usage, error=reason,
                      run_id=run_id, node="lead.e%d" % episode, cost=final.get("total_cost_usd") if mc.cli_of(account) == "claude" else None,
                      duration=proc["duration"], prompt_chars=len(prompt), result_chars=len(proc["stdout"]))
    mc.ledger_append(row, rd)
    return kind, reason, tokens


def wait_workers(rd, timeout=900):
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = read_state(rd)
        if all(n["status"] in TERMINAL for n in state["nodes"].values()):
            return True
        time.sleep(1)
    return False


def final_report(rd, run_id, as_json=False):
    state = read_state(rd)
    rows, table = result_table(rd, state)
    leader = state.get("leader") or {}
    history = leader.get("history", [])
    stats = {}
    for row in mc.read_ledger(os.path.join(rd, "ledger.jsonl")):
        if row.get("event"):
            continue
        cur = stats.setdefault(row["account"], dict(calls=0, input=0, output=0, cached=0, duration=0.0))
        cur["calls"] += 1
        cur["input"] += row.get("input_tokens") or 0
        cur["output"] += row.get("output_tokens") or 0
        cur["cached"] += row.get("cached_input_tokens") or 0
        cur["duration"] += row.get("duration_s") or 0
    if as_json:
        print(json.dumps(dict(run_id=run_id, status=state["status"], finished=state.get("finished"), result=state.get("result"),
                              lead_switches=history, worker_switches=state["worker_switches"], nodes=rows, stats=stats), ensure_ascii=False))
        return
    print("\n## ประวัติการสลับหัวหน้า")
    print(mc.md_table(["จาก", "ไป", "ชนิด", "เหตุผล"], [[h["frm"], h["to"], h["kind"], mc.short(h["reason"], 120)] for h in history]) if history else "ไม่มีการสลับหัวหน้า")
    print("\n## การย้ายงานลูกทีม")
    print(switch_table(state) if state["worker_switches"] else "ไม่มีการย้ายงาน")
    print("\n## ผลของแต่ละงาน\n" + table)
    print("\n## สถิติแยกตามบัญชี (run นี้)")
    print(mc.md_table(["บัญชี", "ครั้ง", "input", "cached", "output", "เวลารวม s"], [[n, c["calls"], c["input"], c["cached"], c["output"], "%.1f" % c["duration"]] for n, c in sorted(stats.items())]))
    print("\nผลลัพธ์: %s" % (os.path.join(rd, state.get("result") or "") if state.get("result") else "-"))


def cmd_lead(args):
    if args.demo and not args.goal:
        args.goal = DEMO_GOAL
    if not args.goal and not args.resume:
        print("ต้องมี --goal หรือ --demo", file=sys.stderr)
        return 2
    os.makedirs(mc.TEAM_ROOT, exist_ok=True)
    if args.resume:
        run_id = args.resume
        rd = run_path(run_id)
        if not os.path.exists(os.path.join(rd, "state.json")):
            print("ไม่พบ run: %s" % run_id, file=sys.stderr)
            return 2
    else:
        run_id, rd = new_run(args.goal, "lead")
        write_graph(rd, dict(goal=args.goal, nodes=[]))
    ready = readiness(fresh=args.fresh_check)
    names = [n for n, v in ready.items() if v["status"] == "ready"]
    if not names:
        print("ไม่มีบัญชีที่พร้อม", file=sys.stderr)
        return 1
    forbid = [x for x in (args.forbid or "").split(",") if x]
    succession = [x for x in (args.succession or "").split(",") if x]
    with locked(rd) as state:
        state["accounts"] = ready
        state["status"] = "running"
        for name, row in quota_of(names).items():
            row["_fetched"] = time.time()
            state["quota"][name] = row
        options = state["options"]
        options.update(max_total=args.max_total, max_per_account=args.max_per_account, timeout=args.timeout,
                       worker_token_budget=args.worker_token_budget, quota_stop=args.quota_stop,
                       sim_limit=[x for x in (args.simulate_limit or "").split(",") if x])
        state.setdefault("leader", None)
        if not state["leader"]:
            state["leader"] = dict(current=None, episode=0, history=[])
        if args.demo:
            options["sim_once"] = True
            options["worker_max_difficulty"] = 1
    difficulty = 1 if args.demo else args.lead_difficulty
    model_claude, effort_claude = yolo.resolve(difficulty, args.lead_model, None)
    effort_codex = mc.DIFFICULTY[difficulty][2]
    opts = dict(sim_limit=[x for x in (args.simulate_limit or "").split(",") if x],
                sim_crash=[x for x in (args.simulate_crash or "").split(",") if x], forbid=forbid, succession=succession,
                heartbeat_timeout=args.heartbeat_timeout, episode_timeout=args.episode_timeout,
                max_dispatch=args.max_dispatch)
    print("run_id: %s\nrun dir: %s\nบัญชีพร้อม: %s" % (run_id, rd, ", ".join(names)), flush=True)
    current = args.lead
    if not current or current not in names or current in forbid:
        current = next_leader(rd, opts, None, [])[0]
    if not current:
        print("ไม่มีบัญชีที่เป็นหัวหน้าได้", file=sys.stderr)
        return 1
    used, episode, idle = [], 0, 0
    if args.demo:
        opts["sim_crash"] = [current]
    while episode < args.max_episodes:
        episode += 1
        if current not in used:
            used.append(current)
        _, has_more = next_leader(rd, opts, current, used)
        budget = args.lead_token_budget
        if args.demo:
            budget = 1 if episode == 2 else None
        elif budget and not has_more:
            budget = None  # หัวหน้าคนสุดท้ายไม่มีคนรับไม้ ไม่จำกัดงบเพื่อให้งานจบ
        opts["episode_budget"] = budget
        before = len(read_state(rd)["nodes"])
        model = model_claude if mc.cli_of(current) == "claude" else args.lead_model_codex or cyolo.default_model(current)
        effort = effort_claude if mc.cli_of(current) == "claude" else effort_codex
        outcome, reason, tokens = run_episode(rd, run_id, current, episode, opts, model, effort)
        print("[lead] รอบ %d จบ: %s tokens=%s" % (episode, outcome, tokens), flush=True)
        state = read_state(rd)
        if state.get("finished"):
            break
        kind = None
        if outcome in ("limit", "crash", "failed"):
            kind = "reactive"
        else:
            leader = state["leader"]
            refresh_quota(rd, [current], max_age=0)
            used_pct = effective_used(read_state(rd)["quota"].get(current))
            if budget and (leader.get("handoff_requested") or tokens >= budget):
                kind, reason = "proactive", "ถึงงบโทเค็นหัวหน้า (%s/%s)" % (tokens, budget)
            elif used_pct is not None and used_pct >= args.quota_stop:
                kind, reason = "proactive", "โควตา %g%%" % used_pct
        if not kind:
            idle = idle + 1 if len(state["nodes"]) == before else 0
            if idle >= 2:
                print("[lead] หัวหน้าไม่คืบหน้า 2 รอบติด หยุด", flush=True)
                break
            continue
        idle = 0
        successor, _ = next_leader(rd, opts, current, used)
        if not successor:
            print("[lead] ไม่มีผู้สืบทอด หยุด (รันต่อด้วย lead --resume %s)" % run_id, flush=True)
            leader_switch(rd, run_id, current, "-", kind, reason or "")
            break
        leader_switch(rd, run_id, current, successor, kind, reason or "")
        current = successor
    state = read_state(rd)
    wait_workers(rd, args.timeout * 2)
    state = read_state(rd)
    failed = [n for n, r in state["nodes"].items() if r["status"] in ("failed", "blocked")]
    with locked(rd) as locked_state:
        locked_state["status"] = "done" if state.get("finished") and not failed else "failed"
    final_report(rd, run_id, args.json)
    return 0 if state.get("finished") and not failed else 1


def add_common(parser):
    parser.add_argument("--max-total", type=int, default=8, help="งานพร้อมกันรวม (ค่าเริ่มต้น 8)")
    parser.add_argument("--max-per-account", type=int, default=3, help="งานพร้อมกันต่อบัญชี (ค่าเริ่มต้น 3)")
    parser.add_argument("--timeout", type=int, default=600, help="timeout ต่องานเป็นวินาที")
    parser.add_argument("--worker-token-budget", type=int, help="งบโทเค็นต่อบัญชี (รวม cache) เกินแล้วหยุดรับงาน")
    parser.add_argument("--quota-stop", type=float, default=QUOTA_STOP, help="หยุดรับงานเมื่อโควตาใช้ไปเกิน %%")
    parser.add_argument("--simulate-limit", help="จำลองโควตาหมดของบัญชี (คั่นด้วยจุลภาค)")
    parser.add_argument("--fresh-check", action="store_true", help="ตรวจความพร้อมใหม่ ไม่ใช้ผล 5 นาทีล่าสุด")
    parser.add_argument("--json", action="store_true")


def main():
    mc.setup_io()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="รันกราฟงาน")
    run.add_argument("graph", nargs="?", default="-", help="ไฟล์ JSON หรือ - (stdin)")
    run.add_argument("--resume", help="รันต่อจาก run เดิม เฉพาะงานที่ล้มหรือถูกบล็อก")
    run.add_argument("--set", action="append", help="แก้ก่อน resume: node.field=value (ว่าง = ลบ)")
    run.add_argument("--gate-timeout", type=int, default=3600, help="รอ human gate นานสุด (วินาที)")
    add_common(run)
    for name, text in (("status", "ภาพรวม run"), ("stats", "สรุป ledger")):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("--run")
        cmd.add_argument("--json", action="store_true")
    cmd = sub.add_parser("check", help="ตรวจความพร้อมทุกบัญชีด้วยการเรียกจริง")
    cmd.add_argument("--cached", action="store_true")
    cmd.add_argument("--json", action="store_true")
    cmd = sub.add_parser("quota", help="โควตาทุกบัญชี")
    cmd.add_argument("--json", action="store_true")
    cmd = sub.add_parser("approve", help="อนุมัติ human gate")
    cmd.add_argument("run")
    cmd.add_argument("node")
    cmd = sub.add_parser("board", help="อ่านหรือเพิ่มกระดาน")
    cmd.add_argument("--run")
    cmd.add_argument("--add")
    cmd.add_argument("--author")
    lead = sub.add_parser("lead", help="รันหัวหน้าทีมเป็นรอบสั้น สลับตัวได้")
    lead.add_argument("--goal")
    lead.add_argument("--demo", action="store_true", help="สาธิต: หัวหน้าล้ม + งบหัวหน้า + ย้ายงานลูกทีม ในรันเดียว")
    lead.add_argument("--lead", help="บัญชีหัวหน้าเริ่มต้น")
    lead.add_argument("--succession", help="ลำดับผู้สืบทอด คั่นด้วยจุลภาค")
    lead.add_argument("--forbid", help="บัญชีที่ห้ามเป็นหัวหน้า")
    lead.add_argument("--lead-token-budget", type=int, help="งบโทเค็นต่อหัวหน้า")
    lead.add_argument("--lead-difficulty", type=int, default=2, choices=range(1, 7))
    lead.add_argument("--lead-model")
    lead.add_argument("--lead-model-codex")
    lead.add_argument("--simulate-crash", help="จำลองหัวหน้าบัญชีนี้ล้มหลังสั่งงานแรก")
    lead.add_argument("--max-episodes", type=int, default=8)
    lead.add_argument("--max-dispatch", type=int, default=6, help="จำนวน dispatch ต่อรอบ")
    lead.add_argument("--episode-timeout", type=int, default=900)
    lead.add_argument("--heartbeat-timeout", type=int, default=240)
    lead.add_argument("--resume", help="ทำต่อจาก run เดิม")
    add_common(lead)
    dispatch = sub.add_parser("dispatch", help="หัวหน้าสั่งงานลูกทีม (process แยก)")
    dispatch.add_argument("--run")
    dispatch.add_argument("--node", required=True)
    dispatch.add_argument("--account", default="any")
    dispatch.add_argument("--difficulty", type=int, default=1, choices=range(1, 7))
    dispatch.add_argument("--prompt")
    dispatch.add_argument("--prompt-file")
    dispatch.add_argument("--depends")
    dispatch.add_argument("--expect")
    dispatch.add_argument("--model")
    dispatch.add_argument("--effort")
    dispatch.add_argument("--cwd")
    dispatch.add_argument("--kind")
    dispatch.add_argument("--prefer")
    wait = sub.add_parser("wait", help="รอให้งานจบ")
    wait.add_argument("--run")
    wait.add_argument("--nodes", required=True)
    wait.add_argument("--timeout", type=int, default=300)
    check = sub.add_parser("checkpoint", help="หัวหน้าเขียนจุดพัก")
    check.add_argument("--run")
    for field in ("done", "running", "next", "decision"):
        check.add_argument("--" + field)
    assemble = sub.add_parser("assemble", help="รวมผลหลายงานเป็นไฟล์เดียว")
    assemble.add_argument("--run")
    assemble.add_argument("--nodes", required=True)
    assemble.add_argument("--out", required=True)
    assemble.add_argument("--headings", action="store_true")
    finish = sub.add_parser("finish", help="หัวหน้าประกาศงานจบ")
    finish.add_argument("--run")
    finish.add_argument("--result")
    worker = sub.add_parser("_worker")
    worker.add_argument("--run", required=True)
    worker.add_argument("--node", required=True)
    worker.add_argument("--gate-timeout", type=int, default=3600)
    args = parser.parse_args()
    handlers = dict(run=cmd_run, status=cmd_status, stats=mc.stats_main, check=cmd_check, quota=cmd_quota,
                    approve=cmd_approve, board=cmd_board, lead=cmd_lead, dispatch=cmd_dispatch, wait=cmd_wait,
                    checkpoint=cmd_checkpoint, assemble=cmd_assemble, finish=cmd_finish, _worker=cmd_worker)
    try:
        return handlers[args.cmd](args)
    except GraphError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
