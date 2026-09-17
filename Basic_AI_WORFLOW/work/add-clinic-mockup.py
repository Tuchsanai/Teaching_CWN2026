from pathlib import Path
from datetime import datetime
root=Path('.')
stamp=datetime.now().strftime('%Y%m%dT%H%M%S')
backup=root/'backup'/('clinic-mockup-'+stamp); backup.mkdir()
p=root/'readme.md'; s=p.read_text()
contract='''Output: ส่ง 2 ไฟล์ ได้แก่ output.md สำหรับเอกสารและแผนภาพ Mermaid และ mockup.html สำหรับ Web UI Mockup ด้วย HTML/CSS
Mockup เฟสแรกมี 3 หน้าหรือส่วน: (1) ตารางนัดหมายกลาง แสดงสาขา วันที่ เวลา หมอ บริการ และสถานะ (2) ฟอร์มจอง/แก้ไขนัดหมาย พร้อมตัวอย่างคำเตือนเวลาชนกัน (3) ตรวจข้อมูลก่อนย้าย แสดงข้อมูลซ้ำ ข้อมูลขาด วันที่กำกวม และรายการรอคนยืนยัน
ใช้ข้อมูลจำลองพร้อมป้ายกำกับ โดยหน้าจอและชื่อข้อมูลต้องสอดคล้องกับ To-Be, Data Model และ Data Quality Findings ไม่ตัดสินข้อมูลกำกวมหรือรวมตัวตนเอง ปุ่มเป็นภาพจำลองได้ ไม่ต้องมี backend หรือย้ายข้อมูลจริง
เกณฑ์ตรวจ Mockup: เปิดในเบราว์เซอร์ได้ เห็นครบ 3 ส่วน ข้อมูล/สถานะสอดคล้องกับเอกสาร และแสดงรายการรอยืนยันชัดเจน บันทึกผลตรวจพร้อมภาพหลักฐาน ไม่บังคับทดสอบธุรกรรมจริง
'''.strip()
old='Output: Markdown ไฟล์เดียว (diagram เป็น Mermaid)'
# This exact standalone output line occurs only in the three clinic examples.
assert sum(line==old for line in s.splitlines())==3
s=s.replace(old+'\n',contract+'\n')
s=s.replace('ผลวิเคราะห์และแผนย้ายระบบ พร้อมรับความต้องการใหม่ |','ผลวิเคราะห์ แผนย้ายระบบ และ Web UI Mockup พร้อมรับความต้องการใหม่ |')
s=s.replace('6. Plan Version Log\n```','6. Plan Version Log\n7. Web UI Mockup (mockup.html)\n```',1)
s=s.replace('ส่งมอบงานรอบแรกครบทั้ง 6 รายการที่ระบุในโจทย์','ส่งมอบงานรอบแรกครบทั้ง 7 รายการ: เอกสาร output.md และ Web UI Mockup ใน mockup.html',1)
a=s.index('### โจทย์ 3 —'); b=s.index('## วิธีเรียน',a)
chunk=s[a:b]
marker='เกณฑ์เรื่องเวอร์ชันแผน'
idx=chunk.index(marker)
chunk=chunk[:idx]+'''#### Web UI Mockup ของระบบคลินิก

ส่ง `mockup.html` เพิ่มจากเอกสาร `output.md` ใช้ HTML/CSS และข้อมูลจำลอง มี 3 หน้าหรือส่วน:

| หน้าหรือส่วน | สิ่งที่ต้องเห็น |
| --- | --- |
| ตารางนัดหมายกลาง | สาขา วันที่ เวลา หมอ บริการ และสถานะนัดหมาย |
| จองหรือแก้ไขนัดหมาย | ช่องข้อมูลการนัดหมาย และตัวอย่างแจ้งเตือนเวลาชนกัน |
| ตรวจข้อมูลก่อนย้าย | ข้อมูลซ้ำ ข้อมูลขาด วันที่กำกวม และรายการที่ต้องให้คนยืนยัน |

**ตรวจรับ:** เปิดในเบราว์เซอร์ได้ครบทั้งสามส่วน ข้อมูลและสถานะตรงกับ To-Be, Data Model และปัญหาข้อมูลที่วิเคราะห์ไว้ พร้อมภาพหลักฐาน ติดป้ายข้อมูลจำลองและรายการรอยืนยันให้ชัด ปุ่มเป็นภาพจำลองได้ ไม่ต้องมี backend หรือย้ายข้อมูลจริง

'''+chunk[idx:]
chunk=chunk.replace('หลังรับ Change Request ผลงานต้องครอบคลุมข้อกำหนดใหม่ทั้งสองข้อ และอธิบายได้ว่าส่วนใดเปลี่ยน ส่วนใดใช้ต่อ และเพราะอะไร','หลังรับ Change Request ให้ปรับทั้งเอกสารและ Mockup: เพิ่มส่วนบันทึกความยินยอมและหน้าจำลองการจองเองผ่าน LINE OA โดยไม่เชื่อมบริการจริง พร้อมอธิบายส่วนที่เปลี่ยน ส่วนที่ใช้ต่อ และเหตุผล')
s=s[:a]+chunk+s[b:]
s=s.replace('| คลินิกทันตกรรม | งานที่ต้องส่งทั้งหกส่วน |','| คลินิกทันตกรรม | เอกสารทั้งหกส่วนและ Web UI Mockup สามส่วน |')
s=s.replace('การจับคู่คนไข้ กรณีให้คนยืนยัน และผลตรวจ Mermaid |','การจับคู่คนไข้ กรณีให้คนยืนยัน ผลตรวจ Mermaid และ Mockup ที่ตรงกับเอกสาร |')
# Keep historical results clearly distinct from the newly expanded assignment.
heading='#### 1.4.3 แล็บโจทย์ 3 — แผนย้ายระบบคลินิกและการแก้หลังรับข้อมูลใหม่\n'
s=s.replace(heading,heading+'\n> โจทย์ปัจจุบันเพิ่ม Web UI Mockup แล้ว ผลทดลองด้านล่างเป็นรอบก่อนเพิ่ม Mockup จึงยังไม่ยืนยันเกณฑ์ส่วนนี้ ต้องทดลองและเก็บหลักฐานเพิ่ม\n',1)
# Update clinic Graph and Dynamic examples only, preserving unrelated problems.
for start,end in [('### 2.6 เติม Prompt สำหรับโจทย์ 3:', '### สิ่งที่ควรเขียนได้หลังจบบท Graph'),('### 3.6 เติม Prompt สำหรับโจทย์ 3:', '### สิ่งที่ควรเขียนได้หลังจบบท Dynamic Workflow')]:
 a=s.index(start); b=s.index(end,a); c=s[a:b]
 c=c.replace('**Output ที่ได้จากการทดลองเดิม**','**Output ที่ได้จากการทดลองเดิม**\n\n> ผลเดิมยังไม่มี Web UI Mockup ตามขอบเขตใหม่ ต้องรันและตรวจส่วนนี้เพิ่มเติม',1)
 c=c.replace('ที่แก้ปัญหาที่พบ | N1 | แผนภาพ Mermaid |','ที่แก้ปัญหาที่พบ และสร้าง Mockup ส่วนตารางนัดหมายกับฟอร์มจอง | N1 | แผนภาพ Mermaid + Mockup สองส่วน |')
 c=c.replace('จัดทำ Plan Version Log และรวมเป็นเอกสารสุดท้าย | N2, N3, N4 | เอกสารสุดท้าย |','จัดทำ Plan Version Log รวม Mockup จาก N3 และเพิ่มส่วนตรวจข้อมูลก่อนย้ายจาก N4 ตรวจหน้าจอเทียบเอกสารพร้อมภาพหลักฐาน | N2, N3, N4 | output.md + mockup.html + ผลตรวจ |')
 c=c.replace('- บันทึกผลงานส่งมอบสุดท้ายเป็น `output.md`: ไฟล์ Markdown เดียว โดยใส่ทุก diagram ใน fenced block ที่ขึ้นต้นด้วย ```mermaid ไม่จำเป็นต้องมีลิงก์ภายนอก','- บันทึกเอกสารและแผนภาพ Mermaid ใน `output.md` และ Web UI Mockup ใน `mockup.html` ตรวจตามเกณฑ์ Mockup ใน INPUT พร้อมบันทึกภาพหลักฐาน')
 c=c.replace('2. คนไข้ต้องจองคิวเองผ่าน LINE OA ได้\n','2. คนไข้ต้องจองคิวเองผ่าน LINE OA ได้\nปรับ mockup.html เพิ่มส่วนความยินยอมและหน้าจำลองจองผ่าน LINE OA ให้ตรงกับเอกสาร โดยไม่เชื่อมบริการจริง พร้อมตรวจและเก็บภาพใหม่\n')
 c=c.replace('# NEW INFORMATION (ข้อมูลใหม่)\nNONE','# NEW INFORMATION (ข้อมูลใหม่)\nNONE')
 if start.startswith('### 3'):
  c=c.replace('# PLAN FORMAT (รูปแบบแผน)\n','# PLAN FORMAT (รูปแบบแผน)\nแผนต้องมีงานสร้าง mockup.html หลังออกแบบ To-Be และ Data Model และมีงานเปิดตรวจทั้งสามส่วนเทียบเอกสารพร้อมเก็บภาพหลักฐาน\n',1)
 s=s[:a]+c+s[b:]
# Loop input remains the single source for the parameterized prompt variants.
ip=root/'labs/prompts/loop/3_clinic_migration-input.md'; inp=ip.read_text()
assert old in inp
inp=inp.replace(old,contract)
inp=inp.replace('[C1]\nมีทุกฟีเจอร์ที่ระบุไว้ในโจทย์','[C1]\nส่ง output.md ครบหกส่วนตามโจทย์ และ mockup.html ครบสามส่วนตามขอบเขต Mockup')
extra=' รวมถึงเปิด mockup.html ในเบราว์เซอร์ ตรวจความครบทั้งสามส่วน ความสอดคล้องกับเอกสาร ป้ายข้อมูลจำลองและรายการรอยืนยัน พร้อมบันทึกภาพหลักฐาน'
inp=inp.rstrip()+extra+'\n'
req,criteria=inp.split('\n[C1]\n',1); req=req.removeprefix('[REQUIREMENT]\n').strip()
c1,rest=criteria.split('\n[C2]\n',1); c2,c3=rest.split('\n[C3]\n',1)
crit='\n'.join('C'+str(i)+'. '+v.strip() for i,v in enumerate([c1,c2,c3],1))
runp=root/'labs/prompts/loop/3_clinic_migration-run.md'; oldrun=runp.read_text(); run=oldrun.split('## REQUIREMENT\n')[0]+'## REQUIREMENT\n'+req+'\n\n## CRITERIA\n'+crit+'\n'
promptp=root/'labs/prompts/loop/3_clinic_migration-prompt.md'; template=(root/'labs/prompts/loop/loop-template.md').read_text(); prompt=template.replace('{{REQUIREMENT}}',req).replace('{{CRITERIA}}',crit)
# Replace the README's matching Loop block with the exact run file.
a=s.index('#### โจทย์ 3: คลินิกทันตกรรม'); b=s.index('#### Prompt นี้ช่วยกำกับงานอย่างไร',a)
c=s[a:b]; x=c.index('````text\n')+len('````text\n'); y=c.index('\n````',x); c=c[:x]+run.rstrip()+c[y:]; s=s[:a]+c+s[b:]
for path,text in [(p,s),(ip,inp),(runp,run),(promptp,prompt)]:
 target=backup/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(path.read_text()); path.write_text(text)
assert run.rstrip() in s
assert '{{REQUIREMENT}}' not in prompt and '{{CRITERIA}}' not in prompt
print('Updated README and 3 clinic Loop prompt files. Historical results marked as predating Mockup requirement.')
