from pathlib import Path
import re
p=Path('readme.md');s=p.read_text()
common='''**ตัวแปรที่ส่งจากโจทย์ไปยัง Template คืออะไร?** ในบทนี้เรียกว่า **Input Parameter (พารามิเตอร์นำเข้า)** ส่วน `{{ชื่อ}}` คือ **Placeholder (ช่องรอแทนค่า)** ไม่ใช่ Random Variable (ตัวแปรสุ่มทางสถิติ) ค่าที่ส่งคือข้อความจากโจทย์ที่เลือก ไม่ได้สุ่มค่า

ค้นหาหัวข้อ `# PARAMETERS` ในบล็อกของโจทย์ด้านล่าง แล้วนำข้อความใต้หัวข้อชื่อเดียวกันไปแทนช่อง `{{...}}` ของ Template โดยแทนทั้งช่องรวมวงเล็บปีกกา ไม่ส่งชื่อช่องเปล่า ๆ

'''
rows={
'1.3':('loop',[('REQUIREMENT','โจทย์ ข้อมูลต้นทาง ฟีเจอร์ และผลงานที่ต้องส่ง','INPUT PARAMETERS → REQUIREMENT'),('CRITERIA','เกณฑ์ตรวจ C1–C3 ของโจทย์นั้น','INPUT PARAMETERS → CRITERIA')],'ตัวอย่างโจทย์ 1: ข้อความ “สร้างเว็บไซต์สำหรับระบบจองห้องประชุม” พร้อมห้าฟีเจอร์และชื่อไฟล์ผลงานอยู่ใน REQUIREMENT ส่วนเงื่อนไขเปิดเว็บได้ ทดสอบฟีเจอร์ และจำนวนคลิกอยู่ใน CRITERIA'),
'2.3':('graph',[('REQUIREMENT','โจทย์ ข้อมูลต้นทาง และผลงานที่ต้องส่ง','INPUT PARAMETERS → REQUIREMENT'),('CRITERIA','เกณฑ์ตรวจ C1–C3 ของโจทย์นั้น','INPUT PARAMETERS → CRITERIA'),('TASK_GRAPH','ตาราง Node / Task / Depends on / Output ที่เตรียมไว้สำหรับโจทย์นั้น','INPUT PARAMETERS → TASK_GRAPH')],'ตัวอย่างโจทย์ 1: REQUIREMENT คือเว็บจองห้อง, CRITERIA คือเกณฑ์ตรวจเว็บ และ TASK_GRAPH คือตาราง N1–N5 สำหรับวิเคราะห์ เขียนเว็บ ทดสอบ และรวมงาน คัดลอกตารางของโจทย์ที่เลือกทั้งตาราง'),
'3.3':('dynamic',[('REQUIREMENT','โจทย์ ข้อมูล ผลงาน และหัวข้อเกณฑ์ตรวจ C1–C3 ที่อยู่ภายใน REQUIREMENT','INPUT (ข้อมูลนำเข้า)'),('CHANGE_REQUEST_OR_NONE','รอบแรกใส่ NONE; เมื่อมีข้อมูลใหม่ใช้ข้อความ Change Request','NEW INFORMATION (ข้อมูลใหม่)')],'ตัวอย่างโจทย์ 3: รอบแรกส่งข้อมูลคลินิก CSV ผลงาน Mockup และ C1–C3 ทั้งหมดใน REQUIREMENT พร้อมค่า NONE อีกช่อง เมื่อได้ผลงานเฟสแรกจึงส่งบล็อก Change Request ในบทสนทนาเดิมเป็น NEW INFORMATION ไม่ต้องเริ่มแผนใหม่จากศูนย์')}
for number,(kind,items,example) in rows.items():
 table='| พารามิเตอร์ในบล็อกโจทย์ | ค่าที่ต้องส่ง | ช่องที่แทนค่าใน Template | อยู่ใต้หัวข้อ |\n| --- | --- | --- | --- |\n'
 template=Path(f'labs/prompts/{kind}/{kind}-template.md').read_text()
 for name,meaning,location in items:
  slot='{{'+name+'}}';assert slot in template
  table+=f'| `{name}` | {meaning} | `{slot}` | {location} |\n'
 a=s.index('### '+number+' ');at=s.index('**เตรียมครั้งเดียว:**',a)
 s=s[:at]+common+table+'\n'+example+'\n\n'+s[at:]
p.write_text(s)
assert s.count('**ตัวแปรที่ส่งจากโจทย์ไปยัง Template คืออะไร?**')==3
print('Added parameter definitions and exact source-to-template mapping tables in 1.3, 2.3, 3.3; all 7 mappings match actual template placeholders.')
q=Path('work/publish-dynamic-cleanup.py').read_text().replace('docs: remove obsolete Dynamic examples and learning outcomes','docs: explain input parameter mappings in all three workflow labs');Path('work/publish-parameter-guides.py').write_text(q)
