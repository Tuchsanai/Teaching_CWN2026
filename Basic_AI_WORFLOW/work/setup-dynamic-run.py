from pathlib import Path
from datetime import datetime,timezone
import json,re
root=Path.cwd();out=Path('work/dynamic-current-run.txt').read_text();out=Path(out);out.mkdir(parents=True,exist_ok=True);Path('work/dynamic-current-run.txt').write_text(str(out));src=out/'source';src.mkdir(exist_ok=True)
for f in ['common.py','meeting.py','expense.py','clinic.py','clinic-phase2.py','verify-docs.py','render-docs.py','phase1-complete.py']:
 s=(Path('work/graph-rerun')/f).read_text()
 s=s.replace('work/graph-current-run.txt','work/dynamic-current-run.txt').replace('nodes/','tasks/').replace('Graph','Dynamic').replace('GRAPH','DYNAMIC').replace('graphD','dynamicD')
 s=re.sub(r'\bN([1-5])',r'T\1',s).replace('Node','Task').replace('node(p,','task(p,')
 s=s.replace('รอบแรกไม่เรียก T1b เพราะเป็นความกำกวมของข้อมูลที่คงรอยืนยัน ไม่ใช่ข้อกำหนดธุรกิจขัดกัน','Plan v1 มีงานตรวจคุณภาพข้อมูลและรายการรอยืนยันอยู่แล้ว จึงไม่ต้องปรับแผนในเฟสแรก')
 if f=='common.py':s=s[s.index('CSS='):];s='from engine import *\nfrom html import escape\n'+s
 (src/f).write_text(s)
info={'created_utc':datetime.now(timezone.utc).isoformat(),'mode':'single-conversation Planner/Executor/Evaluator role simulation; not independent model calls','template':'labs/prompts/dynamic/dynamic-template.md','source_reuse':'Application/document generator and verifier source adapted from Graph run-2026-09-17-090820; this is a controlled demonstration with known solutions, not a blind independent workflow benchmark. Outputs rendered and tests executed anew. No prior screenshots or PASS logs copied.'}
(out/'run-info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
plans={
'1_meeting_room':[('T1','วิเคราะห์ข้อกำหนดและกำหนดหน้าจอ/ข้อมูล',[]),('T2','เขียนตรรกะจองและยกเลิก',['T1']),('T3','สร้าง HTML/CSS',['T1']),('T4','เขียนสคริปต์ตรวจห้าฟีเจอร์และจำนวนคลิก',['T1']),('T5','รวมเว็บ รันทดสอบและประเมิน C1–C3',['T2','T3','T4'])],
'2_expense_claim':[('T1','สกัดข้อกำหนดจากบทสัมภาษณ์',['']),('T2','สร้าง Use Case/Sequence/State',['T1']),('T3','สร้าง ERD',['T1']),('T4','สร้าง Mockup สามส่วนและตาราง Pain Point',['T1']),('T5','รวมเอกสารและตรวจ C1–C3',['T2','T3','T4'])],
'3_clinic_migration':[('T1','ตรวจคุณภาพข้อมูลและระบุรายการรอยืนยัน',[]),('T2','อธิบาย As-Is',['T1']),('T3','ออกแบบ To-Be/Data Model/Mockup',['T1']),('T4','ทำ Data Mapping และแผน Migration',['T1']),('T5','รวม Gap/Roll-out และตรวจ C1–C3',['T2','T3','T4'])]}
for key,tasks in plans.items():
 p=out/key;(p/'tasks').mkdir(parents=True);(p/'plans').mkdir();(p/'events.jsonl').write_text('')
 for suffix,target in [('prompt','prompt-used.md'),('input','input-used.md')]: (p/target).write_text(Path(f'labs/prompts/dynamic/{key}-{suffix}.md').read_text())
 plan={'version':1,'replans':0,'tasks':{t:{'description':d,'dependencies':[x for x in deps if x],'status':'TODO'} for t,d,deps in tasks},'reason':'เริ่มจากโจทย์และ C1–C3','changes':'สร้างแผนเริ่มต้น','impact':[],'reuse':[]}
 (p/'plan-current.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));(p/'plans/plan-v1-initial.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
 (p/'trace.md').write_text('# Dynamic execution trace\n\n'+info['mode']+'\n\n'+info['source_reuse']+'\n\nPlan v1 ถูกบันทึกก่อนเริ่มงาน ทุกงานตรวจ Dependency และ Evaluator ประเมินระหว่างทำ\n\n')
print(out)
