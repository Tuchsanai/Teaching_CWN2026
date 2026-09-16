"""Prepare fresh reviewable inputs; NEVER calls a model. Instructor only."""
import argparse,hashlib,json,shutil,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
names={'lab1':'requirements-check','lab2':'shop-recovery','lab3':'complaint-triage'}
p=argparse.ArgumentParser(); p.add_argument('lab',choices=names); p.add_argument('dataset'); p.add_argument('arm',choices=['P','S']); p.add_argument('--label',default=None)
a=p.parse_args()
allowed=['basic-A','basic-B','rollback-A','rollback-B','transfer-C'] if a.lab=='lab2' else ['A','B','C']
if a.dataset not in allowed: p.error('dataset must be '+','.join(allowed))
label=a.label or f'{a.lab}-{a.dataset}-{a.arm}-{uuid.uuid4().hex[:8]}'
if not label.replace('-','').replace('_','').isalnum(): p.error('invalid label')
work=ROOT/'experiments/workspaces'/label
work.mkdir(parents=True,exist_ok=False)
# New nested repository bounds repo skill discovery; no commit, push, auth or global config changes.
subprocess.run(['git','init','-q',str(work)],check=True)
shutil.copyfile(ROOT/f'experiments/inputs/{a.lab}-{a.dataset}.md',work/'input.md')
for fname in ['references.md','template.md']: shutil.copyfile(ROOT/f'labs/{a.lab}/{fname}',work/fname)
body=(ROOT/f'canonical/{a.lab}.md').read_text()
shared='อ่าน input.md, references.md และ template.md เท่านั้นสำหรับข้อมูลโจทย์ ห้ามอ่านเฉลย ผลรอบอื่น หรือไฟล์นอกพื้นที่นี้ ห้ามเรียก agent อื่น เว็บ หรือแอปภายนอก ไม่แก้โค้ด/สคริปต์/config ส่งคำตอบไทยตาม template โดยไม่อ้างว่าทำสิ่งที่ยังไม่ได้ทำ\n'
if a.lab=='lab2': shared+='อนุญาตรันเฉพาะ ./labctl status, logs, open, start, rollback, verify, stop ในพื้นที่นี้เพื่อแก้โจทย์ ห้าม setup/reset ระหว่างรอบ เก็บหลักฐานจริงและหยุด Lab หลังตรวจเสร็จ หากไม่มี browser ให้ระบุว่ายังไม่ตรวจ\n'
if a.arm=='P':
 (work/'instruction.md').write_text(body)
 prompt=body+'\n'+shared
else:
 skill=work/'.agents/skills'/names[a.lab]; skill.mkdir(parents=True)
 shutil.copyfile(ROOT/'skills'/names[a.lab]/'SKILL.md',skill/'SKILL.md')
 prompt='$'+names[a.lab]+'\n'+shared
(work/'prompt.txt').write_text(prompt)
if a.lab=='lab2':
 shutil.copyfile(ROOT/'labctl',work/'labctl'); (work/'labctl').chmod(0o755)
 runtime=work/'instructor/runtime'; runtime.mkdir(parents=True)
 for fname in ['server.py','control.py']: shutil.copyfile(ROOT/'instructor/runtime'/fname,runtime/fname)
# Metadata outside working input, for parent audit only.
meta={'label':label,'lab':a.lab,'dataset':a.dataset,'arm':a.arm,'instruction_sha256':hashlib.sha256(body.encode()).hexdigest(),'files':{f:hashlib.sha256((work/f).read_bytes()).hexdigest() for f in ['input.md','references.md','template.md']},'native_loaded':'pending','model_run':'pending'}
record=ROOT/'experiments/manifests'; record.mkdir(exist_ok=True); (record/(label+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('WORKSPACE '+str(work)); print('No model launched; no answers copied.')
if a.lab=='lab2': print('BEFORE timing, in that workspace: ./labctl setup '+a.dataset)
print('Model command advice: cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=high --json -o answer.md - < prompt.txt > run.jsonl 2> run.stderr')
