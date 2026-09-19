from pathlib import Path
from datetime import datetime
import re,json
root=Path.cwd(); dest=root/'labs/prompts/graph';backup=root/'backup'/('graph-copy-labs-'+datetime.now().strftime('%Y%m%dT%H%M%S'));backup.mkdir()
def save(p,text):
 if p.exists():
  target=backup/p.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(p.read_text())
 p.write_text(text)
tp=dest/'graph-template.md';old=tp.read_text();sample=old.split('# TASK GRAPH (กราฟงาน)\n',1)[1].split('\n# EXECUTION RULES',1)[0].strip()
template='''บรรทัดที่ขึ้นต้นด้วย "//" คือคำอธิบายสำหรับผู้เรียน ให้ AI ข้ามบรรทัดเหล่านี้

# ROLE (บทบาท)
คุณเป็นผู้ดำเนินงานตามกราฟ ทำงานแต่ละ Node ตาม Dependency และทำหน้าที่ MERGER ที่ N5 เพื่อตรวจและรวมผล

# GOAL (เป้าหมาย)
ส่งผลงานตาม REQUIREMENT โดยใช้ TASK_GRAPH และตรวจตาม CRITERIA พร้อมหลักฐานจริง

# INPUT PARAMETERS (พารามิเตอร์นำเข้า)

## REQUIREMENT
{{REQUIREMENT}}

## CRITERIA
{{CRITERIA}}

## TASK_GRAPH
{{TASK_GRAPH}}
// REQUIREMENT รวมโจทย์ ข้อมูลต้นทาง และผลงานที่ต้องส่ง
// CRITERIA คือเกณฑ์ตรวจของโจทย์; TASK_GRAPH คือตาราง Node / Task / Depends on / Output
// ใช้ตารางที่ส่งมาแทนตารางตัวอย่าง ไม่สร้างตารางตัวอย่างซ้ำเป็นงานอีกชุด

# EXECUTION RULES (กติกาการทำงาน)
1. ทำ Node เมื่อทุก Dependency มีสถานะ DONE เท่านั้น N1 เริ่มก่อน N2–N4 แล้ว N5 จึงรวมผล
2. N2–N4 ใช้ข้อมูลจาก N1 และ INPUT ร่วมกัน แต่ห้ามเห็นผลของกันและกัน ให้ N1 กำหนดชื่อข้อมูลหรือ interface contract ที่ต้องใช้ร่วมกันก่อนแยกงาน
3. ทุก Node ส่ง data contract: { "node": "N2", "status": "DONE | FAILED", "output": "...", "assumptions": [] }
4. บันทึกสถานะและไฟล์ผลลัพธ์หลังจบแต่ละ Node ตามสิ่งที่เกิดขึ้นจริง การใช้หลายบทบาทไม่ใช่หลักฐานว่ารันขนานหรือมีผู้ทำงานอิสระ หากเครื่องมือแยกบริบทไม่ได้ให้ระบุว่าเป็นการจำลองบทบาท

# CONDITIONAL EDGE (ทางเลือกตามเงื่อนไข)
หาก N1 พบข้อกำหนดขัดแย้ง ให้เพิ่ม N1b เพื่อระบุประเด็นและหลักฐานโดยไม่เลือกข้าง และเพิ่ม N1b เป็น Dependency ของ N5
หากไม่พบข้อขัดแย้ง ไม่ต้องเรียก N1b ข้อมูลที่ยังขาดให้คงเป็นเรื่องรอยืนยัน

# MERGE RULES (N5) (กติกาการรวมผล)
- รับเฉพาะ Node ที่ DONE และส่ง data contract ครบ รวมทั้ง N1b หากถูกเรียกใช้
- ตรวจความสอดคล้องของชื่อข้อมูล กติกา หน้าจอ และแบบจำลองตามชนิดผลงาน หากผลขัดกันให้ใช้หลักฐานจาก INPUT; หลักฐานไม่พอให้คงข้อขัดแย้งโดยไม่แต่งข้อสรุป
- ตรวจผลงานรวมตาม CRITERIA ทีละข้อ ระบุ PASS/FAIL พร้อมหลักฐานหรือตำแหน่งที่ตรวจได้ เกณฑ์ที่มีหลายเงื่อนไขผ่านเมื่อครบทุกเงื่อนไข ไม่มีหลักฐานให้ FAIL
- N5 เป็น DONE เมื่อ Dependency ครบและทุกเกณฑ์ PASS เท่านั้น หากแก้จุดเชื่อมต่อให้ตรวจเกณฑ์ที่ได้รับผลกระทบซ้ำ หากยังไม่ผ่านให้ใช้ FAILURE HANDLING

# FAILURE HANDLING (การจัดการเมื่องานล้มเหลว)
- Node ที่ล้มเหลวลองใหม่ได้อีก 1 ครั้ง รวม N5 โดยต้องระบุสาเหตุและสิ่งที่แก้
- ถ้ายังล้มเหลวให้ FAILED แล้วทำต่อเฉพาะ Node ที่ไม่ขึ้นกับ Node นั้น ห้ามข้าม Dependency เพื่ออ้างว่างานครบ

# CONSTRAINTS (ข้อห้าม)
- ห้ามเปลี่ยนข้อกำหนดหรือเกณฑ์ตรวจที่ผู้เรียกส่งมา
- ห้ามแต่งตัวเลข กติกา หรือข้อมูลยืนยันที่ไม่มีในต้นทาง แยกสมมติฐานและเรื่องรอยืนยันให้ชัด
- ใช้วิธีตรวจสำรองเฉพาะเมื่อ CRITERIA อนุญาต และระบุข้อจำกัดตามจริง

# STOP CONDITION (เงื่อนไขหยุด)
หยุดเมื่อ N5 เป็น DONE หรือเมื่อไม่มี Node ที่ทำต่อได้และสิทธิ์ลองใหม่หมดแล้ว โดยรายงานงานที่ขาดและสาเหตุ

# OUTPUT FORMAT (รูปแบบผลลัพธ์)
1. Execution Trace: | Node | Dependency | สถานะ | ผลลัพธ์/ไฟล์ | หมายเหตุ |
2. ผลตรวจโดย N5: | เกณฑ์ | PASS/FAIL | หลักฐาน/ตำแหน่ง | สิ่งที่ยังขาด |
3. ผลงานตาม REQUIREMENT
4. ข้อขัดแย้ง สมมติฐาน เรื่องรอยืนยัน และข้อจำกัดของเครื่องมือ

# RUN RECORD (การเก็บผลแล็บ)
สร้างโฟลเดอร์ผลรอบใหม่ ไม่เขียนทับตัวอย่างเดิม เก็บ Prompt ที่แทนค่าจริงเป็น prompt-used.md เก็บผลแต่ละ Node และ trace.md พร้อมผลตรวจ/ภาพเมื่อเกณฑ์กำหนด ใช้ชื่อไฟล์ผลงานตาม REQUIREMENT
'''
save(tp,template)
tables={
'1_meeting_room':'''| Node | Task | Depends on | Output |
| --- | --- | --- | --- |
| N1 | วิเคราะห์ห้าฟีเจอร์ เกณฑ์สองคลิก และกำหนดหน้าจอ DOM ID ชื่อฟังก์ชัน ข้อมูลจำลอง และ interface contract ที่ทุกส่วนใช้ร่วมกัน | - | ข้อกำหนด + contract |
| N2 | เขียน JavaScript แสดงห้อง ตรวจเวลาว่าง จอง ยกเลิก และอ่านสถานะตาม contract จาก N1 | N1 | โค้ด JavaScript |
| N3 | เขียน HTML/CSS ตามหน้าจอและ DOM ID ของ N1 โดยไม่อ่านโค้ด N2 | N1 | โค้ด HTML/CSS |
| N4 | เขียน Python Playwright ทดลองห้าฟีเจอร์ ตรวจ console error และนับคลิกเข้าถึงจากหน้าแรกตาม contract ของ N1 | N1 | สคริปต์ทดสอบ |
| N5 | รวมเว็บเป็น output.html รันสคริปต์ N4 จริง ตรวจ C1–C3 และแก้จุดเชื่อมต่อพร้อมตรวจซ้ำ | N2, N3, N4 | output.html + ผลตรวจและหลักฐาน |''',
'2_expense_claim':'''| Node | Task | Depends on | Output |
| --- | --- | --- | --- |
| N1 | สกัด Actors/Stakeholders, FR, NFR, BR และที่มาจากสัมภาษณ์ กำหนด contract ของชื่อ Entity/Attribute สถานะ และผู้รับผิดชอบที่แบบจำลองและ Mockup ต้องใช้ร่วมกัน แยกข้อเสนอที่ยังต้องยืนยัน | - | ข้อกำหนด + contract + หลักฐานต้นทาง |
| N2 | สร้าง Use Case, Sequence ยื่นเบิก–อนุมัติ–จ่ายเงิน และ State ที่ระบุผู้รับผิดชอบ โดยยึด contract จาก N1 | N1 | แผนภาพ Mermaid |
| N3 | สร้าง ERD ตาม Entity/Attribute และความสัมพันธ์ที่ระบุใน contract จาก N1 โดยไม่อ่านผล N2 | N1 | ERD ใน Mermaid |
| N4 | สร้าง Mockup ยื่นเบิก ติดตาม และตรวจ/อนุมัติ พร้อมตาราง Pain Point → FR/BR → หน้าจอ ใช้ข้อมูลจำลองและแสดงนโยบายรอยืนยันตาม N1 | N1 | mockup.html + ตารางเชื่อมหน้าจอ |
| N5 | รวมเอกสารทุกส่วน เพิ่ม Traceability Matrix และ Open Issues ตรวจแบบจำลองกับ ERD และ Mockup แล้วตรวจ C1–C3 | N2, N3, N4 | output.md + mockup.html + ผลตรวจ |''',
'3_clinic_migration':'''| Node | Task | Depends on | Output |
| --- | --- | --- | --- |
| N1 | สำรวจ CSV R1–R5 สร้าง Data Quality Findings (ข้อค้นพบปัญหาคุณภาพข้อมูล) พร้อมแถว ผลกระทบ และความกำกวม กำหนดชื่อข้อมูลกลางและ contract สำหรับระบบใหม่กับแผนย้าย โดยแยกสิ่งที่ต้องยืนยัน | - | ข้อค้นพบ + contract |
| N2 | สร้าง As-Is Process (กระบวนการทำงานปัจจุบัน) ตามบริบทและข้อค้นพบจาก N1 | N1 | แผนภาพ Mermaid |
| N3 | สร้าง To-Be Process (กระบวนการทำงานที่ต้องการในอนาคต), Data Model (แบบจำลองข้อมูล) และ Mockup ตารางนัดหมาย จอง/แก้ไข และตรวจข้อมูลก่อนย้าย ตาม contract และข้อค้นพบจาก N1 | N1 | แผนภาพ Mermaid + mockup.html |
| N4 | สร้าง Data Mapping (การจับคู่ข้อมูลต้นทางกับปลายทาง) และ Migration (การย้ายข้อมูลและระบบ) ตาม contract ของ N1 รวมปรับรูปชื่อ/เบอร์และกรณีให้คนยืนยัน โดยไม่อ่านผล N3 | N1 | ตารางจับคู่ + แผนย้าย |
| N5 | รวมผลงาน จัดทำ Gap Analysis (การวิเคราะห์สิ่งที่ยังขาดเพื่อไปสู่ระบบใหม่), Roll-out Plan (แผนทยอยนำระบบไปใช้งาน) และ Plan Version Log (บันทึกการเปลี่ยนแปลงแผน) ตรวจความสอดคล้องและ C1–C3 ทั้งเอกสารและ Mockup | N2, N3, N4 | output.md + mockup.html + ผลตรวจ |'''
}
names={'1_meeting_room':'จองห้องประชุม','2_expense_claim':'เบิกค่าใช้จ่าย','3_clinic_migration':'คลินิกทันตกรรม'}
blocks=[]
for key,table in tables.items():
 raw=(root/f'labs/prompts/loop/{key}-input.md').read_text(); req,tail=raw.split('\n[C1]\n',1);req=req.removeprefix('[REQUIREMENT]\n').strip()
 c1,tail=tail.split('\n[C2]\n',1);c2,c3=tail.split('\n[C3]\n',1)
 criteria='\n'.join(f'C{i}. '+v.strip().replace('CRITIC','MERGER (N5)') for i,v in enumerate([c1,c2,c3],1))
 if key=='1_meeting_room':req=req.replace('Output: Web UI Mock-up ที่เปิดและทดลองใช้งานได้','Output: output.html เป็น Web UI Mock-up ที่เปิดและทดลองใช้งานได้')
 params='## REQUIREMENT\n'+req+'\n\n## CRITERIA\n'+criteria+'\n\n## TASK_GRAPH\n'+table+'\n'
 run='''ใช้ `labs/prompts/graph/graph-template.md` เป็น Template หลัก หากใช้ไฟล์แนบ ให้ใช้ `graph-template.md` ที่แนบไว้

ส่งพารามิเตอร์ REQUIREMENT, CRITERIA และ TASK_GRAPH ด้านล่างเข้าช่องชื่อเดียวกันใน Template แล้วเริ่มทำงานตามกติกากลาง ใช้ TASK_GRAPH นี้แทนตารางตัวอย่าง

# PARAMETERS

'''+params
 expanded=template.replace('{{REQUIREMENT}}',req).replace('{{CRITERIA}}',criteria).replace('{{TASK_GRAPH}}',table)
 for suffix,value in [('input',params),('run',run),('prompt',expanded)]:save(dest/f'{key}-{suffix}.md',value)
 fence='`````' if '```' in run else '```'
 blocks.append(f'#### 2.3.{len(blocks)+1} โจทย์ {len(blocks)+1}: {names[key]}\n\nคัดลอกบล็อกนี้ทั้งหมด หรือเปิด [Prompt สำหรับคัดลอก](labs/prompts/graph/{key}-run.md)\n\n{fence}text\n{run.rstrip()}\n{fence}\n')
section='''### 2.3 Lab: คัดลอก Prompt แล้วให้ AI ทำงานตาม Graph Template

ใช้ **Template ในข้อ 2.2 เป็นกลไกกลาง** เหมือนวิธีทำแล็บ Loop ในข้อ 1.3 นักศึกษาเลือกโจทย์แล้วคัดลอกทั้งบล็อกได้เลย โดยส่ง 3 พารามิเตอร์: **REQUIREMENT** (โจทย์ ข้อมูล และผลงาน), **CRITERIA** (เกณฑ์ตรวจ) และ **TASK_GRAPH** (ตารางงาน) ส่วนกติกา Dependency การรวมผล การลองใหม่ และเงื่อนไขหยุดใช้จาก Template ไม่ต้องเขียนซ้ำ

Graph ต้องส่งตารางงานเพิ่ม เพราะเว็บจองห้อง เอกสารเบิกค่าใช้จ่าย และแผนย้ายคลินิกแบ่งงานต่างกัน ทั้งสามยังใช้โครงสร้าง N1 → N2/N3/N4 → N5 ตามภาพข้อ 2.1 ชื่องานของ Node เปลี่ยนตามโจทย์

**เตรียมครั้งเดียว:** หากเครื่องมืออ่านไฟล์โปรเจกต์ได้ ให้เปิดโฟลเดอร์ `Basic_AI_WORFLOW` หากใช้แชตทั่วไป ให้ดาวน์โหลด [graph-template.md](labs/prompts/graph/graph-template.md) แล้วแนบในบทสนทนา การพิมพ์ชื่อไฟล์อย่างเดียวไม่ทำให้แชตเข้าถึงไฟล์ได้

เริ่มบทสนทนาใหม่สำหรับแต่ละโจทย์ แล้วทำ **แนบ Template → คัดลอกทั้งบล็อก → ส่งให้ AI → เปิดผลงาน → ตรวจ C1/C2/C3 และ Execution Trace** ใช้เครื่องมือที่สร้างไฟล์และตรวจด้วยเบราว์เซอร์ได้เมื่อเกณฑ์กำหนด

'''+('\n---\n\n'.join(blocks))+'''
#### รับ Output แล้วตรวจอะไร

| โจทย์ | ผลงาน | หลักฐานที่ควรเปิดดู |
| --- | --- | --- |
| จองห้องประชุม | output.html | ทดลองห้าฟีเจอร์ ผล Playwright console error และเส้นทางเข้าถึงไม่เกินสองคลิก |
| เบิกค่าใช้จ่าย | output.md และ mockup.html | ข้อกำหนดย้อนถึงสัมภาษณ์ ข้อขัดแย้งวงเงิน แบบจำลองสอดคล้อง แผนภาพ render และ Mockup สามส่วน |
| คลินิก | output.md และ mockup.html | Findings พร้อมแถว/ผลกระทบ ข้อมูลกำกวม การจับคู่ตัวตน แผนภาพ และ Mockup สามส่วน |

ตรวจ Trace ด้วยว่า N1 เสร็จก่อน N2–N4, ทุก Node ส่ง data contract, N5 รอ Dependency ครบ และมีผลตรวจแต่ละเกณฑ์พร้อมหลักฐาน หากเรียก N1b ต้องเสร็จก่อนรวม หาก Node ล้มเหลวต้องเห็นเหตุผลและจำนวนครั้งที่ลองใหม่ งานที่รันเรียงลำดับหรือจำลองบทบาทต้องรายงานตามจริง ไม่อ้างว่าเกิดการรันขนานจากรูปเพียงอย่างเดียว

**สิ่งที่ส่งท้ายแล็บ:** Prompt ที่ใช้จริง ผลงาน ผลแต่ละ Node, Execution Trace และบันทึกตรวจพร้อมหลักฐาน เก็บรอบใหม่แยกจากผลตัวอย่าง ข้อ 2.4–2.6 เป็นบันทึกประกอบจากการทดลองเดิม ไม่ใช้แทนหลักฐานรอบของตน

โจทย์คลินิกเริ่มจากเฟสแรกก่อน เมื่อเสร็จจึงทดลอง Change Request ตามโจทย์ 3 ในบทสนทนาเดิม ให้ตรวจผลกระทบผ่าน Dependency และปรับทั้งเอกสารกับ Mockup พร้อมเก็บฉบับก่อนเปลี่ยน

<details>
<summary>ดูการจับคู่พารามิเตอร์และไฟล์ประกอบ</summary>

| พารามิเตอร์ | ช่องใน Template 2.2 | หน้าที่ |
| --- | --- | --- |
| REQUIREMENT | `{{REQUIREMENT}}` | โจทย์ ข้อมูลต้นทาง และรายการผลงาน |
| CRITERIA | `{{CRITERIA}}` | เกณฑ์ที่ N5 ใช้ตรวจผลงานรวม |
| TASK_GRAPH | `{{TASK_GRAPH}}` | งาน Dependency และ Output ของแต่ละ Node |

'''
for key,name in names.items():section+=f'- {name}: [ข้อมูลแยกส่วน](labs/prompts/graph/{key}-input.md) · [Template ที่แทนค่าแล้ว](labs/prompts/graph/{key}-prompt.md)\n'
section+='\n</details>\n\n'
p=root/'readme.md';s=p.read_text();a=s.index('### 2.2 Prompt Template');b=s.index('### 2.3 ',a)
sec22='''### 2.2 Prompt Template สำหรับ Graph

Template กลางรับโจทย์ เกณฑ์ตรวจ และตารางงานเป็นพารามิเตอร์ แล้วกำกับการทำงานตาม Dependency และตรวจตอนรวมผล ข้อ 2.3 มีบล็อกพร้อมคัดลอกสำหรับทั้งสามโจทย์

[เปิด Template เป็นไฟล์ Markdown](labs/prompts/graph/graph-template.md)

```text
'''+template.rstrip()+'''\n```

<details>
<summary>ตัวอย่างค่า TASK_GRAPH ที่ใช้ประกอบภาพข้อ 2.1</summary>

'''+sample.split('//')[0].strip()+'''

ตารางนี้อธิบายบทบาทในภาพ เมื่อทำแล็บให้ใช้ TASK_GRAPH ของโจทย์ที่เลือกจากข้อ 2.3 แทนตารางนี้ โครงสร้างการส่งงานยังเป็น N1 → N2–N4 → N5 และมี N1b เมื่อพบข้อขัดแย้ง

</details>

'''
s=s[:a]+sec22+s[b:];a=s.index('### 2.3 ');b=s.index('### 2.4 ',a);s=s[:a]+section+s[b:]
s=s.replace('Graph Prompt Template','Template, Prompt พร้อมใช้ และไฟล์ประกอบแล็บ Graph')
s=s.replace('| Graph | [graph-template.md](labs/prompts/graph/graph-template.md) | 2.2 |','| Graph | [graph-template.md](labs/prompts/graph/graph-template.md) | 2.2–2.3 |')
for heading in ['### 2.4 เติม Prompt สำหรับโจทย์ 1: จองห้องประชุม','### 2.5 เติม Prompt สำหรับโจทย์ 2: เบิกค่าใช้จ่าย','### 2.6 เติม Prompt สำหรับโจทย์ 3: ย้ายระบบคลินิก']:
 assert heading in s
 s=s.replace(heading+'\n',heading+'\n\n> เริ่มทำแล็บด้วย Prompt พร้อมคัดลอกในข้อ 2.3 ซึ่งใช้ Template กลางล่าสุด ส่วนด้านล่างเป็นตัวอย่างและบันทึกการทดลองเดิม\n',1)
save(p,s)
report={'template_placeholders':re.findall(r'\{\{(\w+)\}\}',template),'cases':{}}
for key in tables:
 run=(dest/f'{key}-run.md').read_text();expanded=(dest/f'{key}-prompt.md').read_text()
 assert run.rstrip() in s
 assert not re.search(r'\{\{\w+\}\}',expanded)
 assert all('C'+str(i)+'.' in run for i in [1,2,3])
 assert all('| '+n+' |' in run for n in ['N1','N2','N3','N4','N5'])
 report['cases'][key]={'readme_matches_run':True,'expanded_prompt_complete':True,'criteria_and_nodes_present':True}
for link in re.findall(r'\[[^\]]*\]\((labs/prompts/graph/[^)]+)\)',s):assert (root/link).is_file(),link
assert template.rstrip() in s
(root/'work/graph-copy-labs-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
