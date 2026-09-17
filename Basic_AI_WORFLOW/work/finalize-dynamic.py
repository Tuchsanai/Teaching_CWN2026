from pathlib import Path
import sys,json,hashlib,runpy
r=Path(Path('work/dynamic-current-run.txt').read_text());sys.path.insert(0,str(r/'source'))
from engine import *
p=case('3_clinic_migration');v=json.loads((p/'verification-phase2.json').read_text());assert v['automated_pass']
review='''# EVALUATOR — คลินิกหลัง Change Request

C1 ผ่าน: เอกสารหกส่วนยังอยู่ เพิ่มกระบวนการความยินยอมและจอง LINE; Mockup มี appointments, booking, review, consent และ line-booking
C2 ผ่าน: Findings ยังคงเก้าประเภทพร้อมแถว R1–R5 ไม่ตัดสินวัน/ปี/ตัวตนที่กำกวม ข้อมูลต้นทางและ Findings ไม่ถูกเขียนใหม่ในเฟสสอง
C3 ผ่าน: วิธี normalization และ manual review ยังคงอยู่ เพิ่ม Mapping ของ ConsentRecord/LineIdentity/BookingRequest แผนภาพห้าบล็อก render จริง; Mockup เปิดจริงทั้ง desktop/mobile ไม่มี page error หรือ body overflow; consent ไม่ติ๊กล่วงหน้าและ LINE มีป้ายจำลอง
Plan v2 อ้าง NEW INFORMATION มีเหตุผล Changes/Impact/Reuse ครบ; T2 As-Is ใช้ไฟล์เดิมและมี event ทำงานเพียงครั้งเดียว; จำนวน Re-plan = 1 จากสูงสุด 3
ข้อจำกัด: บทบาทจำลองในบทสนทนาเดียว ใช้โค้ดตัวอย่างและตัวตรวจจาก Graph เป็นฐาน ไม่ใช่การทดลองอิสระแบบไม่รู้คำตอบ ปุ่ม Mockup ไม่เชื่อมธุรกรรมจริง การออกแบบความยินยอมไม่ใช่การรับรองข้อกฎหมาย
'''
task(p,'T5-v2',['T2','T3-v2','T4-v2'],{'tasks/T5-v2-review.md':review})
v.update(criteria={'C1':'PASS','C2':'PASS','C3':'PASS'},semantic_review='tasks/T5-v2-review.md');(p/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
audit={}
for p in sorted(r.glob('[123]_*')):
 plan=readplan(p);assert all(t['status'] in ['DONE','DROPPED'] for t in plan['tasks'].values());assert plan['replans']<=3
 ev=[json.loads(x) for x in (p/'events.jsonl').read_text().splitlines()];done=set();evaluated=[];rows=['# บันทึกการทำงาน','','| ขั้นตอน | งาน | แผน | ผลลัพธ์ | การตัดสินของ EVALUATOR |','| --- | --- | --- | --- | --- |']
 for i,e in enumerate(ev):
  if e.get('role')=='EXECUTOR':
   assert set(e['depends_on'])<=done;assert e['task'] not in done
   for name,h in e['sha256'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,(p,name)
   done.add(e['task']);n=ev[i+1];assert n['role']=='EVALUATOR' and n['after_task']==e['task'];evaluated.append(e['task'])
   rows.append(f"| {len(done)} | {e['task']} | v{e['plan_version']} | {', '.join(e['output'])} | {n['decision']} |")
 (p/'execution-table.md').write_text('\n'.join(rows)+'\n')
 with (p/'trace.md').open('a') as f:f.write('\n## STOP\n\nทุกงาน DONE และ EVALUATOR ยืนยัน C1–C3 ของขอบเขตสุดท้ายตามผลตรวจจริง จำนวน Re-plan: '+str(plan['replans'])+'\n')
 log(p,{'role':'EVALUATOR','event':'STOP','goal_met':True,'all_tasks_done':True,'replans':plan['replans'],'criteria_file':'verification.json'})
 audit[p.name]={'dependency_order_valid':True,'all_tasks_done':True,'no_duplicate_execution':True,'artifact_hashes_valid':True,'evaluation_after_every_task':True,'replans':plan['replans'],'plan_version':plan['version'],'independent_model_calls':False}
 (p/'response.md').write_text('# ผลการทดลอง Dynamic\n\n'+(p/'plan-current.md').read_text()+'\n'+(p/'execution-table.md').read_text()+'\nผลตรวจ: [verification.json](verification.json)\n')
(r/'dependency-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
runpy.run_path(str(r/'source/render-docs.py'),run_name='__main__')
print('Final criteria and Dynamic plan/dependency/hash audit PASS')
