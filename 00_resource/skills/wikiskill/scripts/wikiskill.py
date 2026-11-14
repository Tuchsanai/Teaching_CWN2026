#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wikiskill.py - วงรอบ WikiSkill (arXiv:2608.27454 Algorithm 1) ในไฟล์เดียว

รูปแบบ:  python3 scripts/wikiskill.py <คำสั่ง> <work> --ws <ชื่อ workspace>
คำสั่ง:   init baseline rollout maintain propose gate loop status

สามชั้นของ workspace (runs/<ws>/):
  raw/    Trace ของ Training      เขียนครั้งเดียว ไม่แก้
  wiki/   ความรู้ที่สรุปจาก Trace   สะสม ไม่ถูกย้อนกลับ
  skills/ ชุดสกิลที่ใช้งาน          เปลี่ยนเฉพาะเมื่อผ่าน gate

ใช้ไลบรารีมาตรฐานเท่านั้น · Python 3.8 ขึ้นไป
"""
import argparse
import difflib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time

PASS_SCORE = 0.999          # Trace ที่คะแนนถึงค่านี้นับว่า PASS
MAX_FAIL, MAX_PASS = 5, 3   # จำนวน Trace ที่สุ่มให้ Wiki Maintainer
TRACE_CAP = 15000           # ความยาวสูงสุดของ 1 Trace (ตัวอักษร)
MIN_TRACES_READ = 4         # Proposer ต้องเปิด Trace อย่างน้อยเท่านี้ก่อนเสนอ
MAX_ATTEMPTS = 3            # จำนวนครั้งที่เรียกโมเดลได้ต่อ 1 ขั้น
MODEL_TIMEOUT = 1800        # วินาทีต่อการเรียกโมเดล 1 ครั้ง
DEFAULT_TASK_DESC = "เขียนโค้ด Python ตามโจทย์ (ตัวตรวจอัตโนมัติให้คะแนนผลงาน)"

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_DIR = os.path.join(SKILL_DIR, "prompts")
DEFAULT_SKILLOPT = os.path.join(SKILL_DIR, "..", "skill-optimizer", "scripts", "skillopt.py")

NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
PATTERN_RE = re.compile(r"^[A-Za-z0-9._-]+\.md$")
NEXT_CMD = {"init": "baseline", "gate": "rollout", "rollout": "maintain",
            "maintain": "propose", "propose": "gate"}
NEEDS_PHASE = {"baseline": "init", "rollout": "gate", "maintain": "rollout",
               "propose": "maintain", "gate": "propose"}

WIKI_INDEX_0 = "# Wiki Index\n\nยังไม่มี pattern\n"
WIKI_LOG_0 = "# Evolution Log\n"
WIKI_IMPACT_0 = ("# Skill Impact\n\nบันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: "
                 "เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ\n")


# ---------------------------------------------------------------- พื้นฐาน

def die(msg, code=1):
    print(msg)
    sys.stdout.flush()
    sys.exit(code)


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_text(path, text):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1)


def with_newline(text):
    return text if text.endswith("\n") else text + "\n"


def pct(x):
    return "-" if x is None else "%.1f%%" % (x * 100)


def iter_name(k):
    return "iter-%02d" % k


def reset_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def copy_tree(src, dst):
    """แทน dst ด้วยสำเนาของ src (src ไม่มี = dst ว่าง)"""
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        os.makedirs(dst)


def skill_names(skills_dir):
    if not os.path.isdir(skills_dir):
        return []
    return sorted(n for n in os.listdir(skills_dir)
                  if os.path.isfile(os.path.join(skills_dir, n, "SKILL.md")))


def is_perfect(r_best):
    return r_best is not None and r_best >= 1.0 - 1e-9


# ---------------------------------------------------------------- workspace และ state

class Workspace(object):
    def __init__(self, work, name):
        self.work = os.path.abspath(work)
        self.name = name
        self.root = os.path.join(self.work, "runs", name)
        self.state_path = os.path.join(self.root, "state.json")
        self.raw = os.path.join(self.root, "raw")
        self.wiki = os.path.join(self.root, "wiki")
        self.skills = os.path.join(self.root, "skills")
        self.history = os.path.join(self.root, "history")
        self.rollouts = os.path.join(self.root, "rollouts")

    def raw_iter(self, k):
        return os.path.join(self.raw, iter_name(k))

    def hist_iter(self, k):
        return os.path.join(self.history, iter_name(k))

    def trials_dir(self, label):
        return os.path.join(self.rollouts, "runs", label, "trials")

    def load(self):
        if not os.path.isfile(self.state_path):
            die("ไม่พบ %s · ขั้นถัดไปคือ init" % self.state_path)
        return read_json(self.state_path)

    def save(self, st):
        write_text(self.state_path, dump_json(st))


def require_phase(st, cmd):
    """คำสั่งที่ถูกเรียกผิดลำดับ: บอกขั้นถัดไป แล้ว exit 1 (ยังไม่ได้เรียกโมเดล)"""
    phase = st.get("phase")
    if phase == NEEDS_PHASE[cmd]:
        return
    nxt = NEXT_CMD.get(phase, "?")
    extra = ""
    if phase == "gate" and is_perfect(st.get("r_best")):
        extra = " (R_best = 100% แล้ว วงรอบหยุด)"
    die("เรียก %s ตอนนี้ไม่ได้ · ขั้นล่าสุดที่ทำเสร็จคือ %s · ขั้นถัดไปคือ %s%s"
        % (cmd, phase, nxt, extra))


# ---------------------------------------------------------------- Trial (ข้อ 5)

def trial_key(name):
    m = re.match(r"^(.*)-r(\d+)$", name)
    return (m.group(1), int(m.group(2))) if m else (name, 0)


def read_trials(trials_dir):
    """อ่าน grade.json และ metrics.json ของทุก Trial · ผลที่ถูกตัดรายละเอียด = checks เป็น None"""
    out = []
    if not os.path.isdir(trials_dir):
        return out
    for name in sorted(os.listdir(trials_dir), key=trial_key):
        d = os.path.join(trials_dir, name)
        gpath = os.path.join(d, "grade.json")
        if not os.path.isfile(gpath):
            continue
        grade = read_json(gpath)
        mpath = os.path.join(d, "metrics.json")
        metrics = read_json(mpath) if os.path.isfile(mpath) else {}
        checks = grade.get("checks")
        out.append({"trace_id": name, "task": trial_key(name)[0], "dir": d,
                    "score": float(grade.get("score") or 0.0),
                    "checks": checks if isinstance(checks, list) else None,
                    "metrics": metrics})
    return out


def mean_score(trials):
    return sum(t["score"] for t in trials) / len(trials)


def aggregate(trials):
    n = len(trials)
    num = lambda m, key: float(m.get(key) or 0)
    cost = sum(num(t["metrics"], "cost_usd") for t in trials)
    ctx = sum(num(t["metrics"], "input_tokens") + num(t["metrics"], "cache_read")
              + num(t["metrics"], "cache_write") for t in trials)
    tools = sum(num(t["metrics"], "tool_calls") for t in trials)
    return {"trials": n, "cost_usd": round(cost, 3), "context_tokens": int(round(ctx / n)),
            "tool_calls": round(tools / n, 2),
            "skill_read": sum(1 for t in trials if t["metrics"].get("skill_read"))}


def run_trials(ws, cfg, label, split, skills_src):
    """รัน Trial 1 ชุดด้วยคำสั่ง run ของ skill-optimizer กับโฟลเดอร์งาน rollouts/"""
    run_dir = os.path.join(ws.rollouts, "runs", label)
    reset_dir(run_dir)
    if skills_src and skill_names(skills_src):
        shutil.copytree(skills_src, os.path.join(run_dir, "skills"))
    if not os.path.isfile(cfg["skillopt"]):
        die("ไม่พบ skillopt.py ที่ %s (ตั้งด้วย --skillopt ตอน init)" % cfg["skillopt"])
    cmd = [sys.executable, cfg["skillopt"], "run", ws.rollouts, "--label", label,
           "--split", split, "--reps", str(cfg["reps"]),
           "--accounts", ",".join(cfg["accounts"]), "--par", str(cfg["par"]),
           "--model", cfg["model"], "--effort", cfg["effort"]]
    print("[trial] %s · ชุด %s · สกิล: %s" % (
        label, split, ", ".join(skill_names(skills_src)) if skills_src and skill_names(skills_src) else "(ไม่มี)"))
    sys.stdout.flush()
    rc = subprocess.call(cmd)
    if rc != 0:
        die("คำสั่ง run ของ skill-optimizer ล้ม (exit %s) · ป้าย %s" % (rc, label))
    trials = read_trials(ws.trials_dir(label))
    if not trials:
        die("ไม่มีผลของ Trial ใต้ %s (ไม่พบ grade.json)" % ws.trials_dir(label))
    return trials


# ---------------------------------------------------------------- Raw Layer (ข้อ 6)

def clip(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…(ตัด %d ตัวอักษร)" % (len(text) - limit)


def load_events(path):
    events = []
    if not os.path.isfile(path):
        return events
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if isinstance(ev, dict):
                events.append(ev)
    return events


def blocks_of(ev):
    msg = ev.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def result_text(content):
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict):
                parts.append(str(b.get("text", "")) if b.get("type") == "text" else "(%s)" % b.get("type"))
            else:
                parts.append(str(b))
        return "\n".join(parts)
    return "" if content is None else str(content)


def tool_body(name, inp):
    """สิ่งที่เครื่องมือถูกสั่ง: คำสั่ง หรือ ไฟล์ที่เขียน"""
    if not isinstance(inp, dict):
        return str(inp)
    if name == "Bash" and isinstance(inp.get("command"), str):
        return inp["command"]
    if name == "Write" and "file_path" in inp:
        return "%s\n%s" % (inp.get("file_path"), inp.get("content", ""))
    if name == "Edit" and "file_path" in inp:
        return "%s\n%s" % (inp.get("file_path"), inp.get("new_string", ""))
    if name == "Read" and "file_path" in inp:
        return str(inp.get("file_path"))
    return json.dumps(inp, ensure_ascii=False)


def trace_steps(events):
    """ลำดับเหตุการณ์ของ Agent: ("say", ข้อความ) หรือ ("tool", dict) · คืนคำตอบสุดท้ายด้วย"""
    items, by_id, final = [], {}, None
    for ev in events:
        kind = ev.get("type")
        if kind == "assistant":
            for b in blocks_of(ev):
                if b.get("type") == "text" and str(b.get("text", "")).strip():
                    items.append(("say", str(b["text"]).strip()))
                elif b.get("type") == "tool_use":
                    step = {"name": str(b.get("name")), "body": tool_body(b.get("name"), b.get("input")),
                            "result": None, "error": False}
                    by_id[b.get("id")] = step
                    items.append(("tool", step))
        elif kind == "user":
            for b in blocks_of(ev):
                if b.get("type") == "tool_result" and b.get("tool_use_id") in by_id:
                    step = by_id[b["tool_use_id"]]
                    step["result"] = result_text(b.get("content"))
                    step["error"] = bool(b.get("is_error"))
        elif kind == "result":
            final = ev.get("result")
    return items, final


def render_trace(trial, k, brief, items, final, limit):
    m = trial["metrics"]
    checks = trial["checks"] or []
    passed = sum(1 for c in checks if c.get("pass"))
    lines = ["# Trace %s · iteration %d" % (trial["trace_id"], k), "",
             "- ผล: **%s** · คะแนน %.2f (ผ่าน %d จาก %d ข้อตรวจ)" % (
                 "PASS" if trial["score"] >= PASS_SCORE else "FAIL", trial["score"], passed, len(checks)),
             "- คำสั่งที่ใช้ %d ครั้ง · คำสั่งล้ม %d ครั้ง · อ่านสกิล: %s" % (
                 int(m.get("tool_calls") or 0), int(m.get("tool_errors") or 0),
                 "ใช่" if m.get("skill_read") else "ไม่"),
             "", "## โจทย์", "", brief.strip(), "", "## ผลของตัวตรวจ (Grader)", ""]
    for c in checks:
        if c.get("pass"):
            lines.append("- ✓ `%s`" % c.get("id"))
        else:
            note = str(c.get("note") or "").strip()
            lines.append("- ✗ `%s`%s" % (c.get("id"), ": " + note if note else ""))
    if not checks:
        lines.append("(ไม่มีผลรายข้อ)")
    lines += ["", "## สิ่งที่ Agent ทำ", ""]
    n = 0
    for kind, item in items:
        if kind == "say":
            lines += ["**Agent พูด:** " + clip(item, limit), ""]
            continue
        n += 1
        lines += ["### ขั้น %d · %s" % (n, item["name"]), "", "```", clip(item["body"], limit), "```", ""]
        if item["result"] is not None:
            out = ("ERROR " if item["error"] else "") + item["result"]
            lines += ["ผลที่ได้:", "", "```", clip(out, limit), "```", ""]
    if not items:
        lines += ["(ไม่มี transcript.jsonl ของ Trial นี้)", ""]
    lines += ["## คำตอบสุดท้ายของ Agent", "", (final or "(ไม่มีคำตอบสุดท้าย)").strip(), ""]
    return "\n".join(lines)


def build_trace(trial, k):
    """Trace 1 ไฟล์ · ยาวไม่เกิน TRACE_CAP: ย่อคำสั่งและผลของแต่ละขั้นก่อน แล้วจึงตัดท้าย"""
    brief = "(ไม่มี task.json)"
    tpath = os.path.join(trial["dir"], "task.json")
    if os.path.isfile(tpath):
        task = read_json(tpath)
        brief = str(task.get("brief") or json.dumps(task, ensure_ascii=False))
    items, final = trace_steps(load_events(os.path.join(trial["dir"], "transcript.jsonl")))
    if final is None:
        final = trial["metrics"].get("result")
    text = ""
    for limit in (6000, 3000, 1500, 800, 400, 200):
        text = render_trace(trial, k, brief, items, final, limit)
        if len(text) <= TRACE_CAP:
            return text
    mark = "\n…(ตัดท้าย %d ตัวอักษร)\n"
    cut = len(text) - TRACE_CAP + 40
    return text[:len(text) - cut] + mark % cut


def build_summary(trials, k):
    perfect = sum(1 for t in trials if t["score"] >= PASS_SCORE)
    lines = ["# ผลของ Training rollouts · iteration %d" % k, "",
             "คะแนนเฉลี่ย %s · ผ่านครบทุกข้อ %d/%d Trace" % (pct(mean_score(trials)), perfect, len(trials)),
             "", "| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |", "|---|---|---|---|"]
    details = []
    for t in trials:
        failed = [c for c in (t["checks"] or []) if not c.get("pass")]
        lines.append("| %s | %s | %.2f | %s |" % (
            t["trace_id"], "PASS" if t["score"] >= PASS_SCORE else "FAIL", t["score"],
            " ".join(str(c.get("id")) for c in failed) or "-"))
        for c in failed:
            note = str(c.get("note") or "").strip()
            details.append("- %s · `%s`%s" % (t["trace_id"], c.get("id"), ": " + note if note else ""))
    lines += ["", "## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)", ""]
    lines += details or ["- (ไม่มี)"]
    return "\n".join(lines) + "\n"


def check_counts(trials):
    order, got = [], {}
    for t in trials:
        for c in t["checks"] or []:
            cid = str(c.get("id"))
            if cid not in got:
                got[cid] = [0, 0]
                order.append(cid)
            got[cid][1] += 1
            got[cid][0] += 1 if c.get("pass") else 0
    return dict((cid, "%d/%d" % tuple(got[cid])) for cid in order)


# ---------------------------------------------------------------- รายการแก้ (ข้อ 7 และ 8 ใช้ร่วมกัน)

def append_block(text, content):
    base, body = text.rstrip("\n"), content.strip("\n")
    return (base + "\n" if base else "") + body + "\n"


def apply_edit(text, edit):
    """คืน (ข้อความใหม่, None) หรือ (ข้อความเดิม, สาเหตุที่ใช้ไม่ได้)"""
    if not isinstance(edit, dict):
        return text, "รายการแก้ต้องเป็น object"
    op, content, target = edit.get("op"), edit.get("content"), edit.get("target")
    if op not in ("append", "replace", "insert_after"):
        return text, "ไม่รู้จัก op `%s`" % op
    if not isinstance(content, str):
        return text, "%s: ไม่มี content" % op
    if op == "append":
        return append_block(text, content), None
    if not isinstance(target, str) or not target:
        return text, "%s: ไม่มี target" % op
    i = text.find(target)
    if i < 0:
        return text, "%s: ไม่พบ target `%s` ในไฟล์ (ต้องตรงทุกตัวอักษร)" % (op, target[:60])
    end = i + len(target)
    if op == "replace":
        return text[:i] + content + text[end:], None
    # insert_after: บรรทัดใหม่ต่อจากบรรทัดที่ target จบ
    body = content.strip("\n") + "\n"
    if target.endswith("\n"):
        return text[:end] + body + text[end:], None
    j = text.find("\n", end)
    if j < 0:
        return text + "\n" + body, None
    return text[:j + 1] + body + text[j + 1:], None


# ---------------------------------------------------------------- การเรียกโมเดล (ข้อ 11)

def load_prompt(name, cfg):
    path = os.path.join(PROMPT_DIR, name)
    if not os.path.isfile(path):
        die("ไม่พบ prompt %s" % path)
    return read_text(path).replace("{task_desc}", cfg.get("task_desc") or DEFAULT_TASK_DESC)


def model_command(cfg, system_prompt, tools):
    account = cfg["accounts"][0]
    root = os.environ.get("WIKISKILL_ACCOUNT_ROOT") or os.path.join(
        os.path.expanduser("~"), "ai-accounts", ".Claude")
    account_dir = os.path.join(root, account)
    env = dict((key, val) for key, val in os.environ.items()
               if not (key.startswith("CLAUDE") or key.startswith("MA_")))
    env["IS_SANDBOX"] = "1"
    tail = ["-p", "--system-prompt", system_prompt, "--model", cfg["opt_model"],
            "--effort", cfg["opt_effort"], "--output-format", "stream-json", "--verbose",
            "--no-session-persistence", "--strict-mcp-config", "--tools", tools]
    if os.path.isdir(account_dir):
        env["CLAUDE_CONFIG_DIR"] = account_dir
        return ["claude", "--dangerously-skip-permissions", "--disable-slash-commands"] + tail, env
    return [account] + tail, env


def resolve_command(cmd):
    exe = shutil.which(cmd[0]) or (cmd[0] if os.path.isfile(cmd[0]) else None)
    if exe is None:
        die("ไม่พบคำสั่ง `%s` สำหรับเรียกโมเดล" % cmd[0])
    if exe.lower().endswith(".py"):       # คำสั่งของบัญชีที่เป็นสคริปต์ Python (ใช้กับ Agent จำลอง)
        return [sys.executable, exe] + cmd[1:]
    return [exe] + cmd[1:]


def call_model(cfg, system_prompt, user_text, tools, cwd, transcript_path):
    """เรียกโมเดล 1 ครั้ง · ข้อความของผู้ใช้ทาง stdin · stdout เก็บเป็น transcript (stream-json)"""
    cmd, env = model_command(cfg, system_prompt, tools)
    argv = resolve_command(cmd)
    os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
    t0 = time.time()
    fail = None
    with open(transcript_path, "wb") as out:
        try:
            proc = subprocess.run(argv, input=user_text.encode("utf-8"), stdout=out,
                                  stderr=subprocess.PIPE, env=env, cwd=cwd, timeout=MODEL_TIMEOUT)
            if proc.returncode != 0:
                fail = "คำสั่งเรียกโมเดลจบด้วย exit %d: %s" % (
                    proc.returncode, proc.stderr.decode("utf-8", "replace").strip()[-300:])
        except subprocess.TimeoutExpired:
            fail = "หมดเวลา %d วินาที" % MODEL_TIMEOUT
    events = load_events(transcript_path)
    res = None
    for ev in events:
        if ev.get("type") == "result":
            res = ev
    usage = (res or {}).get("usage") or {}
    tok = lambda key: int(usage.get(key) or 0)
    call = {"events": events, "wall_s": time.time() - t0,
            "result": (res or {}).get("result"),
            "num_turns": int((res or {}).get("num_turns") or 0),
            "cost_usd": float((res or {}).get("total_cost_usd") or 0.0),
            "output_tokens": tok("output_tokens"),
            "context_tokens": tok("input_tokens") + tok("cache_read_input_tokens")
                              + tok("cache_creation_input_tokens"),
            "tool_calls": sum(1 for ev in events if ev.get("type") == "assistant"
                              for b in blocks_of(ev) if b.get("type") == "tool_use"),
            "error": None}
    if res is None:
        call["error"] = fail or "ไม่มีบรรทัด result ใน Trace ของการเรียกโมเดล"
    elif res.get("is_error") or not isinstance(res.get("result"), str):
        call["error"] = fail or "โมเดลจบด้วย error: %s" % str(res.get("result"))[:300]
    return call


def extract_json(text):
    """หา JSON object ในคำตอบ (รับทั้งแบบล้วน แบบอยู่ในบล็อก ``` และแบบมีข้อความนำ)"""
    if not isinstance(text, str):
        return None
    cands = [text.strip()]
    cands += [m.group(1).strip() for m in re.finditer(r"```(?:json)?\s*\n(.*?)```", text, re.S)][::-1]
    i, j = text.find("{"), text.rfind("}")
    if 0 <= i < j:
        cands.append(text[i:j + 1])
    for cand in cands:
        try:
            obj = json.loads(cand)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def retry_note(attempt, reason):
    return ("\n\n---\nคำตอบครั้งที่ %d ใช้ไม่ได้: %s\nตอบใหม่ทั้งหมดเป็น JSON object ตามรูปแบบที่กำหนด"
            % (attempt, reason))


# ---------------------------------------------------------------- Wiki Maintainer (ข้อ 7)

def spread_by_task(trials, cap):
    """หยิบทีละโจทย์วนไป ให้ครบทุกโจทย์ก่อนซ้ำโจทย์เดิม"""
    groups, order = {}, []
    for t in trials:
        if t["task"] not in groups:
            groups[t["task"]] = []
            order.append(t["task"])
        groups[t["task"]].append(t)
    out = []
    while len(out) < cap and any(groups[g] for g in order):
        for g in order:
            if groups[g] and len(out) < cap:
                out.append(groups[g].pop(0))
    return out


def sample_traces(trials, k):
    """สุ่มแบบแบ่งชั้น: ไม่ผ่าน <= 5 (คะแนนต่ำก่อน) + ผ่าน <= 3 · seed = เลขรอบ"""
    rng = random.Random(k)
    fail = sorted((t for t in trials if t["score"] < PASS_SCORE),
                  key=lambda t: (t["score"], rng.random()))
    ok = sorted((t for t in trials if t["score"] >= PASS_SCORE), key=lambda t: rng.random())
    return spread_by_task(fail, MAX_FAIL), spread_by_task(ok, MAX_PASS)


def wiki_files(wiki_dir):
    """ไฟล์ของ wiki ตามลำดับ: index · log · skill-impact · patterns (เรียงชื่อ)"""
    out = []
    for name in ("index.md", "log.md", "skill-impact.md"):
        if os.path.isfile(os.path.join(wiki_dir, name)):
            out.append(("wiki/" + name, os.path.join(wiki_dir, name)))
    pdir = os.path.join(wiki_dir, "patterns")
    if os.path.isdir(pdir):
        for name in sorted(os.listdir(pdir)):
            if name.endswith(".md"):
                out.append(("wiki/patterns/" + name, os.path.join(pdir, name)))
    return out


def maintainer_input(k, entry, skills_dir, wiki_dir, sampled):
    """sampled = (รายการ (trace_id, เนื้อหา) ที่ไม่ผ่าน, ที่ผ่าน)"""
    fail, ok = sampled
    parts = ["# Iteration %d\n\n" % k,
             "คะแนน Training ของรอบนี้: %s (ผ่านครบ %d/%d Trace)\n\n" % (
                 pct(entry["train_score"]), entry["train_perfect"], entry["train_n"]),
             "## Active skills (ชุดสกิลที่ Agent ใช้ในรอบนี้)\n\n"]
    names = skill_names(skills_dir)
    for name in names:
        parts.append("### skills/%s/SKILL.md\n\n%s\n\n" % (
            name, read_text(os.path.join(skills_dir, name, "SKILL.md")).rstrip()))
    if not names:
        parts.append("(ยังไม่มีสกิล)\n\n")
    parts.append("## Current wiki\n\n")
    for rel, path in wiki_files(wiki_dir):
        parts.append("### %s\n\n%s\n\n" % (rel, read_text(path).rstrip()))
    parts.append("\n## Execution traces (sampled: %d failing + %d passing)\n\n" % (len(fail), len(ok)))
    for tid, content in fail + ok:
        parts.append('<trace id="%s">\n%s\n\n</trace>\n\n' % (tid, content.rstrip()))
    parts.append("ตอบเป็น JSON object ตามรูปแบบที่กำหนด")
    return "".join(parts)


def check_maintainer_output(obj):
    if not isinstance(obj, dict):
        return "คำตอบไม่ใช่ JSON object"
    for key in ("update_index", "append_log"):
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            return "ต้องมีฟิลด์ `%s` เป็นข้อความ" % key
    for key, field in (("create_patterns", "content"), ("update_patterns", "edits")):
        items = obj.get(key) or []
        if not isinstance(items, list):
            return "`%s` ต้องเป็น array" % key
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                return "ทุกรายการใน `%s` ต้องมี name" % key
            if not PATTERN_RE.match(item["name"]):
                return ("ชื่อไฟล์ pattern `%s` ผิดรูปแบบ: ใช้ได้เฉพาะตัวอักษรอังกฤษ ตัวเลข . _ - "
                        "และต้องลงท้าย .md" % item["name"])
            if field == "content" and not isinstance(item.get("content"), str):
                return "`create_patterns` รายการ %s ไม่มี content" % item["name"]
            if field == "edits" and not isinstance(item.get("edits"), list):
                return "`update_patterns` รายการ %s ไม่มี edits" % item["name"]
    return None


def strip_log_heading(text):
    """โปรแกรมเป็นผู้ใส่หัวข้อของรอบเอง จึงตัดหัวข้อ Iteration ที่โมเดลเขียนนำมา"""
    lines = text.strip("\n").split("\n")
    if lines and re.match(r"^#+\s*Iteration\b", lines[0].strip()):
        lines = lines[1:]
    return "\n".join(lines).strip("\n")


def apply_maintainer_output(wiki_dir, obj, k, train_score):
    """โปรแกรมเป็นผู้เขียนไฟล์ wiki ตามคำตอบ · คืนสรุปสำหรับ state.json"""
    pdir = os.path.join(wiki_dir, "patterns")
    os.makedirs(pdir, exist_ok=True)
    created, updated, skipped = [], set(), []
    for item in obj.get("create_patterns") or []:
        path = os.path.join(pdir, item["name"])
        if os.path.isfile(path):
            write_text(path, append_block(read_text(path), item["content"]))
            updated.add(item["name"])
        else:
            write_text(path, with_newline(item["content"]))
            created.append(item["name"])
    for item in obj.get("update_patterns") or []:
        path = os.path.join(pdir, item["name"])
        if not os.path.isfile(path):
            skipped.append("%s: ไม่มีไฟล์นี้" % item["name"])
            continue
        text = before = read_text(path)
        for n, edit in enumerate(item["edits"], 1):
            text, err = apply_edit(text, edit)
            if err:
                skipped.append("%s #%d %s" % (item["name"], n, err))
        if text != before:
            write_text(path, text)
            updated.add(item["name"])
    write_text(os.path.join(wiki_dir, "index.md"), with_newline(obj["update_index"]))
    log_path = os.path.join(wiki_dir, "log.md")
    log = read_text(log_path) if os.path.isfile(log_path) else WIKI_LOG_0
    write_text(log_path, "%s\n\n## Iteration %d · Training %s\n\n%s\n" % (
        log.rstrip("\n"), k, pct(train_score), strip_log_heading(obj["append_log"])))
    return {"patterns_created": created, "patterns_updated": sorted(updated),
            "edits_skipped": skipped,
            "patterns_total": len([n for n in os.listdir(pdir) if n.endswith(".md")])}


# ---------------------------------------------------------------- Skill Proposer (ข้อ 8)

def proposer_input(k, r_best, view_dir, use_wiki):
    parts = ["# Iteration %d\n\n" % k,
             "Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): %s\n\n" % pct(r_best)]
    if use_wiki:
        for name in ("index.md", "skill-impact.md"):
            parts.append("## wiki/%s\n\n%s\n\n" % (
                name, read_text(os.path.join(view_dir, "wiki", name)).rstrip()))
    parts.append("## summary.md\n\n%s\n\n" % read_text(os.path.join(view_dir, "summary.md")).rstrip())
    parts.append("## Active skills\n\n")
    names = skill_names(os.path.join(view_dir, "skills"))
    parts.append("".join("- skills/%s/SKILL.md\n" % n for n in names) if names else "(ยังไม่มีสกิล)\n")
    parts.append("\nสำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย")
    return "".join(parts)


def files_read(events, view_dir):
    """ไฟล์ที่ Proposer เปิดด้วย Read (ไม่ซ้ำ ตามลำดับที่เปิด) เป็น path นับจาก proposer_view/"""
    out = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for b in blocks_of(ev):
            if b.get("type") != "tool_use" or b.get("name") != "Read":
                continue
            inp = b.get("input") if isinstance(b.get("input"), dict) else {}
            path = str(inp.get("file_path") or inp.get("path") or "").replace("\\", "/")
            i = path.rfind("proposer_view/")
            if i >= 0:
                path = path[i + len("proposer_view/"):]
            path = re.sub(r"^(\./)+", "", path)
            if path and path not in out and os.path.isfile(os.path.join(view_dir, path)):
                out.append(path)
    return out


def skill_diff(name, old, new):
    def lines(text):
        parts = text.split("\n")
        if parts and parts[-1] == "":
            parts.pop()
        return [p + "\n" for p in parts]
    return "".join(difflib.unified_diff(
        lines(old), lines(new),
        fromfile="a/skills/%s/SKILL.md" % name, tofile="b/skills/%s/SKILL.md" % name))


def apply_proposal(skills_dir, proposal, cand_skills):
    """Apply (Algorithm 1 บรรทัด 12): คัดลอก skills_dir ไปเป็น cand_skills แล้วทำตามข้อเสนอ
    คืน (สาเหตุที่ใช้ไม่ได้ หรือ None, ข้อความ diff ของ SKILL.md) · ไม่แตะ skills_dir"""
    copy_tree(skills_dir, cand_skills)
    if not isinstance(proposal, dict):
        return "ข้อเสนอไม่ใช่ JSON object", ""
    action = proposal.get("action")
    if action == "no_action":
        return None, ""
    if action not in ("create", "patch"):
        return "action ต้องเป็น create, patch หรือ no_action (ได้ `%s`)" % action, ""
    name = proposal.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name) or name in (".", ".."):
        return "ชื่อสกิล `%s` ผิดรูปแบบ: ใช้ได้เฉพาะตัวอักษรอังกฤษ ตัวเลข . _ -" % name, ""
    sdir = os.path.join(cand_skills, name)
    skill_path, purpose_path = os.path.join(sdir, "SKILL.md"), os.path.join(sdir, "PURPOSE.md")
    old = read_text(skill_path) if os.path.isfile(skill_path) else ""
    if action == "create":
        skill_md, purpose_md = proposal.get("skill_md"), proposal.get("purpose_md")
        if not isinstance(skill_md, str) or not skill_md.startswith("---"):
            return "skill_md ต้องเป็นทั้งไฟล์ และขึ้นต้นด้วย YAML frontmatter `---`", ""
        if not isinstance(purpose_md, str) or not purpose_md.strip():
            return "create ต้องมี purpose_md", ""
        reset_dir(sdir)
        new = with_newline(skill_md)
        write_text(skill_path, new)
        write_text(purpose_path, with_newline(purpose_md))
        return None, skill_diff(name, old, new)
    if not os.path.isfile(skill_path):
        return "patch: ไม่มีสกิล `%s` ในชุดสกิลที่ใช้งาน (มี: %s)" % (
            name, ", ".join(skill_names(cand_skills)) or "ไม่มี"), ""
    edits = proposal.get("edits")
    if not isinstance(edits, list) or not edits:
        return "patch ต้องมี edits อย่างน้อย 1 รายการ", ""
    new = old
    for n, edit in enumerate(edits, 1):
        new, err = apply_edit(new, edit)
        if err:
            return "รายการแก้ที่ %d ใช้ไม่ได้ · %s" % (n, err), ""
    if new == old:
        return "patch ไม่ได้เปลี่ยนอะไรใน SKILL.md", ""
    write_text(skill_path, new)
    extra = proposal.get("purpose_append")
    if isinstance(extra, str) and extra.strip():
        base = read_text(purpose_path) if os.path.isfile(purpose_path) else ""
        base = base.rstrip("\n")
        write_text(purpose_path, (base + "\n\n" if base else "") + extra.strip("\n") + "\n")
    return None, skill_diff(name, old, new)


# ---------------------------------------------------------------- Gate (ข้อ 9)

def impact_entry(k, proposal, outcome, val_score, r_before, r_after, diff):
    action = proposal.get("action")
    rationale = " ".join(str(proposal.get("rationale") or "-").split())
    if outcome == "ACCEPTED":
        verdict = "รับ (R_best ใหม่ %s)" % pct(r_after)
    elif outcome == "REJECTED":
        verdict = "ไม่รับ ย้อนกลับไปใช้ชุดสกิลเดิม"
    else:
        verdict = "ไม่มีข้อเสนอ ใช้ชุดสกิลเดิม"
    lines = ["## Iteration %d · %s `%s` · %s" % (k, action, proposal.get("name") or "-", outcome), "",
             "- Validation ของสกิลที่เสนอ: %s · R_best ก่อนหน้า: %s -> %s" % (
                 pct(val_score) if val_score is not None else "(ไม่ได้วัด)", pct(r_before), verdict),
             "- เหตุผลของข้อเสนอ: %s" % rationale]
    if action != "no_action":
        lines += ["", "Diff ของ SKILL.md ที่เสนอ:", "", "```diff", diff.rstrip("\n"), "```"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- คำสั่ง

def cmd_init(ws, args):
    if os.path.isfile(ws.state_path):
        die("มี %s อยู่แล้ว · ไม่ทำอะไร (ใช้ชื่อ workspace อื่น หรือ loop/status กับของเดิม)" % ws.state_path)
    suite_src = os.path.join(ws.work, "suite")
    suite_json = os.path.join(suite_src, "suite.json")
    if not os.path.isfile(suite_json):
        die("ไม่พบ %s · <work> ต้องมีโฟลเดอร์ suite/" % suite_json)
    accounts = [a.strip() for a in args.accounts.split(",") if a.strip()]
    if not accounts:
        die("--accounts ต้องมีอย่างน้อย 1 บัญชี")
    cfg = {"name": ws.name, "skillopt": os.path.abspath(args.skillopt or DEFAULT_SKILLOPT),
           "accounts": accounts, "iters": args.iters, "reps": args.reps, "par": args.par,
           "model": args.model, "effort": args.effort,
           "opt_model": args.opt_model, "opt_effort": args.opt_effort,
           "task_desc": args.task_desc, "use_wiki": not args.no_wiki}
    for d in (ws.raw, ws.skills, ws.history, os.path.join(ws.rollouts, "suite"),
              os.path.join(ws.rollouts, "runs")):
        os.makedirs(d, exist_ok=True)
    grader = str(read_json(suite_json).get("grader") or "grade.py")
    for name in ("suite.json", grader):
        src = os.path.join(suite_src, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(ws.rollouts, "suite", name))
    if cfg["use_wiki"]:
        os.makedirs(os.path.join(ws.wiki, "patterns"), exist_ok=True)
        write_text(os.path.join(ws.wiki, "index.md"), WIKI_INDEX_0)
        write_text(os.path.join(ws.wiki, "log.md"), WIKI_LOG_0)
        write_text(os.path.join(ws.wiki, "skill-impact.md"), WIKI_IMPACT_0)
    ws.save({"cfg": cfg, "k": 0, "phase": "init", "r_best": None, "history": []})
    print("สร้าง workspace %s แล้ว: ชุดสกิลว่าง · wiki %s · ขั้นถัดไปคือ baseline" % (
        ws.root, "ว่าง" if cfg["use_wiki"] else "ไม่ใช้ (--no-wiki)"))


def cmd_baseline(ws, args):
    st = ws.load()
    if st.get("baseline"):
        print("วัด baseline ไปแล้ว (%s) · ไม่ทำอะไร" % pct(st["baseline"].get("val_score")))
        return
    require_phase(st, "baseline")
    trials = run_trials(ws, st["cfg"], "k00-val", "val", None)
    score = mean_score(trials)
    base = aggregate(trials)
    base["val_score"] = score
    st["baseline"], st["r_best"], st["phase"] = base, score, "gate"
    ws.save(st)
    print("Baseline Validation (ชุดสกิลว่าง): %s = R_best เริ่มต้น" % pct(score))


def cmd_rollout(ws, args):
    st = ws.load()
    if st.get("phase") == "gate" and is_perfect(st.get("r_best")):
        print("R_best = 100% แล้ว · ไม่เริ่มรอบใหม่")
        return
    require_phase(st, "rollout")
    k = st["k"] + 1
    skills_in = skill_names(ws.skills)
    trials = run_trials(ws, st["cfg"], "k%02d-train" % k, "train", ws.skills)
    raw = ws.raw_iter(k)
    reset_dir(os.path.join(raw, "traces"))
    for t in trials:
        write_text(os.path.join(raw, "traces", t["trace_id"] + ".md"), build_trace(t, k))
    write_text(os.path.join(raw, "summary.md"), build_summary(trials, k))
    entry = {"k": k, "skills_in": skills_in, "train_score": mean_score(trials),
             "train_perfect": sum(1 for t in trials if t["score"] >= PASS_SCORE),
             "train_n": len(trials), "train_checks": check_counts(trials),
             "train": aggregate(trials)}
    st["history"].append(entry)
    st["k"], st["phase"] = k, "rollout"
    ws.save(st)
    print("รอบ %d · Training %s (ผ่านครบ %d/%d) · Trace อยู่ที่ %s" % (
        k, pct(entry["train_score"]), entry["train_perfect"], entry["train_n"], raw))


def cmd_maintain(ws, args):
    st = ws.load()
    require_phase(st, "maintain")
    cfg, k, entry = st["cfg"], st["k"], st["history"][-1]
    if not cfg.get("use_wiki", True):
        st["phase"] = "maintain"
        ws.save(st)
        print("รอบ %d · --no-wiki: ข้าม Wiki Maintainer" % k)
        return
    trials = read_trials(ws.trials_dir("k%02d-train" % k))
    traces_dir = os.path.join(ws.raw_iter(k), "traces")
    trials = [t for t in trials if os.path.isfile(os.path.join(traces_dir, t["trace_id"] + ".md"))]
    if not trials:
        die("ไม่พบ Trace ของรอบ %d ใต้ %s" % (k, traces_dir))
    fail, ok = sample_traces(trials, k)
    load = lambda ts: [(t["trace_id"], read_text(os.path.join(traces_dir, t["trace_id"] + ".md"))) for t in ts]
    user_text = maintainer_input(k, entry, ws.skills, ws.wiki, (load(fail), load(ok)))
    hist = ws.hist_iter(k)
    write_text(os.path.join(hist, "maintainer_input.md"), user_text)
    system_prompt = load_prompt("maintainer.md", cfg)
    stats = {"calls": 0, "tool_calls": 0, "cost_usd": 0.0, "wall_s": 0.0,
             "output_tokens": 0, "context_tokens": 0}
    obj, note = None, ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        call = call_model(cfg, system_prompt, user_text + note, "", hist,
                          os.path.join(hist, "maintainer_transcript_%d.jsonl" % attempt))
        stats["cost_usd"] += call["cost_usd"]
        stats["wall_s"] += call["wall_s"]
        for key in ("tool_calls", "output_tokens", "context_tokens"):
            stats[key] = call[key]
        stats["calls"] = call["num_turns"]
        reason = call["error"]
        if not reason:
            obj = extract_json(call["result"])
            reason = check_maintainer_output(obj) if obj is not None else "คำตอบไม่ใช่ JSON object"
        if not reason:
            break
        obj = None
        print("[maintain] คำตอบครั้งที่ %d ใช้ไม่ได้: %s" % (attempt, reason))
        note = retry_note(attempt, reason)
    if obj is None:
        die("Wiki Maintainer ตอบใช้ไม่ได้ครบ %d ครั้ง · wiki ไม่ถูกแก้" % MAX_ATTEMPTS)
    write_text(os.path.join(hist, "maintainer_output.json"), dump_json(obj))
    entry["sampled"] = {"fail": [t["trace_id"] for t in fail], "pass": [t["trace_id"] for t in ok]}
    entry.update(apply_maintainer_output(ws.wiki, obj, k, entry["train_score"]))
    stats["cost_usd"], stats["wall_s"] = round(stats["cost_usd"], 4), round(stats["wall_s"], 1)
    entry["maintainer"] = stats
    st["phase"] = "maintain"
    ws.save(st)
    print("รอบ %d · Wiki Maintainer: pattern ใหม่ %d · แก้ %d · รวม %d%s" % (
        k, len(entry["patterns_created"]), len(entry["patterns_updated"]), entry["patterns_total"],
        " · รายการแก้ที่ข้าม %d" % len(entry["edits_skipped"]) if entry["edits_skipped"] else ""))


def cmd_propose(ws, args):
    st = ws.load()
    require_phase(st, "propose")
    cfg, k, entry = st["cfg"], st["k"], st["history"][-1]
    use_wiki = cfg.get("use_wiki", True)
    hist, raw = ws.hist_iter(k), ws.raw_iter(k)
    view = os.path.join(hist, "proposer_view")
    reset_dir(view)
    if use_wiki:
        shutil.copytree(ws.wiki, os.path.join(view, "wiki"))
    shutil.copytree(os.path.join(raw, "traces"), os.path.join(view, "traces"))
    copy_tree(ws.skills, os.path.join(view, "skills"))
    shutil.copy2(os.path.join(raw, "summary.md"), os.path.join(view, "summary.md"))
    user_text = proposer_input(k, st["r_best"], view, use_wiki)
    write_text(os.path.join(hist, "proposer_input.md"), user_text)
    system_prompt = load_prompt("proposer.md" if use_wiki else "proposer_nowiki.md", cfg)
    n_traces = len([n for n in os.listdir(os.path.join(view, "traces")) if n.endswith(".md")])
    need = min(MIN_TRACES_READ, n_traces)
    cand_skills = os.path.join(hist, "candidate", "skills")
    stats = {"attempts": 0, "reads": [], "traces_read": 0, "patterns_read": 0,
             "calls": 0, "cost_usd": 0.0, "wall_s": 0.0, "context_tokens": 0}
    proposal, diff, note, reason = None, "", "", ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        call = call_model(cfg, system_prompt, user_text + note, "Read", view,
                          os.path.join(hist, "proposer_transcript_%d.jsonl" % attempt))
        reads = files_read(call["events"], view)
        stats["attempts"] = attempt
        stats["reads"] = reads
        stats["traces_read"] = len([p for p in reads if p.startswith("traces/")])
        stats["patterns_read"] = len([p for p in reads if p.startswith("wiki/patterns/")])
        stats["calls"] += call["num_turns"]
        stats["cost_usd"] += call["cost_usd"]
        stats["wall_s"] += call["wall_s"]
        stats["context_tokens"] += call["context_tokens"]
        reason = call["error"]
        cand = None
        if not reason:
            cand = extract_json(call["result"])
            if cand is None:
                reason = "ข้อความสุดท้ายไม่ใช่ JSON object"
            elif cand.get("action") != "no_action" and stats["traces_read"] < need:
                reason = "เปิด Trace แล้ว %d ไฟล์ ต้องเปิดอย่างน้อย %d ไฟล์ใน traces/ ก่อนเสนอ" % (
                    stats["traces_read"], need)
            else:
                reason, diff = apply_proposal(ws.skills, cand, cand_skills)
        if not reason:
            proposal = cand
            break
        print("[propose] ข้อเสนอครั้งที่ %d ใช้ไม่ได้: %s" % (attempt, reason))
        note = retry_note(attempt, reason)
    if proposal is None:
        proposal = {"action": "no_action",
                    "rationale": "ข้อเสนอใช้ไม่ได้ครบ %d ครั้ง (ครั้งสุดท้าย: %s)" % (MAX_ATTEMPTS, reason)}
        apply_proposal(ws.skills, proposal, cand_skills)
        diff = ""
    write_text(os.path.join(hist, "proposal.json"), dump_json(proposal))
    write_text(os.path.join(hist, "proposal.diff"), diff)
    entry["proposal"] = {"action": proposal.get("action"), "name": proposal.get("name"),
                         "rationale": proposal.get("rationale")}
    stats["cost_usd"], stats["wall_s"] = round(stats["cost_usd"], 4), round(stats["wall_s"], 1)
    entry["proposer"] = stats
    st["phase"] = "propose"
    ws.save(st)
    print("รอบ %d · Skill Proposer: %s `%s` · เปิด pattern %s / Trace %d ไฟล์ · ชุดที่เสนออยู่ที่ %s" % (
        k, proposal.get("action"), proposal.get("name") or "-",
        stats["patterns_read"] if use_wiki else "-", stats["traces_read"], cand_skills))


def cmd_gate(ws, args):
    st = ws.load()
    require_phase(st, "gate")
    cfg, k, entry = st["cfg"], st["k"], st["history"][-1]
    use_wiki = cfg.get("use_wiki", True)
    hist = ws.hist_iter(k)
    proposal = read_json(os.path.join(hist, "proposal.json"))
    cand_skills = os.path.join(hist, "candidate", "skills")
    r_before = st["r_best"]
    val_trials, val_score = [], None
    if proposal.get("action") == "no_action":
        outcome = "NO_ACTION"
    else:
        val_trials = run_trials(ws, cfg, "k%02d-val" % k, "val", cand_skills)
        val_score = mean_score(val_trials)
        outcome = "ACCEPTED" if val_score > r_before else "REJECTED"   # เท่ากัน = ไม่รับ
    if outcome == "ACCEPTED":
        copy_tree(cand_skills, ws.skills)
        st["r_best"] = val_score
    entry.update({"val_score": val_score, "r_best_before": r_before,
                  "accepted": outcome == "ACCEPTED", "outcome": outcome,
                  "r_best_after": st["r_best"], "skills_out": skill_names(ws.skills)})
    if val_trials:
        entry["val"] = aggregate(val_trials)
    if use_wiki:      # จดทุกผลตัดสิน · wiki ไม่ถูกย้อนกลับ
        dpath = os.path.join(hist, "proposal.diff")
        diff = read_text(dpath) if os.path.isfile(dpath) else ""
        ipath = os.path.join(ws.wiki, "skill-impact.md")
        impact = read_text(ipath) if os.path.isfile(ipath) else WIKI_IMPACT_0
        write_text(ipath, impact.rstrip("\n") + "\n\n" + impact_entry(
            k, proposal, outcome, val_score, r_before, st["r_best"], diff))
        copy_tree(ws.wiki, os.path.join(hist, "wiki"))
    copy_tree(ws.skills, os.path.join(hist, "skills"))
    write_text(os.path.join(hist, "gate.json"), dump_json({
        "k": k, "val_score": val_score, "r_best_before": r_before, "outcome": outcome,
        "val_trials": [{"trace_id": t["trace_id"], "score": t["score"]} for t in val_trials]}))
    st["phase"] = "gate"
    ws.save(st)
    print("รอบ %d · Validation ของสกิลที่เสนอ %s · R_best ก่อนหน้า %s -> %s · สกิลที่ใช้งาน: %s" % (
        k, pct(val_score) if val_score is not None else "(ไม่ได้วัด)", pct(r_before), outcome,
        ", ".join(skill_names(ws.skills)) or "(ไม่มี)"))


def cmd_loop(ws, args):
    st = ws.load()
    if args.iters is not None:
        st["cfg"]["iters"] = args.iters
        ws.save(st)
    steps = {"baseline": cmd_baseline, "rollout": cmd_rollout, "maintain": cmd_maintain,
             "propose": cmd_propose, "gate": cmd_gate}
    while True:
        st = ws.load()
        phase = st.get("phase")
        if phase == "gate" and (is_perfect(st.get("r_best")) or st["k"] >= st["cfg"]["iters"]):
            break
        nxt = NEXT_CMD.get(phase)
        if nxt is None:
            die("state.json มี phase ที่ไม่รู้จัก: %s" % phase)
        print("[loop] %s" % nxt)
        sys.stdout.flush()
        steps[nxt](ws, args)
    cmd_status(ws, args)


def cmd_status(ws, args):
    """อ่าน state.json และชื่อโฟลเดอร์ใน skills/ เท่านั้น"""
    st = ws.load()
    cfg = st["cfg"]
    out = ["", "workspace %s · โมเดลที่ทำโจทย์ %s/%s · โมเดลของ Maintainer และ Proposer %s/%s · wiki: %s" % (
        cfg["name"], cfg["model"], cfg["effort"], cfg["opt_model"], cfg["opt_effort"],
        "ใช้" if cfg.get("use_wiki", True) else "ไม่ใช้")]
    base = st.get("baseline")
    if not base:
        print("\n".join(out + ["ยังไม่ได้วัด baseline"]))
        return
    out += ["Baseline Validation (ชุดสกิลว่าง): %s · R_best ตอนนี้: %s · สกิลที่ใช้งาน: %s" % (
        pct(base.get("val_score")), pct(st.get("r_best")), ", ".join(skill_names(ws.skills)) or "(ไม่มี)"),
        "",
        "| รอบ | Training (สกิลก่อนแก้) | pattern ใหม่ | pattern ที่แก้ | pattern รวม "
        "| Proposer อ่าน (pattern/Trace) | ข้อเสนอ | Validation | R_best ก่อน | ผล |",
        "|---|---|---|---|---|---|---|---|---|---|"]
    count = lambda e, key: str(len(e[key])) if key in e else "-"
    trials, trial_cost = base.get("trials", 0), base.get("cost_usd", 0.0)
    calls, call_cost = 0, 0.0
    for e in st.get("history", []):
        prop, pr = e.get("proposal"), e.get("proposer")
        if pr:
            reads = "%s/%s" % (pr.get("patterns_read", "-") if cfg.get("use_wiki", True) else "-",
                               pr.get("traces_read", "-"))
        else:
            reads = "-"
        out.append("| %d | %s (%d/%d) | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            e["k"], pct(e["train_score"]), e["train_perfect"], e["train_n"],
            count(e, "patterns_created"), count(e, "patterns_updated"),
            str(e["patterns_total"]) if "patterns_total" in e else "-", reads,
            "%s `%s`" % (prop.get("action"), prop.get("name") or "-") if prop else "-",
            pct(e.get("val_score")), pct(e.get("r_best_before")),
            e.get("outcome") or "(ยังไม่ตัดสิน)"))
        for part in ("train", "val"):
            trials += e.get(part, {}).get("trials", 0)
            trial_cost += e.get(part, {}).get("cost_usd", 0.0)
        if "maintainer" in e:
            calls += 1
            call_cost += e["maintainer"].get("cost_usd", 0.0)
        if pr:
            calls += pr.get("calls", 0)
            call_cost += pr.get("cost_usd", 0.0)
    k, iters, phase = st.get("k", 0), cfg["iters"], st.get("phase")
    if phase == "gate" and is_perfect(st.get("r_best")) and k < iters:
        status = "หยุดแล้ว เพราะ R_best = 100%% ที่รอบ %d (หยุดก่อนครบ %d รอบ)" % (k, iters)
    elif phase == "gate" and k >= iters:
        status = "หยุดแล้ว เพราะครบ %d รอบ" % iters
    else:
        status = "ยังไม่จบ (รอบ %d · ขั้นล่าสุด %s)" % (k, phase)
    out += ["", "รวม: Trial ของ Inference Agent %d ครั้ง ($%.2f) · การเรียกโมเดลของ Maintainer + Proposer %d ครั้ง ($%.2f)" % (
        trials, trial_cost, calls, call_cost), "สถานะ: " + status]
    print("\n".join(out))


COMMANDS = {"init": cmd_init, "baseline": cmd_baseline, "rollout": cmd_rollout,
            "maintain": cmd_maintain, "propose": cmd_propose, "gate": cmd_gate,
            "loop": cmd_loop, "status": cmd_status}


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    ap = argparse.ArgumentParser(description="WikiSkill: วงรอบปรับสกิลที่มี wiki คั่นกลาง")
    sub = ap.add_subparsers(dest="cmd")
    sub.required = True
    for name in ("init", "baseline", "rollout", "maintain", "propose", "gate", "loop", "status"):
        p = sub.add_parser(name)
        p.add_argument("work", help="โฟลเดอร์งานที่มี suite/ และ runs/")
        p.add_argument("--ws", required=True, help="ชื่อ workspace (runs/<ws>/)")
        if name == "init":
            p.add_argument("--accounts", required=True, help="คำสั่งของบัญชี คั่นด้วย , เช่น yolo1,yolo2")
            p.add_argument("--iters", type=int, default=8)
            p.add_argument("--reps", type=int, default=3)
            p.add_argument("--par", type=int, default=6)
            p.add_argument("--model", default="sonnet")
            p.add_argument("--effort", default="medium")
            p.add_argument("--opt-model", dest="opt_model", default="sonnet")
            p.add_argument("--opt-effort", dest="opt_effort", default="high")
            p.add_argument("--task-desc", dest="task_desc", default=DEFAULT_TASK_DESC)
            p.add_argument("--no-wiki", dest="no_wiki", action="store_true")
            p.add_argument("--skillopt", default=None)
        if name == "loop":
            p.add_argument("--iters", type=int, default=None, help="ใช้แทนจำนวนรอบสูงสุดของ init")
    args = ap.parse_args(argv)
    if not NAME_RE.match(args.ws):
        die("ชื่อ workspace ใช้ได้เฉพาะตัวอักษรอังกฤษ ตัวเลข . _ -")
    COMMANDS[args.cmd](Workspace(args.work, args.ws), args)


if __name__ == "__main__":
    main()
