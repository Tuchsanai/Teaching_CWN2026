#!/usr/bin/env python3
"""ledger กลางของระบบหลายบัญชี (สำเนาเดียวกันอยู่ใน yolo/scripts และ cyolo/scripts)

เก็บเฉพาะตัวเลขและข้อความ error สั้น ๆ ไม่เก็บข้อความ prompt หรือ secret
"""
import fcntl
import json
import os
from datetime import datetime

ROOT = os.environ.get("MA_TEAM_ROOT", "/workspace/.agent-team")
LEDGER = os.path.join(ROOT, "ledger.jsonl")
FIELDS = ["ts_start", "ts_end", "run_id", "node", "account", "cli", "model", "effort",
          "duration_s", "input_tokens", "cached_input_tokens", "cache_write_tokens",
          "output_tokens", "reasoning_tokens", "cost_usd", "status", "error",
          "prompt_chars", "result_chars"]
ZERO = {"duration_s", "input_tokens", "cached_input_tokens", "cache_write_tokens",
        "output_tokens", "reasoning_tokens", "prompt_chars", "result_chars"}


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _append(path, line):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line)
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)


def record(row, run_ledger=None):
    """เพิ่ม 1 แถวสำหรับการเรียก CLI หนึ่งครั้ง คืน dict ที่บันทึก"""
    out = {k: row.get(k, 0 if k in ZERO else "") for k in FIELDS}
    out["cost_usd"] = row.get("cost_usd")
    if row.get("effort_from"):
        out["effort_from"] = row["effort_from"]
    line = json.dumps(out, ensure_ascii=False) + "\n"
    _append(LEDGER, line)
    if run_ledger:
        _append(run_ledger, line)
    return out


def event(name, run_id, run_ledger=None, **fields):
    """บันทึกเหตุการณ์ที่ไม่ใช่การเรียก CLI เช่น worker_switch / lead_switch"""
    row = {"event": name, "ts": now_iso(), "run_id": run_id}
    row.update(fields)
    line = json.dumps(row, ensure_ascii=False) + "\n"
    _append(LEDGER, line)
    if run_ledger:
        _append(run_ledger, line)


def read(path=None):
    path = path or LEDGER
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
    return rows


def calls(rows):
    return [r for r in rows if "event" not in r]


def tokens_used(row):
    """โทเค็นที่ใช้จริงเพื่อคิดงบ: input ใหม่ + cache write + output (ไม่นับ cache read)"""
    if row.get("cli") == "codex":
        return max(row.get("input_tokens", 0) - row.get("cached_input_tokens", 0), 0) \
            + row.get("output_tokens", 0)
    return row.get("input_tokens", 0) + row.get("cache_write_tokens", 0) + row.get("output_tokens", 0)


def table(headers, rows):
    def esc(v):
        return str(v).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _aggregate(rows, key):
    groups = {}
    for r in rows:
        k = r.get(key) or "-"
        g = groups.setdefault(k, {"calls": 0, "ok": 0, "failed": 0, "input_tokens": 0,
                                  "cached_input_tokens": 0, "cache_write_tokens": 0,
                                  "output_tokens": 0, "reasoning_tokens": 0,
                                  "cost_usd": 0.0, "total_s": 0.0})
        g["calls"] += 1
        g["ok" if r.get("status") == "ok" else "failed"] += 1
        for f in ("input_tokens", "cached_input_tokens", "cache_write_tokens",
                  "output_tokens", "reasoning_tokens"):
            g[f] += r.get(f, 0) or 0
        g["cost_usd"] += r.get("cost_usd") or 0
        g["total_s"] += r.get("duration_s", 0) or 0
    for g in groups.values():
        g["cost_usd"] = round(g["cost_usd"], 6)
        g["total_s"] = round(g["total_s"], 1)
        g["avg_s"] = round(g["total_s"] / g["calls"], 1)
    return groups


def summarize(rows):
    rows = calls(rows)
    total = _aggregate([dict(r, _all="ALL") for r in rows], "_all").get("ALL", {})
    return {"total": total, "by_account": _aggregate(rows, "account"),
            "by_model": _aggregate(rows, "model"), "by_run": _aggregate(rows, "run_id")}


def render(summary):
    heads = ["ครั้ง", "สำเร็จ", "ล้ม", "input", "cached", "cache write", "output",
             "reasoning", "$ ตามรายการ", "เวลารวม s", "เฉลี่ย s"]
    keys = ["calls", "ok", "failed", "input_tokens", "cached_input_tokens", "cache_write_tokens",
            "output_tokens", "reasoning_tokens", "cost_usd", "total_s", "avg_s"]
    parts = []
    for title, name, label in (("ตามบัญชี", "by_account", "บัญชี"), ("ตามรุ่น", "by_model", "รุ่น"),
                               ("ตาม run", "by_run", "run")):
        rows = [[k] + [v[x] for x in keys] for k, v in sorted(summary[name].items())]
        rows.append(["รวม"] + [summary["total"].get(x, 0) for x in keys])
        parts.append("### " + title + "\n" + table([label] + heads, rows))
    return "\n\n".join(parts)


def stats_cli(run_id=None, as_json=False, cli=None):
    """พิมพ์สถิติ คืน exit code 0 เสมอเมื่อคำสั่งทำงานสำเร็จ"""
    rows = calls(read())
    if cli:
        rows = [r for r in rows if r.get("cli") == cli]
    if run_id:
        rows = [r for r in rows if r.get("run_id") == run_id]
    if as_json:
        print(json.dumps(summarize(rows), ensure_ascii=False, indent=1))
    elif not rows:
        print("ยังไม่มีสถิติ (ยังไม่มีการเรียกผ่านสคริปต์ของสกิล)")
    else:
        print(render(summarize(rows)))
    return 0
