#!/usr/bin/env python3
"""ของใช้ร่วมของสกิล yolo / cyolo / agent-team (ไลบรารีมาตรฐานเท่านั้น)
ไฟล์นี้มีสำเนาเหมือนกันทุกไบต์ใน yolo/scripts และ cyolo/scripts เพื่อให้แต่ละสกิลใช้เดี่ยวได้
ห้ามอ่านหรือพิมพ์ไฟล์ credential จากโมดูลนี้
"""
import fcntl
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

BASE = os.environ.get("MA_BASE", "/root/ai-accounts")
TEAM_ROOT = os.environ.get("MA_TEAM_ROOT", "/workspace/.agent-team")
GLOBAL_LEDGER = os.path.join(TEAM_ROOT, "ledger.jsonl")

# ความยาก -> (รุ่น Claude, effort Claude, effort Codex)
DIFFICULTY = {
    1: ("haiku", "low", "low"),
    2: ("sonnet", "medium", "medium"),
    3: ("opus", "high", "high"),
    4: ("opus", "xhigh", "xhigh"),
    5: ("opus", "max", "max"),
    6: ("opus", "max", "ultra"),
}

LEDGER_FIELDS = [
    "ts_start", "ts_end", "run_id", "node", "account", "cli", "model", "effort",
    "duration_s", "input_tokens", "cached_input_tokens", "cache_write_tokens",
    "output_tokens", "reasoning_tokens", "cost_usd", "status", "error",
    "prompt_chars", "result_chars",
]

STATUS_TH = {
    "ready": "พร้อม",
    "expired": "ล็อกอินแล้วแต่หมดอายุ",
    "not_logged_in": "ไม่ได้ล็อกอิน",
    "limit": "โควตาหมด/ถูกจำกัด",
    "error": "เรียกไม่สำเร็จ",
}


def setup_io():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def accounts(prefix):
    """prefix = 'yolo' หรือ 'cyolo' คืนรายชื่อบัญชีที่มีโฟลเดอร์จริง เรียงตามเลข"""
    root = os.path.join(BASE, ".Claude" if prefix == "yolo" else ".Codex")
    found = []
    try:
        for name in os.listdir(root):
            match = re.fullmatch(prefix + r"(\d+)", name)
            if match and os.path.isdir(os.path.join(root, name)):
                found.append((int(match.group(1)), name))
    except OSError:
        pass
    return [name for _, name in sorted(found)]


def cli_of(account):
    return "codex" if account.startswith("cyolo") else "claude"


def simulated_limit(account):
    names = [x.strip() for x in os.environ.get("MA_SIMULATE_LIMIT", "").split(",")]
    return account in names


def classify_error(text):
    """คืนชนิดความล้มเหลว: auth / quota / rate_limit / other"""
    low = (text or "").lower()
    if re.search(r"not logged in|oauth|authenticat|unauthorized|\b401\b|please run /login", low):
        return "auth"
    if re.search(r"rate.?limit|\b429\b|too many requests|overloaded", low):
        return "rate_limit"
    if re.search(r"usage limit|quota|limit reached|hit your|out of .*usage|credits?\b.*(exhaust|empty|out)|simulated", low):
        return "quota"
    return "other"


def short(text, limit=200):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "<email>", text)
    return text[:limit]


def total_tokens(row):
    """โทเค็นที่ประมวลผลทั้งหมดต่อแถว (Codex input รวม cached อยู่แล้ว / Claude แยก)"""
    n = (row.get("input_tokens") or 0) + (row.get("output_tokens") or 0)
    if row.get("cli") == "claude":
        n += (row.get("cached_input_tokens") or 0) + (row.get("cache_write_tokens") or 0)
    return n


def make_row(ts_start, account, model, effort, status, usage=None, error=None,
             run_id=None, node=None, cost=None, duration=None, prompt_chars=0,
             result_chars=0, extra=None):
    usage = usage or {}
    row = {
        "ts_start": ts_start, "ts_end": now_iso(), "run_id": run_id, "node": node,
        "account": account, "cli": cli_of(account), "model": model, "effort": effort,
        "duration_s": round(duration, 3) if duration is not None else 0,
        "input_tokens": usage.get("input", 0),
        "cached_input_tokens": usage.get("cached", 0),
        "cache_write_tokens": usage.get("cache_write", 0),
        "output_tokens": usage.get("output", 0),
        "reasoning_tokens": usage.get("reasoning", 0),
        "cost_usd": cost, "status": status, "error": short(error) if error else None,
        "prompt_chars": prompt_chars, "result_chars": result_chars,
    }
    if extra:
        row.update(extra)
    return row


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
    # /workspace เป็น bind mount: ใช้ lock ใน filesystem ของ container
    os.makedirs("/tmp/agent-team-locks", exist_ok=True)
    with open("/tmp/agent-team-locks/ledger.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with open(path, "ab") as handle:
            handle.write(data)


def ledger_append(row, run_dir=None):
    _append(GLOBAL_LEDGER, row)
    if run_dir:
        _append(os.path.join(run_dir, "ledger.jsonl"), row)


def read_ledger(path=None):
    rows = []
    try:
        with open(path or GLOBAL_LEDGER, encoding="utf-8") as handle:
            for line in handle:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return rows


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        out.append("| " + " | ".join("-" if c is None else str(c) for c in row) + " |")
    return "\n".join(out)


def run_process(cmd, timeout=600, cwd=None, env=None, on_line=None, should_stop=None):
    """รันโดยปิด stdin เสมอ อ่าน stdout ทีละบรรทัด ฆ่าทั้ง process group เมื่อหมดเวลา
    คืน dict: rc, stdout, stderr, timed_out, stopped, duration"""
    start = time.time()
    proc = subprocess.Popen(
        cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=cwd, env=env, start_new_session=True, encoding="utf-8", errors="replace",
    )
    out_lines, err_lines = [], []

    def read_out():
        for line in proc.stdout:
            out_lines.append(line)
            if on_line:
                try:
                    on_line(line)
                except Exception:
                    pass

    def read_err():
        for line in proc.stderr:
            err_lines.append(line)

    threads = [threading.Thread(target=read_out, daemon=True),
               threading.Thread(target=read_err, daemon=True)]
    for thread in threads:
        thread.start()
    timed_out = stopped = False
    while proc.poll() is None:
        if timeout and time.time() - start > timeout:
            timed_out = True
        elif should_stop is not None and should_stop():
            stopped = True
        if timed_out or stopped:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            break
        time.sleep(0.2)
    proc.wait()
    for thread in threads:
        thread.join(timeout=5)
    return {
        "rc": proc.returncode, "stdout": "".join(out_lines), "stderr": "".join(err_lines),
        "timed_out": timed_out, "stopped": stopped, "duration": time.time() - start,
    }


def clean_env(*drop_prefixes):
    env = dict(os.environ)
    for key in list(env):
        if key == "CLAUDECODE" or any(key.startswith(p) for p in drop_prefixes):
            env.pop(key)
    return env


def read_prompt(args):
    """รับ prompt จากอาร์กิวเมนต์, --prompt-file หรือ '-' (stdin)"""
    if getattr(args, "prompt_file", None):
        with open(args.prompt_file, encoding="utf-8-sig") as handle:
            return handle.read()
    if args.prompt == "-" or args.prompt is None:
        return sys.stdin.buffer.read().decode("utf-8-sig")
    return args.prompt


def aggregate(rows, key):
    table = {}
    for row in rows:
        name = row.get(key) or "-"
        cur = table.setdefault(name, dict(calls=0, ok=0, fail=0, input=0, cached=0, cache_write=0,
                                          output=0, reasoning=0, cost=0.0, duration=0.0))
        cur["calls"] += 1
        cur["ok" if row.get("status") == "ok" else "fail"] += 1
        cur["input"] += row.get("input_tokens") or 0
        cur["cached"] += row.get("cached_input_tokens") or 0
        cur["cache_write"] += row.get("cache_write_tokens") or 0
        cur["output"] += row.get("output_tokens") or 0
        cur["reasoning"] += row.get("reasoning_tokens") or 0
        cur["cost"] += row.get("cost_usd") or 0
        cur["duration"] += row.get("duration_s") or 0
    return table


def stats_report(rows):
    headers = ["ครั้ง", "สำเร็จ", "ล้ม", "input", "cached", "cache write", "output", "reasoning",
               "ราคาตามรายการ USD", "เวลารวม s", "เฉลี่ย s"]
    blocks = []
    for title, key in (("ตามบัญชี", "account"), ("ตามรุ่น", "model"), ("ตาม run", "run_id")):
        table = aggregate(rows, key)
        data = [[name, c["calls"], c["ok"], c["fail"], c["input"], c["cached"], c["cache_write"],
                 c["output"], c["reasoning"], "%.4f" % c["cost"], "%.1f" % c["duration"],
                 "%.1f" % (c["duration"] / c["calls"])] for name, c in sorted(table.items())]
        blocks.append("### %s\n%s" % (title, md_table([title.replace("ตาม", "")] + headers, data)))
    return "\n\n".join(blocks)


def stats_main(args):
    rows = [r for r in read_ledger() if not r.get("event")]
    if getattr(args, "run", None):
        rows = [r for r in rows if r.get("run_id") == args.run]
    if not rows:
        if getattr(args, "json", False):
            print(json.dumps({"rows": 0, "by_account": {}, "by_model": {}, "by_run": {}}))
        else:
            print("ยังไม่มีสถิติใน ledger (%s)" % GLOBAL_LEDGER)
        return 0
    if getattr(args, "json", False):
        print(json.dumps({"rows": len(rows), "by_account": aggregate(rows, "account"),
                          "by_model": aggregate(rows, "model"),
                          "by_run": aggregate(rows, "run_id")}, ensure_ascii=False))
    else:
        print("แถวที่นับ: %d (ไม่รวมแถวเหตุการณ์) · ที่มา %s\n" % (len(rows), GLOBAL_LEDGER))
        print(stats_report(rows))
    return 0
