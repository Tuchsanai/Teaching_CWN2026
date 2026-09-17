from pathlib import Path
import json,hashlib,re
root=Path.cwd();p=Path(Path('work/clinic-current-run.txt').read_text());rel=p.relative_to(root).as_posix()
v=json.loads((p/'verification-phase2.json').read_text());assert v['automated_checks_pass']
with (p/'trace.md').open('a') as f:f.write('''
## Iteration 2 — Critic
- C1 PASS: เอกสารและ Mockup เพิ่มความยินยอมกับ LINE OA ครบ พร้อม Plan v2, Impact และ Reuse; สามส่วนเฟสแรกยังอยู่
- C2 PASS: raw และ Findings เฟสแรกยังคงเดิม ข้อกำหนดใหม่ไม่ลบความกำกวมหรือยืนยันตัวตนแทนคน
- C3 PASS: Mermaid ห้าบล็อก render จริง; Playwright เปิด Mockup ครบห้าส่วนทั้ง 1440 และ 390; ไม่มี console/page error; ไม่มี horizontal overflow ระดับหน้า; ช่องยินยอมไม่ถูกเลือกล่วงหน้า; LINE ติดป้ายจำลอง
- ตรวจภาพหน้าจอทั้งห้าส่วนแล้ว: ตารางและฟอร์มอ่านได้ ไม่มีการทับซ้อนที่เห็นในภาพ; สถานะรอยืนยันไม่ปะปนกับการยืนยันนัดจริง
- อ่านความสอดคล้อง: หน้าจอแรกใช้ SourceRow ก่อนสร้าง Appointment; ฟอร์มเจ้าหน้าที่ใช้ข้อมูล Branch/Doctor/Service; คิวตรวจตรง ReviewIssue; ความยินยอมตรง ConsentRecord; LINE แยก LineIdentity และ BookingRequest ก่อนสร้าง Appointment
หยุดเมื่อผ่านทุกเกณฑ์ ภาพหน้าจอและผลตรวจทั้งหมดมาจากรอบนี้ ไม่มีการทดสอบ API ธุรกรรม หรือการปฏิบัติตามกฎหมายจริง
''')
v['criteria']={'C1':'PASS','C2':'PASS','C3':'PASS'};v['semantic_review']='trace.md; performed by Codex in the same conversation, not independent review'
(p/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
verify=(root/'work/verify-clinic.py').read_text().replace("p=Path(Path('work/clinic-current-run.txt').read_text()); phase=sys.argv[1]","p=Path(__file__).resolve().parent; phase=sys.argv[1]")
verify=verify.replace("text=(p/'output.md').read_text();", "doc_name='output-phase1.md' if phase=='phase1' else 'output.md'; ui_name='mockup-phase1.html' if phase=='phase1' else 'mockup.html'\ntext=(p/doc_name).read_text();")
verify=verify.replace("(p/'mockup.html').as_uri()","(p/ui_name).as_uri()")
verify=verify.replace("['output.md','mockup.html','prompt-used.md']","[doc_name,ui_name,'prompt-used.md']")
(p/'verify.py').write_text(verify)
(p/'README.md').write_text('''# ผลทดลองคลินิกพร้อม Web UI Mockup

ใช้เอกสารเฟสแรกของรอบเดิมเป็นฐานที่ตรวจใหม่ เพิ่ม Mockup ใหม่และทำ Change Request ต่อหลังเฟสแรก ไม่ใช่การสร้างเอกสารทั้งหมดใหม่จากศูนย์ ไม่ใช้ผล PASS เดิมแทนผลตรวจใหม่

- output-phase1.md / mockup-phase1.html: baseline ก่อน Change Request
- output.md / mockup.html: ผลสุดท้ายรวมความยินยอมและ LINE OA
- prompt-used.md / input-used.md / prompt-phase2.md: ขอบเขตที่ใช้รอบนี้
- trace.md: บันทึก Generator/Critic และการตรวจความหมายในบทสนทนาเดียว
- verification-phase1.json / verification-phase2.json: ผลเครื่องมือตรวจของแต่ละเฟส
- verification.json: สรุปผลสุดท้ายรวมการตรวจความหมาย

รันซ้ำบน Remote ด้วย `/opt/venv/bin/python verify.py phase1` หรือ `phase2` จากโฟลเดอร์นี้ ใช้ Chromium และ Mermaid ที่ติดตั้งแล้วตาม path ในสคริปต์ ไม่มีการติดตั้งหรือเชื่อมบริการจริง การรันซ้ำเขียนทับผลตรวจและภาพของเฟสที่เลือก

ขอบเขตการทดสอบ: render Mermaid, เปิด Mockup, ตรวจ DOM และภาพทั้งจอคอมพิวเตอร์และมือถือ ไม่ทดสอบธุรกรรมหรือ LINE API และไม่รับรองความครบตามกฎหมาย
''')
(p/'response.md').write_text('''# สรุปผล Loop

| Iteration | สิ่งที่เปลี่ยน | ผล |
| --- | --- | --- |
| 1 | เพิ่ม Mockup สามส่วนจากแผนเดิมและตรวจใหม่ | C1–C3 PASS |
| 2 | หลัง Change Request เพิ่มความยินยอมและ LINE OA ในเอกสารและ Mockup | C1–C3 PASS หลังแก้ |

ผลงาน: output.md และ mockup.html; baseline: output-phase1.md และ mockup-phase1.html
หลักฐาน: trace.md และ verification.json พร้อมภาพ phase1/phase2
ประเด็นค้าง: วันที่ ตัวตน ตารางหมอ ระยะเวลาบริการ และนโยบายความยินยอม/LINE ต้องยืนยันก่อนนำไปใช้จริง
''')
pth=root/'readme.md';s=pth.read_text();a=s.index('#### 1.4.3 แล็บโจทย์ 3');b=s.index('<a id="graph"></a>',a)
section=f'''#### 1.4.3 แล็บโจทย์ 3 — แผนย้ายระบบคลินิกและ Web UI Mockup (แบบจำลองหน้าจอเว็บไซต์)

**ผลงานรอบอัปเดต**

ทดลองใหม่หลังเพิ่ม Mockup โดยใช้เอกสารออกแบบเดิมเป็นฐาน ตรวจตามเกณฑ์ปัจจุบัน และสร้างหน้าจอใหม่ Codex ในบทสนทนาเดียวทำบทบาท Generator และ Critic; ผลทดสอบและภาพด้านล่างสร้างใหม่ทั้งหมด ไม่ใช่การนำ PASS เดิมมาใช้

ส่งเอกสาร `output.md` ครบหกส่วนและ `mockup.html` เฟสแรกมีสามส่วน: ตารางนัดหมายกลาง จอง/แก้ไขนัดหมาย และตรวจข้อมูลก่อนย้าย หลังรับ Change Request เพิ่มส่วนความยินยอมและหน้าจองผ่าน LINE OA

**หน้าจอเฟสแรก — อ่านตามลำดับงาน**

1. **ตารางนัดหมายกลาง:** แสดงข้อมูลต้นฉบับ R1–R5 พร้อมสาขา หมอ บริการ และป้ายรอยืนยัน แยกจากนัดที่ยืนยันแล้ว

![Mockup ตารางนัดหมายกลางของคลินิก ข้อมูลจำลองและสถานะรอยืนยัน]({rel}/phase1-1440-appointments.png)

2. **จองหรือแก้ไขนัดหมาย:** เห็นข้อมูลที่ต้องใช้และตัวอย่างคำเตือนเวลาอาจชน โดยยังไม่ตัดสินแทนเจ้าของข้อมูล

![Mockup ฟอร์มจองและแก้ไขนัดหมาย พร้อมคำเตือนความเสี่ยงเวลาชน]({rel}/phase1-1440-booking.png)

3. **ตรวจข้อมูลก่อนย้าย:** แสดงข้อมูลซ้ำ เบอร์ขาด วันที่กำกวม และรายการที่ต้องให้คนยืนยัน

![Mockup ตรวจข้อมูลก่อนย้ายและคิวรอคนยืนยัน]({rel}/phase1-1440-review.png)

**วงจรสร้าง–ตรวจ–แก้**

| Iteration / ช่วง | สิ่งที่เกิดขึ้น | ผลตรวจ |
| --- | --- | --- |
| 1 / เฟสแรก | ตรวจแผนเดิมและเพิ่ม Mockup สามส่วน แล้วเปิดตรวจจริง | C1–C3 ผ่าน; Mermaid 3 บล็อก render ได้ |
| 2 / ตรวจเมื่อโจทย์เพิ่ม | เพิ่มความยินยอมและ LINE OA เข้า C1 แล้วตรวจ baseline | C1 ไม่ผ่านเพราะยังขาดสองส่วนใหม่; C2–C3 ของขอบเขตเดิมยังผ่าน |
| 2 / หลังแก้ | เพิ่มเอกสารและ Mockup สองส่วน พร้อม Plan v2 และผลกระทบ | C1–C3 ผ่าน; Mermaid 5 บล็อก render ได้ และ Mockup ครบ 5 ส่วน |

**หน้าจอส่วนเพิ่มหลัง Change Request**

![Mockup ความยินยอม ข้อความรอยืนยันและตัวเลือกที่ยังไม่ติ๊ก]({rel}/phase2-1440-consent.png)

![Mockup จองเองผ่าน LINE OA โดยไม่เชื่อมบริการจริง]({rel}/phase2-1440-line-booking.png)

**หลักฐานตามเกณฑ์**

| เกณฑ์ | ผล | หลักฐาน |
| --- | --- | --- |
| C1 ผลงานครบ | PASS | เอกสารหกส่วน + Mockup สามส่วนแรก และสองส่วนเพิ่มตาม Change Request |
| C2 คุณภาพข้อมูล | PASS | อ่านเทียบ CSV R1–R5 กับข้อค้นพบเก้าประเภท; Python ยืนยันว่าวันที่สองแบบของ R5 ไม่ตรงวันพุธ |
| C3 จับคู่ตัวตน แผนภาพ และ Mockup | PASS | ตรวจ normalization และกรณีให้คนยืนยัน; render Mermaid จริง; Playwright เปิดทุกส่วนที่ความกว้าง 1440 และ 390 พิกเซล ไม่พบ console/page error หรือหน้าล้นแนวนอน และตรวจภาพประกอบ |

การตรวจความหมายเป็นการอ่านโดย Critic ในบทสนทนาเดียว ส่วนผลเครื่องมือแยกไว้ใน JSON ปุ่มเป็นภาพจำลอง ไม่ย้ายข้อมูลหรือเชื่อม LINE จริง ประเด็นวันที่ ตัวตน ตารางหมอ และนโยบายยังต้องให้ผู้รับผิดชอบยืนยัน

[เปิด Mockup]({rel}/mockup.html) · [อ่านเอกสาร]({rel}/output.md) · [ดูเฟสแรก]({rel}/mockup-phase1.html) · [อ่าน Trace]({rel}/trace.md) · [ผลตรวจ]({rel}/verification.json) · [Prompt ที่ใช้]({rel}/prompt-used.md) · [สคริปต์และวิธีตรวจ]({rel}/README.md)

'''
s=s[:a]+section+s[b:]
s=s.replace('ผลด้านล่างสร้างใหม่วันที่ **17 กันยายน 2026**','ผลด้านล่างทดลองวันที่ **17 กันยายน 2026**')
s=s.replace('และไม่ได้นำผลจากโฟลเดอร์ทดลองเดิมมาใช้แทนผลใหม่','โจทย์คลินิกรอบอัปเดตใช้เอกสารเดิมเป็นฐาน เพิ่ม Mockup แล้วตรวจหลักฐานใหม่ทั้งหมดตามรายละเอียดในข้อ 1.4.3')
s=s.replace('| 3. ย้ายระบบคลินิก | แผนย้ายระบบเฟสแรกและฉบับหลัง Change Request |','| 3. ย้ายระบบคลินิก | แผนย้ายระบบและ Mockup ก่อน/หลัง Change Request |')
pth.write_text(s)
# Save editable diagram generation source with the image assets.
(root/'img/render-graph-workflow.py').write_text((root/'work/graph-layout.py').read_text())
for phase in ['phase1','phase2']:
 v=json.loads((p/f'verification-{phase}.json').read_text());assert v['automated_checks_pass']
assert '### 1.5 ' not in s and '### 1.6 ' not in s
links=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',section)
missing=[x for x in links if not (root/x).exists()];assert not missing,missing
(p/'sha256.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name!='sha256.json'},indent=2))
print('README updated with new clinic evidence, all new links exist. Loop removals preserved.')
