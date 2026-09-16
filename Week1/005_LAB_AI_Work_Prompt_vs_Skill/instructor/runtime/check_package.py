"""Scoped package audit; no model/network use. Functional output recorded separately."""
import csv,datetime,hashlib,json,re,subprocess,sys,uuid
from pathlib import Path
from urllib.parse import unquote
R=Path(__file__).resolve().parents[2]
print('UTC',datetime.datetime.now(datetime.timezone.utc).isoformat(), 'Python',sys.version)
errors=[]; count=0
for md in R.rglob('*.md'):
 if any(x in md.parts for x in ['workspaces','.git','.lab-runtime','.ipynb_checkpoints']): continue
 content=md.read_text(); visible=re.sub(r'```.*?```','',content,flags=re.S)
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',visible):
  target=target.split('#')[0]
  if not target or re.match(r'\w+://',target): continue
  count+=1
  if not (md.parent/unquote(target)).exists(): errors.append(f'broken link {md.relative_to(R)} -> {target}')
print('Local links checked:',count)
for n,name in [(1,'requirements-check'),(2,'shop-recovery'),(3,'complaint-triage')]:
 full=(R/f'skills/{name}/SKILL.md').read_text(); _,front,body=full.split('---',2); body=body.lstrip('\n')
 canonical=(R/f'canonical/lab{n}.md').read_text()
 assert body==canonical, 'instruction body differs'
 assert f'name: {name}' in front and 'description: ' in front
 assert len(re.findall(r'^## [1-8]\.',body,re.M))==8
 assert not list((R/f'skills/{name}').rglob('*.py'))
 print(f'PASS lab{n} skill YAML fields, 8 sections, exact canonical SHA256',hashlib.sha256(canonical.encode()).hexdigest())
for label in ['A','B','C']:
 for lab in ['lab1','lab3']:
  data=(R/f'experiments/inputs/{lab}-{label}.md').read_text()
  assert 'เฉลย' not in data and 'exemplar' not in data and 'Accuracy' not in data
 if label in ['A','B']:
  data=(R/f'experiments/inputs/lab1-{label}.md').read_text()
  ids=re.findall(r'\[((?:CH|MT|PL)\d+)\]',data)
  assert len(ids)==15 and len(set(ids))==15
 data=(R/f'experiments/inputs/lab3-{label}.md').read_text()
 assert len(re.findall(r'^\[C\d\d\]',data,re.M))==6
 assert len(re.findall(r'^\| O\d\d \|',data,re.M))==5
 day=20 if label=='B' else 12
 for elapsed in [7,8,10,2]:
  received=datetime.date(2026,9,day-elapsed); claimed=datetime.date(2026,9,day)
  assert (claimed-received).days==elapsed
 print('PASS data-only bundles and complaint cardinality/date arithmetic',label)
for lab,ds in [('lab1','A'),('lab3','B'),('lab2','rollback-A')]:
 work=[]
 for arm in ['P','S']:
  label='audit-'+lab+'-'+arm+'-'+uuid.uuid4().hex[:8]
  cmd=[sys.executable,str(R/'instructor/runtime/prepare_experiment.py'),lab,ds,arm,'--label',label]
  result=subprocess.run(cmd,text=True,capture_output=True,check=True)
  print('$ '+' '.join(cmd)); print(result.stdout,end='')
  w=R/'experiments/workspaces'/label; work.append(w)
  assert not list(w.rglob('*key*')) and not list(w.rglob('*exemplar*'))
  if arm=='P': assert not (w/'.agents').exists(); assert (w/'prompt.txt').read_text().startswith((R/f'canonical/{lab}.md').read_text())
  else: assert list((w/'.agents/skills').glob('*/SKILL.md')); assert (w/'prompt.txt').read_text().startswith('$')
 for file in ['input.md','references.md','template.md']: assert (work[0]/file).read_bytes()==(work[1]/file).read_bytes()
 print('PASS matched P/S data, refs, templates; isolated native placement; no keys',lab)
 if lab=='lab2':
  w=work[1]
  try:
   for args,expected in [(['setup','rollback-A'],0),(['verify'],1),(['start'],0),(['verify'],1),(['rollback'],0),(['verify'],0)]:
    result=subprocess.run([str(w/'labctl'),*args],cwd=w,text=True,capture_output=True,timeout=15)
    print('$ ./labctl '+' '.join(args)); print(result.stdout+result.stderr,end=''); assert result.returncode==expected
  finally:
   result=subprocess.run([str(w/'labctl'),'stop'],cwd=w,text=True,capture_output=True,check=True); print(result.stdout,end='')
  print('PASS generated experiment runtime functional and stopped')
with (R/'experiments/scores.csv').open() as f:
 rows=list(csv.reader(f)); assert len(rows)==2 and len(rows[0])==len(rows[1]) and not any(rows[1]); print('PASS fillable CSV remains blank')
if errors:
 print('\n'.join(errors)); raise SystemExit(1)
print('ALL PACKAGE CHECKS PASSED')
