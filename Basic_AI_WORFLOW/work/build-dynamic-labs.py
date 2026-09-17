from pathlib import Path
root=Path('labs/prompts/dynamic');template=(root/'dynamic-template.md').read_text()
intro='''### 3.3 Lab: คัดลอก Prompt แล้วให้ AI ทำงานตาม Dynamic Template

ใช้ **Template ในข้อ 3.2 เป็นกลไกกลาง** เหมือนวิธีทำแล็บในข้อ 1.3 และ 2.3 โดยส่ง **REQUIREMENT** (โจทย์ ข้อมูล ผลงาน และเกณฑ์ C1–C3) กับ **CHANGE_REQUEST_OR_NONE** (ข้อมูลใหม่; รอบแรกใส่ NONE) ไม่ต้องกำหนดตารางงานตายตัว ให้ PLANNER สร้างแผนตามโจทย์และให้ EVALUATOR ใช้เกณฑ์เดียวกันตรวจผล

Template นี้มีช่องข้อมูลสองช่อง จึงใส่เกณฑ์ตรวจไว้ภายใน REQUIREMENT ไม่ใช่เพิ่มช่อง CRITERIA ที่ไม่มีใน Template กติกาการเลือกงาน การปรับแผนสูงสุด 3 ครั้ง และเงื่อนไขหยุดใช้ตามข้อ 3.2

**เตรียมครั้งเดียว:** หากเครื่องมืออ่านไฟล์โปรเจกต์ได้ ให้เปิดโฟลเดอร์ `Basic_AI_WORFLOW` หากใช้แชตทั่วไป ให้ดาวน์โหลด [dynamic-template.md](labs/prompts/dynamic/dynamic-template.md) แล้วแนบในบทสนทนา การพิมพ์ชื่อไฟล์อย่างเดียวไม่ทำให้แชตเข้าถึงไฟล์ได้ หรือใช้ Prompt ฉบับรวม Template ของแต่ละโจทย์ด้านล่าง

เริ่มบทสนทนาใหม่สำหรับแต่ละโจทย์ แล้วทำ **แนบ Template → คัดลอกทั้งบล็อก → ส่งให้ AI → เปิดผลงาน → ตรวจ C1/C2/C3 และบันทึกแผน** ใช้เครื่องมือสร้างไฟล์และเปิดเบราว์เซอร์เมื่อเกณฑ์กำหนด หากไม่มีเครื่องมือให้รายงานสิ่งที่ยังตรวจไม่ได้ ไม่อ้างผลทดสอบที่ไม่ได้รันจริง

'''
header='''ใช้ `labs/prompts/dynamic/dynamic-template.md` เป็น Template หลัก หากใช้ไฟล์แนบ ให้ใช้ `dynamic-template.md` ที่แนบไว้

แทนค่า REQUIREMENT และ CHANGE_REQUEST_OR_NONE ลงในช่องชื่อเดียวกันของ Template แล้วเริ่มทำงานตามกติกากลาง ให้ PLANNER นำเกณฑ์ C1–C3 ไปวางแผน และ EVALUATOR ตรวจด้วยเกณฑ์เดียวกัน เก็บบันทึกแผน บันทึกการทำงาน ผลตรวจ และหลักฐานจริง ไม่จำเป็นต้อง Re-plan หากแผนเดิมยังเหมาะสม

# PARAMETERS

'''
section=intro
for i,(name,title) in enumerate([('1_meeting_room','จองห้องประชุม'),('2_expense_claim','เบิกค่าใช้จ่าย'),('3_clinic_migration','คลินิกทันตกรรม')],1):
 original=Path('labs/prompts/graph/'+name+'-input.md').read_text().split('## TASK_GRAPH')[0].strip()
 requirement=original.removeprefix('## REQUIREMENT\n').replace('## CRITERIA','### เกณฑ์ตรวจ C1–C3').replace('MERGER (N5)','EVALUATOR')
 params='## REQUIREMENT\n'+requirement+'\n\n## CHANGE_REQUEST_OR_NONE\nNONE\n'
 run=header+params
 (root/(name+'-input.md')).write_text(params)
 (root/(name+'-run.md')).write_text(run)
 expanded=template.replace('{{REQUIREMENT}}',requirement).replace('{{CHANGE_REQUEST_OR_NONE}}','NONE')
 (root/(name+'-prompt.md')).write_text(expanded)
 section+=f'---\n\n#### 3.3.{i} โจทย์ {i}: {title}\n\nคัดลอกบล็อกนี้ทั้งหมด หรือเปิด [Prompt สำหรับคัดลอก](labs/prompts/dynamic/{name}-run.md) · [ฉบับรวม Template พร้อมใช้](labs/prompts/dynamic/{name}-prompt.md)\n\n````text\n{run}````\n\n'
change='''ทำต่อในบทสนทนาเดิมโดยใช้ Dynamic Template เดิม เก็บ Plan และผลงานเฟสแรกไว้เป็นหลักฐาน ไม่เริ่มโจทย์ใหม่จากศูนย์

# NEW INFORMATION
เจ้าของคลินิกแจ้งเพิ่ม:
1. ต้องเก็บความยินยอมของคนไข้ตาม PDPA
2. คนไข้ต้องจองคิวเองผ่าน LINE OA ได้

ปรับทั้ง output.md และ mockup.html โดยเพิ่มส่วนบันทึกความยินยอมและหน้าจำลองการจองเองผ่าน LINE OA ไม่เชื่อมบริการจริง ระบุเรื่องนโยบายที่ยังต้องยืนยัน

ให้ EVALUATOR ประเมินผลกระทบจากข้อกำหนดใหม่ และ PLANNER ปรับแผนตาม RE-PLAN RULES ระบุเหตุผล สิ่งที่เปลี่ยน Impact analysis (งานและผลงานที่ได้รับผลกระทบ) และ Reuse (ผลงานเดิมที่ใช้ต่อได้) ทำงาน DONE ซ้ำเฉพาะส่วนที่มีผลกระทบรองรับ นับจำนวน Re-plan ต่อจากรอบก่อน ไม่เริ่มนับใหม่

ใช้ C1–C3 เดิมและตรวจขอบเขตใหม่เพิ่ม: เอกสารและ Mockup มีส่วนความยินยอมและการจองผ่าน LINE OA จำลองที่สอดคล้องกัน เปิดดูได้ มีป้ายข้อมูลจำลอง เก็บภาพและผลตรวจจริง พร้อมบันทึกเวอร์ชันแผนและการตัดสินของ EVALUATOR ถ้าถึงขีดจำกัด Re-plan ให้หยุดและรายงานสิ่งที่ยังตัดสินใจไม่ได้
'''
(root/'3_clinic_migration-change-request.md').write_text(change)
section+='''##### ส่ง Change Request หลังได้แผนและผลงานเฟสแรก

ส่งบล็อกนี้ **ในบทสนทนาเดิมของโจทย์ 3** หลังตรวจและเก็บผลงานเฟสแรกแล้ว ข้อมูลนี้ทำหน้าที่เป็น NEW INFORMATION ของ Template ไม่ใช่โจทย์ใหม่ เพื่อให้เห็นผลกระทบและการใช้ผลงานเดิมต่อ

[เปิด Prompt สำหรับ Change Request](labs/prompts/dynamic/3_clinic_migration-change-request.md)

```text
'''+change+'''```

#### รับ Output แล้วตรวจอะไร

- มี Plan v1 พร้อมงาน Dependency และสถานะ โดยทำ TODO เมื่อ Dependency เสร็จแล้วเท่านั้น
- มีบันทึกการทำงานและคำตัดสินของ EVALUATOR พร้อมหลักฐานตรวจ C1–C3 และเปิดผลงานที่ส่งได้จริง
- หากปรับแผน มีเหตุที่ตรงกับ Trigger พร้อมสิ่งที่เปลี่ยน Impact และ Reuse ไม่บังคับสร้าง v2 เพื่อให้ดูเหมือนมี Dynamic
- โจทย์คลินิกเก็บผลงานก่อนและหลัง Change Request เพื่อเทียบส่วนที่เปลี่ยนและส่วนที่ใช้ต่อ หากถึงขีดจำกัดให้แสดงข้อค้างแทนการอ้างว่าผ่าน

ส่วนนี้เป็น Prompt สำหรับเริ่มแล็บ ยังไม่ใช่ผลการรันหรือหลักฐานว่าทั้งสามโจทย์ผ่านแล้ว
'''
p=Path('readme.md');s=p.read_text();assert '### 3.3 ' not in s;p.write_text(s.rstrip()+'\n\n'+section)
for name in ['1_meeting_room','2_expense_claim','3_clinic_migration']:
 run=(root/(name+'-run.md')).read_text();assert run in section
 expanded=(root/(name+'-prompt.md')).read_text();assert '{{' not in expanded and 'TASK_GRAPH' not in expanded and 'MERGER' not in expanded
for i in range(1,4):assert f'#### 3.3.{i} ' in section
print('Added section 3.3 with three copy-ready labs, 9 input/run/expanded files and clinic follow-up. Checked template substitution and README consistency.')
