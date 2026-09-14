#!/usr/bin/env python3
"""Summarize actual Codex turn.completed usage; no estimates or overwritten CSVs."""
import argparse
import csv
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--out', default='metrics.csv')
args = parser.parse_args()
root = Path(__file__).resolve().parent
rows = []
for log in sorted(root.rglob('log.jsonl')):
    events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    usage = [event['usage'] for event in events if event.get('type') == 'turn.completed']
    if not usage:
        continue  # Copy/browser commands have no model usage.
    meta = json.loads((log.parent / 'meta.json').read_text())
    rows.append({'step': str(log.parent.relative_to(root)),
                 'duration_s': meta['duration_s'],
                 'input_tokens': sum(u['input_tokens'] for u in usage),
                 'output_tokens': sum(u['output_tokens'] for u in usage)})
output = Path(args.out)
if not output.is_absolute():
    output = root / output
with output.open('x', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['step', 'duration_s', 'input_tokens', 'output_tokens'])
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps({'runs': len(rows), 'duration_s': round(sum(float(r['duration_s']) for r in rows), 3),
                  'input_tokens': sum(r['input_tokens'] for r in rows),
                  'output_tokens': sum(r['output_tokens'] for r in rows)}, ensure_ascii=False))
