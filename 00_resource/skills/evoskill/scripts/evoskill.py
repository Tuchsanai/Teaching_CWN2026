#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""evoskill.py : โปรแกรมควบคุมการรันของสกิล evoskill (วงรอบ EvoSkill v2 · arXiv:2610.25931)

    python3 evoskill.py <คำสั่ง> <work> --run <ชื่อ> [ตัวเลือก]

<work> = โฟลเดอร์ที่มี bench/ (สิ่งที่ผู้ใช้ส่ง) และ runs/ (1 การรัน = 1 โฟลเดอร์ runs/<ชื่อ>/)
คำสั่ง : init adapt audit base turn rollout test run status noise eval export
Agent 3 ตัว : Benchmark Adaptor (adapt) · Solver (base rollout test eval ผ่าน skillopt.py run) · Evolver (turn)
ใช้เฉพาะไลบรารีมาตรฐาน · Python 3.8 ขึ้นไป · ทุกคำสั่งพิมพ์ผลทาง stdout (ข้อผิดพลาดพิมพ์ทาง stderr แล้ว exit 1)
"""
import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPTS)
PROMPTS = os.path.join(SKILL_DIR, "prompts")

SPLITS = ("train", "validation", "test")
SHORT = {"train": "train", "validation": "val", "test": "test"}          # ชื่อชุดที่ skillopt.py ใช้
LONG = {"train": "train", "val": "validation", "test": "test", "all": "all"}
STEPS = ("adapt", "base", "turn", "rollout", "test")
EVO_KEYS = ("traces", "solver_workspaces", "reference", "scores", "skills", "staging", "evolver_workspace")
EVO_READONLY = ("traces", "scores", "solver_workspaces", "skills", "reference")
PLUGIN_IMPORTS = ("json", "os", "pathlib", "re", "typing", "dataclasses", "collections", "itertools",
                  "functools", "plugin_api")
FROZEN = ("benchmark_plugin.py", "benchmark_grader.py", "tasks.json")
PASS = 0.999
TINY = 1e-9
ADAPTOR_TIMEOUT = 1800
SOLVER_TIMEOUT = 600
CUT_INPUT, CUT_RESULT, CUT_TEXT = 2500, 1200, 1500
EXPORT_MAX = 400 * 1024
EXPORT_SKIP_EXT = (".jsonl", ".stderr", ".pyc")
RESERVED_LEG = re.compile(r"^(base|v\d+)_(train|val|test)$")
RUN_SIZE = re.compile(r"(\d+)\s*epochs?\s*[·x×,]\s*(\d+)\s*samples?\s+per\s+task", re.I)

# สคริปต์ที่รันใน mount namespace ใหม่ (unshare -m) ก่อนเริ่ม Agent
#   $1 = โฟลเดอร์ทำงานที่ Agent เห็น · $2 = จำนวน bind · ตามด้วย <src> <dst> <rw|ro> ต่อ 1 bind
#   ถัดมา = จำนวนโฟลเดอร์ที่ต้องซ่อน ตามด้วย path · ที่เหลือ = คำสั่งของ Agent
# ลำดับสำคัญ: ผูกทุกโฟลเดอร์ก่อน (ต้นทางยังมองเห็นอยู่) แล้วจึงแทนโฟลเดอร์ที่ซ่อนด้วย tmpfs ว่าง
NS_SCRIPT = r'''
set -eu
cwd="$1"; shift
n="$1"; shift
i=0
while [ "$i" -lt "$n" ]; do
  src="$1"; dst="$2"; mode="$3"; shift 3
  mkdir -p "$dst"
  mount --bind "$src" "$dst"
  if [ "$mode" = "ro" ]; then mount -o remount,bind,ro "$dst"; fi
  i=$((i+1))
done
n="$1"; shift
i=0
while [ "$i" -lt "$n" ]; do
  hide="$1"; shift
  if [ -d "$hide" ]; then mount -t tmpfs tmpfs "$hide"; fi
  i=$((i+1))
done
cd "$cwd"
exec "$@"
'''

# โปรแกรมที่รัน list_tasks() ของ plug-in ใน process แยก
LIST_TASKS = r'''
import json, sys
setup, root, out = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, setup)
import benchmark_plugin
rows = []
for t in benchmark_plugin.list_tasks(root):
    rows.append(t.to_dict() if hasattr(t, "to_dict") else dict(t))
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
'''


# ───────────────────────── ส่วนกลาง ─────────────────────────

def die(msg, code=1):
    sys.stdout.flush()
    print("evoskill: " + msg, file=sys.stderr)
    sys.exit(code)


def say(msg=""):
    print(msg, flush=True)


def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace").replace("\r\n", "\n")


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_json(path, obj):
    """เขียนผ่านไฟล์ชั่วคราวแล้วสลับชื่อ ไฟล์จึงไม่ขาดครึ่งเมื่อโปรแกรมถูกหยุดกลางทาง"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rm_error(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_tree(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path, onerror=_rm_error)
    elif os.path.lexists(path):
        os.remove(path)


def copy_tree(src, dst, skip_names=()):
    """คัดลอกทั้งโฟลเดอร์ (ลบปลายทางเดิมก่อน) · skip_names = ชื่อที่ไม่คัดลอกทุกระดับ"""
    remove_tree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*skip_names) if skip_names else None)


def list_files(base):
    """path ของทุกไฟล์ใต้ base (เทียบกับ base · คั่นด้วย /) เรียงตามชื่อ"""
    out = []
    for root, dirs, names in os.walk(base):
        dirs.sort()
        for name in names:
            out.append(os.path.relpath(os.path.join(root, name), base).replace(os.sep, "/"))
    return sorted(out)


def hash_tree(base):
    return {rel: sha256(os.path.join(base, rel)) for rel in list_files(base)} if os.path.isdir(base) else {}


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


def num(value, default=0):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


# ───────────────────────── โฟลเดอร์งานและสถานะ ─────────────────────────

def work_dir(path):
    work = os.path.abspath(path)
    if not os.path.isdir(work):
        die("ไม่พบโฟลเดอร์งาน: %s" % work)
    return work


def run_dir(args):
    name = args.run
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", name or ""):
        die("ชื่อการรัน (--run) ใช้ได้เฉพาะตัวอักษรอังกฤษ ตัวเลข . _ - (ได้ %r)" % name)
    return os.path.join(work_dir(args.work), "runs", name)


def load_state(rd):
    path = os.path.join(rd, "state.json")
    if not os.path.isfile(path):
        die("ไม่พบการรันนี้ (%s) · สร้างด้วยคำสั่ง init ก่อน" % path)
    st = read_json(path)
    if not isinstance(st, dict) or "phase" not in st:
        die("อ่าน state.json ไม่ได้: %s" % path)
    st.setdefault("legs", {})
    st.setdefault("turns", [])
    return st


def save_state(rd, st):
    write_json(os.path.join(rd, "state.json"), st)


def next_step(st):
    """ขั้นถัดไปตามตารางลำดับของขั้น · None = จบแล้ว"""
    phase, k, epochs = st.get("phase"), st.get("k") or 0, st.get("epochs") or 0
    if phase == "init":
        return "adapt"
    if phase == "adapt":
        return "base"
    if phase == "base":
        return "turn"
    if phase == "turn":
        return "rollout"
    if phase == "rollout":
        return "turn" if k < epochs else "test"
    return None


def step_epoch(st, step):
    k = st.get("k") or 0
    return k + 1 if step == "turn" else k


def require_step(st, step):
    nxt = next_step(st)
    if nxt == step:
        return
    if nxt is None:
        die("ทำ `%s` ไม่ได้: การรัน %s จบแล้ว (วัด Test Set แล้ว)" % (step, st["cfg"]["name"]))
    die("ทำ `%s` ไม่ได้: ขั้นล่าสุดที่ทำเสร็จคือ `%s` · ขั้นถัดไปคือ `%s` (epoch %d) · ยังไม่ได้เรียกโมเดล" % (
        step, st.get("phase"), nxt, step_epoch(st, nxt)))


def data_root_of(work):
    base = os.path.join(work, "bench", "data")
    dirs = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))) if os.path.isdir(base) else []
    if len(dirs) != 1:
        die("ใต้ %s ต้องมีโฟลเดอร์ข้อมูล (data root) 1 โฟลเดอร์พอดี · พบ %d โฟลเดอร์" % (base, len(dirs)))
    return os.path.join(base, dirs[0])


def data_root(st, work):
    path = st["cfg"].get("data")
    return path if path and os.path.isdir(path) else data_root_of(work)


def load_tasks(rd):
    tasks = read_json(os.path.join(rd, "setup", "tasks.json"))
    if not isinstance(tasks, list) or not tasks:
        die("อ่าน setup/tasks.json ไม่ได้ · ต้องทำขั้น adapt ให้เสร็จก่อน")
    return tasks


def verify_freeze(rd):
    """ก่อนใช้ setup/ ทุกครั้ง: hash ของ 3 ไฟล์ต้องตรงกับที่ล็อกไว้ใน freeze.json"""
    freeze = read_json(os.path.join(rd, "setup", "freeze.json"))
    if not isinstance(freeze, dict) or not isinstance(freeze.get("sha256"), dict):
        die("ไม่พบ setup/freeze.json · ต้องทำขั้น adapt ให้เสร็จก่อน")
    for name in FROZEN:
        path = os.path.join(rd, "setup", name)
        if not os.path.isfile(path):
            die("ไฟล์ setup/%s หายไปหลังล็อก · หยุดก่อนเรียกโมเดล" % name)
        if sha256(path) != freeze["sha256"].get(name):
            die("ไฟล์ setup/%s ถูกแก้หลังล็อก (hash ไม่ตรงกับ setup/freeze.json) · หยุดก่อนเรียกโมเดล" % name)


# ───────────────────────── ชุดสกิล ─────────────────────────

def skill_names(folder):
    """สกิล = โฟลเดอร์ชั้นแรกที่มี SKILL.md"""
    if not folder or not os.path.isdir(folder):
        return []
    return sorted(d for d in os.listdir(folder) if os.path.isfile(os.path.join(folder, d, "SKILL.md")))


def frontmatter_fields(text):
    m = re.match(r"^﻿?---[ \t]*\n(.*?\n)---[ \t]*(?:\n|$)", text, re.S)
    fields, key = {}, None
    for line in (m.group(1) if m else "").split("\n"):
        hit = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if hit:
            key = hit.group(1)
            value = hit.group(2).strip()
            fields[key] = "" if value in (">", "|", ">-", "|-", ">+", "|+") else value.strip("\"'")
        elif key and line.strip() and line[:1] in (" ", "\t"):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


def skill_info(folder):
    names = skill_names(folder)
    md_bytes, problems = 0, []
    for name in names:
        path = os.path.join(folder, name, "SKILL.md")
        md_bytes += os.path.getsize(path)
        if not frontmatter_fields(read_text(path)).get("description"):
            problems.append(name)
    mds = set("%s/SKILL.md" % name for name in names)
    others = [rel for rel in list_files(folder) if rel not in mds] if os.path.isdir(folder) else []
    return {"skills": names, "skill_md_bytes": md_bytes, "skill_other_files": others, "skill_problems": problems}


# ───────────────────────── transcript ของ Agent ─────────────────────────

def read_events(path):
    events = []
    try:
        f = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return events
    with f:
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
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def tool_text(name, inp):
    """ข้อความที่แสดงแทนการใช้เครื่องมือ 1 ครั้ง: คำสั่ง หรือไฟล์ที่เขียน"""
    if not isinstance(inp, dict):
        return json.dumps(inp, ensure_ascii=False)
    if isinstance(inp.get("command"), str):
        return inp["command"]
    path = inp.get("file_path") or inp.get("path") or inp.get("notebook_path")
    if isinstance(path, str):
        for key in ("content", "new_string", "new_source"):
            if isinstance(inp.get(key), str):
                return path + "\n" + inp[key]
        return path
    for key in ("prompt", "pattern", "query"):
        if isinstance(inp.get(key), str):
            return inp[key]
    return json.dumps(inp, ensure_ascii=False)


def result_text(block):
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, dict):
                parts.append("[%s]" % item.get("type"))
        return "\n".join(parts)
    return "" if content is None else json.dumps(content, ensure_ascii=False)


def agent_stats(transcript, evo_real=None, old_scripts=()):
    """สถิติของ 1 ครั้งที่เรียก Agent (ฟิลด์ชุดแรกของ stats.json)"""
    s = {"ok": False, "tool_calls": 0, "tools": {}, "bash": 0, "bash_python": 0, "rerun_old_scripts": 0,
         "subagents": 0, "compactions": 0, "touch": {key: 0 for key in EVO_KEYS},
         "num_turns": None, "cost_usd": None, "output_tokens": None, "context_tokens": None}
    old_names = sorted(set(os.path.basename(p) for p in old_scripts))
    real = evo_real.replace("\\", "/") if evo_real else None
    for ev in read_events(transcript):
        kind = ev.get("type")
        if kind == "assistant":
            for block in blocks_of(ev):
                if block.get("type") != "tool_use":
                    continue
                name = str(block.get("name"))
                s["tool_calls"] += 1
                s["tools"][name] = s["tools"].get(name, 0) + 1
                if name in ("Task", "Agent"):
                    s["subagents"] += 1
                text = json.dumps(block.get("input"), ensure_ascii=False).replace("\\\\", "/").replace("\\", "/")
                if real:
                    text = text.replace(real, "/evo")           # รันแบบไม่แยกเครื่อง: path จริงของ evo/
                for key in EVO_KEYS:
                    if re.search(r"/evo/%s(?![A-Za-z0-9_])" % key, text):
                        s["touch"][key] += 1
                if name.lower() == "bash":
                    command = block.get("input", {}).get("command") if isinstance(block.get("input"), dict) else ""
                    command = command if isinstance(command, str) else ""
                    s["bash"] += 1
                    if re.search(r"(?<![\w./-])python3?(?![\w-])", command):
                        s["bash_python"] += 1
                    if any(re.search(r"(?<![\w.-])%s(?![\w.-])" % re.escape(n), command) for n in old_names):
                        s["rerun_old_scripts"] += 1
        elif kind == "system" and ev.get("subtype") == "compact_boundary":
            s["compactions"] += 1
        elif kind == "result":
            usage = ev.get("usage") if isinstance(ev.get("usage"), dict) else {}
            cost = ev.get("total_cost_usd")
            s["ok"] = not ev.get("is_error")
            s["num_turns"] = ev.get("num_turns")
            s["cost_usd"] = round(cost, 4) if isinstance(cost, (int, float)) else None
            s["output_tokens"] = usage.get("output_tokens")
            parts = [usage.get(key) for key in ("input_tokens", "cache_read_input_tokens",
                                                "cache_creation_input_tokens")]
            parts = [p for p in parts if isinstance(p, (int, float)) and not isinstance(p, bool)]
            s["context_tokens"] = sum(parts) if parts else None
    return s


def cut(text, limit):
    text = text.rstrip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…(ตัด %d ตัวอักษร)" % (len(text) - limit)


def fenced(text):
    fence = "```"
    while fence in text:
        fence += "`"
    return "%s\n%s\n%s" % (fence, text, fence)


def write_actions(transcript, path, title, message=None):
    """transcript ที่คนอ่านได้ ตามลำดับเวลา"""
    events = read_events(transcript)
    results = {}
    for ev in events:
        if ev.get("type") == "user":
            for block in blocks_of(ev):
                if block.get("type") == "tool_result":
                    results[block.get("tool_use_id")] = result_text(block)
    out = ["# %s" % title, ""]
    if message:
        out += ["ข้อความที่ได้รับ: %s" % " ".join(message.split()), ""]
    step = 0
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        who = "subagent" if ev.get("parent_tool_use_id") else "Agent"
        for block in blocks_of(ev):
            if block.get("type") == "text" and str(block.get("text") or "").strip():
                out += ["**%s พูด:** %s" % (who, cut(str(block["text"]).strip(), CUT_TEXT)), ""]
            elif block.get("type") == "tool_use":
                step += 1
                out += ["### ขั้น %d · %s" % (step, block.get("name")), "",
                        fenced(cut(tool_text(block.get("name"), block.get("input")), CUT_INPUT)), ""]
                if block.get("id") in results:
                    out += ["ผลที่ได้:", "", fenced(cut(results[block.get("id")], CUT_RESULT)), ""]
    if step == 0 and len(out) <= 4:
        out += ["(ไม่มีข้อความหรือการใช้เครื่องมือใน transcript)", ""]
    write_text(path, "\n".join(out))


# ───────────────────────── เรียก Agent (Benchmark Adaptor และ Evolver) ─────────────────────────

def session_members(sid):
    """pid ของทุก process ที่อยู่ใน session เดียวกับ Agent (อ่านจาก /proc · มีเฉพาะ Linux)"""
    pids = []
    try:
        names = os.listdir("/proc")
    except OSError:
        return pids
    for name in names:
        if not name.isdigit():
            continue
        try:
            with open("/proc/%s/stat" % name, "rb") as f:
                fields = f.read().decode("ascii", "replace").rsplit(")", 1)[1].split()
            if int(fields[3]) == sid:                           # state ppid pgrp session
                pids.append(int(name))
        except (OSError, ValueError, IndexError):
            continue
    return pids


def kill_group(proc):
    """หยุดทั้งกลุ่ม process ของ Agent: ขอให้จบก่อน (SIGTERM) รอ 5 วินาที แล้วบังคับ (SIGKILL)"""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            members = session_members(proc.pid)                 # รวม process ที่ย้ายไปอยู่กลุ่มอื่นใน session เดิม
            try:
                os.killpg(proc.pid, sig)
            except OSError:
                pass
            for pid in members:
                try:
                    os.kill(pid, sig)
                except OSError:
                    pass
            if sig == signal.SIGTERM:
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
    try:
        proc.kill()
    except OSError:
        pass


def is_under(path, parent):
    path, parent = os.path.realpath(path), os.path.realpath(parent)
    return path == parent or path.startswith(parent.rstrip(os.sep) + os.sep)


def call_agent(st, work, system_append, message_file, transcript, model, effort, session, timeout,
               cwd_real, cwd_seen, binds, env_dirs):
    """เรียก Claude Code 1 เซสชัน · คืน (timed_out, wall_s, returncode)

    session = None (ไม่เก็บเซสชัน) | ("new", uuid) | ("resume", uuid)
    binds   = [(โฟลเดอร์จริง, path ที่ Agent เห็น, "rw"|"ro")] ใช้เมื่อแยกเครื่อง
    env_dirs = ตัวแปร EVOSKILL_*_DIR ที่ส่ง path จริงให้ Agent เมื่อไม่แยกเครื่อง
    """
    account = st["cfg"]["accounts"][0]
    options = ["-p", "--append-system-prompt", system_append, "--model", model, "--effort", effort,
               "--disallowedTools", "WebSearch,WebFetch", "--output-format", "stream-json", "--verbose",
               "--strict-mcp-config"]
    if session is None:
        options += ["--no-session-persistence"]
    elif session[0] == "new":
        options += ["--session-id", session[1]]
    else:
        options += ["--resume", session[1]]
    env = {k: v for k, v in os.environ.items()
           if not (k.upper().startswith("CLAUDE") or k.upper().startswith("MA_"))}
    env["IS_SANDBOX"] = "1"
    root = os.environ.get("EVOSKILL_ACCOUNT_ROOT") or os.path.join(os.path.expanduser("~"), "ai-accounts", ".Claude")
    account_dir = os.path.join(root, account)
    if os.path.isdir(account_dir):
        exe = shutil.which("claude")
        if not exe:
            die("พบโฟลเดอร์ของบัญชี %s แต่ไม่พบคำสั่ง claude ใน PATH" % account_dir)
        argv = [exe, "--dangerously-skip-permissions", "--disable-slash-commands"] + options
        env["CLAUDE_CONFIG_DIR"] = account_dir
    else:
        try:
            parts = shlex.split(account, posix=(os.name != "nt"))
        except ValueError as e:
            die("อ่านคำสั่งของบัญชี %r ไม่ได้: %s" % (account, e))
        exe = shutil.which(parts[0]) if parts else None
        if not exe:
            die("ไม่พบโฟลเดอร์ของบัญชี %s และไม่พบคำสั่ง '%s' ใน PATH (ตั้ง EVOSKILL_ACCOUNT_ROOT ถ้าบัญชีอยู่ที่อื่น)"
                % (account_dir, parts[0] if parts else account))
        argv = [exe] + parts[1:] + options
    isolate = os.name != "nt" and os.environ.get("EVOSKILL_NO_ISOLATION") != "1" and shutil.which("unshare")
    if isolate:
        hides = ["/workspace"] if os.path.isdir("/workspace") else []
        if not any(is_under(work, h) for h in hides):
            hides.append(os.path.realpath(work))                # โฟลเดอร์งานอยู่นอก /workspace ก็ต้องถูกซ่อน
        for needed, label in ((exe, "คำสั่งของ Agent"), (account_dir, "โฟลเดอร์ของบัญชี")):
            if os.path.exists(needed) and any(is_under(needed, h) for h in hides):
                die("%s (%s) อยู่ใต้โฟลเดอร์ที่ถูกซ่อนจาก Agent (%s) จึงแยกเครื่องไม่ได้ · ย้ายออกนอกโฟลเดอร์นั้น"
                    % (label, needed, ", ".join(hides)))
        cmd = ["unshare", "-m", "--propagation", "private", "bash", "-c", NS_SCRIPT, "evoskill-ns",
               cwd_seen, str(len(binds))]
        for src, dst, mode in binds:
            cmd += [os.path.realpath(src), dst, mode]
        cmd += [str(len(hides))] + hides + argv
        cwd = "/"
    else:
        say("คำเตือน: รัน Agent โดยไม่แยกเครื่อง (ไม่มีคำสั่ง unshare หรือตั้ง EVOSKILL_NO_ISOLATION=1) · ใช้กับ Agent จำลองเท่านั้น ห้ามใช้วัดผลจริง")
        env.update(env_dirs)
        cmd, cwd = argv, cwd_real
    os.makedirs(os.path.dirname(transcript), exist_ok=True)
    timed_out, start, code = False, time.time(), None
    with open(message_file, "rb") as stdin, open(transcript, "wb") as out, \
            open(transcript + ".stderr", "wb") as err:
        try:
            proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=stdin, stdout=out, stderr=err,
                                    start_new_session=(os.name != "nt"))
        except OSError as e:
            die("เริ่ม Agent ไม่ได้ (%s): %s" % (cmd[0], e))
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_group(proc)
            proc.wait()
        except KeyboardInterrupt:
            kill_group(proc)
            proc.wait()
            raise
    return timed_out, round(time.time() - start, 1), code


def stderr_tail(transcript, chars=600):
    try:
        text = read_text(transcript + ".stderr").strip()
    except OSError:
        return ""
    return text[-chars:]


def load_prompt(name):
    path = os.path.join(PROMPTS, name)
    if not os.path.isfile(path):
        die("ไม่พบ prompt: %s" % path)
    return read_text(path)


# ───────────────────────── init ─────────────────────────

def cmd_init(args):
    work = work_dir(args.work)
    rd = run_dir(args)
    if os.path.isfile(os.path.join(rd, "state.json")):
        die("มีการรัน %s อยู่แล้ว (%s) · ไม่ได้แก้อะไร · ใช้ชื่ออื่น หรือทำต่อด้วยคำสั่ง run" % (
            args.run, os.path.join(rd, "state.json")))
    bench = os.path.join(work, "bench")
    instruction = os.path.abspath(args.instruction) if args.instruction else os.path.join(bench, "instruction.md")
    files = {"instruction": instruction, "split": os.path.join(bench, "split.json"),
             "grader": os.path.join(bench, "benchmark_grader.py")}
    solver_prompt = os.path.join(bench, "solver_prompt.txt")
    for path in list(files.values()) + [solver_prompt]:
        if not os.path.isfile(path):
            die("ไม่พบไฟล์ที่ผู้ใช้ต้องส่ง: %s" % path)
    data = data_root_of(work)
    m = RUN_SIZE.search(read_text(instruction))
    if not m:
        die("คำสั่งของผู้ใช้ (%s) ไม่ได้บอกขนาดของการรัน · ต้องมีข้อความรูปแบบ `<E> epochs · <N> samples per task` "
            "เช่น `3 epochs · 3 samples per task` (ตัวคั่นเป็น · x หรือ ,)" % instruction)
    epochs, samples = int(m.group(1)), int(m.group(2))
    if epochs < 1 or samples < 1:
        die("ขนาดของการรันต้องเป็น 1 ขึ้นไปทั้งจำนวน epoch และจำนวนครั้งต่อโจทย์ (ได้ %d และ %d)" % (epochs, samples))
    split = read_json(files["split"])
    if not isinstance(split, dict) or any(not isinstance(split.get(s), list) for s in SPLITS):
        die("split.json ต้องเป็น {\"train\": [...], \"validation\": [...], \"test\": [...]} : %s" % files["split"])
    ids = [i for s in SPLITS for i in split[s]]
    if len(ids) != len(set(ids)) or not split["train"]:
        die("split.json: id ของโจทย์ต้องไม่ซ้ำกันข้ามชุด และชุด train ต้องมีโจทย์อย่างน้อย 1 ข้อ")
    accounts = [x.strip() for x in (args.accounts or "").split(",") if x.strip()]
    if not accounts:
        die("ต้องระบุ --accounts อย่างน้อย 1 บัญชี เช่น --accounts yolo1,yolo2")
    if args.par < 1 or args.turn_minutes <= 0:
        die("--par ต้องเป็น 1 ขึ้นไป และ --turn-minutes ต้องมากกว่า 0")
    if args.skillopt:
        skillopt = os.path.abspath(args.skillopt)
    else:
        parent = os.path.dirname(SKILL_DIR)
        candidates = [os.path.join(parent, name, "scripts", "skillopt.py")
                      for name in ("skill-optimizer", "my-skill-optimizer")]
        skillopt = next((c for c in candidates if os.path.isfile(c)), candidates[0])
    if not os.path.isfile(skillopt):
        die("ไม่พบ skillopt.py ของบท 05 ที่ %s · ระบุด้วย --skillopt <path>" % skillopt)

    inputs = os.path.join(rd, "inputs")
    os.makedirs(inputs, exist_ok=True)
    shutil.copyfile(files["instruction"], os.path.join(inputs, "instruction.md"))
    shutil.copyfile(files["split"], os.path.join(inputs, "split.json"))
    shutil.copyfile(files["grader"], os.path.join(inputs, "benchmark_grader.py"))
    run_json = {key: {"file": path, "sha256": sha256(path)} for key, path in files.items()}
    run_json["data"] = {"dir": data, "files": len(list_files(data))}
    run_json["run_size"] = {"epochs": epochs, "samples_per_task": samples}
    write_json(os.path.join(rd, "RUN.json"), run_json)
    st = {
        "cfg": {
            "name": args.run, "data": data, "skillopt": skillopt, "accounts": accounts, "par": args.par,
            "solver_prompt": read_text(solver_prompt),
            "solver_model": args.solver_model, "solver_effort": args.solver_effort,
            "evolver_model": args.evolver_model, "evolver_effort": args.evolver_effort,
            "adaptor_model": args.adaptor_model,
            "turn_minutes": int(args.turn_minutes) if args.turn_minutes == int(args.turn_minutes) else args.turn_minutes,
            "fresh_session": bool(args.fresh_session),
        },
        "epochs": epochs, "n": samples, "phase": "init", "k": 0, "session_id": None,
        "legs": {}, "turns": [], "adapt": None, "session_cost": 0,
    }
    save_state(rd, st)
    say("สร้างการรัน %s: %d epochs · %d samples per task · โจทย์ train %d · validation %d · test %d · ข้อมูล %d ไฟล์" % (
        args.run, epochs, samples, len(split["train"]), len(split["validation"]), len(split["test"]),
        run_json["data"]["files"]))
    say("Solver %s/%s · Evolver %s/%s · Benchmark Adaptor %s/high · บัญชี %s · par %d · %s" % (
        args.solver_model, args.solver_effort, args.evolver_model, args.evolver_effort, args.adaptor_model,
        ",".join(accounts), args.par, "เซสชันใหม่ทุก epoch" if args.fresh_session else "เซสชันเดียวตลอดการรัน"))
    say("ขั้นถัดไป: adapt")
    return 0


# ───────────────────────── adapt / audit ─────────────────────────

def check_plugin_imports(path):
    try:
        tree = ast.parse(read_text(path), filename=path)
    except SyntaxError as e:
        die("benchmark_plugin.py มี syntax ผิด: %s" % e)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = ["." * node.level + (node.module or "")]
        elif isinstance(node, ast.Name) and node.id in ("__import__", "exec", "eval"):
            mods = [node.id + "()"]
        else:
            continue
        for mod in mods:
            top = mod.split(".")[0]
            if top == "__future__":                              # ไม่ใช่การโหลดโมดูล
                continue
            if top not in PLUGIN_IMPORTS and mod not in bad:
                bad.append(mod)
    if bad:
        die("benchmark_plugin.py import สิ่งที่ไม่อนุญาต: %s · ใช้ได้เฉพาะ %s" % (
            ", ".join(bad), " ".join(PLUGIN_IMPORTS)))


def freeze_tasks(rd, data, user_split):
    """รัน list_tasks() ใน process แยก ตรวจรูปแบบและการแบ่งชุด แล้วเขียน setup/tasks.json"""
    setup = os.path.join(rd, "setup")
    out = os.path.join(setup, "tasks.json.raw")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    try:
        p = subprocess.run([sys.executable, "-c", LIST_TASKS, setup, data, out], cwd=setup, env=env,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    except subprocess.TimeoutExpired:
        die("list_tasks() ของ plug-in ทำงานเกิน 120 วินาที")
    rows = read_json(out)
    remove_tree(out)
    if p.returncode != 0 or not isinstance(rows, list):
        die("รัน list_tasks(%s) ของ plug-in ไม่สำเร็จ (exit %s): %s" % (
            data, p.returncode, p.stderr.decode("utf-8", errors="replace").strip()[-600:]))
    if not rows:
        die("list_tasks() ของ plug-in ไม่คืนโจทย์เลย")
    seen, tasks = set(), []
    for row in rows:
        if not isinstance(row, dict):
            die("list_tasks() ต้องคืน Task ของ plugin_api ทุกตัว")
        tid = row.get("id")
        if not isinstance(tid, str) or not tid or re.search(r"[/\\\s]", tid) or tid in (".", ".."):
            die("id ของโจทย์ต้องเป็นข้อความที่ใช้เป็นชื่อโฟลเดอร์ได้ (ได้ %r)" % (tid,))
        if tid in seen:
            die("plug-in คืน id ซ้ำ: %s" % tid)
        seen.add(tid)
        if row.get("split") not in SPLITS:
            die("โจทย์ %s: split ต้องเป็น train validation หรือ test (ได้ %r)" % (tid, row.get("split")))
        if not isinstance(row.get("instruction"), str) or not row["instruction"].strip():
            die("โจทย์ %s: instruction ต้องเป็นข้อความโจทย์ที่ไม่ว่าง" % tid)
        task = {"id": tid, "split": row["split"], "instruction": row["instruction"],
                "inputs": row.get("inputs") or [], "answer_files": row.get("answer_files") or [],
                "grading": row.get("grading") or {}, "category": row.get("category") or ""}
        if not isinstance(task["inputs"], list) or not isinstance(task["answer_files"], list) \
                or not isinstance(task["grading"], dict):
            die("โจทย์ %s: inputs และ answer_files ต้องเป็น list · grading ต้องเป็น dict" % tid)
        tasks.append(task)
    problems = []
    for split in SPLITS:
        want, got = set(user_split[split]), set(t["id"] for t in tasks if t["split"] == split)
        if want - got:
            problems.append("ชุด %s ขาด %s" % (split, " ".join(sorted(want - got))))
        if got - want:
            problems.append("ชุด %s เกิน %s" % (split, " ".join(sorted(got - want))))
    if problems:
        die("การแบ่งชุดของ plug-in ไม่ตรงกับ split.json ของผู้ใช้: %s · ไม่ล็อก" % " · ".join(problems))
    write_json(os.path.join(setup, "tasks.json"), tasks)
    return tasks


def needle_forms(text):
    """รูปที่ข้อความอาจปรากฏในไฟล์: ตามจริง · แบบ JSON · แบบ JSON ที่ escape ตัวอักษรไทย"""
    forms = [text, json.dumps(text, ensure_ascii=False)[1:-1], json.dumps(text)[1:-1]]
    return [f for i, f in enumerate(forms) if f and f not in forms[:i]]


def audit(rd, data):
    """ตรวจการรั่วใน reference/ · คืน dict ของผล (ไม่เขียนไฟล์)"""
    ref = os.path.join(rd, "reference")
    files = list_files(ref) if os.path.isdir(ref) else []
    held = [t for t in load_tasks(rd) if t["split"] in ("validation", "test")]
    needles = []                                                 # (คำอธิบาย, รูปของข้อความที่ค้น)
    for t in held:
        needles.append(("id ของโจทย์ชุด %s (%s)" % (t["split"], t["id"]), [t["id"]]))
        head = t["instruction"].strip()[:60]
        if head:
            needles.append(("ข้อความโจทย์ของชุด %s (%s)" % (t["split"], t["id"]), needle_forms(head)))
        spec = read_json(os.path.join(data, "tasks", "%s.json" % t["id"]))
        func = spec.get("function") if isinstance(spec, dict) else None
        if isinstance(func, str) and func.strip():
            needles.append(("ชื่อฟังก์ชันของโจทย์ชุด %s (%s: %s)" % (t["split"], t["id"], func), [func]))
    user_lines = set()
    for rel in list_files(data) if os.path.isdir(data) else []:
        user_lines.update(line.strip() for line in read_text(os.path.join(data, rel)).split("\n"))
    grader = os.path.join(rd, "inputs", "benchmark_grader.py")
    grader_lines = []
    for line in read_text(grader).split("\n") if os.path.isfile(grader) else []:
        line = line.strip()
        if len(line) >= 40 and line not in user_lines and line not in grader_lines:
            grader_lines.append(line)
    held_leaks, grader_leaks = [], []
    for rel in files:
        name = "reference/" + rel
        text = read_text(os.path.join(ref, rel))
        for label, forms in needles:
            if any(form in name or form in text for form in forms):
                held_leaks.append("%s: %s" % (name, label))
        if os.path.basename(rel) == "benchmark_grader.py":
            grader_leaks.append("%s: ไฟล์ของตัวตรวจ" % name)
        hits = [line for line in grader_lines if line in text]
        if hits:
            grader_leaks.append("%s: บรรทัดของตัวตรวจ %d บรรทัด เช่น `%s`" % (name, len(hits), hits[0][:80]))
    answers = sum(1 for rel in files if "answers" in rel.split("/")[:-1])
    return {"files": files, "answers": answers, "held": held_leaks, "grader": grader_leaks,
            "leaks": held_leaks + grader_leaks}


def audit_markdown(result):
    lines = ["| รายการ | ผล |", "|---|---|",
             "| ไฟล์ใน reference/ | %d ไฟล์ |" % len(result["files"]),
             "| มีเฉลยอ้างอิงของชุด Training | %s |" % ("ใช่ %d ไฟล์" % result["answers"] if result["answers"] else "ไม่มี"),
             "| ของชุด Validation หรือ Test | %s |" % ("พบ %d รายการ" % len(result["held"]) if result["held"] else "ไม่พบ"),
             "| โค้ดของตัวตรวจ | %s |" % ("พบ %d รายการ" % len(result["grader"]) if result["grader"] else "ไม่พบ"),
             "", "ไฟล์ทั้งหมด:"]
    lines += ["- reference/%s" % rel for rel in result["files"]]
    if result["leaks"]:
        lines += ["", "สิ่งที่รั่ว:"] + ["- %s" % leak for leak in result["leaks"]]
    return "\n".join(lines) + "\n"


def cmd_adapt(args):
    work = work_dir(args.work)
    rd = run_dir(args)
    st = load_state(rd)
    require_step(st, "adapt")
    cfg = st["cfg"]
    data = data_root(st, work)
    inputs = os.path.join(rd, "inputs")
    run_json = read_json(os.path.join(rd, "RUN.json"), {})
    for key, name in (("instruction", "instruction.md"), ("split", "split.json"), ("grader", "benchmark_grader.py")):
        path = os.path.join(inputs, name)
        if not os.path.isfile(path) or sha256(path) != (run_json.get(key) or {}).get("sha256"):
            die("inputs/%s ไม่ตรงกับ hash ใน RUN.json · สำเนาของสิ่งที่ผู้ใช้ส่งถูกแก้หลัง init" % name)
    user_split = read_json(os.path.join(inputs, "split.json"))

    # 1 เตรียมโต๊ะทำงานของ Benchmark Adaptor
    adapt = os.path.join(rd, "adapt")
    remove_tree(adapt)
    for sub in ("setup", "reference", "work", "data"):
        os.makedirs(os.path.join(adapt, sub))
    for name in ("plugin_api.py", "plugin_skeleton.py"):
        shutil.copyfile(os.path.join(SCRIPTS, name), os.path.join(adapt, "setup", name))
    shutil.copyfile(os.path.join(inputs, "benchmark_grader.py"), os.path.join(adapt, "setup", "benchmark_grader.py"))
    copy_tree(data, os.path.join(adapt, "data", os.path.basename(data)), ("__pycache__",))
    shutil.copyfile(os.path.join(inputs, "split.json"), os.path.join(adapt, "data", "split.json"))

    # 2 เรียก Benchmark Adaptor 1 เซสชัน
    tdir = os.path.join(rd, "turns", "adaptor")
    remove_tree(tdir)
    os.makedirs(tdir)
    system_append = load_prompt("adaptor.md").replace("{setup_dir}", "/ba/setup").replace(
        "{reference_dir}", "/ba/reference")
    write_text(os.path.join(tdir, "system_append.md"), system_append)
    message = os.path.join(tdir, "message.md")
    shutil.copyfile(os.path.join(inputs, "instruction.md"), message)
    transcript = os.path.join(tdir, "transcript.jsonl")
    say("adapt: เรียก Benchmark Adaptor (%s/high · บัญชี %s · ไม่เกิน %d วินาที)" % (
        cfg["adaptor_model"], cfg["accounts"][0], ADAPTOR_TIMEOUT))
    timed_out, wall, code = call_agent(
        st, work, system_append, message, transcript, cfg["adaptor_model"], "high", None, ADAPTOR_TIMEOUT,
        cwd_real=os.path.join(adapt, "work"), cwd_seen="/ba/work",
        binds=[(adapt, "/ba", "rw"), (os.path.join(adapt, "data"), "/data", "ro")],
        env_dirs={"EVOSKILL_BA_DIR": adapt, "EVOSKILL_DATA_DIR": os.path.join(adapt, "data")})
    stats = agent_stats(transcript)
    stats["wall_s"] = wall
    write_actions(transcript, os.path.join(tdir, "actions.md"), "Benchmark Adaptor")
    write_json(os.path.join(tdir, "stats.json"), stats)

    # 3 เซสชันต้องจบปกติ และต้องมี plug-in
    if timed_out or not stats["ok"]:
        die("Benchmark Adaptor จบไม่ปกติ (%s) · phase ยังเป็น init · รัน adapt ซ้ำได้\n%s" % (
            "หมดเวลา %d วินาที" % ADAPTOR_TIMEOUT if timed_out else "exit %s · ไม่มีบรรทัด result หรือเป็น error" % code,
            stderr_tail(transcript)))
    plugin = os.path.join(adapt, "setup", "benchmark_plugin.py")
    if not os.path.isfile(plugin):
        die("Benchmark Adaptor ไม่ได้เขียน /ba/setup/benchmark_plugin.py · phase ยังเป็น init · รัน adapt ซ้ำได้")

    # 4 ล็อก: plug-in จาก Adaptor · plugin_api.py และตัวตรวจจากต้นฉบับ (ไม่ใช่สำเนาที่ Adaptor แตะได้)
    setup = os.path.join(rd, "setup")
    remove_tree(setup)
    os.makedirs(setup)
    shutil.copyfile(plugin, os.path.join(setup, "benchmark_plugin.py"))
    shutil.copyfile(os.path.join(SCRIPTS, "plugin_api.py"), os.path.join(setup, "plugin_api.py"))
    shutil.copyfile(os.path.join(inputs, "benchmark_grader.py"), os.path.join(setup, "benchmark_grader.py"))
    check_plugin_imports(os.path.join(setup, "benchmark_plugin.py"))

    # 5 รายการโจทย์ และการแบ่งชุดต้องตรงกับของผู้ใช้
    tasks = freeze_tasks(rd, data, user_split)

    # 6 reference/ และ freeze.json
    copy_tree(os.path.join(adapt, "reference"), os.path.join(rd, "reference"), ("__pycache__",))
    touched = os.path.join(adapt, "setup", "benchmark_grader.py")
    freeze = {
        "frozen_at": utc_now().strftime("%Y-%m-%d %H:%M UTC"),
        "sha256": {name: sha256(os.path.join(setup, name)) for name in FROZEN},
        "grader_unchanged_by_adaptor": os.path.isfile(touched) and sha256(touched) == sha256(
            os.path.join(inputs, "benchmark_grader.py")),
        "tasks": {split: [t["id"] for t in tasks if t["split"] == split] for split in SPLITS},
    }
    write_json(os.path.join(setup, "freeze.json"), freeze)

    # 7 ตรวจการรั่ว
    result = audit(rd, data)
    report = audit_markdown(result)
    write_text(os.path.join(setup, "audit.md"), report)
    stats["tasks"] = {split: len(freeze["tasks"][split]) for split in SPLITS}
    stats["reference"] = {"files": len(result["files"]), "answers": result["answers"], "leaks": result["leaks"]}
    stats["audit_ok"] = not result["leaks"]
    st["adapt"] = stats
    if result["leaks"]:
        save_state(rd, st)                                       # บันทึกผล แต่ phase ยังเป็น init
        sys.stdout.write(report)
        die("พบการรั่วใน reference/ %d รายการ (ดู setup/audit.md) · phase ยังเป็น init · แก้คำสั่งของผู้ใช้แล้วรัน adapt ซ้ำ"
            % len(result["leaks"]))
    st["phase"] = "adapt"
    save_state(rd, st)
    say("adapt เสร็จ: โจทย์ train %d · validation %d · test %d · reference/ %d ไฟล์ (เฉลยของ Training %d ไฟล์) · "
        "ตรวจการรั่ว: สะอาด · %.1f วินาที · $%.2f%s" % (
            stats["tasks"]["train"], stats["tasks"]["validation"], stats["tasks"]["test"], len(result["files"]),
            result["answers"], wall, num(stats["cost_usd"]),
            "" if freeze["grader_unchanged_by_adaptor"] else " · ⚠ Adaptor แก้สำเนาของตัวตรวจ (ไม่ถูกใช้)"))
    return 0


def cmd_audit(args):
    work = work_dir(args.work)
    rd = run_dir(args)
    st = load_state(rd)
    verify_freeze(rd)
    result = audit(rd, data_root(st, work))
    sys.stdout.write(audit_markdown(result))
    sys.stdout.flush()
    return 1 if result["leaks"] else 0


# ───────────────────────── rollout ของ Solver (ผ่าน skillopt.py run) ─────────────────────────

def summarize_leg(label, split, skills, model, tasks, tdir, n):
    by_task, scores, missing, abnormal = {}, [], [], []
    cost, ctx, tools, skill_read, grader_failed = 0.0, [], [], 0, 0
    for task in tasks:
        row = []
        for rep in range(1, n + 1):
            name = "%s-r%d" % (task["id"], rep)
            grade = read_json(os.path.join(tdir, name, "grade.json"))
            metrics = read_json(os.path.join(tdir, name, "metrics.json"))
            score = grade.get("score") if isinstance(grade, dict) else None
            if isinstance(score, bool) or not isinstance(score, (int, float)) or not isinstance(metrics, dict):
                missing.append(name)
                continue
            row.append(score)
            cost += num(metrics.get("cost_usd"))
            ctx.append(sum(num(metrics.get(key)) for key in ("input_tokens", "cache_read", "cache_write")))
            tools.append(num(metrics.get("tool_calls")))
            skill_read += 1 if metrics.get("skill_read") else 0
            checks = grade.get("checks")
            if isinstance(checks, list) and checks and isinstance(checks[0], dict) and checks[0].get("id") == "grader":
                grader_failed += 1
            if metrics.get("timed_out") or metrics.get("ok") is False:
                abnormal.append(name)
        by_task[task["id"]] = row
        scores += row
    if missing or not scores:
        return None, missing, abnormal
    passed = {tid: [s >= PASS for s in row] for tid, row in by_task.items()}
    leg = {
        "n": len(scores), "tasks": len(tasks), "score": sum(scores) / len(scores),
        "passes": sum(1 for s in scores if s >= PASS),
        "pass3": sum(1 for p in passed.values() if any(p)),
        "all3": sum(1 for p in passed.values() if all(p)),
        "none3": sum(1 for p in passed.values() if not any(p)),
        "mixed": sum(1 for p in passed.values() if any(p) and not all(p)),
        "by_task": by_task,
        "cost_usd": round(cost, 4),
        "context_tokens": int(round(sum(ctx) / len(ctx))),
        "tool_calls": round(sum(tools) / len(tools), 2),
        "skill_read": skill_read, "grader_failed": grader_failed,
        "label": label, "split": split, "skills": skills, "model": model,
    }
    return leg, missing, abnormal


def idle_rollouts(tasks, tdir, n):
    """rollout ที่ Solver ไม่ได้ทำงาน = จบไม่ปกติ (ok เป็น false หรือหมดเวลา) และไม่มีคำสั่งเลย (tool_calls = 0)
    เช่น บัญชีติดลิมิตการใช้งาน · คืน [(ชื่อ rollout, บัญชี, ข้อความ result)]"""
    idle = []
    for task in tasks:
        for rep in range(1, n + 1):
            name = "%s-r%d" % (task["id"], rep)
            metrics = read_json(os.path.join(tdir, name, "metrics.json"))
            if not isinstance(metrics, dict):
                continue
            abnormal = metrics.get("ok") is False or bool(metrics.get("timed_out"))
            if abnormal and not num(metrics.get("tool_calls")):
                result = metrics.get("result")
                if not isinstance(result, str) or not result.strip():
                    result = "(หมดเวลา ไม่มีบรรทัด result)" if metrics.get("timed_out") else "(ไม่มีบรรทัด result)"
                idle.append((name, str(metrics.get("account") or "?"), " ".join(result.split())[:300]))
    return idle


def run_leg(st, rd, label, split, skills_dir, model=None):
    """Solver ทำโจทย์ 1 ชุดด้วยชุดสกิล 1 ชุด · split = train | val | test | all · คืนสรุปของ leg"""
    cfg = st["cfg"]
    legs = os.path.join(rd, "legs")
    summary_path = os.path.join(legs, "%s.json" % label)
    done = read_json(summary_path)
    if isinstance(done, dict) and "score" in done:               # leg ที่เสร็จแล้วไม่รันซ้ำ
        st["legs"][label] = done
        save_state(rd, st)
        say("leg %s เสร็จแล้ว (%.1f%% · ผ่าน %d/%d) · ไม่รันซ้ำ" % (
            label, done["score"] * 100, done.get("passes", 0), done.get("n", 0)))
        return done
    verify_freeze(rd)                                            # 1
    tasks = load_tasks(rd)
    wanted = [t for t in tasks if split == "all" or SHORT[t["split"]] == split]
    if not wanted:
        die("leg %s: ไม่มีโจทย์ในชุด %s" % (label, split))
    model = model or cfg["solver_model"]
    suite_dir = os.path.join(legs, "suite")                      # 2
    os.makedirs(suite_dir, exist_ok=True)
    write_json(os.path.join(suite_dir, "suite.json"), {
        "name": "evoskill-%s" % cfg["name"], "skill_name": "-", "timeout": SOLVER_TIMEOUT,
        "grader": "benchmark_grader.py", "prompt": cfg["solver_prompt"],
        "tasks": [{"id": t["id"], "split": SHORT[t["split"]], "brief": t["instruction"], "grading": t["grading"]}
                  for t in tasks],
    })
    shutil.copyfile(os.path.join(rd, "setup", "benchmark_grader.py"), os.path.join(suite_dir, "benchmark_grader.py"))
    leg_dir = os.path.join(legs, "runs", label)                  # 3
    remove_tree(leg_dir)
    os.makedirs(leg_dir)
    names = skill_names(skills_dir)
    if names:
        copy_tree(skills_dir, os.path.join(leg_dir, "skills"), ("__pycache__",))
    skillopt = cfg["skillopt"]                                   # 4
    if not os.path.isfile(skillopt):
        die("ไม่พบ skillopt.py ที่ %s (cfg.skillopt ใน state.json)" % skillopt)
    cmd = [sys.executable, skillopt, "run", legs, "--label", label, "--split", split, "--reps", str(st["n"]),
           "--accounts", ",".join(cfg["accounts"]), "--par", str(cfg["par"]), "--model", model,
           "--effort", cfg["solver_effort"]]
    say("leg %s: Solver ทำโจทย์ชุด %s %d ข้อ x %d ครั้ง · สกิล %s" % (
        label, split, len(wanted), st["n"], ", ".join(names) if names else "(ไม่มี)"))
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        code = subprocess.call(cmd, env=env, stdin=subprocess.DEVNULL)
    except OSError as e:
        die("leg %s: เรียก skillopt.py ไม่ได้: %s" % (label, e))
    if code != 0:
        die("leg %s: `skillopt.py run` ล้ม (exit %s) · leg นี้ยังไม่เสร็จ รันคำสั่งเดิมซ้ำเพื่อทำใหม่ทั้ง leg" % (label, code))
    idle = idle_rollouts(wanted, os.path.join(leg_dir, "trials"), st["n"])                              # 5
    if idle:                                                     # คะแนน 0 จากบัญชีที่ใช้ไม่ได้ ต้องไม่ถูกนับเป็นผลของสกิล
        say("leg %s: Solver ไม่ได้ทำงาน %d จาก %d rollout (จบไม่ปกติและไม่มีคำสั่งเลย)" % (
            label, len(idle), len(wanted) * st["n"]))
        for name, account, result in idle:
            say("  ✗ %s · บัญชี %s · result: %s" % (name, account, result))
        st["legs"].pop(label, None)
        die("leg %s ไม่ถือว่าเสร็จ: ไม่เขียน legs/%s.json และไม่บันทึกลง state.json · บัญชีที่มีปัญหา: %s · "
            "แก้บัญชี (หรือรอให้พ้นลิมิต) แล้วสั่งคำสั่งเดิมซ้ำเพื่อรัน leg นี้ใหม่ทั้ง leg" % (
                label, label, ", ".join(sorted(set(a for _n, a, _r in idle)))))
    leg, missing, abnormal = summarize_leg(label, LONG[split], names, model, wanted,
                                           os.path.join(leg_dir, "trials"), st["n"])
    if leg is None:
        die("leg %s: ผลไม่ครบ ขาด %d จาก %d rollout (%s) · รันคำสั่งเดิมซ้ำเพื่อทำใหม่ทั้ง leg" % (
            label, len(missing), len(wanted) * st["n"], " ".join(missing[:8])))
    if abnormal:
        say("⚠ leg %s: rollout จบไม่ปกติ %d ครั้ง (%s) · คะแนนส่วนนี้อาจไม่ได้สะท้อนสกิล" % (
            label, len(abnormal), " ".join(abnormal[:8])))
    if leg["grader_failed"]:
        say("⚠ leg %s: ตัวตรวจล้ม %d rollout" % (label, leg["grader_failed"]))
    st["legs"][label] = leg
    save_state(rd, st)
    write_json(summary_path, leg)                                # เขียนเป็นอย่างสุดท้าย = เครื่องหมายว่า leg เสร็จ
    say("leg %s เสร็จ: คะแนน %.1f%% · ผ่าน %d/%d · $%.2f" % (
        label, leg["score"] * 100, leg["passes"], leg["n"], leg["cost_usd"]))
    return leg


def cmd_base(args):
    rd = run_dir(args)
    st = load_state(rd)
    require_step(st, "base")
    for split in ("train", "val", "test"):
        run_leg(st, rd, "base_%s" % split, split, None)
    st["phase"], st["k"] = "base", 0
    save_state(rd, st)
    say("base เสร็จ · ขั้นถัดไป: turn (epoch 1)")
    return 0


def cmd_rollout(args):
    rd = run_dir(args)
    st = load_state(rd)
    require_step(st, "rollout")
    k = st["k"]
    skills = os.path.join(rd, "skills_v%d" % k)
    if not os.path.isdir(skills):
        die("ไม่พบ %s · ตาที่ %d ของ Evolver ยังไม่เสร็จ" % (skills, k))
    run_leg(st, rd, "v%d_val" % k, "val", skills)                # Validation ก่อน Training
    if k < st["epochs"]:
        run_leg(st, rd, "v%d_train" % k, "train", skills)        # epoch สุดท้ายไม่มี Training
    st["phase"] = "rollout"
    save_state(rd, st)
    nxt = next_step(st)
    say("rollout ของ epoch %d เสร็จ · ขั้นถัดไป: %s (epoch %d)" % (k, nxt, step_epoch(st, nxt)))
    return 0


def cmd_test(args):
    rd = run_dir(args)
    st = load_state(rd)
    require_step(st, "test")
    epochs = st["epochs"]
    skills = os.path.join(rd, "skills_v%d" % epochs)
    if not os.path.isdir(skills):
        die("ไม่พบ %s" % skills)
    run_leg(st, rd, "v%d_test" % epochs, "test", skills)         # ชุดของ epoch สุดท้าย วัด 1 ครั้ง
    st["phase"] = "test"
    save_state(rd, st)
    say("test เสร็จ · การรันจบแล้ว")
    return 0


def cmd_eval(args):
    rd = run_dir(args)
    st = load_state(rd)
    if st.get("phase") == "init":
        die("ทำ `eval` ไม่ได้: ยังไม่ได้ทำขั้น adapt (ยังไม่มีรายการโจทย์ที่ล็อกแล้ว)")
    label = args.label
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", label) or RESERVED_LEG.match(label) or label == "suite":
        die("--label %r ใช้ไม่ได้: ใช้ตัวอักษรอังกฤษ ตัวเลข . _ - และห้ามซ้ำกับชื่อ leg ของวงรอบ (base_* vK_*)" % label)
    spec = args.skills
    if spec == "none":
        skills = None
    elif re.match(r"^v\d+$", spec):
        skills = os.path.join(rd, "skills_%s" % spec)
        if not os.path.isdir(skills):
            die("ไม่พบชุดสกิล %s ของการรันนี้ (%s)" % (spec, skills))
    else:
        skills = os.path.abspath(spec)
        if not os.path.isdir(skills):
            die("--skills ต้องเป็น v1 v2 … none หรือโฟลเดอร์ skills ที่มีอยู่ (ไม่พบ %s)" % skills)
    run_leg(st, rd, label, args.split, skills, model=args.model)
    return 0


# ───────────────────────── ตาของ Evolver ─────────────────────────

def sync_evo(st, rd, epoch):
    """ส่งผลของชุด Training ของ epoch ก่อนหน้าเข้า evo/ · ของ Validation และ Test ไม่ถูกส่งเลย"""
    evo = os.path.join(rd, "evo")
    for key in EVO_KEYS:
        os.makedirs(os.path.join(evo, key), exist_ok=True)
    ref = os.path.join(evo, "reference")
    if not os.listdir(ref) and os.path.isdir(os.path.join(rd, "reference")):   # คัดลอกครั้งแรกครั้งเดียว
        copy_tree(os.path.join(rd, "reference"), ref)
    label = "base_train" if epoch == 0 else "v%d_train" % epoch
    if label not in st["legs"]:
        die("ยังไม่มีผลของ leg %s ที่ต้องส่งให้ Evolver" % label)
    trials = os.path.join(rd, "legs", "runs", label, "trials")
    traces = os.path.join(evo, "traces", "epoch_%d" % epoch)
    spaces = os.path.join(evo, "solver_workspaces", "epoch_%d" % epoch)
    for path in (traces, spaces):
        remove_tree(path)
        os.makedirs(path)
    scores, given = {}, 0
    for task in load_tasks(rd):
        if task["split"] != "train":                             # เฉพาะชุด Training
            continue
        for rep in range(1, st["n"] + 1):
            src = os.path.join(trials, "%s-r%d" % (task["id"], rep))
            name = "%s_s%d" % (task["id"], rep)
            grade = read_json(os.path.join(src, "grade.json"))
            if not isinstance(grade, dict) or not os.path.isdir(src):
                die("ไม่พบผลของ rollout %s/%s-r%d · ลบ legs/%s.json แล้วรัน leg นี้ใหม่" % (label, task["id"], rep, label))
            checks = grade.get("checks")
            failed = isinstance(checks, list) and checks and isinstance(checks[0], dict) \
                and checks[0].get("id") == "grader"
            scores[name] = "grader_failed" if failed else grade.get("score")    # คะแนนอย่างเดียว ไม่มีผลรายข้อ
            transcript = os.path.join(src, "transcript.jsonl")
            if os.path.isfile(transcript):
                shutil.copyfile(transcript, os.path.join(traces, name + ".jsonl"))
            sandbox = os.path.join(src, "sandbox")
            if os.path.isdir(sandbox):
                copy_tree(sandbox, os.path.join(spaces, name), ("skills", "__pycache__"))
            else:
                os.makedirs(os.path.join(spaces, name))
            given += 1
    write_json(os.path.join(evo, "scores", "epoch_%d.json" % epoch), scores)
    used = os.path.join(evo, "skills", "epoch_%d" % epoch)       # ชุดสกิลที่ Solver ของ epoch นั้นใช้
    remove_tree(used)
    source = os.path.join(rd, "skills_v%d" % epoch)
    if epoch > 0 and os.path.isdir(source):
        copy_tree(source, used)
    else:
        os.makedirs(used)
    return given


def cmd_turn(args):
    work = work_dir(args.work)
    rd = run_dir(args)
    st = load_state(rd)
    require_step(st, "turn")
    verify_freeze(rd)
    cfg = st["cfg"]
    k = st["k"] + 1
    evo = os.path.join(rd, "evo")
    given = sync_evo(st, rd, k - 1)                              # 1
    staging = os.path.join(evo, "staging")
    workspace = os.path.join(evo, "evolver_workspace")
    before = hash_tree(staging)
    old_scripts = [rel for rel in list_files(workspace) if rel.endswith((".py", ".sh"))]

    tdir = os.path.join(rd, "turns", "turn_%d" % k)              # 2
    remove_tree(tdir)
    os.makedirs(tdir)
    now = utc_now()
    deadline = now + datetime.timedelta(minutes=cfg["turn_minutes"])
    message = load_prompt("evolver_message.md").replace("{now}", now.strftime("%Y-%m-%d %H:%M")).replace(
        "{deadline}", deadline.strftime("%Y-%m-%d %H:%M")).replace("{k}", str(k))
    write_text(os.path.join(tdir, "message.md"), message)
    system_append = load_prompt("evolver_system.md").replace("{n}", str(st["n"]))
    write_text(os.path.join(rd, "turns", "evolver_system_append.md"), system_append)

    fresh = k == 1 or bool(cfg.get("fresh_session")) or not st.get("session_id")       # 3
    session_id = str(uuid.uuid4()) if fresh else st["session_id"]
    transcript = os.path.join(tdir, "transcript.jsonl")
    timeout = int(cfg["turn_minutes"] * 60 + 60)
    say("turn %d: เรียก Evolver (%s/%s · %s · rollout ที่ส่งให้ %d ครั้ง · ไม่เกิน %d วินาที)" % (
        k, cfg["evolver_model"], cfg["evolver_effort"], "เซสชันใหม่" if fresh else "เซสชันเดิม", given, timeout))
    timed_out, wall, code = call_agent(
        st, work, system_append, os.path.join(tdir, "message.md"), transcript, cfg["evolver_model"],
        cfg["evolver_effort"], ("new" if fresh else "resume", session_id), timeout,
        cwd_real=evo, cwd_seen="/evo",
        binds=[(evo, "/evo", "rw")] + [(os.path.join(evo, key), "/evo/%s" % key, "ro") for key in EVO_READONLY],
        env_dirs={"EVOSKILL_EVO_DIR": evo})
    stats = agent_stats(transcript, evo_real=evo, old_scripts=old_scripts)
    write_actions(transcript, os.path.join(tdir, "actions.md"), "ตาที่ %d ของ Evolver" % k, message)

    if not stats["ok"] and not timed_out:                        # 4
        write_json(os.path.join(tdir, "stats.json"), dict(stats, k=k, wall_s=wall, timed_out=False))
        die("ตาที่ %d ของ Evolver จบไม่ปกติ (exit %s · ไม่มีบรรทัด result หรือเป็น error) · phase ไม่เปลี่ยน · "
            "รัน turn ซ้ำเพื่อทำตานี้ใหม่\n%s" % (k, code, stderr_tail(transcript)))
    if timed_out:
        stats["ok"] = False
        say("⚠ ตาที่ %d หมดเวลา (%d วินาที) · ใช้ staging/ ตามสภาพที่เป็นอยู่" % (k, timeout))

    skills = os.path.join(rd, "skills_v%d" % k)                  # 5 รับเสมอ ไม่มีประตูรับ
    copy_tree(staging, skills, ("__pycache__",))

    total = stats["cost_usd"]                                    # 6
    previous = 0.0 if fresh else num(st.get("session_cost"))
    if total is None:
        turn_cost, session_cost = None, previous
    elif fresh or total + TINY < previous:                       # ยอดที่รายงานไม่ใช่ยอดสะสม = ค่าของตานี้เอง
        turn_cost, session_cost = total, round(previous + total, 4)
    else:                                                        # --resume: ยอดสะสมของเซสชัน
        turn_cost, session_cost = round(total - previous, 4), total
    after = hash_tree(staging)
    stats["cost_usd"] = turn_cost
    stats.update({
        "session_cost_usd": session_cost, "k": k, "wall_s": wall, "timed_out": timed_out, "fresh_session": fresh,
        "session_id": session_id, "rollouts_given": given, "old_scripts": len(old_scripts),
    })
    stats.update(skill_info(skills))
    stats.update({
        "files_added": sorted(f for f in after if f not in before),
        "files_removed": sorted(f for f in before if f not in after),
        "files_changed": sorted(f for f in after if f in before and after[f] != before[f]),
        "workspace_files": list_files(workspace),
    })
    write_json(os.path.join(tdir, "stats.json"), stats)
    st["turns"] = [t for t in st["turns"] if t.get("k") != k] + [stats]
    st["session_id"], st["session_cost"] = session_id, session_cost
    st["k"], st["phase"] = k, "turn"
    save_state(rd, st)
    say("turn %d เสร็จ: skills_v%d = %s · SKILL.md %.1f KB · ไฟล์อื่น %d · เพิ่ม %d แก้ %d ลบ %d · เครื่องมือ %d ครั้ง · "
        "%.1f นาที · $%.2f" % (
            k, k, ", ".join(stats["skills"]) or "(ว่าง)", stats["skill_md_bytes"] / 1024.0,
            len(stats["skill_other_files"]), len(stats["files_added"]), len(stats["files_changed"]),
            len(stats["files_removed"]), stats["tool_calls"], wall / 60.0, num(turn_cost)))
    if stats["skill_problems"]:
        say("⚠ สกิลที่ไม่มี description ใน frontmatter: %s" % ", ".join(stats["skill_problems"]))
    return 0


# ───────────────────────── run ─────────────────────────

def cmd_run(args):
    rd = run_dir(args)
    funcs = {"adapt": cmd_adapt, "base": cmd_base, "turn": cmd_turn, "rollout": cmd_rollout, "test": cmd_test}
    while True:
        st = load_state(rd)
        step = next_step(st)
        if step is None:
            break
        say("── %s (epoch %d) ──" % (step, step_epoch(st, step)))
        funcs[step](args)
        if args.stop_after == step:
            say("หยุดหลังขั้น %s ตาม --stop-after" % step)
            break
    return cmd_status(args)


# ───────────────────────── status ─────────────────────────

def pct(x):
    return "%.1f%%" % (x * 100)


def leg_cell(leg):
    if not leg:
        return "-"
    return "%s (%d/%d)" % (pct(leg["score"]), leg["passes"], leg["n"])


def points(x):
    return round(x * 100, 6) + 0.0                               # กัน -0.0


def per_point(cost, gain):
    return "$%.3f" % (cost / gain) if gain > TINY else "ไม่เพิ่ม"


def status_text(st):
    cfg, legs, epochs = st["cfg"], st.get("legs") or {}, st["epochs"]
    turns = sorted(st.get("turns") or [], key=lambda t: t.get("k") or 0)
    adapt = st.get("adapt") if isinstance(st.get("adapt"), dict) else None
    adapt_cost = num(adapt.get("cost_usd")) if adapt else 0
    evolver_cost = sum(num(t.get("cost_usd")) for t in turns)
    out = ["", "การรัน %s · %d epochs · %d samples per task · Solver %s/%s · Evolver %s/%s · %s" % (
        cfg["name"], epochs, st["n"], cfg["solver_model"], cfg["solver_effort"], cfg["evolver_model"],
        cfg["evolver_effort"], "เซสชันใหม่ทุก epoch" if cfg.get("fresh_session") else "เซสชันเดียวตลอดการรัน")]
    if adapt and isinstance(adapt.get("tasks"), dict):
        ref = adapt.get("reference") or {}
        out.append("Benchmark Adaptor: โจทย์ train %d · validation %d · test %d · reference/ %d ไฟล์ "
                   "(เฉลยของ Training %d ไฟล์) · ตรวจการรั่ว: %s · $%.2f" % (
                       adapt["tasks"].get("train", 0), adapt["tasks"].get("validation", 0),
                       adapt["tasks"].get("test", 0), ref.get("files", 0), ref.get("answers", 0),
                       "สะอาด" if adapt.get("audit_ok") else "พบการรั่ว", adapt_cost))
    out += ["",
            "| epoch | ชุดสกิลที่ Solver ใช้ | SKILL.md | ไฟล์อื่น | Training คะแนน (ผ่าน) | Validation คะแนน (ผ่าน) "
            "| ตาของ Evolver (นาที) | เครื่องมือ | Bash | รันสคริปต์เดิมซ้ำ | ย่อบริบท | ค่าใช้จ่าย |",
            "|" + "---|" * 12,
            "| 0 | (ไม่มีสกิล) | - | - | %s | %s | - | - | - | - | - | - |" % (
                leg_cell(legs.get("base_train")), leg_cell(legs.get("base_val")))]
    for t in turns:
        k = t.get("k") or 0
        out.append("| %d | %s | %.1f KB | %d | %s | %s | %.1f | %d | %d | %d | %d | $%.2f |" % (
            k, ", ".join(t.get("skills") or []) or "(ว่าง)", num(t.get("skill_md_bytes")) / 1024.0,
            len(t.get("skill_other_files") or []), leg_cell(legs.get("v%d_train" % k)),
            leg_cell(legs.get("v%d_val" % k)), num(t.get("wall_s")) / 60.0, num(t.get("tool_calls")),
            num(t.get("bash")), num(t.get("rerun_old_scripts")), num(t.get("compactions")), num(t.get("cost_usd"))))
    out.append("")
    base, last = legs.get("base_test"), legs.get("v%d_test" % epochs)
    if base:
        out += ["| Test Set (held-out) | คะแนน | pass@1 (rollout ที่ผ่าน) | pass@3 (ผ่านอย่างน้อย 1 ครั้ง) "
                "| all@3 (ผ่านทุกครั้ง) |", "|" + "---|" * 5]
        rows = [("ไม่มีสกิล", base)] + ([("skills_v%d (epoch สุดท้าย)" % epochs, last)] if last else [])
        for name, leg in rows:
            out.append("| %s | %s | %d/%d | %d/%d | %d/%d |" % (
                name, pct(leg["score"]), leg["passes"], leg["n"], leg["pass3"], leg["tasks"],
                leg["all3"], leg["tasks"]))
        out.append("")
    out.append("รวม: rollout ของ Solver %d ครั้ง ($%.2f) · Evolver %d ตา ($%.2f) · Benchmark Adaptor $%.2f" % (
        sum(num(leg.get("n")) for leg in legs.values()), sum(num(leg.get("cost_usd")) for leg in legs.values()),
        len(turns), evolver_cost, adapt_cost))
    if base and last:
        gain = points(last["score"] - base["score"])
        rate = points(float(last["passes"]) / last["n"] - float(base["passes"]) / base["n"])
        out.append("Test Set: คะแนนเพิ่ม %+.1f จุด · pass rate เพิ่ม %+.1f จุด · ต้นทุนของ Evolver ต่อ 1 จุดที่เพิ่ม: "
                   "คะแนน %s · pass rate %s" % (gain, rate, per_point(evolver_cost, gain), per_point(evolver_cost, rate)))
    nxt = next_step(st)
    if nxt is None:
        out.append("สถานะ: จบแล้ว (วัด Test Set แล้ว)")
    else:
        out.append("สถานะ: ยังไม่จบ · ขั้นถัดไป: %s (epoch %d)" % (nxt, step_epoch(st, nxt)))
    return "\n".join(out) + "\n"


def cmd_status(args):
    sys.stdout.write(status_text(load_state(run_dir(args))))
    sys.stdout.flush()
    return 0


# ───────────────────────── noise ─────────────────────────

def leg_order(legs):
    def key(name):
        m = re.match(r"^(base|v(\d+))_(train|val|test)$", name)
        if not m:
            return (1, 0, 0, name)
        return (0, int(m.group(2)) if m.group(2) else 0, ("train", "val", "test").index(m.group(3)), name)
    return sorted(legs, key=key)


def sample_means(leg):
    """คะแนนของครั้งที่ i = ค่าเฉลี่ยของทุกโจทย์ในครั้งนั้น"""
    rows = [row for row in leg.get("by_task", {}).values() if row]
    reps = min(len(row) for row in rows) if rows else 0
    return [sum(row[i] for row in rows) / len(rows) for i in range(reps)]


def noise_text(st):
    legs, n = st.get("legs") or {}, st["n"]
    out = ["", "1) โจทย์แยกตามจำนวนครั้งที่ผ่านจาก %d ครั้ง (ผ่าน = คะแนน 0.999 ขึ้นไป)" % n, "",
           "| leg | ชุดสกิล | โจทย์ | ผ่าน %d/%d | ผ่าน 0/%d | ผ่านบางครั้ง | คะแนนต่างกันระหว่างครั้ง |" % (n, n, n),
           "|" + "---|" * 7]
    for name in leg_order(legs):
        leg = legs[name]
        varying = sum(1 for row in leg.get("by_task", {}).values() if row and max(row) - min(row) > TINY)
        out.append("| %s | %s | %d | %d | %d | %d | %d โจทย์ |" % (
            name, ", ".join(leg.get("skills") or []) or "(ไม่มี)", leg["tasks"], leg["all3"], leg["none3"],
            leg["mixed"], varying))
    pairs = n * n
    out += ["", "2) ถ้าใช้ประตูรับแบบ \"วัดโจทย์ละ 1 ครั้ง แล้วรับเมื่อคะแนนสูงกว่าเดิม\" จะตัดสินอย่างไร",
            "   (จับคู่ครั้งที่ i ของชุดเดิม กับครั้งที่ j ของชุดใหม่ ทุกแบบ = %d คู่ต่อ 1 การตัดสิน)" % pairs, "",
            "| ชุด | เทียบ | ค่าเฉลี่ย %d ครั้ง (เดิม → ใหม่) | รับ | เสมอ (ไม่รับ) | ไม่รับเพราะต่ำกว่า |" % n,
            "|" + "---|" * 6]
    versions = sorted(int(m.group(1)) for m in (re.match(r"^v(\d+)_(?:train|val)$", name) for name in legs) if m)
    for split, title in (("train", "Training"), ("val", "Validation")):
        chain = [("ไม่มีสกิล", "base_%s" % split)] + [("v%d" % v, "v%d_%s" % (v, split)) for v in sorted(set(versions))]
        chain = [(label, legs[name]) for label, name in chain if name in legs]
        for (old_label, old), (new_label, new) in zip(chain, chain[1:]):
            a, b = sample_means(old), sample_means(new)
            total = len(a) * len(b)
            up = sum(1 for x in a for y in b if y - x > TINY)
            tie = sum(1 for x in a for y in b if abs(y - x) <= TINY)
            out.append("| %s | %s → %s | %s → %s | %d/%d | %d/%d | %d/%d |" % (
                title, old_label, new_label, pct(old["score"]), pct(new["score"]), up, total, tie, total,
                total - up - tie, total))
    out += ["", "แถวที่ \"รับ\" ไม่ใช่ 0/%d หรือ %d/%d ทั้งหมด = การตัดสินขึ้นกับว่าสุ่มได้ rollout ครั้งไหน" % (
        pairs, pairs, pairs)]
    return "\n".join(out) + "\n"


def cmd_noise(args):
    sys.stdout.write(noise_text(load_state(run_dir(args))))
    sys.stdout.flush()
    return 0


# ───────────────────────── export ─────────────────────────

def export_tree(src, dst):
    count = 0
    for root, dirs, names in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(names):
            path = os.path.join(root, name)
            if name.endswith(EXPORT_SKIP_EXT) or os.path.getsize(path) > EXPORT_MAX:
                continue
            target = os.path.join(dst, os.path.relpath(path, src))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(path, target)
            count += 1
    return count


def cmd_export(args):
    rd = run_dir(args)
    st = load_state(rd)
    dst = os.path.join(os.path.abspath(args.to), args.run)
    if is_under(dst, rd) or is_under(rd, dst):
        die("--to ต้องไม่ใช่โฟลเดอร์ของการรันเอง (%s)" % rd)
    remove_tree(dst)
    os.makedirs(dst)
    count = 0
    singles = ["RUN.json", "state.json", "inputs/instruction.md", "setup/benchmark_plugin.py", "setup/tasks.json",
               "setup/freeze.json", "setup/audit.md"]                      # ไม่เก็บตัวตรวจ
    for rel in singles:
        src = os.path.join(rd, rel)
        if os.path.isfile(src):
            target = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(src, target)
            count += 1
    write_text(os.path.join(dst, "status.txt"), status_text(st))
    write_text(os.path.join(dst, "noise.txt"), noise_text(st))
    count += 2
    trees = ["reference", "turns", "evo/evolver_workspace", "evo/scores"]
    trees += sorted(d for d in os.listdir(rd) if re.match(r"^skills_v\d+$", d))
    for rel in trees:
        src = os.path.join(rd, rel)
        if os.path.isdir(src):
            os.makedirs(os.path.join(dst, rel), exist_ok=True)
            count += export_tree(src, os.path.join(dst, rel))
    legs = os.path.join(rd, "legs")
    rollouts = sealed_count = 0
    for name in sorted(os.listdir(legs)) if os.path.isdir(legs) else []:
        if name.endswith(".json") and os.path.isfile(os.path.join(legs, name)):
            os.makedirs(os.path.join(dst, "legs"), exist_ok=True)
            shutil.copyfile(os.path.join(legs, name), os.path.join(dst, "legs", name))
            count += 1
    runs = os.path.join(legs, "runs")
    for label in sorted(os.listdir(runs)) if os.path.isdir(runs) else []:
        trials = os.path.join(runs, label, "trials")
        for trial in sorted(os.listdir(trials)) if os.path.isdir(trials) else []:
            src = os.path.join(trials, trial)
            grade = read_json(os.path.join(src, "grade.json"))
            metrics = read_json(os.path.join(src, "metrics.json"))
            if not isinstance(grade, dict) or not isinstance(metrics, dict):
                continue
            sealed = metrics.get("split") == "val"                          # รายละเอียดของ Validation Set ไม่ถูกเก็บ
            if sealed:
                grade = {"score": grade.get("score"), "checks": "sealed (Validation Set)"}
                metrics = {k: v for k, v in metrics.items() if k not in ("commands", "result")}
                sealed_count += 1
            target = os.path.join(dst, "legs", "runs", label, "trials", trial)
            write_json(os.path.join(target, "grade.json"), grade)
            write_json(os.path.join(target, "metrics.json"), metrics)
            count += 2
            rollouts += 1
            for name in ("solve.py", "test_solve.py"):
                path = os.path.join(src, "sandbox", name)
                if not sealed and os.path.isfile(path) and os.path.getsize(path) <= EXPORT_MAX:
                    os.makedirs(os.path.join(target, "sandbox"), exist_ok=True)
                    shutil.copyfile(path, os.path.join(target, "sandbox", name))
                    count += 1
    say("export %s → %s: %d ไฟล์ · rollout %d ครั้ง (ของ Validation Set ที่ตัดรายละเอียด %d ครั้ง)" % (
        args.run, dst, count, rollouts, sealed_count))
    return 0


# ───────────────────────── main ─────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        prog="evoskill.py",
        description="evoskill: วงรอบ EvoSkill v2 (Benchmark Adaptor → Solver ↔ Evolver → Test) "
                    "· <work> = โฟลเดอร์ที่มี bench/ และ runs/")
    sub = p.add_subparsers(dest="command", metavar="{init,adapt,audit,base,turn,rollout,test,run,status,noise,eval,export}")
    sub.required = True

    def add(name, func, text):
        sp = sub.add_parser(name, help=text, description=text)
        sp.add_argument("work", help="โฟลเดอร์งานที่มี bench/ และ runs/")
        sp.add_argument("--run", required=True, help="ชื่อการรัน (โฟลเดอร์ runs/<ชื่อ>/)")
        sp.set_defaults(func=func)
        return sp

    sp = add("init", cmd_init, "สร้างการรัน: inputs/ RUN.json state.json (ไม่เรียกโมเดล)")
    sp.add_argument("--accounts", required=True, help="คำสั่งของบัญชีที่ใช้ คั่นด้วย , เช่น yolo1,yolo2")
    sp.add_argument("--instruction", default="", help="คำสั่งของผู้ใช้ (ค่าเริ่มต้น <work>/bench/instruction.md)")
    sp.add_argument("--solver-model", dest="solver_model", default="sonnet")
    sp.add_argument("--solver-effort", dest="solver_effort", default="medium")
    sp.add_argument("--evolver-model", dest="evolver_model", default="sonnet")
    sp.add_argument("--evolver-effort", dest="evolver_effort", default="high")
    sp.add_argument("--adaptor-model", dest="adaptor_model", default="sonnet", help="effort เป็น high เสมอ")
    sp.add_argument("--par", type=int, default=6, help="จำนวน rollout ที่รันพร้อมกัน (ค่าเริ่มต้น 6)")
    sp.add_argument("--turn-minutes", dest="turn_minutes", type=float, default=30,
                    help="เวลาสูงสุดของ 1 ตาของ Evolver (ค่าเริ่มต้น 30)")
    sp.add_argument("--fresh-session", dest="fresh_session", action="store_true",
                    help="การทดลองตัดส่วนประกอบ: Evolver เริ่มเซสชันใหม่ทุก epoch")
    sp.add_argument("--skillopt", default="", help="ที่อยู่ของ skillopt.py ของบท 05 "
                                                   "(ค่าเริ่มต้น ../skill-optimizer/scripts/skillopt.py นับจากโฟลเดอร์ของสกิลนี้)")

    add("adapt", cmd_adapt, "Benchmark Adaptor 1 เซสชัน แล้วล็อกด้วย hash และตรวจการรั่ว (เรียกโมเดล)")
    add("audit", cmd_audit, "ตรวจ reference/ ซ้ำ · สะอาด exit 0 · พบการรั่ว exit 1 (ไม่เรียกโมเดล)")
    add("base", cmd_base, "epoch 0: Solver ทำโจทย์ทุกชุดโดยไม่มีสกิล (เรียกโมเดล)")
    add("turn", cmd_turn, "ตาของ Evolver 1 ครั้ง → skills_vK (เรียกโมเดล)")
    add("rollout", cmd_rollout, "Solver ทำโจทย์ด้วย skills_vK → vK_val และ vK_train (เรียกโมเดล)")
    add("test", cmd_test, "วัดชุดสกิลของ epoch สุดท้ายกับ Test Set 1 ครั้ง (เรียกโมเดล)")
    sp = add("run", cmd_run, "ทำทุกขั้นที่เหลือจนจบ แล้วพิมพ์ status (เรียกโมเดล)")
    sp.add_argument("--stop-after", dest="stop_after", choices=("adapt", "base", "turn", "rollout"), default=None,
                    help="หยุดหลังขั้นนั้น 1 ครั้ง")
    add("status", cmd_status, "ตารางสรุปของการรัน อ่านจาก state.json เท่านั้น (ไม่เรียกโมเดล)")
    add("noise", cmd_noise, "ความแกว่งของ rollout และผลของประตูรับแบบวัดครั้งเดียว (ไม่เรียกโมเดล)")
    sp = add("eval", cmd_eval, "วัดชุดสกิลใดก็ได้ → leg ชื่อ <ป้าย> (เรียกโมเดล)")
    sp.add_argument("--label", required=True, help="ชื่อ leg")
    sp.add_argument("--skills", required=True, help="v1 | v2 | … | none | โฟลเดอร์ skills")
    sp.add_argument("--split", required=True, choices=("train", "val", "test", "all"))
    sp.add_argument("--model", default=None, help="โมเดลของ Solver (ค่าเริ่มต้น ตามที่ตั้งตอน init)")
    sp = add("export", cmd_export, "เขียนสำเนาของการรันที่ตัดรายละเอียดแล้ว (ไม่เรียกโมเดล)")
    sp.add_argument("--to", required=True, help="โฟลเดอร์ปลายทาง · เขียนที่ <โฟลเดอร์>/<ชื่อ>/")
    return p


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", newline="\n")   # ภาษาไทยและ LF เหมือนกันทุกเครื่อง
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        die("ถูกหยุดกลางทาง · รันคำสั่ง run ซ้ำเพื่อทำต่อจากขั้นที่ค้าง", 130)


if __name__ == "__main__":
    sys.exit(main())
