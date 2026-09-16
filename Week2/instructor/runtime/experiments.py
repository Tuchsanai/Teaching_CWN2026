"""Instructor only: fresh-context technical pilot. Never retry a paid failure."""
import argparse,datetime,hashlib,json,os,shutil,signal,subprocess,tempfile,time
from pathlib import Path
from lab_paths import LAB_DIRS
from lab_content import read_section, read_dataset
ROOT=Path(__file__).resolve().parents[2]
NAMES={'lab1':'shop-requirements','lab2':'shop-recovery','lab3':'shop-complaints'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def prepare(lab,variant,condition,label):
 out=ROOT/'evidence/experiments'/label
 if out.exists():raise SystemExit('Refusing overwrite/retry: '+str(out))
 out.mkdir(parents=True)
 work=Path(tempfile.mkdtemp(prefix='week2-input-'))
 subprocess.run(['git','init','-q',str(work)],check=True)
 (work/'input.md').write_text(read_dataset(ROOT,lab,variant))
 (work/'manual.md').write_text(read_section(ROOT,lab,'manual'))
 body=read_section(ROOT,lab,'skill')
 common='\nทำงานกับ input.md และ manual.md ในโฟลเดอร์นี้เท่านั้น ตอบร่างแรกภาษาไทย ห้ามอ่านเฉลย ผลรอบอื่น หรือไฟล์นอกโฟลเดอร์ ห้ามใช้เว็บหรือ subagents ห้ามแก้ไฟล์หรือรันบริการ ตอบจากหลักฐานที่ให้ ไม่มีผู้เรียนโต้ตอบในรอบนี้ จึงบอกสิ่งที่ต้องถามแทนการหยุดรอ'
 if condition=='S':
  target=work/'.agents/skills'/NAMES[lab];target.mkdir(parents=True)
  shutil.copy(ROOT/f'.agents/skills/{NAMES[lab]}/SKILL.md',target/'SKILL.md')
  prompt='$'+NAMES[lab]+common+'\nยืนยันการใช้ native Skill โดยใช้เครื่องมืออ่าน .agents/skills/'+NAMES[lab]+'/SKILL.md ก่อนทำงาน เพื่อให้ตรวจการโหลดได้จาก log'
 else:prompt=body+common
 (out/'prompt.txt').write_text(prompt)
 manifest={str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in work.rglob('*') if p.is_file() and '.git' not in p.parts}
 (out/'input-manifest.json').write_text(json.dumps(manifest,indent=2))
 shutil.copytree(work,out/'input-snapshot',ignore=shutil.ignore_patterns('.git'))
 return out,work,prompt

def run(lab,variant,condition,label):
 out,work,prompt=prepare(lab,variant,condition,label)
 # Authentication stays in cyolo1. No credentials inspected or copied.
 cmd=['cyolo1','exec','-m','gpt-6-astra','-c','model_reasoning_effort="high"','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--ephemeral','-c','project_doc_max_bytes=0','-c','features.multi_agent=false','--json','-o',str(out/'answer.md'),prompt]
 meta={'label':label,'lab':lab,'variant':variant,'condition':condition,'model':'gpt-6-astra','effort':'high','account':'cyolo1','utc_start':utc(),'timeout_seconds':240,'workspace':str(work),'stdin':'/dev/null','command_argv':cmd,'human_corrections':'not-measured','human_hints':'not-measured','learner_time':'not-measured','design':'technical pilot, one unassisted call; not a classroom study'}
 start=time.monotonic();timed=False
 with (out/'events.jsonl').open('w') as log,(out/'stderr.txt').open('w') as err:
  p=subprocess.Popen(cmd,cwd=work,stdin=subprocess.DEVNULL,stdout=log,stderr=err,start_new_session=True)
  try:rc=p.wait(timeout=240)
  except subprocess.TimeoutExpired:
   timed=True;os.killpg(p.pid,signal.SIGTERM)
   try:rc=p.wait(timeout=8)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
 meta.update(seconds=round(time.monotonic()-start,3),utc_end=utc(),exit_code=rc,timed_out=timed)
 events=[]
 for line in (out/'events.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except json.JSONDecodeError:pass
 meta['usage']=[e.get('usage') for e in events if e.get('type')=='turn.completed']
 meta['errors']=[e for e in events if e.get('type') in ('turn.failed','error')]
 commands=[e.get('item',{}) for e in events if e.get('item',{}).get('type')=='command_execution']
 meta['tool_commands']=commands
 meta['native_read_confirmed']=any('SKILL.md' in str(e.get('command','')) and e.get('exit_code')==0 and NAMES[lab] in str(e.get('command','')) for e in commands) if condition=='S' else None
 meta['success']=rc==0 and not timed and not meta['errors'] and (out/'answer.md').exists() and bool((out/'answer.md').read_text().strip())
 (out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 shutil.rmtree(work)
 print(json.dumps({k:meta[k] for k in ['label','seconds','success','usage','native_read_confirmed','errors']},ensure_ascii=False),flush=True)
 return meta
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--labs',nargs='+',default=['lab1','lab3','lab2']);a=ap.parse_args()
 for lab in a.labs:
  for variant,condition in [('A','P'),('B','S'),('A','S'),('B','P')]:
   m=run(lab,variant,condition,f'{lab}-{variant}-{condition}')
   if not m['success']:
    print('PAID RUN FAILED: not retried; stopping queue for explicit review',flush=True);raise SystemExit(1)
