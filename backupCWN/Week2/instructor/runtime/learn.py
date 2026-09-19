#!/usr/bin/env python3
"""Ready no-code learner launcher. Instructor provisions Python and logged-in cyolo1."""
import argparse,datetime,json,os,re,shutil,signal,subprocess,tempfile,time,hashlib
from pathlib import Path
from lab_paths import LAB_DIRS
from lab_content import read_section, read_dataset
ROOT=Path(__file__).resolve().parents[2]
STATE=Path(tempfile.gettempdir())/('week2-learner-'+hashlib.sha256(str(ROOT).encode()).hexdigest()[:10]+'.json')
NAMES={'lab1':'shop-requirements','lab2':'shop-recovery','lab3':'shop-complaints'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def prepare(lab,variant,cond):
 work=Path(tempfile.mkdtemp(prefix='week2-learner-input-'));subprocess.run(['git','init','-q',str(work)],check=True)
 (work/'input.md').write_text(read_dataset(ROOT,lab,variant))
 (work/'manual.md').write_text(read_section(ROOT,lab,'manual'))
 if cond=='S':shutil.copytree(ROOT/f'.agents/skills/{NAMES[lab]}',work/f'.agents/skills/{NAMES[lab]}')
 out=ROOT/'learner-results'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f');out.mkdir(parents=True)
 d={'lab':lab,'variant':variant,'condition':cond,'workspace':str(work),'out':str(out),'n':0};STATE.write_text(json.dumps(d))
 print('READY',lab,variant,cond,'\nWORKSPACE',work,'\nRESULTS',out,'\nใช้ ./learn run start หรือ ./learn inspect โดยไม่แก้ไฟล์ใด')
def execute(d,stage):
 work=Path(d['workspace']);out=Path(d['out']);n=d['n']+1;run=out/f'{n:02}-{stage}';run.mkdir()
 blocks=re.findall(r'```text\n(.*?)\n```',read_section(ROOT,d['lab'],'prompts'),re.S)
 if stage=='ask':
  print('วางคำขอภาษาคน แล้วพิมพ์ END เป็นบรรทัดสุดท้าย:');lines=[]
  while True:
   line=input()
   if line=='END':break
   lines.append(line)
  prompt='\n'.join(lines)
 else:
  prompt=blocks[(0 if d['condition']=='P' else 1) if stage=='start' else {'analyze':2,'revise':3,'verify':4}[stage]]
  if stage!='start':
   if not d.get('last'):raise SystemExit('ต้อง run start ก่อน')
   shutil.copy(d['last'],work/'previous-answer.md');prompt+='\nอ่าน previous-answer.md เป็นร่างก่อนหน้าเพื่อทบทวนกับ input.md และ manual.md'
 if d['condition']=='S':
  if not re.search(r'\$[a-z][a-z-]*',prompt):prompt='$'+NAMES[d['lab']]+' '+prompt
  selected=re.search(r'\$([a-z][a-z-]*)',prompt).group(1)
  prompt+='\nยืนยันการใช้ native Skill โดยอ่าน .agents/skills/'+selected+'/SKILL.md ด้วยเครื่องมืออ่านไฟล์ก่อนทำงาน'
 prompt+='\nใช้เฉพาะไฟล์ในโฟลเดอร์นี้ ห้ามอ่านเฉลยหรือผลรอบอื่น ห้ามใช้เว็บหรือ subagents ผู้เรียนไม่เขียนโค้ด หากขอสร้างหรือปรับ Skill ให้ AI เขียนเฉพาะไฟล์ Skill ที่ระบุเอง ไม่แก้ runtime และไม่ส่งข้อความภายนอก'
 (run/'prompt.txt').write_text(prompt)
 cmd=['cyolo1','exec','-m','gpt-6-astra','-c','model_reasoning_effort="high"','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--ephemeral','-c','project_doc_max_bytes=0','-c','features.multi_agent=false','--json','-o',str(run/'answer.md'),prompt]
 print('กำลังเรียก cyolo1 gpt-6-astra high; deadline 240s; ไม่ retry อัตโนมัติ',flush=True)
 meta={'utc_start':utc(),'command_argv':cmd,'stdin':'/dev/null','workspace':str(work),'stage':stage};t=time.monotonic();timed=False
 with (run/'events.jsonl').open('w') as log,(run/'stderr.txt').open('w') as err:
  p=subprocess.Popen(cmd,cwd=work,stdin=subprocess.DEVNULL,stdout=log,stderr=err,start_new_session=True)
  try:rc=p.wait(timeout=240)
  except subprocess.TimeoutExpired:
   timed=True;os.killpg(p.pid,signal.SIGTERM)
   try:rc=p.wait(timeout=8)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
 events=[]
 for line in (run/'events.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except:pass
 meta.update(seconds=round(time.monotonic()-t,3),utc_end=utc(),exit_code=rc,timed_out=timed,usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'],errors=[e for e in events if e.get('type') in ['turn.failed','error']])
 (run/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));d['n']=n
 if (run/'answer.md').exists():d['last']=str(run/'answer.md');print((run/'answer.md').read_text())
 STATE.write_text(json.dumps(d));print('หลักฐาน',run)
 if rc or timed or meta['errors']:raise SystemExit('รอบล้มเหลว เก็บหลักฐานแล้ว ไม่เรียกซ้ำอัตโนมัติ')
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
 p=sub.add_parser('prepare');p.add_argument('lab',choices=NAMES);p.add_argument('variant',choices=['A','B','C']);p.add_argument('condition',choices=['P','S'])
 p=sub.add_parser('run');p.add_argument('stage',choices=['start','analyze','revise','verify','ask'])
 sub.add_parser('inspect');sub.add_parser('close');a=ap.parse_args()
 if a.cmd=='prepare':prepare(a.lab,a.variant,a.condition);return
 if not STATE.exists():raise SystemExit('ใช้ ./learn prepare ก่อน')
 d=json.loads(STATE.read_text());work=Path(d['workspace'])
 if a.cmd=='inspect':
  print(json.dumps(d,ensure_ascii=False,indent=2))
  print('Native skills:',[str(p.relative_to(work)) for p in work.glob('.agents/skills/*/SKILL.md')]);return
 if a.cmd=='close':
  if work.name.startswith('week2-learner-input-') and work.parent==Path(tempfile.gettempdir()):shutil.rmtree(work,ignore_errors=True)
  STATE.unlink();print('CLOSED; เก็บ learner-results ไว้');return
 execute(d,a.stage)
if __name__=='__main__':main()
