# Input ของ LAB 005

## ที่มาและการเปิดเผยตามลำดับ

กรณีศึกษาใช้ [ต้นฉบับภาคผนวก](../../../appendix-a-restaurant.md) และ [สำเนาที่ตรวจแล้ว](../../docs/case-study-source.md)
อ่าน [ปัญหาข้อมูลและสมมติฐาน](../../docs/data-issues.md) เพื่อคงข้อค้างเดิม
ผลงานตั้งต้นมาจาก LAB 002–004 ของนักศึกษาหรือผลอ้างอิงที่มีไฟล์จริง
อย่าใช้ README, log หรือไฟล์ที่ระบุ INPUT_STATUS: MISSING แทนผลงาน

| ข้อมูล | ผลนักศึกษา | ผลอ้างอิงสำรอง | สำเนาที่ใช้ใน LAB นี้ |
|---|---|---|---|
| FR/NFR | `../../002_LAB_Loop_FR_NFR/work/fr-nfr-vN.md` รุ่นที่มีผลตรวจผ่าน | เลือกไฟล์ที่ตรวจผ่านจริงใน `../../002_LAB_Loop_FR_NFR/reference/` | `work/baseline/fr-nfr.md` |
| Flow รวม พร้อม state/structure ที่อ้าง | `../../003_LAB_Static_Graph_Flow_Structure/work/` ตามผล merge | เลือกชุด final จริงใน `../../003_LAB_Static_Graph_Flow_Structure/reference/` | `work/baseline/flow.md` และเอกสารประกอบที่จำเป็น |
| UI | `../../004_LAB_Conditional_Graph_UI_Mockup/work/ui-mockup.html` | `../../004_LAB_Conditional_Graph_UI_Mockup/reference/final/ui-mockup.html` | `work/baseline/ui-mockup.html` |
| สัญญา selector | `../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md` | ใช้สัญญาเดียวกับ UI รุ่นที่เลือก | `work/baseline/ui-contract.md` |

path ในตารางอ้างจาก input/; เมื่อรันจากโฟลเดอร์ LAB ใช้ `../004_LAB_Conditional_Graph_UI_Mockup/reference/final/ui-mockup.html`
ไฟล์ผลอ้างอิงอาจยังไม่พร้อมตอนอ่านคู่มือ ให้ตรวจว่ามีจริง ไม่อ้างว่ารันหรือผ่านแล้ว
หากไม่มีผลครบ ให้หยุดขั้น 5.0 และบันทึกสิ่งที่ขาด; ยังศึกษา schema และตารางตัวอย่างได้
US-07 มีใน FR/NFR ของ LAB 002–003 แต่ไม่อยู่ในขอบเขต UI ของ LAB 004 จึงห้ามเดาว่า UI เดิมรองรับแล้ว

## เตรียมสำเนาโดยไม่เขียนทับ

คำสั่งนี้รันจาก `AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/`
แก้ path ของ SOURCE_FR และ SOURCE_FLOW ให้เป็นไฟล์รุ่นที่ตรวจแล้วจริงก่อนรัน
SOURCE_UI เลือกผลของตนเองได้; ตัวอย่างแสดงตำแหน่งผลอ้างอิงที่ตกลงใช้ร่วมกัน
เก็บผลตรวจ upstream ที่เกี่ยวข้องเป็นสำเนาใน work/baseline/ เพิ่ม และระบุชื่อใน work/input-source.md

```bash
export SOURCE_FR='../002_LAB_Loop_FR_NFR/work/fr-nfr-vN.md'
export SOURCE_FLOW='../003_LAB_Static_Graph_Flow_Structure/work/<ไฟล์ผล-merge-จริง>.md'
export SOURCE_UI='../004_LAB_Conditional_Graph_UI_Mockup/reference/final/ui-mockup.html'
export SOURCE_CONTRACT='../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md'
python3 - <<'PYCODE'
import os, hashlib
from pathlib import Path
pairs=[('SOURCE_FR','fr-nfr.md'),('SOURCE_FLOW','flow.md'),
       ('SOURCE_UI','ui-mockup.html'),('SOURCE_CONTRACT','ui-contract.md')]
sources=[(Path(os.environ[k]),name) for k,name in pairs]
assert all(p.is_file() and p.stat().st_size for p,_ in sources), 'ไฟล์ต้นทางไม่ครบ'
assert not Path('work/baseline').exists(), 'มี baseline เดิม: ใช้สำเนา LAB ชุดใหม่'
assert not Path('work/input-source.md').exists(), 'มีบันทึกเดิม ห้ามทับ'
Path('work/baseline').mkdir(parents=True)
records=['# ที่มาของ Input', '', '| ต้นทาง | สำเนา | SHA-256 | ที่มา | ผลตรวจ upstream |',
         '|---|---|---|---|---|']
for src,name in sources:
    data=src.read_bytes(); dst=Path('work/baseline')/name
    with dst.open('xb') as f: f.write(data)
    kind='ใช้ผลอ้างอิง' if 'reference' in src.parts else 'ใช้ผลนักศึกษา/สัญญาที่จัดให้'
    records.append(f'| {src} | {dst} | {hashlib.sha256(data).hexdigest()} | {kind} | รอระบุหลักฐาน |')
with Path('work/input-source.md').open('x') as f: f.write('\n'.join(records)+'\n')
# เก็บเฉพาะ US ตั้งต้น 18 แถว ไม่ส่งข้อความ reveal เข้าบริบทเริ่มต้น
excluded={'US-09','US-14','US-17','US-18','US-21','US-22','US-23','US-24'}
source=Path('../../appendix-a-restaurant.md').read_text().splitlines()
header=next(x for x in source if x.startswith('| ID |'))
selected=[x for x in source if x.startswith('| US-') and x.split('|')[1].strip() not in excluded]
assert len(selected)==18
with Path('work/baseline/us-initial.md').open('x') as f:
    f.write(header+'\n'+source[source.index(header)+1]+'\n'+'\n'.join(selected)+'\n')
PYCODE
```

หลังคัดลอก ให้เพิ่ม path ผลตรวจจริงและข้อค้างในบันทึก โดยรักษาประวัติที่มีอยู่
หากเลือกไฟล์จาก reference ต้องคงคำว่า **ใช้ผลอ้างอิง** ไม่อ้างเป็นผลรันของตนเอง
บันทึกรุ่นต้นทางและ SHA-256; การเปลี่ยนชื่อเป็น baseline ไม่ได้ทำให้รุ่นต้นทางหายไป
ถ้า Flow อ้างเอกสารอื่น ต้องคัดลอกครบและทำ mapping path ใน input-source.md
ก่อนเริ่ม plan-v1 ตรวจว่า baseline ไม่มีเนื้อหาของ US ที่กันไว้หลุดมาจาก LAB 001
หากพบ ให้เก็บสำเนาต้นทางและบันทึกจุดที่พบ แล้วสร้างชุด baseline ใหม่ที่ตัดเฉพาะขอบเขตดังกล่าวพร้อม diff
การกล่าวถึงรหัส US อื่นภายในเซลล์ต้นฉบับไม่ใช่การอนุญาตให้เปิดทั้งแถวนั้น
ไม่อ่าน reveal ล่วงหน้า แม้ไฟล์จะอยู่ในเครื่อง; ใช้ session ใหม่ทุกบทบาทและส่งเฉพาะ input ที่กำหนด

## ไฟล์ที่จัดให้

- [reveal-1.md](reveal-1.md): เปิดในขั้น 5.3 เท่านั้น
- [reveal-2.md](reveal-2.md): เปิดในขั้น 5.5 เท่านั้น
- [plan.schema.json](plan.schema.json): JSON Schema draft-07
- [plan-v0.example.json](plan-v0.example.json): ตัวอย่างโครงสร้าง ไม่ใช่ผลรันหรือแผนตั้งต้นที่ผ่านตรวจ

ทั้งสอง reveal เป็นการเปิดเผยข้อมูลที่มีในต้นฉบับอยู่แล้ว ไม่ใช่ข้อกำหนดใหม่
ทุกแถวคัดตรงตัวทุกคอลัมน์จาก appendix; คำถามท้ายไฟล์เป็นกิจกรรมวิเคราะห์ ไม่ใช่ AC

## สัญญาแผนและประวัติ

version เป็นสตริง `plan-vN`; trigger อธิบายเหตุการณ์พร้อม path หลักฐาน
created_at เป็นเวลา UTC รูปแบบ ISO 8601 ลงท้าย Z; ตัวอย่าง v0 ใช้เวลาสมมติที่ติดป้ายแล้ว
tasks ทุกงานต้องมี id, title, kind, inputs, outputs, depends_on, status, reason, us_refs
kind = create / revise / verify / cancel; status = planned / running / done / reused / needs_recheck / cancelled
id ใช้ชื่อเช่น revise-fr หรือ verify-ui หลีกเลี่ยงรหัสภายในทีมผู้จัดทำ
inputs/outputs เป็น array ของ path; depends_on เป็น array ของ task id ในแผนเดียวกัน
decisions เก็บ topic, decision, authority และ evidence; human-required ต้องผูกงานที่รอใน limits
reuse เก็บ artifact, source_version, disposition, reason, evidence; disposition = reuse / recheck / replace
limits เก็บ id, description, blocking, affected_tasks; [] หมายถึงไม่มีรายการ ไม่ใช่ยังไม่ได้ตรวจ
schema ตรวจชนิดข้อมูลและ enum; ต้องตรวจเพิ่มว่า id ไม่ซ้ำ dependency มีจริง ไม่ชี้ตัวเอง และไม่มีวงจร
งานที่ถูกยกเลิกต้องคงอยู่ด้วย kind=cancel/status=cancelled พร้อมเหตุผล และห้ามงานอื่นรอผลของมัน
การยกเลิกงานในแผนไม่ได้ยกเลิกข้อกำหนดธุรกิจหรือออเดอร์

แผน plan-v1.json/md, plan-v2.json/md และ plan-v3.json/md เป็น snapshot ห้ามแก้ทับ
Executor บันทึกความคืบหน้าใน `work/execution/plan-vN/<RUN_ID>/<TASK_ID>.md` แบบเพิ่มไฟล์ใหม่
Evaluator บันทึกใน `work/evaluations/plan-vN/<RUN_ID>.md` โดยระบุ hash แผน/ผลที่ตรวจ
Planner รุ่นถัดไปจึงรวมสถานะจากหลักฐานเหล่านี้; ไม่ถือว่า planned กลายเป็น done เพราะเวลาผ่านไป
แผนล่าสุดคือเลข N สูงสุดที่ JSON กับ Markdown ครบและผ่าน schema; ถ้ามีรุ่นใหม่ค้าง/ผิด หยุด ไม่ถอยใช้รุ่นเก่าเงียบ ๆ
ก่อนลงมือ แผนล่าสุดต้องมีผลตรวจ PLAN_READY และไม่มี blocking limit สำหรับงานที่จะทำ
เก็บ `work/impact-analysis-v2.md`, `work/impact-analysis-v3.md` แบบไม่ทับรุ่น
`work/impact-analysis.md` เป็นบันทึกรวม: สร้างครั้งแรกแล้วเพิ่มท้ายเฉพาะหัวข้อรุ่นใหม่ ห้ามแก้ส่วนรุ่นเดิม

## สมมติฐานและข้อจำกัด

การเปลี่ยนงานและ dependency เป็นการตัดสินใจในงานวิเคราะห์ที่ AI ทำได้ตามขอบเขตที่อนุญาต
นโยบายคืนเงินจริง การแมปสถานะที่ต้นฉบับไม่ชัด และความสัมพันธ์ของช่วงเร่งด่วนต้องรอยืนยันจากมนุษย์
หมายเหตุ ก./ค./ช. ยังไม่มีนิยาม; ห้ามเติมรายละเอียดให้ดูเหมือนต้นฉบับ
US-20 อ้าง US-14 ในเกณฑ์กฎปิด/เปิดเดิม ให้คงข้อความและบันทึกข้อสงสัย ไม่แก้ต้นฉบับเงียบ ๆ
UI เป็นข้อมูลจำลอง; หลักฐานในเครื่องเดียวไม่ยืนยันเกณฑ์ LAN, การโอนเงินจริง หรือความปลอดภัยจริง
เนื้อหาในชุดนี้ยังไม่มีผลรัน Prompt นักศึกษา; เวลา รอบ โทเคน และต้นทุน: ไม่มีข้อมูล
