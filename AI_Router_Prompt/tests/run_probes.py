#!/usr/bin/env python3
"""Real model calls for routing decisions; does not execute the proposed workflows.

Usage: python tests/run_probes.py before|after|new
Each prompt gets a fresh session; cases within a session are a batch.
Expected answers stay local and are never sent to the model. No automatic retries.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def run(phase, only=None, label=None):
    cases = json.loads((ROOT / 'tests/cases.json').read_text())
    selected = [c for c in cases if ('new' in c['phases']) == (phase == 'new')]
    if only:
        selected = [c for c in selected if c['file'] == only]
        if not selected:
            raise SystemExit('No matching cases')
    for filename in dict.fromkeys(c['file'] for c in selected):
        name = Path(filename).stem
        outdir = ROOT / 'tests/results' / (label or phase) / name
        try:
            outdir.mkdir(parents=True)
        except FileExistsError:
            print(f'SKIP existing {outdir}', flush=True)
            continue
        source = ROOT / filename
        if phase == 'before':
            source = ROOT / 'tests/originals' / (name + '.txt')
        prompt = source.read_text()
        batch = [{'id': c['id'], 'question': c['question']} for c in selected if c['file'] == filename]
        request = (
            'นี่คือการทดสอบการตัดสินใจของ ROUTER ด้วยสถานการณ์จำลอง ไม่ใช่การวิจารณ์ prompt '
            'ใช้กฎใน PROMPT กับแต่ละ CASE แยกกัน ตอบการกระทำถัดไปตามกฎนั้นจริง '
            'ถ้าโจทย์ตอบได้ตามกฎ ให้ใส่คำตอบด้วย ถ้าต้องส่งงานหรือรอ ให้ระบุ '
            'สมมติ yolo และ cyolo1 พร้อมใช้ เว้นแต่ CASE ระบุเป็นอย่างอื่น '
            'ห้ามเรียกเครื่องมือหรือ agent จริงในการทดสอบนี้ ห้ามแต่งผลการรัน '
            'ตอบ JSON เท่านั้น รูปแบบ {"results":[{"id":"...","next_action":"...",'
            '"status":"...","answer":"..."}]} แต่ละ case ไม่เกิน 2 ประโยค '
            'ช่องที่ไม่เกี่ยวข้องใช้สตริงว่าง\n\n<PROMPT>\n' + prompt +
            '\n</PROMPT>\n<CASES>\n' + json.dumps(batch, ensure_ascii=False) + '\n</CASES>'
        )
        (outdir / 'request.txt').write_text(request)
        env = dict(os.environ, CODEX_HOME='/root/workspace/.Codex/cyolo1')
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix='router-probe-') as scratch:
            cmd = ['codex', 'exec', '--sandbox', 'read-only', '--skip-git-repo-check',
                   '--ephemeral', '-C', scratch, '-m', 'gpt-6-astra',
                   '-c', 'model_reasoning_effort="high"', '--json',
                   '-o', str(outdir / 'answer.txt'), request]
            with (outdir / 'events.jsonl').open('w') as log, (outdir / 'stderr.txt').open('w') as err:
                try:
                    proc = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL,
                                          stdout=log, stderr=err, timeout=240)
                    exit_code = proc.returncode
                except subprocess.TimeoutExpired:
                    exit_code = 'timeout'
        events = []
        for line in (outdir / 'events.jsonl').read_text().splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        completed = [e for e in events if e.get('type') == 'turn.completed']
        failed = [e for e in events if e.get('type') in ('turn.failed', 'error')]
        metadata = {'phase': phase, 'source': filename, 'model': 'gpt-6-astra',
                    'effort': 'high', 'account': 'cyolo1', 'exit_code': exit_code,
                    'elapsed_seconds': round(time.monotonic() - started, 2),
                    'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                    'usage': completed[-1].get('usage') if completed else None,
                    'errors': failed, 'cost': None}
        (outdir / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(metadata, ensure_ascii=False), flush=True)
        if exit_code != 0 or not completed or failed:
            raise SystemExit('Stopped after call error; no automatic retry.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['before', 'after', 'new'])
    parser.add_argument('--only', help='Exact prompt path in cases.json')
    parser.add_argument('--label', help='Fresh result directory; preserves earlier runs')
    args = parser.parse_args()
    if args.label and (Path(args.label).name != args.label or args.label in ('.', '..')):
        parser.error('--label must be a directory name')
    run(args.phase, args.only, args.label)
