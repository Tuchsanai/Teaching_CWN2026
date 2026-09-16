"""Additional teaching demonstrations, separate from comparison; cyolo1 only."""
from experiments import run,ROOT,utc
from pathlib import Path
import tempfile,subprocess,json,os,signal,time,shutil
for lab in ['lab1','lab2','lab3']:
 m=run(lab,'C','S',f'{lab}-C-S-transfer')
 if not m['success'] or not m['native_read_confirmed']:raise SystemExit('STOP: no automatic retry')
# Creation demo uses the actual ready learner launcher with pasted natural language.
# No answer key is provided. Learner prompts below are saved in real run logs.
subprocess.run([str(ROOT/'learn'),'prepare','lab3','C','S'],check=True)
create='''สร้าง Skill ใหม่ชื่อ complaint-desk ใน .agents/skills/complaint-desk/SKILL.md ให้ฉัน โดยคุณเป็นคนเขียนไฟล์ ไม่ให้ฉันเขียนโค้ด เป็นคำแนะนำข้อความล้วน ใช้เมื่อจัดคิวและร่างตอบข้อร้องเรียนจาก input.md และ manual.md ต้องตรวจนโยบายที่มีผล อ้าง ID ทุกเคส แยกข้อมูลขาด จัดคิวอันตรายก่อน ส่งข้อยกเว้นให้คน ไม่อนุมัติหรือส่งข้อความเอง มี name description จุดประสงค์ ข้อมูลเข้า ขั้นตอน ผลลัพธ์และรายการตรวจ ห้ามคัดลอกข้อมูลเฉพาะชุด C หรือคำตอบไว้ใน Skill สร้างไฟล์จริงแล้วสรุป path'''
revise='''ปรับ .agents/skills/complaint-desk/SKILL.md จากตัวอย่างข้อบกพร่อง v1 ที่ผู้สอนแต่งว่า ใช้กฎ 7 วันและห้ามเปลี่ยนใจเสมอ ตัวอย่างนี้ไม่ใช่ข้อผิดพลาดที่สังเกตจากการทดลองของคุณ ให้ Skill ตรวจรุ่น วันที่มีผล และขอบเขตจากข้อมูลใหม่ทุกครั้ง ไม่เก็บจำนวนวันตายตัว และถ้านโยบายระดับคิวทับกันให้แยกข้อเท็จจริงกับการประเมินความเสี่ยง ระบุระดับชั่วคราวพร้อมคำถามถึงผู้มีอำนาจ คุณแก้ไฟล์ให้เอง คงการอ้าง ID และห้ามอนุมัติข้อยกเว้น ไม่อ่านเฉลย ไม่ทำงาน C ในรอบนี้'''
rerun='''$complaint-desk อ่าน .agents/skills/complaint-desk/SKILL.md ด้วยเครื่องมืออ่านไฟล์เพื่อยืนยัน native จากนั้นทำ input.md ชุด C กับ manual.md ใช้ข้อมูลชุดนี้เท่านั้น ไม่อ่านคำตอบก่อนหน้า และไม่แก้ไฟล์ ส่งร่างภาษาไทยพร้อม ID'''
import learn
for label,prompt in [('create',create),('improve',revise),('rerun-C',rerun)]:
 state=json.loads(learn.STATE.read_text());w=Path(state['workspace']);out=Path(state['out'])
 for old in w.glob('previous-answer.md'):old.unlink()
 r=subprocess.run([str(ROOT/'learn'),'run','ask'],input=prompt+'\nEND\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 d=json.loads(learn.STATE.read_text());e=ROOT/'evidence/creation'/label;e.mkdir(parents=True,exist_ok=True)
 (e/'launcher-stdout.txt').write_text(r.stdout);(e/'launcher-stderr.txt').write_text(r.stderr)
 for x in Path(d['last']).parent.iterdir():shutil.copy(x,e/x.name)
 if (w/'.agents/skills/complaint-desk/SKILL.md').exists():shutil.copy(w/'.agents/skills/complaint-desk/SKILL.md',e/'SKILL.md')
 print('creation stage',label,'exit',r.returncode,flush=True)
 if r.returncode:raise SystemExit('demo failed, no retry')
subprocess.run([str(ROOT/'learn'),'close'],check=True)
