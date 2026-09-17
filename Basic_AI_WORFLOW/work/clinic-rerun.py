from pathlib import Path
from datetime import datetime
import re,json
root=Path.cwd(); stamp=datetime.now().strftime('%Y-%m-%d-%H%M%S'); run=root/'lab-results/loop/3_clinic_migration'/('run-'+stamp); run.mkdir()
(root/'work/clinic-current-run.txt').write_text(str(run))
translations={'As-Is Process':'กระบวนการทำงานปัจจุบัน','To-Be Process':'กระบวนการทำงานที่ต้องการในอนาคต','Data Quality Findings':'ข้อค้นพบปัญหาคุณภาพข้อมูล','Data Model':'แบบจำลองข้อมูล','Data Mapping':'การจับคู่ข้อมูลต้นทางกับปลายทาง','Gap Analysis':'การวิเคราะห์สิ่งที่ยังขาดเพื่อไปสู่ระบบใหม่','Roll-out Plan':'แผนทยอยนำระบบไปใช้งาน','Plan Version Log':'บันทึกการเปลี่ยนแปลงแผน','Impact Analysis':'การวิเคราะห์ผลกระทบ','Migration':'การย้ายข้อมูลและระบบ','Reuse':'การนำผลงานเดิมมาใช้ต่อ','Web UI Mockup':'แบบจำลองหน้าจอเว็บไซต์'}
def thai(text):
 for en,th in translations.items():
  text=re.sub(r'\b'+re.escape(en)+r'\b(?! \('+re.escape(th)+r'\))',en+' ('+th+')',text)
 return text
p=root/'readme.md'; s=p.read_text()
for start,end in [('### โจทย์ 3 —','## วิธีเรียน'),('#### โจทย์ 3: คลินิกทันตกรรม','#### Prompt นี้ช่วยกำกับงานอย่างไร'),('#### 1.4.3 แล็บโจทย์ 3','<a id="graph"></a>'),('### 2.6 เติม Prompt สำหรับโจทย์ 3','### สิ่งที่ควรเขียนได้หลังจบบท Graph'),('### 3.6 เติม Prompt สำหรับโจทย์ 3','### สิ่งที่ควรเขียนได้หลังจบบท Dynamic Workflow')]:
 a=s.index(start); b=s.index(end,a); s=s[:a]+thai(s[a:b])+s[b:]
p.write_text(s)
for name in ['input','run','prompt']:
 p=root/f'labs/prompts/loop/3_clinic_migration-{name}.md'; p.write_text(thai(p.read_text()))
old=root/'lab-results/loop/3_clinic_migration/run-2026-09-17-074505'
base=thai((old/'output-phase1.md').read_text())
base=base.replace('Loop รอบใหม่ •','Loop ตรวจซ้ำตามเกณฑ์ที่เพิ่ม Mockup •')
base+='''
## Web UI Mockup (แบบจำลองหน้าจอเว็บไซต์)

ส่ง mockup.html ควบคู่กับเอกสารนี้ หน้าจอเป็นข้อมูลจำลองสำหรับตรวจแบบ ไม่ได้ทำธุรกรรมหรือย้ายข้อมูลจริง

| ส่วนหน้าจอ | ข้อมูลและกติกาในเอกสาร | สิ่งที่แสดง |
| --- | --- | --- |
| ตารางนัดหมายกลาง | SourceRow, Branch, Doctor, Service; ยังไม่สร้าง Appointment เมื่อข้อมูลไม่ยืนยัน | แสดง R1–R5 พร้อมวันที่ต้นฉบับและป้ายรอยืนยัน แยกจากนัดที่ยืนยันแล้ว |
| จองหรือแก้ไขนัด | Appointment, Patient, Branch, Doctor, Service และการตรวจทรัพยากร | ฟอร์มสาธิตและคำเตือนความเสี่ยง R3/R4 ไม่ตัดสินว่าเวลาชนจริงก่อนยืนยันวันและระยะเวลา |
| ตรวจข้อมูลก่อนย้าย | SourceRow และ ReviewIssue | ข้อมูลซ้ำ R1/R2, เบอร์ขาด R3, วันที่กำกวม R1/R4/R5 และตัวตน R1/R2/R5 ที่ยังต้องยืนยัน |

ปุ่มแสดงว่าเป็นตัวอย่างและไม่บันทึกจริง ชื่อและเบอร์เป็นข้อมูลตัวอย่างจากโจทย์ มีคำแปลไทยกำกับคำศัพท์หลัก หน้าจอไม่รวมตัวตนอัตโนมัติ และไม่ถือวันที่ตัวอย่างเป็นค่าที่ผ่านการตรวจแล้ว
'''
(run/'output.md').write_text(base); (run/'output-phase1.md').write_text(base)
(run/'prompt-used.md').write_text((root/'labs/prompts/loop/3_clinic_migration-prompt.md').read_text())
(run/'input-used.md').write_text((root/'labs/prompts/loop/3_clinic_migration-input.md').read_text())
(run/'run-info.json').write_text(json.dumps({'created':stamp,'execution':'Codex in this conversation, Generator and Critic roles; not independent agents','method':'Updated existing clinic design to expanded criteria; new mockup; all evidence regenerated','source_document':str(old.relative_to(root)/'output-phase1.md'),'historical_verification_reused':False},ensure_ascii=False,indent=2))
(run/'trace.md').write_text('''# บันทึก Loop — โจทย์คลินิกเพิ่ม Mockup

รอบนี้ใช้ Codex ในบทสนทนาเดียวสลับบทบาท ไม่ใช่ผู้ตรวจอิสระ ใช้เอกสารออกแบบเดิมเป็นจุดตั้งต้น แล้วสร้าง Mockup ใหม่และตรวจหลักฐานใหม่ทั้งหมด ไม่คัดลอก PASS หรือภาพจากรอบเดิม

## Requirement → ผลงาน → วิธีตรวจ (ก่อนสร้าง)
- C1: เอกสารหกส่วน + Mockup สามส่วน → output.md, mockup.html → อ่านหัวข้อและเปิดหน้าจอจริง
- C2: ปัญหาอย่างน้อยห้าประเภท พร้อมแถว ผลกระทบ และข้อมูลกำกวม → Findings เก้าประเภท → อ่านเทียบ CSV R1–R5 และตรวจวันด้วย Python
- C3: normalization และคนยืนยัน + Mermaid + Mockup สอดคล้อง → เอกสารและ UI → ตรวจชื่อ/เบอร์ กรณี R1–R5, render ทุกแผนภาพ, เปิดหน้าจอและตรวจภาพ

## Iteration 1 — Generator
คงข้อมูลต้นทางและกติกาที่ยังถูกต้อง เพิ่ม Mockup ตารางนัดหมาย ฟอร์มจอง และคิวตรวจข้อมูล โดยยังไม่เพิ่ม Change Request เฟสสอง รอผล Critic จากการตรวจจริง
''')
css='''*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#172c3e;font:16px/1.65 "Noto Sans Thai",Tahoma,sans-serif}header{background:#163f51;color:white;padding:34px 5%}header p{color:#dcecf1;margin:7px 0}h1{font-size:32px;margin:0}h2{font-size:25px;margin:0 0 8px}h3{margin:8px 0}nav{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}nav a{color:white;border:1px solid #73929e;padding:6px 15px;border-radius:24px;text-decoration:none}main{max-width:1260px;margin:auto;padding:28px 24px}section{background:white;border:1px solid #dce5ed;border-radius:18px;padding:28px;margin:0 0 25px;scroll-margin-top:20px}.tag{display:inline-block;font-size:13px;border-radius:16px;padding:3px 11px;background:#e4f4ef;color:#09644f}.warn{background:#fff4d9;color:#704812;border-left:4px solid #d79a2e;padding:14px 18px;border-radius:8px}.muted{color:#5a6c7d}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px}th{text-align:left;background:#eff5f8}th,td{padding:13px 12px;border-bottom:1px solid #e1e7ee;vertical-align:top}label{display:block;font-weight:600}input,select{display:block;width:100%;padding:11px;border:1px solid #becedb;background:#fafcfe;border-radius:8px;font:inherit;color:#172c3e}input[type=checkbox]{display:inline;width:auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}button{padding:12px 20px;border:0;border-radius:9px;background:#dce5ed;color:#485d6c;font:inherit;margin-top:18px}.count{font-size:14px;color:#5a6c7d}.phone{max-width:430px;border:8px solid #dae4ea;border-radius:24px;margin:20px auto;padding:23px;background:#f9fffc}.phone h3{color:#176c4e}footer{text-align:center;padding:20px;color:#5a6c7d}@media(max-width:650px){.grid{grid-template-columns:1fr}main{padding:16px 10px}section{padding:18px}h1{font-size:25px}header{padding:24px 18px}h2{font-size:21px}}'''
rows=[('R1','ลาดกระบัง','03/09/2026','10:00','สมชาย ใจดี','หมอเอ','ขูดหินปูน','วันที่ / นัดอาจซ้ำ'),('R2','ลาดกระบัง','2026-09-03','10:00','สมชาย ใจดี','หมอเอ','ขูดหินปูน','ยืนยันนัดซ้ำกับ R1'),('R3','บางนา','3 ก.ย. 69','13:30','คุณมาลี','หมอบี','จัดฟัน','ปี / ติดต่อ / เวลา'),('R4','บางนา','03/09/2026','13:30','วิชัย ศรีสุข','หมอบี','อุดฟัน','วันที่ / เวลา'),('R5','อ่อนนุช','09/03/2026','09:00','Somchai Jaidee','หมอเอ','ตรวจฟัน','วันที่ / ตัวตน / วันหมอ')]
tr=''.join('<tr>'+''.join('<td>'+v+'</td>' for v in row)+'</tr>' for row in rows)
html='''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Clinic Workspace — แบบจำลองระบบนัดหมายกลาง</title><style>'''+css+'''</style></head><body><header><span class="tag">LAB 03 · ข้อมูลจำลอง</span><h1>ระบบนัดหมายกลางของคลินิก</h1><p>เห็นนัดหมายร่วมกัน · ตรวจข้อมูลก่อนย้าย · ยืนยันก่อนรวมตัวตน</p><nav><a href="#appointments">01 ตารางนัดหมาย</a><a href="#booking">02 จอง / แก้ไข</a><a href="#review">03 ตรวจข้อมูล</a><!--PHASE2_NAV--></nav></header><main>
<section id="appointments"><span class="count">01 / ภาพรวมสามสาขา</span><h2>ตารางนัดหมายกลาง</h2><p class="muted">ข้อมูลจำลองจาก R1–R5 · แสดงวันที่ต้นฉบับก่อนยืนยัน</p><p class="warn">รายการทั้งหมดอยู่ระหว่างตรวจข้อมูล ยังไม่ใช่นัดยืนยันในระบบใหม่ ห้ามใช้เพื่อจัดตารางจริง</p><div class="table-wrap"><table><thead><tr><th>แถว</th><th>สาขา</th><th>วันที่ต้นฉบับ</th><th>เวลา</th><th>คนไข้ตัวอย่าง</th><th>หมอ</th><th>บริการ</th><th>รอยืนยัน</th></tr></thead><tbody>'''+tr+'''</tbody></table></div></section>
<section id="booking"><span class="count">02 / ตัวอย่างหน้าจอเจ้าหน้าที่</span><h2>จองหรือแก้ไขนัดหมาย</h2><p class="muted">ฟอร์มจำลอง · ไม่บันทึกหรือจองทรัพยากรจริง</p><div class="grid"><label>ชื่อคนไข้<input placeholder="เลือกคนไข้ที่ยืนยันตัวตนแล้ว"></label><label>สาขา<select><option>บางนา</option><option>ลาดกระบัง</option><option>อ่อนนุช</option></select></label><label>หมอ<select><option>หมอบี</option><option>หมอเอ</option></select></label><label>บริการ<select><option>จัดฟัน</option><option>อุดฟัน</option><option>ตรวจฟัน</option></select></label><label>วันที่<input placeholder="รอยืนยันรูปแบบวันที่"></label><label>เวลา<input value="13:30" readonly></label></div><p class="warn">ตัวอย่างคำเตือน: R3/R4 ใช้หมอบีเวลา 13:30 เหมือนกัน อาจชนกันหากเป็นวันเดียวกัน ต้องยืนยันวันที่และระยะเวลาบริการก่อน ไม่สรุปว่าเวลาชนแล้ว</p><button disabled>บันทึกนัด — ปุ่มจำลอง</button></section>
<section id="review"><span class="count">03 / ตรวจข้อมูลก่อนย้าย</span><h2>รายการที่ต้องให้คนยืนยัน</h2><p class="muted">Data Mapping (การจับคู่ข้อมูลต้นทางกับปลายทาง) · เก็บต้นฉบับทุกแถว</p><div class="table-wrap"><table><thead><tr><th>แถว</th><th>สิ่งที่พบ</th><th>การจัดการ / ผู้ยืนยัน</th></tr></thead><tbody><tr><td>R1 / R2</td><td>นัดอาจซ้ำ เบอร์ปรับรูปตรงกัน แต่วันที่ R1 กำกวม</td><td>รอสาขาลาดกระบังยืนยันวันและตัวตนก่อนรวม</td></tr><tr><td>R3</td><td>ไม่มีเบอร์ ปี 69 ไม่ระบุศักราช ไม่มีรหัสบัญชี LINE</td><td>รอสาขาบางนายืนยันปี ตัวตน และช่องทางติดต่อ</td></tr><tr><td>R3 / R4</td><td>หมอและเวลาเหมือนกัน วันที่และระยะเวลายังไม่ยืนยัน</td><td>รอเจ้าหน้าที่ตารางหมอยืนยันความพร้อม</td></tr><tr><td>R5</td><td>09/03/2026 อาจเป็น 9 มีนาคม หรือ 3 กันยายน ทั้งสองไม่ใช่วันพุธ</td><td>รอสาขาอ่อนนุชยืนยันวันและหมายเหตุ</td></tr><tr><td>R1 / R2 / R5</td><td>เบอร์ปรับรูปเป็น 0812345678 เหมือนกัน ชื่อข้ามภาษา</td><td>รอคนไข้และเจ้าหน้าที่ยืนยัน ห้ามรวมตัวตนอัตโนมัติ</td></tr></tbody></table></div><p class="warn">ทุกแถวคงข้อมูลต้นฉบับไว้ ไม่มีการรวมคนไข้ ลบข้อมูล หรือนำเข้าระบบจริง</p></section>
<!--PHASE2--></main><footer>แบบจำลองหน้าจอเพื่อการเรียนรู้ · ไม่เชื่อม Google Sheet, LINE หรือข้อมูลคนไข้จริง</footer></body></html>'''
(run/'mockup.html').write_text(html);(run/'mockup-phase1.html').write_text(html)
print('RUN_DIR',run)
