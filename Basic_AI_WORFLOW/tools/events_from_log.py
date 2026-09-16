#!/usr/bin/env python3
"""Summarize Codex/Claude JSONL without inventing event timestamps.

Codex cached tokens are a subset of input; Claude cache reads are separate.
Claude input includes uncached input plus cache_creation_input_tokens.
Malformed lines are retained verbatim as unknown rows and reported to stderr.
Displayed paths strip the project cwd prefix before truncation; raw logs stay intact.
Other paths under the machine home directory are relative to the project cwd too.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys


PROJECT_CWD = str(Path.cwd().resolve())


def relative_paths(text):
    text = text.replace(PROJECT_CWD + "/", "").replace(PROJECT_CWD, ".")
    return re.sub(
        re.escape(str(Path.home())) + r"/[^\s\x27\x22`<>|;\\)\]},]*",
        lambda match: os.path.relpath(match.group(), PROJECT_CWD), text)


def compact(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def cell(value, limit=200):
    text = " ".join(relative_paths(compact(value)).split())[:limit]
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;")


def mapping(value):
    return value if isinstance(value, dict) else {}


def read_text(path):
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace").strip()
    except OSError:
        return ""


def read_events(path):
    events = []
    for number, line in enumerate(read_text(path).splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except (ValueError, RecursionError):
            print(f"{path.name}:{number}: invalid JSON; preserving raw line", file=sys.stderr)
            events.append(line)
    return events


def detect_engine(directory, events):
    marker = read_text(directory / ".engine").split()
    if marker and marker[0] in ("codex", "claude"):
        return marker[0]
    for event in events:
        event = mapping(event)
        if event.get("type") == "thread.started":
            return "codex"
        if event.get("type") == "system" and event.get("subtype") == "init":
            return "claude"
    return "unknown"


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else 0


def summarize(events, engine):
    rows, totals = [], [0, 0, 0]
    for raw in events:
        if not isinstance(raw, dict):
            rows.append(("unknown", raw))
            continue
        kind = raw.get("type", "unknown")
        if engine == "codex":
            if kind in ("thread.started", "item.started", "item.updated"):
                continue
            if kind == "item.completed":
                item = mapping(raw.get("item"))
                item_kind = item.get("type", "unknown")
                if item_kind == "command_execution":
                    detail = relative_paths(compact(item.get("command", "")))[:200]
                    if item.get("exit_code") is not None:
                        detail += f" → exit {item['exit_code']}"
                    rows.append(("command", detail))
                elif item_kind == "file_change":
                    changes = item.get("changes", [])
                    if not isinstance(changes, list):
                        changes = [changes]
                    rows.append(("file", "; ".join(
                        " ".join(str(change[k]) for k in ("kind", "path") if k in change)
                        if isinstance(change, dict) else compact(change) for change in changes)))
                elif item_kind in ("agent_message", "reasoning"):
                    rows.append(("message" if item_kind == "agent_message" else "reasoning", item.get("text", "")))
                else:
                    rows.append(("todo" if item_kind == "todo_list" else item_kind, item))
            elif isinstance(kind, str) and kind.startswith("turn."):
                if kind == "turn.completed":
                    usage = mapping(raw.get("usage"))
                    for i, key in enumerate(("input_tokens", "cached_input_tokens", "output_tokens")):
                        totals[i] += number(usage.get(key))
                    rows.append(("turn", raw))
                elif kind == "turn.failed":
                    rows.append(("error", raw.get("error", raw)))
                else:
                    rows.append(("turn", raw))
            elif kind == "error":
                rows.append(("error", raw.get("message", raw)))
            else:
                rows.append((kind, raw))
        elif engine == "claude":
            if kind == "system" and raw.get("subtype") == "init":
                rows.append(("init", raw.get("model", "")))
            elif kind in ("assistant", "user"):
                content = mapping(raw.get("message")).get("content", [])
                if not isinstance(content, list):
                    rows.append(("message", content))
                    continue
                if not content:
                    rows.append((kind, raw))
                for block in content:
                    if not isinstance(block, dict):
                        rows.append((kind, block))
                        continue
                    block_kind = block.get("type", "unknown")
                    if block_kind == "text":
                        rows.append(("message", block.get("text", "")))
                    elif block_kind == "tool_use":
                        name = block.get("name", "")
                        inputs = mapping(block.get("input"))
                        key = "command" if name == "Bash" else "file_path" if name in ("Read", "Write", "Edit") else None
                        rows.append((f"tool:{name}", inputs.get(key, inputs) if key else block.get("input", {})))
                    else:
                        rows.append((block_kind, block))
            elif kind == "result":
                usage = mapping(raw.get("usage"))
                for i, key in enumerate(("input_tokens", "cache_read_input_tokens", "output_tokens")):
                    totals[i] += number(usage.get(key))
                totals[0] += number(usage.get("cache_creation_input_tokens"))
                rows.append(("result", {key: raw[key] for key in (
                    "subtype", "is_error", "duration_ms", "num_turns", "total_cost_usd") if key in raw}))
            else:
                rows.append((kind, raw))
        else:
            rows.append((kind, raw))
    return rows, totals


def parse_time(value):
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return stamp if stamp.tzinfo else None
    except (ValueError, OverflowError):
        return None


def metadata(directory, suffix):
    times, lines = [], []
    for label, filename in (("Start", ".start"), ("End", ".end")):
        raw = read_text(directory / (filename + suffix))
        stamp = parse_time(raw)
        times.append(stamp)
        display = (f"{stamp.astimezone(timezone.utc).isoformat()} (UTC) / "
                   f"{stamp.astimezone(timezone(timedelta(hours=7))).isoformat()}") if stamp else raw or "-"
        lines.append(f"{label}: {cell(display)}  ")
    duration = f"{(times[1] - times[0]).total_seconds():g} seconds" if all(times) else "-"
    lines.append(f"Duration: {duration}  ")
    exit_value = read_text(directory / (".exit" + suffix))
    if exit_value:
        lines.append(f"Exit: {cell(exit_value.removeprefix('exit='))}  ")
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    directory = args.directory
    events = read_events(directory / "log.jsonl")
    engine = detect_engine(directory, events)
    title = f"{directory.resolve().parent.name}/{directory.resolve().name}"
    lines = [f"# Events — {title} ({engine})", ""]
    phases = [("Phase 1", "", events)]
    if (directory / "log-phase2.jsonl").exists():
        phases.append(("Phase 2", "2", read_events(directory / "log-phase2.jsonl")))
    token_rows = []
    for phase, suffix, phase_events in phases:
        if suffix:
            lines.extend([f"## {phase}", ""])
        lines.extend(metadata(directory, suffix))
        lines.extend(["", "| # | เวลา | ประเภท | รายละเอียด |", "| --- | --- | --- | --- |"])
        rows, totals = summarize(phase_events, engine)
        for i, (kind, detail) in enumerate(rows, 1):
            # Keep the exit status even when a command uses the entire 200-char budget.
            limit = 230 if kind == "command" else 200
            lines.append(f"| {i} | - | {cell(kind)} | {cell(detail, limit)} |")
        total = totals[0] + totals[2] + (totals[1] if engine == "claude" else 0)
        token_rows.append(f"| {phase} | {totals[0]} | {totals[1]} | {totals[2]} | {total} |")
        lines.append("")
    lines.extend(["## Tokens", "", "| Phase | input | cached | output | total |", "| --- | --- | --- | --- | --- |", *token_rows, ""])
    if engine == "claude":
        lines.extend(["input รวม input_tokens + cache_creation_input_tokens; cached คือ cache_read_input_tokens; total = input + cached + output", ""])
    try:
        (directory / "events.md").write_text("\n".join(lines), encoding="utf-8")
    except OSError as exc:
        print(f"events_from_log: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
