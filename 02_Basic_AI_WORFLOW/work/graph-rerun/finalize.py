from common import *
import re,shutil
p=case('3_clinic_migration');v=json.loads((p/'verification-phase2.json').read_text());assert v['automated_pass']
review='''# ผล N5-v2 — คลินิกหลัง Change Request
C1 PASS: เพิ่มความยินยอมและ LINE OA ทั้งเอกสารและ Mockup พร้อม Impact/Reuse และ Plan v2
C2 PASS: คง raw และ Findings จากเฟสแรก ความกำกวมเดิมยังระบุครบ ไม่มีข้อมูลใหม่ไปยืนยันวันที่หรือตัวตนแทนเจ้าของข้อมูล
C3 PASS: render Mermaid ห้าบล็อกใหม่จริง เปิด UI ห้าส่วนทั้ง 1440/390 ไม่มี console/page error หรือหน้าล้นแนวนอน ช่องยินยอมไม่เลือกล่วงหน้า และ LINE ติดป้ายจำลอง
อ่านความสอดคล้อง: ConsentRecord ตรงช่องวัตถุประสงค์/รุ่นข้อความ/การตัดสินใจ/เวลา; LineIdentity แยกตัวตนบัญชีจาก Patient; BookingRequest เกิดก่อน Appointment ยืนยันแล้ว คง normalization และกรณีให้คนยืนยันเดิม
N2 ใช้ไฟล์เดิมและ hash เดิม ไม่ทำใหม่ ส่วน N1-v2, N3-v2, N4-v2 ทำตามผลกระทบก่อน N5-v2
ข้อจำกัด: การจำลองบทบาทในบทสนทนาเดียว ไม่มีการแยกบริบทหรือรันขนาน; ไม่ทดสอบธุรกรรมหรือ API จริงและไม่รับรองตามกฎหมาย
'''
node(p,'N5-v2',['N2','N3-v2','N4-v2'],{'nodes/N5-v2-review.md':review},['ใช้ N2 เดิมตาม Impact/Reuse'])
with (p/'trace.md').open('a') as f:f.write(review+'\nหยุดเฟสสองเมื่อ N5-v2 DONE\n')
v['criteria']={'C1':'PASS','C2':'PASS','C3':'PASS'};v['semantic_review']='nodes/N5-v2-review.md';(p/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
audit={}
for key in ['1_meeting_room','2_expense_claim','3_clinic_migration']:
 p=case(key);events=[json.loads(x) for x in (p/'events.jsonl').read_text().splitlines()];done=set();hashes=True
 for e in events:
  assert set(e['depends_on'])<=done,(key,e['node']);assert e['status']=='DONE'
  for f,h in e['sha256'].items():assert hashlib.sha256((p/f).read_bytes()).hexdigest()==h,(key,f)
  done.add(e['node'])
 audit[key]={'dependency_order_valid':True,'node_artifact_hashes_valid':True,'nodes_completed':[e['node'] for e in events],'context_isolation':False,'parallel_execution':False}
 table='| Node | Dependency | สถานะ | ผลลัพธ์ |\n| --- | --- | --- | --- |\n'
 for e in events:table+='| '+e['node']+' | '+(', '.join(e['depends_on']) or '—')+' | DONE | '+', '.join(e['output'])+' |\n'
 (p/'execution-table.md').write_text(table)
 with (p/'trace.md').open('a') as f:f.write('\n## ตารางสรุป\n\n'+table)
 review_file='nodes/N5-v2-review.md' if key=='3_clinic_migration' else 'nodes/N5-review.md'
 (p/'response.md').write_text('# สรุปผล Graph\n\n'+table+'\n'+(p/review_file).read_text()+'\nหลักฐาน: verification.json, trace.md และ events.jsonl\n')
 (p/'sha256.json').write_text(json.dumps({f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name!='sha256.json'},indent=2))
(RUN/'dependency-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
# Save verification tools with paths relative to this sealed run.
verify=(ROOT/'work/graph-rerun/verify-docs.py').read_text().replace("RUN=Path(Path('work/graph-current-run.txt').read_text());",'RUN=Path(__file__).resolve().parent;')
(RUN/'verify-docs.py').write_text(verify)
render=(ROOT/'work/graph-rerun/render-docs.py').read_text().replace("run=Path(Path('work/graph-current-run.txt').read_text());",'run=Path(__file__).resolve().parent;')
(RUN/'render-docs.py').write_text(render)
(RUN/'source').mkdir()
for name in ['common.py','meeting.py','expense.py','clinic.py','phase1-complete.py','clinic-phase2.py']:
 (RUN/'source'/name).write_text((ROOT/'work/graph-rerun'/name).read_text())
(RUN/'README.md').write_text('''# Graph Lab — ผลรันใหม่ครบสามโจทย์

อ่านแต่ละโฟลเดอร์: prompt-used.md คือ Prompt เต็มที่ใช้, nodes/ คือผลแยก Node, events.jsonl และ trace.md คือร่องรอย, execution-table.md คือตารางสรุป, verification.json คือผลสุดท้าย และ response.md คือคำตอบสรุป

วิธีรัน: Codex ในบทสนทนาเดียวจำลองบทบาทและสร้างไฟล์ตามลำดับ Dependency บน Remote ไม่ใช่หลายโมเดลที่แยกบริบทหรือทำงานขนาน จึงยังไม่พิสูจน์การแยกบริบท N2–N4 โค้ดต้นทางและข้อมูลของรอบนี้อยู่ใน source/ เพื่อการตรวจสอบ ไม่ได้นำผลงาน Loop เดิมมาเปลี่ยนชื่อเป็น Graph

## ตรวจซ้ำ
จากโฟลเดอร์รอบนี้:
- `/opt/venv/bin/python 1_meeting_room/nodes/N4-test.py` ทดสอบเว็บด้วยการคลิกจริง
- `/opt/venv/bin/python verify-docs.py` ตรวจเอกสารและ Mockup ฉบับปัจจุบันของเบิกค่าใช้จ่ายกับคลินิก
- `/opt/venv/bin/python render-docs.py` สร้าง HTML อ่านเอกสารพร้อมภาพแผนภาพ

เครื่องมือใช้ Chromium และ Mermaid ที่ติดตั้งอยู่แล้วตาม path ในสคริปต์ ไม่มีการติดตั้งหรือเชื่อมธุรกรรมจริง การตรวจซ้ำจะเขียนทับ JSON/ภาพที่เกี่ยวข้อง จึงควรคัดลอกชุดผลก่อนตรวจหากต้องการรักษาหลักฐานเดิม

คลินิกเก็บ output-phase1.md, mockup-phase1.html และ verification-phase1.json ก่อน Change Request พร้อมผลเฟสสองแยกกัน
ระบบเบิกค่าใช้จ่ายเก็บ verification-parser-attempt1.json: ครั้งแรกตัวตรวจอ่าน cardinality ผิดว่าเป็นหัว Entity แก้ regex แล้วตรวจใหม่ ไม่ได้แก้ผลงานให้หลบเกณฑ์

dependency-audit.json ตรวจลำดับ Dependency และ hash ไฟล์ Node เท่านั้น ไม่ใช่หลักฐานว่ารันขนานหรือบริบทเป็นอิสระ การตัดสินความหมายโดย Codex อยู่ใน nodes/N5-review.md และของคลินิกเพิ่ม N5-v2-review.md
''')
base=RUN.relative_to(ROOT).as_posix();m=base+'/1_meeting_room';e=base+'/2_expense_claim';c=base+'/3_clinic_migration'
section=f'''### 2.4 ผลลัพธ์จากการทดลอง Graph: โจทย์ 1 → 2 → 3

ผลรอบนี้ใช้ **Graph Template ในข้อ 2.2 และพารามิเตอร์จากข้อ 2.3** ครบทั้งสามโจทย์บน Remote เก็บ Prompt ที่ใช้จริง ผลแต่ละ Node, Execution Trace, ผลตรวจ และภาพไว้ด้วยกัน

**วิธีรันและข้อจำกัด:** Codex ในบทสนทนาเดียวจำลองบทบาทและทำตามลำดับ Dependency ไม่ได้แยกบริบทหรือรัน N2–N4 ขนานจริง จึงยังไม่พิสูจน์ความเป็นอิสระของ Node ตามกราฟ งานและหลักฐานเครื่องมือสร้างใหม่ในรอบนี้ ไม่ใช้ผลงานหรือ PASS ของ Loop แทน

| โจทย์ | ผลงาน | กระบวนการที่เห็น | ผลตามเกณฑ์ |
| --- | --- | --- | --- |
| จองห้องประชุม | เว็บที่จองและยกเลิกได้ | N1 กำหนด contract → N2 ตรรกะ / N3 หน้าจอ / N4 ทดสอบ → N5 รวมและรันทดสอบ | C1–C3 ผ่าน |
| เบิกค่าใช้จ่าย | เอกสาร แผนภาพ และ Mockup สามส่วน | เพิ่ม N1b เก็บข้อขัดแย้งวงเงินก่อน N5 รวม | C1–C3 ผ่าน |
| ย้ายระบบคลินิก | แผนย้ายและ Mockup ก่อน/หลัง Change Request | เฟสสองทำใหม่ตามผลกระทบและใช้ N2 เดิม | C1–C3 ผ่านทั้งสองเฟส |

**เลือกอ่านทีละแล็บ:** [1. จองห้องประชุม](#graph-lab-1) · [2. เบิกค่าใช้จ่าย](#graph-lab-2) · [3. คลินิก](#graph-lab-3)

---

<a id="graph-lab-1"></a>

#### 2.4.1 แล็บโจทย์ 1 — เว็บจองห้องประชุม

**ผลงานที่ได้:** เว็บหน้าเดียวมีห้องตัวอย่างสามห้อง ดูเวลาว่าง กรอกการจอง ยกเลิก และดูสถานะ ข้อมูลอยู่ในหน่วยความจำ รีเฟรชแล้วเริ่มจากตัวอย่างเดิม

![เว็บจองห้องประชุมจาก Graph รอบใหม่]({m}/screen-overview.png)

**การส่งงานระหว่าง Node**

| Node | สิ่งที่ส่งต่อ | ผล |
| --- | --- | --- |
| N1 | ห้าฟีเจอร์ ชื่อ DOM/ฟังก์ชัน และข้อมูลที่ทุกส่วนใช้ร่วมกัน | DONE |
| N2 | ตรรกะ JavaScript ตาม contract | DONE |
| N3 | HTML/CSS ตาม contract | DONE |
| N4 | Python Playwright สำหรับคลิกและตรวจผล | DONE |
| N5 | รวม HTML กับ JavaScript แล้วรัน N4 จริง | DONE |

**หลักฐานตามเกณฑ์:** C1 ทดลองครบห้าฟีเจอร์; C2 ไม่พบ console/page error และตรวจเพิ่มว่ากันเวลาซ้อน คืนเวลาว่างหลังยกเลิก และปฏิเสธช่วงเวลาผิด; C3 เข้าถึงรายการห้อง ฟอร์ม และสถานะได้ทันที ส่วนดูเวลาว่างกับยกเลิกรายการตัวอย่างใช้หนึ่งคลิก

การนับคลิกหมายถึงการเข้าถึงฟีเจอร์จากหน้าแรก ไม่รวมการกรอกและส่งฟอร์ม โดยเลื่อนหน้าจอได้

![ผลหลังยกเลิกการจอง สถานะและเวลาว่างเปลี่ยนจริง]({m}/screen-cancelled.png)

[เปิดเว็บ]({m}/output.html) · [อ่าน Trace]({m}/trace.md) · [ผลทดสอบ]({m}/verification.json) · [สคริปต์ N4]({m}/nodes/N4-test.py) · [Prompt ที่ใช้]({m}/prompt-used.md)

---

<a id="graph-lab-2"></a>

#### 2.4.2 แล็บโจทย์ 2 — ข้อกำหนดและ Mockup ระบบเบิกค่าใช้จ่าย

**ผลงานที่ได้:** เอกสาร Actors/Stakeholders, FR, BR, NFR, Use Case, ERD, Sequence, State, Traceability, Open Issues และ Mockup ยื่นเบิก ติดตาม และตรวจ/อนุมัติ พร้อมตารางเชื่อมปัญหากับหน้าจอ

![ข้อกำหนด FR จากผล Graph รอบใหม่]({e}/screen-document-table.png)

**การส่งงานระหว่าง Node**

| Node | สิ่งที่ทำ | ผล |
| --- | --- | --- |
| N1 | สกัดคำสัมภาษณ์และกำหนดชื่อข้อมูล/สถานะร่วมกัน | DONE |
| N1b | เก็บหลักฐานวงเงิน 5,000/10,000 โดยไม่เลือกข้าง | DONE ก่อนรวม |
| N2 | Use Case, Sequence และ State | DONE |
| N3 | ERD ตาม contract ของ N1 | DONE |
| N4 | Mockup สามส่วนและ Pain Point → FR/BR → หน้าจอ | DONE |
| N5 | รวมเอกสาร ตรวจความสอดคล้องและเกณฑ์ทั้งหมด | DONE |

![ERD จากผล Node N3]({e}/phase1-diagram-4.png)

**Mockup ตามงานของผู้ใช้**

![หน้าจำลองยื่นเบิก พร้อมพื้นที่รูปและข้อมูลลูกค้า]({e}/phase1-1440-submit.png)

![หน้าจำลองติดตามสถานะและผู้รับผิดชอบ]({e}/phase1-1440-tracking.png)

![หน้าจำลองตรวจอนุมัติ พร้อมนโยบายที่รอยืนยัน]({e}/phase1-1440-review.png)

**หลักฐานตามเกณฑ์:** C1 เอกสารและ Mockup ครบ; C2 เชื่อมคำสัมภาษณ์ครบสิบหน่วยความหมายและคงข้อขัดแย้งวงเงิน ไม่สร้างตัวเลขวงเงินที่พัก; C3 แผนภาพทั้งสี่ render จริง ชื่อ Entity/Attribute และผู้รับผิดชอบสอดคล้อง และเปิด Mockup ครบสามส่วนทั้งจอคอมพิวเตอร์และมือถือ

ตัวตรวจ ERD ครั้งแรกอ่านเครื่องหมายความสัมพันธ์ผิดเป็นหัว Entity จึงรายงานไม่พบ Employee ทั้งที่มีอยู่ แก้ตัวตรวจแล้วผ่าน โดยเก็บผลครั้งแรกไว้ การ render และการตรวจโครงสร้างจึงต้องอ่านร่วมกับการตรวจความหมาย ไม่ใช้คะแนนอัตโนมัติอย่างเดียว

[เปิดเอกสารพร้อมแผนภาพ]({e}/output.render.html) · [อ่าน Markdown]({e}/output.md) · [เปิด Mockup]({e}/mockup.html) · [อ่าน Trace]({e}/trace.md) · [ผลตรวจ]({e}/verification.json) · [ผลตัวตรวจครั้งแรก]({e}/verification-parser-attempt1.json) · [Prompt ที่ใช้]({e}/prompt-used.md)

---

<a id="graph-lab-3"></a>

#### 2.4.3 แล็บโจทย์ 3 — ย้ายระบบคลินิกพร้อม Mockup และ Change Request

**ผลงานเฟสแรก:** As-Is Process (กระบวนการปัจจุบัน), Data Quality Findings (ปัญหาคุณภาพข้อมูล), To-Be Process (กระบวนการใหม่) และ Data Model (แบบจำลองข้อมูล), Data Mapping (การจับคู่ข้อมูล) และแผนย้าย, Gap Analysis (สิ่งที่ยังขาด) และแผนทยอยใช้ระบบ, Plan Version Log (บันทึกแผน) พร้อม Mockup สามส่วน

![ข้อค้นพบข้อมูลคลินิก ระบุแถว หลักฐาน ผลกระทบ และวิธีจัดการ]({c}/screen-document-table.png)

![Mockup ตารางนัดหมายกลางและข้อมูลรอยืนยัน]({c}/phase1-1440-appointments.png)

![Mockup จองหรือแก้ไขนัด พร้อมตัวอย่างความเสี่ยงเวลาชน]({c}/phase1-1440-booking.png)

![Mockup คิวตรวจข้อมูลก่อนย้าย]({c}/phase1-1440-review.png)

**การส่งงานและการใช้ผลเดิมต่อ**

| Node | เฟสแรก | หลังเพิ่มความยินยอมและ LINE OA |
| --- | --- | --- |
| N1 | Findings และ contract | N1-v2 เพิ่มข้อมูลกลางที่ต้องใช้ |
| N2 | As-Is | ใช้ไฟล์เดิมและ hash เดิม เพราะข้อกำหนดใหม่ไม่เปลี่ยนสภาพปัจจุบัน |
| N3 | To-Be, Data Model และ Mockup | N3-v2 เพิ่มกระบวนการ แบบจำลอง และหน้าจอสองส่วน |
| N4 | Mapping และ Migration | N4-v2 เพิ่มหลักฐานความยินยอมและการเชื่อมบัญชี |
| N5 | รวม Gap/Roll-out/Plan v1 และตรวจ | N5-v2 รอ N2 เดิมกับ N3-v2/N4-v2 แล้วรวมและตรวจ Plan v2 |

ก่อนแก้เฟสสองตรวจพบว่า baseline ยังขาดสองข้อใหม่ใน C1 จึงติดตามส่วนที่ต้องเปลี่ยนผ่าน Dependency คง raw, Findings, normalization และสามส่วน UI เดิมไว้

![Mockup ความยินยอมหลัง Change Request]({c}/phase2-1440-consent.png)

![Mockup จองเองผ่าน LINE OA หลัง Change Request]({c}/phase2-1440-line-booking.png)

![Impact และ Reuse ระบุ Node ที่ทำใหม่และที่ใช้ต่อ]({c}/screen-impact.png)

**หลักฐานตามเกณฑ์:** C1 ครบทั้งเอกสารและ Mockup รวมข้อกำหนดใหม่; C2 อ่านเทียบ Findings เก้าประเภทกับ R1–R5 และตรวจวันของ R5 ด้วย Python; C3 มีกติกาปรับชื่อ/เบอร์และกรณีให้คนยืนยัน แผนภาพเฟสแรกสามบล็อกและเฟสสองห้าบล็อก render ได้จริง Mockup เปิดครบทั้งความกว้าง 1440 และ 390 พิกเซล ไม่พบ console/page error หรือหน้าล้นแนวนอน

หน้าจอเป็นข้อมูลจำลอง ไม่ย้ายข้อมูลหรือเชื่อม LINE จริง วันที่ ตัวตน ระยะเวลาบริการ และนโยบายความยินยอมยังต้องยืนยันก่อนใช้จริง

[เปิดเอกสารพร้อมแผนภาพ]({c}/output.render.html) · [เปิด Mockup สุดท้าย]({c}/mockup.html) · [ดู Mockup เฟสแรก]({c}/mockup-phase1.html) · [อ่าน Trace]({c}/trace.md) · [ผลตรวจเฟสแรก]({c}/verification-phase1.json) · [ผลตรวจสุดท้าย]({c}/verification.json) · [Prompt แรก]({c}/prompt-used.md) · [Change Request]({c}/prompt-phase2.md)

[วิธีตรวจซ้ำและไฟล์ทั้งรอบ]({base}/README.md) · [ตรวจลำดับ Dependency และ hash]({base}/dependency-audit.json)

'''
p=ROOT/'readme.md';s=p.read_text();marker='### สิ่งที่ควรเขียนได้หลังจบบท Graph';assert marker in s and '### 2.4 ' not in s
s=s.replace(marker,section+marker,1)
s=s.replace('เก็บผลการรันใหม่พร้อมหลักฐานของตนเอง โดยไม่ใช้ผลการทดลองเดิมแทน','เก็บผลการรันใหม่พร้อมหลักฐานของตนเอง โดยไม่ใช้ผลการทดลองเดิมแทน ดูผลทดลอง Graph รอบใหม่ประกอบได้ในข้อ 2.4')
s=s.replace('ส่วนบท Graph มี Template และ Prompt สำหรับรันใหม่ โดยนำตัวอย่างผลเดิมออกแล้ว ส่วนบท Dynamic ยังเป็นบันทึกเดิมและต้องปรับลิงก์เมื่อมีผลรันใหม่','ส่วนบท Graph ข้อ 2.4 ใช้ผลทดลองรอบใหม่ครบสามโจทย์ รวม Mockup และ Change Request ของคลินิก โดยเป็นการจำลองบทบาทในบทสนทนาเดียวและตรวจเครื่องมือจริง ส่วนบท Dynamic ยังเป็นบันทึกเดิมและต้องปรับลิงก์เมื่อมีผลรันใหม่')
s=s.replace('### เทียบโจทย์เดียวกันผ่านหลักฐานเดิม','### เทียบโจทย์เดียวกันผ่านหลักฐานในบทเรียน')
s=s.replace('| เบิกค่าใช้จ่าย | ตรวจเอกสารย้อนกับข้อมูลสัมภาษณ์ | ตรวจความสอดคล้องของแบบจำลองตอนรวม |','| เบิกค่าใช้จ่าย | ตรวจเอกสารย้อนกับข้อมูลสัมภาษณ์ | ใช้ N1b เก็บข้อขัดแย้งและรวมเอกสารกับ Mockup |')
s=s.replace('| คลินิกหลัง Change Request | ตรวจพบส่วนที่ขาด แล้วแก้ตามเกณฑ์ | ระบุ Node ที่ต้องรันซ้ำตามข้อมูลที่เปลี่ยน |','| คลินิกหลัง Change Request | ตรวจพบส่วนที่ขาด แล้วแก้ตามเกณฑ์ | ทำ N1/N3/N4/N5 รุ่นใหม่และใช้ N2 เดิม |')
p.write_text(s)
for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',section):
 if not link.startswith('#'):assert (ROOT/link).exists(),link
assert all(s.count('id="graph-lab-'+str(i)+'"')==1 for i in [1,2,3])
print('Graph section 2.4 added with 3 separate labs, fresh screenshots, node traces and verification links. Dependency/hash audit PASS.')
