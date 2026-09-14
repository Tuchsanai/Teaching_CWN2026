#!/usr/bin/env python3
"""Check actual JSON event types; text inside command output is not an event."""
import argparse, datetime, hashlib, json, re, time
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('--out', default='model-event-check.json')
args = parser.parse_args()
root = Path(__file__).resolve().parent
started = datetime.datetime.now(datetime.timezone.utc)
tick = time.monotonic()
runs = []
for path in sorted(root.rglob('log.jsonl')):
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    completed = [e for e in events if e.get('type') == 'turn.completed']
    failed = [e for e in events if e.get('type') == 'turn.failed']
    if not completed and not failed:
        continue
    meta = json.loads((path.parent / 'meta.json').read_text())
    false_matches = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        event = json.loads(line)
        if re.search('turn.failed', line) and event.get('type') != 'turn.failed':
            false_matches.append({'line': number, 'event_type': event.get('type'),
                                  'matched_text': re.search('turn.failed', line).group()})
    runs.append({'step': str(path.parent.relative_to(root)),
                 'log_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'turn_completed': len(completed), 'turn_failed': len(failed),
                 'process_exit_code': meta.get('exit_code'),
                 'regex_text_matches_not_failed_events': false_matches})
report = {'started_at': started.isoformat(),
          'ended_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'duration_s': round(time.monotonic() - tick, 6),
          'method': 'Parse JSONL and compare event.type exactly',
          'runs': runs, 'model_calls': len(runs),
          'passed': bool(runs) and all(x['turn_completed'] >= 1 and x['turn_failed'] == 0 and x['process_exit_code'] == 0 for x in runs)}
out = Path(args.out)
if not out.is_absolute(): out = root / out
with out.open('x') as stream: json.dump(report, stream, ensure_ascii=False, indent=2)
print(json.dumps({'model_calls': len(runs), 'passed': report['passed'],
                  'failed_events': sum(x['turn_failed'] for x in runs),
                  'regex_false_matches': sum(len(x['regex_text_matches_not_failed_events']) for x in runs)}, ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
