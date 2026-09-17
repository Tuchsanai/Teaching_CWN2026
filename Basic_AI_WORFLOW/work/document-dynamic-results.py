from pathlib import Path
import json,re,hashlib
r=Path(Path('work/dynamic-current-run.txt').read_text());rel=r.relative_to(Path.cwd()).as_posix()
# Make committed verification helpers resolve their suite independently of scratch pointers.
for name in ['verify-docs.py','render-docs.py']:
 p=r/'source'/name;s=p.read_text().replace("Path(Path('work/dynamic-current-run.txt').read_text())","Path(__file__).resolve().parents[1]");p.write_text(s)
(r/'README.md').write_text('''# Dynamic Workflow — ผลรอบสาธิต

ใช้ Prompt จากหัวข้อ 3.3 และ Dynamic Template 3.2 จำลอง Planner/Executor/Evaluator ในบทสนทนาเดียว ไม่ได้เรียกโมเดลแยกบทบาท โค้ดสร้างผลงานและตัวตรวจดัดแปลงจากชุด Graph รอบก่อน จึงเป็นการสาธิตแบบรู้ตัวอย่างคำตอบแล้ว ไม่ใช่การทดลองอิสระสำหรับเปรียบเทียบประสิทธิภาพเวิร์กโฟลว์

โค้ดใน source/ สร้างไฟล์และบันทึกการตัดสินที่ออกแบบไว้ในรอบนี้ เงื่อนไข Re-plan ของระบบเบิกค่าใช้จ่ายเป็นกรณีสาธิตที่กำหนดไว้จากข้อขัดแย้งในโจทย์ ไม่ใช่การค้นพบโดยโมเดลอิสระระหว่างรัน แต่การตรวจ Dependency, สถานะ, hash, Playwright และการ render Mermaid รันจริงใหม่ทั้งหมด ไม่คัดลอกภาพหรือ PASS เก่ามาเป็นหลักฐาน

## อ่านหลักฐาน

แต่ละโจทย์มี prompt-used.md/input-used.md, plans/plan-v1-initial.*, snapshot หลังแต่ละงาน, plan-current.md/json, events.jsonl, execution-table.md, trace.md, ผลงาน, verification.json และภาพใหม่

- จองห้อง: Plan v1 จบโดยไม่ต้อง Re-plan
- เบิกค่าใช้จ่าย: Plan v2 เพิ่ม T1b เก็บข้อขัดแย้งวงเงิน และเพิ่ม Dependency ให้ T5
- คลินิก: เฟสแรก Plan v1; หลัง Change Request เป็น v2 เพิ่มงานที่ได้รับผลกระทบ ใช้ T2 As-Is เดิมโดยไม่รันซ้ำ พร้อม output-phase1.md และ mockup-phase1.html สำหรับเทียบ

ผล semantic review เป็นการตรวจในบทสนทนาเดียวและอ่านผลงานที่ใช้โค้ดตัวอย่างเป็นฐาน ไม่ใช่คะแนนของผู้ประเมินอิสระ ภาพ Mockup เบิกเงินและคลินิกไม่ทำธุรกรรมจริง

## รันตรวจซ้ำบน Remote

ต้องมี Python/Playwright, Chromium และ Mermaid ตามตำแหน่งที่สคริปต์ระบุ

```sh
/opt/venv/bin/python 1_meeting_room/tasks/T4-test.py
/opt/venv/bin/python source/verify-docs.py
/opt/venv/bin/python source/render-docs.py
```

คำสั่งตรวจซ้ำจะเขียนผลตรวจ/ภาพในชุดนี้ใหม่ ควรคัดลอกชุดผลทดลองก่อนหากต้องการเก็บ baseline เดิม สคริปต์สร้างผลงานใน source/ ต้องมีแผนและสถานะเริ่มต้นก่อนทำงาน; ไม่ควรรันซ้ำทับสถานะ DONE

ดู [ข้อมูลวิธีรัน](run-info.json) และ [ผลตรวจลำดับงาน/สถานะ/hash](dependency-audit.json)
''')
section='''### 3.4 ผลลัพธ์จากการทดลอง Dynamic Workflow: โจทย์ 1 → 2 → 3

นำ Prompt ในข้อ **3.3** มาใช้กับทั้งสามโจทย์ โดยเก็บ Plan, การทำงานของ EXECUTOR, คำตัดสินของ EVALUATOR และผลทดสอบพร้อมภาพ เหมือนรูปแบบการอ่านผลในข้อ 1.4 และ 2.4

**วิธีรันและขอบเขตของหลักฐาน:** รอบนี้เป็นการสาธิตบทบาทในบทสนทนาเดียว ใช้โค้ดสร้างผลงานและตัวตรวจที่ดัดแปลงจากรอบ Graph เป็นฐาน รวมถึงกรณี Re-plan ที่ออกแบบไว้ จึงไม่ใช่การทดลองอิสระแบบไม่รู้คำตอบหรือหลักฐานว่า Dynamic ดีกว่า Graph การเปิดเว็บ การคลิกทดสอบ การ render แผนภาพ และภาพหน้าจอรันใหม่จริงบน Remote ไม่ใช้ภาพหรือ PASS เก่าแทนผลรอบนี้

| โจทย์ | แผนสุดท้าย | Re-plan | เหตุผลและผลตรวจ |
| --- | --- | --- | --- |
| จองห้องประชุม | v1 | 0 | แผนเดิมครอบคลุมงาน; C1–C3 ผ่าน |
| เบิกค่าใช้จ่าย | v2 | 1 | เพิ่มงานจัดการข้อขัดแย้งวงเงิน; C1–C3 ผ่าน |
| ย้ายระบบคลินิก | v2 | 1 | เพิ่มความยินยอมและ LINE OA หลังเฟสแรก; C1–C3 ผ่านทั้งสองเฟส |

**เลือกอ่านทีละแล็บ:** [1. จองห้อง](#dynamic-lab-1) · [2. เบิกค่าใช้จ่าย](#dynamic-lab-2) · [3. คลินิก](#dynamic-lab-3)

---

<a id="dynamic-lab-1"></a>

#### 3.4.1 แล็บโจทย์ 1 — เว็บจองห้องประชุม

**ผลงาน:** เว็บหน้าเดียว แสดงห้อง ดูเวลาว่าง จอง ยกเลิก และดูสถานะ ข้อมูลสาธิตอยู่ในหน่วยความจำ รีเฟรชแล้วเริ่มใหม่

![เว็บจองห้องจากรอบ Dynamic](BASE/1_meeting_room/screen-overview.png)

**แผนและการตัดสิน:** T1 วิเคราะห์ข้อกำหนด → T2 ตรรกะ / T3 หน้าจอ / T4 สคริปต์ตรวจ → T5 รวมและตรวจ โดยทำทีละงานเมื่อ Dependency พร้อม EVALUATOR ไม่พบเหตุที่ต้องเปลี่ยนแผน จึงจบที่ v1 ไม่สร้าง v2 เพื่อให้ดูเหมือนมีการปรับแผน

![Plan v1 หลังงานจองห้องเสร็จ](BASE/1_meeting_room/screen-plan.png)

**หลักฐานตามเกณฑ์:** ทดลองครบห้าฟีเจอร์ ตรวจเวลาซ้อน ช่วงเวลาผิด และเวลาที่คืนหลังยกเลิก ไม่พบ console/page error และหน้า 390 พิกเซลไม่ล้นแนวนอน ห้อง ฟอร์ม และสถานะเข้าถึงได้ทันที ส่วนดูเวลาว่างและยกเลิกรายการตัวอย่างใช้หนึ่งคลิก การนับเป็นการเข้าถึงฟีเจอร์ ไม่รวมกรอกและส่งฟอร์ม และอนุญาตให้เลื่อนหน้า

![ผลหลังยกเลิกการจอง](BASE/1_meeting_room/screen-cancelled.png)

[ไฟล์เว็บ](BASE/1_meeting_room/output.html) · [Prompt](BASE/1_meeting_room/prompt-used.md) · [บันทึกการทำงาน](BASE/1_meeting_room/execution-table.md) · [Trace](BASE/1_meeting_room/trace.md) · [ผลทดสอบ](BASE/1_meeting_room/verification.json)

---

<a id="dynamic-lab-2"></a>

#### 3.4.2 แล็บโจทย์ 2 — ข้อกำหนดและ Mockup ระบบเบิกค่าใช้จ่าย

**ผลงาน:** ข้อกำหนด FR/BR/NFR แผนภาพ Use Case, ERD, Sequence, State ตารางเชื่อมสัมภาษณ์ และ Mockup ยื่นเบิก ติดตาม และตรวจ/อนุมัติ โดยไม่ทำธุรกรรมจริง

![ข้อกำหนดจากรอบ Dynamic](BASE/2_expense_claim/screen-document-table.png)

**จุดปรับแผนในกรณีสาธิต:** หลัง T1 เก็บหลักฐานวงเงิน 5,000/10,000 EVALUATOR ระบุว่าแผนยังขาดงานจัดการข้อขัดแย้ง PLANNER จึงเพิ่ม T1b และให้ T5 รอ T1b ก่อนตรวจรับ ข้อกำหนดจาก T1 ใช้ต่อ ไม่เลือกวงเงินฝ่ายใดและไม่แต่งวงเงินค่าที่พัก

| ส่วนที่เปลี่ยน | Plan v1 → Plan v2 |
| --- | --- |
| เหตุผล | พบงานจัดการข้อขัดแย้งที่ยังไม่มีในแผน |
| Changes | เพิ่ม T1b และ Dependency ของ T5 |
| Impact | Open Issues และหน้าตรวจต้องแสดงรอยืนยันนโยบาย |
| Reuse | หลักฐานสัมภาษณ์และข้อกำหนดของ T1 |

![Plan v2 ของงานเบิกค่าใช้จ่าย](BASE/2_expense_claim/screen-plan.png)

![หน้าจำลองยื่นเบิก](BASE/2_expense_claim/phase1-1440-submit.png)

![หน้าจำลองติดตามใบเบิก](BASE/2_expense_claim/phase1-1440-tracking.png)

![หน้าจำลองตรวจและอนุมัติ](BASE/2_expense_claim/phase1-1440-review.png)

**หลักฐานตามเกณฑ์:** ครบเอกสารและ Mockup สามส่วน; สัมภาษณ์สิบหน่วยความหมายเชื่อมกับ FR/BR และคงข้อขัดแย้งทั้งสองประโยค; Entity/Attribute และสถานะสอดคล้องกับ ERD; แผนภาพสี่บล็อก render จริง และเปิด Mockup ที่ 1440/390 พิกเซลผ่าน โดยตรวจภาพและข้อความ ไม่อ้างว่าปุ่มอนุมัติหรือจ่ายเงินทำงานจริง

[เอกสาร](BASE/2_expense_claim/output.md) · [Mockup](BASE/2_expense_claim/mockup.html) · [Prompt](BASE/2_expense_claim/prompt-used.md) · [Plan v2](BASE/2_expense_claim/plan-current.md) · [บันทึกการทำงาน](BASE/2_expense_claim/execution-table.md) · [ผลทดสอบ](BASE/2_expense_claim/verification.json)

---

<a id="dynamic-lab-3"></a>

#### 3.4.3 แล็บโจทย์ 3 — ย้ายระบบคลินิกพร้อม Mockup และ Change Request

**เฟสแรก:** ส่งเอกสารหกส่วนและ Mockup ตารางนัดหมาย จอง/แก้ไข และตรวจข้อมูลก่อนย้าย พบปัญหาเก้าประเภทพร้อมแถวต้นทาง โดยคงวัน/ปี/ตัวตนที่กำกวมไว้รอยืนยัน แผน v1 มีงานตรวจคุณภาพข้อมูลอยู่แล้ว จึงยังไม่ต้อง Re-plan

![ข้อค้นพบคุณภาพข้อมูล](BASE/3_clinic_migration/screen-document-table.png)

![Mockup ตารางนัดหมายเฟสแรก](BASE/3_clinic_migration/phase1-1440-appointments.png)

![Mockup ตรวจข้อมูลก่อนย้าย](BASE/3_clinic_migration/phase1-1440-review.png)

**เฟสสอง:** หลังผลงานเฟสแรกผ่าน ส่ง Change Request ตามข้อ 3.3 ในงานเดิม EVALUATOR ระบุว่าขอบเขตใหม่ยังขาดส่วนความยินยอมและ LINE OA จึงสร้าง Plan v2 พร้อมผลกระทบและส่วนที่ใช้ต่อ

| งาน | การตัดสินใน Plan v2 |
| --- | --- |
| T1 ข้อมูลกลาง | เพิ่ม T1-v2 สำหรับข้อมูลและข้อกำหนดใหม่ |
| T2 As-Is | ใช้ผลงานเดิม ไม่ทำซ้ำ |
| T3 To-Be / Data Model / Mockup | เพิ่ม T3-v2 รองรับความยินยอมและจองผ่าน LINE |
| T4 Mapping / Migration | เพิ่ม T4-v2 ตรวจข้อมูลที่ขอบเขตใหม่ต้องใช้ |
| T5 รวมและตรวจ | เพิ่ม T5-v2 ตรวจเอกสาร แผนภาพ และ Mockup อีกครั้ง |

![Plan v2 ของคลินิก](BASE/3_clinic_migration/screen-plan.png)

![หน้าจำลองความยินยอม](BASE/3_clinic_migration/phase2-1440-consent.png)

![หน้าจำลองจองผ่าน LINE OA](BASE/3_clinic_migration/phase2-1440-line-booking.png)

**หลักฐานตามเกณฑ์:** เฟสแรกแผนภาพสามบล็อกและ Mockup สามส่วนผ่าน เฟสสองแผนภาพห้าบล็อกและ Mockup ห้าส่วนผ่านที่ 1440/390 พิกเซล เก็บ Findings และวิธีปรับรูปแบบข้อมูลเดิมไว้ ตรวจ hash และ event ว่า T2 ถูกใช้ต่อโดยไม่ทำซ้ำ ช่องความยินยอมไม่ติ๊กล่วงหน้าและ LINE เป็นภาพจำลอง ไม่เชื่อมบริการจริง

[เอกสารเฟสแรก](BASE/3_clinic_migration/output-phase1.md) · [เอกสารสุดท้าย](BASE/3_clinic_migration/output.md) · [Mockup สุดท้าย](BASE/3_clinic_migration/mockup.html) · [Prompt เฟสแรก](BASE/3_clinic_migration/prompt-used.md) · [Change Request](BASE/3_clinic_migration/prompt-phase2.md) · [Trace](BASE/3_clinic_migration/trace.md) · [ผลเฟสแรก](BASE/3_clinic_migration/verification-phase1.json) · [ผลสุดท้าย](BASE/3_clinic_migration/verification.json)

[วิธีรันและขอบเขตหลักฐานของชุดนี้](BASE/README.md) · [ผลตรวจ Dependency สถานะและ hash](BASE/dependency-audit.json)
'''.replace('BASE',rel)
p=Path('readme.md');s=p.read_text();assert '### 3.4 ' not in s;p.write_text(s.rstrip()+'\n\n'+section)
for target in re.findall(r'\]\(([^)]+)\)',section):
 if not target.startswith('#'):assert Path(target).is_file(),target
for p in sorted(r.glob('[123]_*')):
 hashes={x.relative_to(p).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob('*') if x.is_file() and x.name!='sha256.json'};(p/'sha256.json').write_text(json.dumps(hashes,indent=2))
print('Added README 3.4 with three result sections; every linked artifact exists.')
