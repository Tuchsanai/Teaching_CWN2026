#!/usr/bin/env python3
"""Collect reference log metrics. Missing measurements are not zero."""
import argparse
import csv
import json
import math
from pathlib import Path
import re
import sys

MISSING = "ไม่มีข้อมูล"
FIELDS = ["lab", "step", "calls", "failed", "input_tokens", "cached_input_tokens",
          "output_tokens", "reasoning_tokens", "duration_s"]
USAGE = {"input_tokens": "input_tokens", "cached_input_tokens": "cached_input_tokens",
         "output_tokens": "output_tokens", "reasoning_tokens": "reasoning_output_tokens"}
DURATION_KEYS = ("duration_s", "wall_time_s", "wall_s", "wall_time_seconds", "duration_seconds")


def number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) and value >= 0 else None
    except (ValueError, TypeError):
        return None


def display(value):
    return int(value) if value == int(value) else value


def duration(folder, warnings):
    meta = folder / "meta.json"
    if meta.is_file():
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key in DURATION_KEYS:
                    value = number(data.get(key))
                    if value is not None:
                        return display(value)
        except (OSError, ValueError, UnicodeError) as exc:
            warnings.append(f"{meta}: {exc}")
    note = folder / "run-meta.md"
    if note.is_file():
        try:
            content = note.read_text(encoding="utf-8")
            # Read explicit seconds only, never infer from timestamps or minutes.
            labels = "|".join(DURATION_KEYS + (r"duration \(s\)", r"wall time \(s\)", "wall time", "wall seconds", r"เวลา wall \(วินาที\)"))
            for line in content.splitlines():
                clean = line.replace("**", "").replace("`", "").strip()
                match = re.match(r"^(?:[-*]\s*|\|\s*)?(?:" + labels + r")\s*[:=|]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:s|seconds|วินาที)?\s*\|?\s*$", clean, re.I)
                if match:
                    return display(float(match.group(1)))
        except (OSError, UnicodeError) as exc:
            warnings.append(f"{note}: {exc}")
    return MISSING


def collect(path, root, warnings):
    rel = path.relative_to(root)
    row = {"lab": rel.parts[0], "step": path.parent.relative_to(root / rel.parts[0] / "reference").as_posix(),
           "calls": 0, "failed": 0}
    totals = {key: 0 for key in USAGE}
    known = {key: True for key in USAGE}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        warnings.append(f"{path}: {exc}")
        lines = []
        row["calls"] = row["failed"] = MISSING
    for index, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            warnings.append(f"{path}:{index}: malformed JSON ignored; counts may be incomplete")
            continue
        if not isinstance(event, dict):
            warnings.append(f"{path}:{index}: non-object event ignored")
            continue
        kind = event.get("type")
        if kind not in ("turn.completed", "turn.failed"):
            continue
        row["calls"] += 1
        row["failed"] += int(kind == "turn.failed")
        usage = event.get("usage")
        # Failed turns may report usage too. Absence there means cost is unknown.
        usage = usage if isinstance(usage, dict) else {}
        for field, key in USAGE.items():
            value = number(usage.get(key))
            if value is None:
                known[field] = False
            else:
                totals[field] += value
    for field in USAGE:
        row[field] = display(totals[field]) if known[field] and isinstance(row["calls"], int) and row["calls"] > 0 else MISSING
        if row["calls"] and not known[field]:
            warnings.append(f"{path}: {field} incomplete; observed subtotal={totals[field]:g}")
    row["duration_s"] = duration(path.parent, warnings)
    return row


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="..", help="Directory containing 00?_LAB_* folders")
    parser.add_argument("--out", default="work/metrics.csv")
    parser.add_argument("--summary", default="work/metrics-summary.md")
    args = parser.parse_args(argv)
    root, out, summary = Path(args.root).resolve(), Path(args.out), Path(args.summary)
    if not root.is_dir():
        parser.error("--root must be an existing directory")
    if out.exists() or summary.exists() or out.resolve() == summary.resolve():
        parser.error("Choose two distinct new output paths; existing evidence is not overwritten")
    warnings = []
    rows = [collect(path, root, warnings) for path in sorted(root.glob("00?_LAB_*/reference/**/log.jsonl"))]
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# สรุปทรัพยากรต่อ LAB", "",
             "calls = จำนวน event turn.completed + turn.failed; failed เป็นส่วนหนึ่งของ calls",
             "จำนวน event ไม่ยืนยันจำนวน process CLI และไม่ใช่จำนวนรอบสร้าง–ตรวจ–แก้",
             "โทเคนรวมจาก usage ของ terminal events; ขาด key แม้หนึ่งครั้งให้ไม่มีข้อมูล พร้อม subtotal ในข้อสังเกต",
             "cached_input_tokens และ reasoning_tokens แยกแสดง ไม่บวกซ้ำเป็นโทเคนรวม",
             "duration_s ใช้ meta.json ก่อน run-meta.md ในโฟลเดอร์เดียวกับ log เท่านั้น",
             "ผลรวม duration_s เป็นผลรวมเวลาต่อไฟล์ ไม่ใช่เวลา wall ของกราฟที่รันขนาน",
             "แต่ละโฟลเดอร์ log ต้องมี metadata ของการรันนั้นเอง; ไม่กระจายเวลารวมจากโฟลเดอร์แม่",
             "สแกนเฉพาะ reference/; ไม่ครอบคลุม work/ หรือผลทดลอง Single/Dynamic โดยอัตโนมัติ",
             "ไม่มีข้อมูลไม่เท่ากับ 0; ไม่พบ log ไม่ได้หมายความว่าไม่มีการเรียก", "",
             "| " + " | ".join(FIELDS[:1] + FIELDS[2:]) + " |",
             "| " + " | ".join(["---"] * (len(FIELDS) - 1)) + " |"]
    # Include existing LAB folders without logs, so missing coverage is explicit.
    labs = sorted(p.name for p in root.glob("00?_LAB_*") if p.is_dir())
    for lab in labs:
        subset = [r for r in rows if r["lab"] == lab]
        values = [lab]
        for field in FIELDS[2:]:
            values.append(display(sum(r[field] for r in subset)) if subset and all(r[field] != MISSING for r in subset) else MISSING)
        lines.append("| " + " | ".join(map(str, values)) + " |")
    if not rows:
        lines.extend(["", "ไม่พบ log ที่เข้าเงื่อนไข: ไม่มีข้อมูล; CSV มีเฉพาะหัวตาราง"])
    lines.extend(["", "## ข้อสังเกต", ""])
    lines.extend("- " + warning for warning in warnings)
    if not warnings:
        lines.append("ไม่พบปัญหารูปแบบจากไฟล์ที่อ่าน; ค่าที่ขาดยังแสดงไม่มีข้อมูล")
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for warning in warnings:
        print(warning, file=sys.stderr)
    print(f"Collected {len(rows)} log files -> {out}; {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
