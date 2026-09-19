"""Record shell timestamps and usage reported by turn.completed, without estimates."""
import datetime
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sys

node, dest, start, end, code = sys.argv[1:]
dest = Path(dest)
events = [json.loads(line) for line in (dest / 'log.jsonl').read_text().splitlines() if line.strip()]
completed = [event for event in events if event.get('type') == 'turn.completed']
failed = [event for event in events if event.get('type') == 'turn.failed']
usage = completed[-1].get('usage') if completed else None
meta = {
    'node': node, 'attempt': int(os.environ.get('RUN_ATTEMPT', '1')),
    'tool': 'Codex CLI 0.154.0',
    'model': 'gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ)',
    'effort': 'high', 'effort_source': 'CLI flag',
    'start_epoch': start, 'end_epoch': end,
    'started_at_utc': datetime.datetime.fromtimestamp(float(start), datetime.timezone.utc).isoformat(),
    'finished_at_utc': datetime.datetime.fromtimestamp(float(end), datetime.timezone.utc).isoformat(),
    'duration_s': float(Decimal(end) - Decimal(start)),
    'exit_code': int(code), 'usage': usage,
    'turn_completed_count': len(completed), 'turn_failed_count': len(failed),
    'execution_status': 'completed' if completed and not failed and int(code) == 0 else 'failed',
    'prompt_sha256': hashlib.sha256((dest / 'prompt.md').read_bytes()).hexdigest(),
    'execution_context': 'execution-context.txt via -c developer_instructions' if os.environ.get('USE_EXECUTION_CONTEXT') == '1' else None,
    'output_capture': 'final-response.md is the final message; deliverables are written by the model in session work/',
}
for name in ('meta.json', 'run-meta.json'):
    (dest / name).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'node': node, 'duration_s': meta['duration_s'], 'usage': usage, 'status': meta['execution_status']}))
