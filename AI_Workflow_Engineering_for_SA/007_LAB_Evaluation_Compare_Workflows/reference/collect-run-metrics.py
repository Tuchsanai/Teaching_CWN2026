#!/usr/bin/env python3
"""Collect this LAB's measured AI runs without treating missing usage as zero.
Run from any directory; outputs lab-metrics.csv beside this script.
"""
import csv
import json
from pathlib import Path

ref = Path(__file__).resolve().parent
metrics_meta = json.loads((ref / "step-01-metrics/meta.json").read_text())
rows = [{"step": "step-01-metrics", "duration_s": metrics_meta["duration_s"], "input_tokens": "ไม่มีข้อมูล", "output_tokens": "ไม่มีข้อมูล"}]
for path in sorted(ref.glob("step-*/**/log.jsonl")):
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    terminal = [e for e in events if e.get("type") in ("turn.completed", "turn.failed")]
    meta_path = path.with_name("meta.json")
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    row = {"step": path.parent.relative_to(ref).as_posix(),
           "duration_s": meta.get("duration_s", "ไม่มีข้อมูล")}
    for key in ("input_tokens", "output_tokens"):
        row[key] = sum(e["usage"][key] for e in terminal) if terminal and all(isinstance(e.get("usage", {}).get(key), int) for e in terminal) else "ไม่มีข้อมูล"
    rows.append(row)
with (ref / "lab-metrics.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=["step", "duration_s", "input_tokens", "output_tokens"])
    writer.writeheader()
    writer.writerows(rows)
print("Measured AI runs:", len(rows))
