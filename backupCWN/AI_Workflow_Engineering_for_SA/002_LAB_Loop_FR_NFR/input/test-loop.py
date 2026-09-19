#!/usr/bin/env python3
"""Controller tests with a fake executable; NOT student AI pre-run evidence."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
FAKE = r'''#!/usr/bin/env python3
import json, os, re, sys, time
from pathlib import Path
args=sys.argv[1:]
payload=sys.stdin.read()
if '-o' in args:
 out=args[args.index('-o')+1]
else:
 out=re.search(r'ตำแหน่งบันทึกจริง=([^;]+);',payload).group(1)
scenario=os.environ['SCENARIO']
if scenario=='timeout': time.sleep(3)
if 'check-round-' in out:
 n=int(re.search(r'round-(\d+)',out).group(1))
 scope=['01','02','03','04','05','06','07','08','10','11','12','13','15','16','19','20','25','26']
 keys=[('US-'+u,c) for u in scope for c in ['F','B','A','V','N']]
 if scenario=='extra': keys=[('US-'+u,c) for u in scope for c in ['F','B','A','V','N','E1']]
 count=len(keys) if scenario in ('pass','extra','badscore','null','failed','token','time','claude') else (88 if scenario=='stagnant' else 85+n)
 passed=set(range(count))
 if scenario=='regression' and n==2: passed=set(range(1,count+1))
 text='# Fake controller fixture (not AI evidence)\n\n| US | เกณฑ์ | ผล | หลักฐาน | ข้อบกพร่อง | Feedback |\n|---|---|---|---|---|---|\n'
 for i,(u,c) in enumerate(keys):
  v='PASS' if i in passed else 'FAIL'
  text+=f'| {u} | {c} | {v} | fixture | fixture | fixture |\n'
 result='PASS' if count==len(keys) else 'FAIL'
 if scenario=='badscore': count-=1
 text+=f'\nRESULT: {result}\nSCORE: {count}/{len(keys)}\n'
else:
 text='# Fake draft for controller test only\n'
if '-o' in args: Path(out).write_text(text)
if scenario=='null':
 print('unreadable usage log')
elif scenario=='failed':
 print(json.dumps({'type':'turn.failed','error':{'message':'fixture'}}))
elif '-o' not in args:
 print(json.dumps({'type':'result','result':text,'usage':{'input_tokens':1,'output_tokens':1},'is_error':False}))
else:
 print(json.dumps({'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':1}}))
'''

class ControllerTests(unittest.TestCase):
    def run_case(self, scenario, **limits):
        with tempfile.TemporaryDirectory(prefix='.test-loop-', dir=HERE) as d:
            root=Path(d)
            shutil.copytree(LAB/'prompts',root/'prompts')
            (root/'input').mkdir(); (root/'work').mkdir(); (root/'bin').mkdir()
            for name in ['run-loop.sh','loop-support.py','user-stories-lab002.md']:
                shutil.copy2(HERE/name,root/'input'/name)
            (root/'work/fr-nfr-v0.md').write_text('test fixture only')
            (root/'work/baseline-source.txt').write_text('controller fixture; not student output')
            if scenario=='extra':
                with (root/'prompts/checker-criteria.md').open('a') as f:
                    f.write('\nเกณฑ์เพิ่ม: E1 | fixture condition\n')
            for name in ['codex','claude']:
                p=root/'bin'/name; p.write_text(FAKE); p.chmod(0o755)
            env={**os.environ,'PATH':str(root/'bin')+os.pathsep+os.environ['PATH'],
                 'SCENARIO':scenario,'MAX_ROUNDS':'3','MAX_SECONDS':'60','MAX_TOKENS':'0','AI_CMD':'codex exec', **limits}
            run=subprocess.run(['bash','input/run-loop.sh'],cwd=root,env=env,capture_output=True,text=True,timeout=20)
            log=json.loads((root/'work/loop-log.json').read_text())
            import jsonschema
            jsonschema.Draft202012Validator(json.loads((HERE/'loop-log.schema.json').read_text()),format_checker=jsonschema.FormatChecker()).validate(log)
            self.assertIsNotNone(log['finished_at'])
            before=(root/'work/loop-log.json').read_bytes()
            again=subprocess.run(['bash','input/run-loop.sh'],cwd=root,env=env,capture_output=True,text=True)
            self.assertEqual(again.returncode,2)
            self.assertEqual(before,(root/'work/loop-log.json').read_bytes())
            return run.returncode,log

    def test_pass_stops_without_fixer(self):
        code,s=self.run_case('pass'); self.assertEqual(code,0); self.assertEqual(s['stop_reason'],'pass')
        self.assertEqual([x['phase'] for x in s['calls']],['generator','checker'])
    def test_two_consecutive_non_improvements(self):
        code,s=self.run_case('stagnant'); self.assertEqual(code,1); self.assertEqual(s['stop_reason'],'no_improvement')
        self.assertEqual(len(s['rounds']),3); self.assertEqual(s['rounds'][-1]['no_improvement_streak'],2)
        self.assertEqual(len(s['calls']),6)
    def test_max_rounds_and_regression_despite_score_gain(self):
        code,s=self.run_case('regression'); self.assertEqual(code,1); self.assertEqual(s['stop_reason'],'max_rounds')
        self.assertTrue(s['rounds'][1]['regressions']); self.assertEqual(len(s['calls']),6)
    def test_invalid_score_rejected(self):
        code,s=self.run_case('badscore'); self.assertEqual(code,2); self.assertEqual(s['stop_reason'],'checker_invalid')
    def test_failed_event_rejected(self):
        code,s=self.run_case('failed'); self.assertEqual(code,2); self.assertEqual(s['stop_reason'],'ai_error')
    def test_unreadable_usage_is_null(self):
        code,s=self.run_case('null'); self.assertEqual(code,0); self.assertIsNone(s['total_tokens'])
    def test_unknown_usage_with_budget_stops(self):
        code,s=self.run_case('null',MAX_TOKENS='10'); self.assertEqual(code,2); self.assertEqual(s['stop_reason'],'token_usage_unknown')
    def test_token_limit(self):
        code,s=self.run_case('token',MAX_TOKENS='1'); self.assertEqual(code,2); self.assertEqual(s['stop_reason'],'token_limit')
    def test_timeout(self):
        code,s=self.run_case('timeout',MAX_SECONDS='1'); self.assertEqual(code,2); self.assertEqual(s['stop_reason'],'time_limit')
    def test_optional_criterion(self):
        code,s=self.run_case('extra'); self.assertEqual(code,0); self.assertEqual(s['rounds'][0]['score']['possible'],108)
    def test_claude_adapter_with_mock_only(self):
        code,s=self.run_case('claude',AI_CMD='claude -p'); self.assertEqual(code,0); self.assertEqual(s['total_tokens'],4)
    def test_lower_round_limit(self):
        code,s=self.run_case('stagnant',MAX_ROUNDS='1'); self.assertEqual(code,1); self.assertEqual(s['stop_reason'],'max_rounds')
        self.assertEqual(len(s['calls']),2)

if __name__=='__main__': unittest.main(verbosity=2)
