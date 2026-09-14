#!/usr/bin/env python3
"""Local file/log adapter; never calls an AI or invents usage."""
import json
import re
import sys
from pathlib import Path

SCOPE = ['01','02','03','04','05','06','07','08','10','11','12','13','15','16','19','20','25','26']
STATE = Path('work/loop-log.json')

def save(s):
    tmp = STATE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(STATE)

def criteria():
    raw = Path('prompts/checker-criteria.md').read_text()
    extra = re.findall(r'^เกณฑ์เพิ่ม: (E\d+) \| .+', raw, re.M)
    if len(extra) != len(set(extra)):
        raise ValueError('เกณฑ์เพิ่มซ้ำ')
    return ['F','B','A','V','N'] + extra

def matrix(path):
    rows = {}
    active = False
    for line in Path(path).read_text().splitlines():
        if not line.startswith('|'):
            active = False
            continue
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if cols == ['US','เกณฑ์','ผล','หลักฐาน','ข้อบกพร่อง','Feedback']:
            active = True
            continue
        if active and cols[0].startswith('US-'):
            if len(cols) != 6 or cols[2] not in ('PASS','FAIL') or not cols[3]:
                raise ValueError('แถวตารางหลักผิดรูปแบบ/ไม่มีหลักฐาน')
            key = (cols[0], cols[1])
            if key in rows:
                raise ValueError('คู่ US/เกณฑ์ซ้ำ')
            rows[key] = cols[2]
    expected = {('US-'+u,c) for u in SCOPE for c in criteria()}
    if set(rows) != expected:
        raise ValueError('คู่ US/เกณฑ์ไม่ครบหรือเกินขอบเขต')
    return rows

def events(path):
    try:
        lines = Path(path).read_text().splitlines()
        parsed = [json.loads(x) for x in lines if x.strip()]
        if not parsed or not all(isinstance(e, dict) for e in parsed):
            return [], False
        return parsed, True
    except (OSError, ValueError):
        return [], False

def usage(parsed):
    totals = []
    for e in parsed:
        if e.get('type') == 'turn.completed' or (e.get('type') == 'result' and not e.get('is_error')):
            u = e.get('usage')
            if not isinstance(u, dict):
                return None
            a, b = u.get('input_tokens'), u.get('output_tokens')
            if type(a) is not int or type(b) is not int or min(a,b) < 0:
                return None
            # Claude reports cache input separately; Codex cached_input_tokens is included in input_tokens.
            cache = 0
            if e.get('type') == 'result':
                for k in ('cache_creation_input_tokens','cache_read_input_tokens'):
                    v = u.get(k, 0)
                    if type(v) is not int or v < 0:
                        return None
                    cache += v
            totals.append(a+b+cache)
    return sum(totals) if totals else None

def main():
    cmd, *a = sys.argv[1:]
    if cmd == 'init':
        utc, epoch, max_rounds, max_seconds, max_tokens, engine = a
        if STATE.exists():
            raise ValueError('มี loop-log เดิมแล้ว ให้เก็บเป็นชุดใหม่ก่อน')
        save(dict(started_at=utc, started_epoch=int(epoch), finished_at=None, wall_seconds=None,
                  ai_cmd=engine, baseline_source=Path('work/baseline-source.txt').read_text().strip(),
                  limits=dict(max_rounds=int(max_rounds), max_seconds=int(max_seconds), max_tokens=int(max_tokens)),
                  stop_reason=None, total_tokens=None, calls=[], rounds=[]))
        return
    s = json.loads(STATE.read_text())
    if cmd == 'payload':
        phase, n, out = a
        n = int(n)
        prompt = {'generator':'step-01-generator','checker':'step-02-checker','fixer':'step-03-fixer'}[phase]
        print(Path('prompts/'+prompt+'.md').read_text())
        print(f'\n## ค่าจากตัวเรียก\nN={n}; ตำแหน่งบันทึกจริง={out}; ส่ง Markdown ฉบับเต็มทางคำตอบสุดท้าย ไม่เขียนไฟล์เอง')
        paths = ['input/user-stories-lab002.md','prompts/checker-criteria.md','work/baseline-source.txt']
        paths += ['work/fr-nfr-v0.md'] if phase == 'generator' else [f'work/fr-nfr-v{n}.md']
        paths += [f'work/check-round-{r}.md' for r in range(1, n + (phase == 'fixer'))]
        for p in paths:
            print(f'\n--- BEGIN INPUT {p} ---\n{Path(p).read_text()}\n--- END INPUT ---')
    elif cmd == 'extract':
        log, out = a
        parsed, valid = events(log)
        result = [e for e in parsed if e.get('type') == 'result' and not e.get('is_error')]
        if not valid or len(result) != 1 or not isinstance(result[0].get('result'),str):
            raise ValueError('ไม่พบผลลัพธ์ Claude ที่สำเร็จ')
        Path(out).write_text(result[0]['result'])
    elif cmd == 'call':
        phase,n,start,end,t0,t1,rc,log,out = a
        parsed, valid = events(log)
        failed = any(e.get('type') in ('turn.failed','error') or e.get('is_error') for e in parsed)
        output_ok = Path(out).is_file() and bool(Path(out).read_text().strip())
        ok = int(rc) == 0 and not failed and output_ok
        tok = usage(parsed) if valid and not failed else None
        s['calls'].append(dict(phase=phase, round=int(n), started_at=start, finished_at=end,
                               wall_seconds=max(0,int(t1)-int(t0)), exit_code=int(rc),
                               log=log, output=out, tokens=tok, success=ok))
        ts = [c['tokens'] for c in s['calls']]
        s['total_tokens'] = sum(ts) if all(t is not None for t in ts) else None
        save(s)
        if not ok:
            raise ValueError('เรียก AI ไม่สำเร็จ/พบ turn.failed/ไม่มี output; ดู JSONL และ stderr')
    elif cmd == 'check':
        n,path = a
        n = int(n)
        content = Path(path).read_text()
        tail = re.search(r'\nRESULT: (PASS|FAIL)\nSCORE: (\d+)/(\d+)\n?\Z', content)
        if not tail or len(re.findall(r'^RESULT:',content,re.M)) != 1 or len(re.findall(r'^SCORE:',content,re.M)) != 1:
            raise ValueError('สองบรรทัดสุดท้าย RESULT/SCORE ผิดรูปแบบ')
        result,x,y = tail.groups(); x,y = int(x),int(y)
        current = matrix(path)
        if y != len(current) or x != sum(v == 'PASS' for v in current.values()):
            raise ValueError('SCORE ไม่ตรงตารางหลัก')
        ever_passed = set()
        for r in range(1,n):
            ever_passed |= {k for k,v in matrix(f'work/check-round-{r}.md').items() if v == 'PASS'}
        regressions = ['/'.join(k) for k in sorted(ever_passed) if current[k] == 'FAIL']
        expected = 'PASS' if x == y and not regressions else 'FAIL'
        if result != expected:
            raise ValueError('RESULT ไม่ตรงคะแนน/regression')
        prev = s['rounds'][-1] if s['rounds'] else None
        stagnant = prev['no_improvement_streak']+1 if prev and x <= prev['score']['earned'] else 0
        s['rounds'].append(dict(round=n, document=f'work/fr-nfr-v{n}.md', check=path,
                                result=result, score=dict(earned=x,possible=y),
                                regressions=regressions, no_improvement_streak=stagnant))
        save(s)
        print(stagnant)
    elif cmd == 'budget':
        elapsed = int(a[0])-s['started_epoch']
        limit = s['limits']
        if elapsed >= limit['max_seconds']:
            print('time_limit')
        elif limit['max_tokens'] and s['calls'] and s['total_tokens'] is None:
            print('token_usage_unknown')
        elif limit['max_tokens'] and s['total_tokens'] is not None and s['total_tokens'] >= limit['max_tokens']:
            print('token_limit')
    elif cmd == 'finish':
        reason,utc,epoch = a
        s.update(stop_reason=reason, finished_at=utc, wall_seconds=max(0,int(epoch)-s['started_epoch']))
        save(s)
    else:
        raise ValueError('unknown command')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
