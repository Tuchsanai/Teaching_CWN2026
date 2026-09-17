# AI Workflow Engineering: Loop · Graph · Dynamic Workflow

โจทย์เดิม แต่เปลี่ยนวิธีออกแบบ Workflow → ผลลัพธ์ที่ได้ต่างกัน

สื่อการสอนภาษาไทยฉบับอ่าน อ้างอิง [AI_Workflow_Engineering.html](AI_Workflow_Engineering.html) ครบทั้งบทนำและบทที่ 1–4 อ่านแนวคิด Prompt ร่องรอย และผลเปรียบเทียบได้จากหน้านี้ ส่วนผลงานและหลักฐานฉบับเต็มเปิดผ่านลิงก์ของแต่ละการทดลอง

เปิดไฟล์สไลด์ด้วยเบราว์เซอร์ ใช้ปุ่มลูกศรเปลี่ยนหน้า กด `o` หรือปุ่ม **Overview** เพื่อดูภาพรวมแล้วเลือกหน้า สไลด์มี **107 หน้า** ตาม [tests/results.json](tests/results.json) ผลตรวจและข้อจำกัดอยู่ใน [docs/test-report.md](docs/test-report.md) ส่วนผลตรวจการทดลองอยู่ใน [tests/experiments-results.json](tests/experiments-results.json)

สารบัญ

- [บทนำ](#บทนำ)
- [บทที่ 1 Loop Engineering](#บทที่-1-loop-engineering)
- [บทที่ 2 Graph Engineering](#บทที่-2-graph-engineering)
- [บทที่ 3 Dynamic Workflow](#บทที่-3-dynamic-workflow)
- [บทที่ 4 สรุปและเปรียบเทียบ](#บทที่-4-สรุปและเปรียบเทียบ)
- [ภาคผนวก](#ภาคผนวก)

## บทนำ

### แนวคิดและ Learning Path

ใช้โจทย์กลางเดิมทดลองด้วย Workflow ต่างกัน แล้วเปรียบเทียบ **วิธีคิด → วิธีเขียน Prompt → ผลลัพธ์** ทุกชุดต้องมีร่องรอยระหว่างทาง เพราะความต่างของ Workflow อยู่ที่กระบวนการด้วย

| Workflow | สิ่งที่จะได้เรียนรู้ |
| --- | --- |
| Loop | ทำ → ตรวจ → แก้ วนจนผ่านเกณฑ์ |
| Graph | แตกงานเป็นส่วน ทำขนานกัน แล้วรวมกลับ |
| Dynamic | วางแผนก่อน ทำไปเจออะไรใหม่ก็ปรับแผนได้ |

![Learning Path: Loop ไป Graph ไป Dynamic แล้วเปรียบเทียบ](img/01-learning-path.png)

ภาพ Learning Path: จากวงจรที่เข้าใจง่าย ไปสู่การจัด Dependency การปรับแผน และการเลือก Workflow ให้เหมาะกับโจทย์

### เป้าหมายการเรียนรู้

1. อธิบายและออกแบบ Loop: Generate → Evaluate → Improve
2. อธิบายส่วนประกอบ Graph: Node, Edge, State, Dependency
3. ออกแบบ Sequential, Fan-out/Fan-in และ Conditional Graph
4. บอกความต่างของ Static Graph กับ Dynamic Workflow
5. ออกแบบ Planner–Executor–Evaluator
6. เขียน Prompt ควบคุมแต่ละ Workflow แล้วรันจริงบน Codex / Claude Code รวมถึงลองใช้ skill `cyolo` และ `yolo`
7. เปรียบเทียบโจทย์เดียวกันทั้ง 3 Workflow แล้วสรุปว่าสถานการณ์แบบใดควรใช้แบบใด

### โครงสร้างการสอน 5 ขั้น

| ขั้น | ชื่อ | เนื้อหา |
| --- | --- | --- |
| 1 | Theory | แนวคิด ส่วนประกอบ การทำงาน ปัญหาที่เหมาะ ข้อดีและข้อจำกัด |
| 2 | Workflow Diagram | รูป Excalidraw แสดงการไหลของงาน |
| 3 | Prompt Template | Template ครบ 8 ส่วน พร้อมเหตุผลในการออกแบบ |
| 4 | ทดลองจริง | เติมโจทย์ในช่อง REQUIREMENT แล้วดู Prompt → Process → Output |
| 5 | สังเกตผล | อ่านตารางร่องรอยและตอบคำถามจากหลักฐาน |

### รูปแบบมาตรฐาน 3 กล่อง

```text
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│ ① PROMPT ที่ป้อน   [📋] │ → │ ② PROCESS ที่เกิดขึ้น    │ → │ ③ OUTPUT ที่ได้          │
│ Template + โจทย์ ตัวเต็ม │   │ Iteration Log /         │   │ ผลสุดท้าย                │
│ (ห้ามย่อ · กด copy ได้)  │   │ Execution Trace /       │   │ ถ้าเป็นเว็บ → ฝังของจริง │
│                         │   │ Plan Version Log        │   │ ให้เปิดใช้ได้ในสไลด์     │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘
```

Prompt ต้องครบทั้ง Template และโจทย์; Process ต้องมาจากการรันจริง; Output ต้องเปิดตรวจได้ สไลด์มีปุ่ม Copy และกล่องเลื่อนสำหรับข้อความยาว มีเว็บที่คลิกได้และ Markdown ที่ render Mermaid แล้ว ในฉบับอ่านนี้ใช้โค้ดบล็อก ตาราง และลิงก์ไปไฟล์จริงแทนกล่องโต้ตอบ

### โจทย์กลาง 3 ข้อ

ทุกโจทย์ให้ AI วิเคราะห์ Requirement → สร้างโครงสร้างระบบ → สร้างผลลัพธ์ที่ตรวจสอบและเปรียบเทียบได้ แล้วทดลองครบทั้ง 3 Workflow

| โจทย์ | แนวงาน | ประเด็นฝึก | Workflow ที่คาดว่าเห็นจุดเด่น |
| --- | --- | --- | --- |
| จองห้องประชุม | Requirement → UI Prototype | ความครบของ feature และ UX | Loop |
| เบิกค่าใช้จ่าย | สัมภาษณ์ → System Model | ข้อขัดแย้งและความสอดคล้องของ artifact | Graph |
| ย้ายระบบนัดหมายคลินิก | As-Is → To-Be + Migration | สำรวจข้อมูล ขอบเขตไม่แน่นอน และ Change Request | Dynamic |

#### โจทย์ 1 — ระบบจองห้องประชุม

```text
สร้างเว็บไซต์สำหรับระบบจองห้องประชุม
ระบบต้องสามารถ: แสดงห้องประชุม, ดูเวลาว่าง, จองห้อง, ยกเลิกการจอง, แสดงสถานะการจอง
Output: Web UI Mock-up ที่เปิดและทดลองใช้งานได้
```

เกณฑ์ตรวจ: ครบ 5 feature เปิดและคลิกใช้งานจริงด้วย Playwright และ Navigation ไปถึงทุก feature ภายใน 2 คลิก

#### โจทย์ 2 — วิเคราะห์ Requirement ระบบเบิกค่าใช้จ่าย

Input คือบันทึกสัมภาษณ์ดิบ มีข้อขัดแย้งและข้อมูลที่ยังไม่ครบ

```text
[พนักงานฝ่ายขาย] อยากถ่ายรูปใบเสร็จแล้วเบิกได้เลย ไม่อยากกรอกเยอะ
                 ส่วนใหญ่เบิกค่าน้ำมัน ค่าที่พัก ค่ารับรองลูกค้า
[หัวหน้าทีม]     ผมต้องอนุมัติทุกใบ ถ้าเกิน 5,000 บาทต้องให้ผู้จัดการฝ่ายอนุมัติอีกชั้น
[ผู้จัดการฝ่าย]   อะไรเกิน 10,000 ค่อยส่งมาผม ต่ำกว่านั้นหัวหน้าทีมจบได้เลย
[ฝ่ายบัญชี]      ต้องตรวจใบเสร็จซ้ำ เคยมีคนเบิกใบเดียวสองรอบ
                 ต้องเบิกภายใน 30 วันนับจากวันที่ในใบเสร็จ จ่ายเงินรอบวันที่ 25 ของเดือน
[ฝ่ายบัญชี]      ค่ารับรองลูกค้าต้องระบุชื่อลูกค้าและชื่อบริษัท
[HR]             พนักงานแต่ละระดับมีวงเงินค่าที่พักต่อคืนไม่เท่ากัน
[พนักงานฝ่ายขาย] อยากเห็นว่าใบเบิกของเราค้างอยู่ที่ใคร
```

Output เป็น Markdown ไฟล์เดียว มี diagram เป็น Mermaid และประกอบด้วย Actor/Stakeholder, FR-xx และ NFR, BR-xx, Use Case Diagram, ERD, Sequence Diagram “ยื่นเบิก → อนุมัติ → จ่ายเงิน”, State Diagram ของใบเบิก, Traceability Matrix (ประโยคต้นทาง → FR/BR → Use Case → Entity) และ Open Issues

เกณฑ์ตรวจ:

- ทุกประโยคในบันทึก trace ไป FR/BR ได้อย่างน้อย 1 รายการ
- ตรวจพบข้อขัดแย้ง 5,000 vs 10,000 และส่งเป็น Open Issue โดยไม่ตัดสินเอง
- ไม่แต่งตัวเลขวงเงินค่าที่พัก
- Entity/Attribute ใน Sequence และ State ตรงกับ ERD
- State ตอบได้ว่า “ค้างอยู่ที่ใคร”
- Mermaid ทุกบล็อก render ได้

โจทย์นี้ใช้ฝึก fan-out สร้าง Use Case / ERD / Sequence แล้ว fan-in ตรวจความสอดคล้องและตัดสินข้อขัดแย้งด้วยหลักฐาน

#### โจทย์ 3 — ย้ายระบบนัดหมายคลินิกจาก Google Sheet สู่ระบบกลาง

```text
บริบท: คลินิกทันตกรรม 3 สาขา ใช้ Google Sheet แยกสาขา ร่วมกับจองผ่าน LINE ต้องการย้ายมาระบบนัดหมายกลาง

สาขา,วันที่,เวลา,ชื่อคนไข้,เบอร์,หมอ,บริการ,หมายเหตุ
ลาดกระบัง,03/09/2026,10:00,สมชาย ใจดี,081-234-5678,หมอเอ,ขูดหินปูน,
ลาดกระบัง,2026-09-03,10:00,สมชาย ใจดี,0812345678,หมอเอ,ขูดหินปูน,จองซ้ำทางไลน์
บางนา,3 ก.ย. 69,13:30,คุณมาลี,,หมอบี,จัดฟัน,ไม่มีเบอร์ ติดต่อทางไลน์
บางนา,03/09/2026,13:30,วิชัย ศรีสุข,089-111-2222,หมอบี,อุดฟัน,
อ่อนนุช,09/03/2026,09:00,Somchai Jaidee,081 234 5678,หมอเอ,ตรวจฟัน,หมอเอมาช่วยสาขานี้ทุกวันพุธ

งานรอบแรก:
1. As-Is Process (Mermaid flowchart)
2. Data Quality Findings (ปัญหา / แถว / ผลกระทบ)
3. To-Be Process และ Data Model
4. Data Mapping + แผน Migration (รวมวิธีจับคู่ตัวตนคนไข้)
5. Gap Analysis + Roll-out Plan
6. Plan Version Log
```

เกณฑ์ตรวจ: พบปัญหาข้อมูลอย่างน้อย 5 ประเภท ระบุความกำกวมโดยอ้างหลักฐาน มีกลยุทธ์จับคู่ตัวตนคนไข้พร้อมกรณีให้คนยืนยัน บันทึก Plan v1 → v2 พร้อมเหตุผล และทำ Impact Analysis ระบุ artifact ที่กระทบกับส่วนที่ reuse ได้

#### Change Request ของโจทย์ 3

ส่งหลังได้ Plan v1 โดยใช้ thread เดิม:

```text
เจ้าของคลินิกแจ้งเพิ่ม:
1. ต้องเก็บความยินยอมของคนไข้ตาม PDPA
2. คนไข้ต้องจองคิวเองผ่าน LINE OA ได้
```

| Workflow | แนวทางรับมือข้อมูลใหม่ตาม Template |
| --- | --- |
| Loop | CRITIC ตรวจใหม่ แล้ว GENERATOR แก้เฉพาะเกณฑ์ที่ FAIL |
| Graph | ระบุ Node ที่ต้องรันซ้ำ และ reuse ผลที่ input ไม่เปลี่ยน |
| Dynamic | NEW INFORMATION ทำให้ Re-plan พร้อมเหตุผล Impact และ Reuse |

### Prompt Anatomy: 8 ส่วน

![Prompt Anatomy แสดงส่วนประกอบของคำสั่ง](img/03-prompt-anatomy.png)

ภาพ Prompt Anatomy: ออกแบบคำสั่งให้บอกทั้งงาน วิธีทำ วิธีตรวจ และเงื่อนไขหยุด

| ส่วน | คำถามตอนออกแบบ | ตัวอย่าง |
| --- | --- | --- |
| Role | AI สวมบทบาทอะไร กี่บทบาท | แยกผู้เขียนกับผู้ตรวจ |
| Goal | งานเสร็จหน้าตาเป็นอย่างไร | ได้หน้าเว็บที่กดจองห้องได้ |
| Input | รับข้อมูลอะไร | Requirement หรือบันทึกสัมภาษณ์ |
| Workflow | ทำอะไรก่อนหลัง อะไรทำพร้อมกัน | Generate → Evaluate → Improve |
| Constraints | ห้ามทำอะไร | ห้ามแต่งตัวเลขที่โจทย์ไม่ได้ให้ |
| Evaluation Criteria | ตรวจอย่างไรให้ตอบผ่าน/ไม่ผ่าน | มีปุ่มยกเลิกหรือไม่ |
| Output Format | ส่งผลรูปแบบใด | Iteration Log และผลงานสุดท้าย |
| Stop Condition | เมื่อไรต้องหยุด | ผ่านครบหรือครบจำนวนรอบ |

เกณฑ์ที่ตอบได้ว่า **PASS หรือ FAIL** ช่วยให้ตรวจได้ชัดกว่า “ดี” “สวย” หรือ “ครบถ้วน” ที่ไม่ได้ระบุสิ่งที่ต้องตรวจ

| ส่วนที่เปลี่ยน | Loop | Graph | Dynamic |
| --- | --- | --- | --- |
| Role | Generator + Critic | ผู้ทำแต่ละ Node + Merger | Planner + Executor + Evaluator |
| Workflow | วงจรซ้ำ | ตาราง Node + Dependency | แผนที่แก้ไขได้ มี version |
| ต้องกำหนดเพิ่ม | เกณฑ์ผ่าน จำนวนรอบ | data contract กติกา Merge | เงื่อนไข Re-plan กติกาเปลี่ยนแผน |
| Output | Iteration Log | Execution Trace | Plan Version Log |

บรรทัด `//` ใน Template เป็นคำอธิบายสำหรับผู้เรียน และ Template สั่ง AI ให้ข้าม จึงคัดลอกได้ทั้งก้อน ก่อนรันให้แทนช่องข้อมูลในวงเล็บปีกกาด้วยโจทย์และเกณฑ์จริง

### วิธีรันการทดลอง

![Experiment Pipeline จาก Prompt ไป CLI หลักฐานและสไลด์](img/11-experiment-pipeline.png)

ภาพ Experiment Pipeline: เตรียม prompt → รัน CLI → เก็บ output/trace → ถอด events จาก log → capture ด้วย Playwright → ประกอบสื่อ

ใช้สำเนาโฟลเดอร์ทดลองใหม่ คง prompt ต้นฉบับ และเลือกคำสั่งตาม engine แทน `<task>` และ `<workflow>` ก่อนใช้:

```bash
cd experiments/<task>/<workflow>
# Codex CLI เฟสแรก
cyolo1 exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o response.md "$(cat prompt.md)" > log.jsonl
# หรือ Claude Code ชุดเสริม
yolo1 -p --model fable --effort high --strict-mcp-config --output-format stream-json --verbose "$(cat prompt.md)" > log.jsonl
# กลับรากโปรเจกต์เพื่อถอด log และถ่ายภาพ
cd ../../..
python3 tools/events_from_log.py experiments/<task>/<workflow>
python3 tools/shoot.py experiments/<task>/<workflow>
```

เลือกคำสั่ง AI เพียงคำสั่งเดียวต่อการรัน รายละเอียดการเก็บเวลา exit status คำตอบ Claude และ resume เฟส 2 อยู่ในภาคผนวกและ [experiments/README.md](experiments/README.md) ชื่อโมเดลในคำสั่งเป็นค่าของ harness; ชื่อโมเดลที่ไม่ปรากฏใน log รายงานว่า “ไม่มีข้อมูล”

```text
experiments/<task>/<workflow>/
├─ prompt.md              # Template + โจทย์ + RUN HARNESS
├─ prompt-phase2.md       # Change Request ของโจทย์ 3
├─ trace.md               # กระบวนการที่ AI บันทึก
├─ events.md              # ถอดจาก log จริงด้วยสคริปต์
├─ response.md            # คำตอบสุดท้ายเฟสแรก
├─ response-phase2.md     # คำตอบเฟส 2
├─ log.jsonl              # log ดิบจาก CLI
├─ log-phase2.jsonl       # log ดิบเฟส 2
├─ output.html / output.md
└─ *.png                  # ภาพจาก Playwright
```

ชื่อ task คือ `1_meeting_room`, `2_expense_claim`, `3_clinic_migration`; workflow คือ `loop`, `graph`, `dynamic` และชุดเสริม `loop_claude` ของโจทย์จองห้องประชุม ร่องรอยฉบับเต็มเก็บในไฟล์ที่ลิงก์ในแต่ละหัวข้อ

## บทที่ 1 Loop Engineering

### Theory: Generate → Evaluate → Improve

เหมือนนักเรียนส่งการบ้าน ครูตรวจตามเกณฑ์ ไม่ผ่านก็แก้เฉพาะจุดแล้วส่งใหม่ GENERATOR สร้างผลงาน CRITIC ตรวจทีละข้อพร้อมหลักฐาน จากนั้น Improve เฉพาะข้อที่ FAIL และกลับไป Evaluate

![วงจร Loop: สร้าง ตรวจ แก้ แล้วตรวจซ้ำ](img/02-loop-cycle.png)

ภาพ Loop Cycle: เส้นย้อนกลับเข้า Evaluate ย้ำว่าทุกครั้งที่แก้ต้องตรวจใหม่

การแยก GENERATOR กับ CRITIC ช่วยระบุหน้าที่ตรวจให้ชัด ต้องใช้เกณฑ์ที่พิสูจน์ได้ เช่น “มีปุ่มยกเลิกหรือไม่” “ครบ 5 feature” และ “เข้าถึงทุก feature ภายใน 2 คลิก” พร้อมหลักฐานแต่ละข้อ

หยุดเมื่อผ่านครบ ทำครบ 3 Iteration หรือเกณฑ์เดิม FAIL 2 ครั้งติดโดยไม่ดีขึ้นแล้วรายงาน `blocked` พร้อมสิ่งที่ยังติดขัด เหมาะกับงานชิ้นเดียว เกณฑ์ชัด และปรับซ้ำได้ จุดอ่อนคือแก้ทีละจุดและอาจไม่เห็นภาพรวม

### Loop Prompt Template

```text
บรรทัดที่ขึ้นต้นด้วย "//" คือคำอธิบายสำหรับผู้เรียน ให้ AI ข้ามบรรทัดเหล่านี้

# ROLE (บทบาท)
คุณสวมบทบาทที่แยกจากกัน 2 บทบาท:
- GENERATOR: สร้างหรือปรับปรุงผลงาน
- CRITIC: ตรวจผลงานตามเกณฑ์อย่างเคร่งครัด ผู้ตรวจต้องไม่ผ่อนปรน

# GOAL (เป้าหมาย)
สร้างผลงานที่ผ่านเกณฑ์ทุกข้อด้านล่าง

# INPUT (ข้อมูลนำเข้า)
{{REQUIREMENT}}

# CRITERIA (เกณฑ์ตรวจ — ทุกข้อต้องตอบได้ว่า PASS หรือ FAIL)
C1. มีทุกฟีเจอร์ที่ระบุไว้ในโจทย์
C2. {{CRITERION_2}}
C3. {{CRITERION_3}}
// ตัวอย่าง "คำโปรยสินค้า": C1 มีชื่อสินค้า  C2 มีราคา  C3 ไม่เกิน 30 คำ — ทุกข้อตอบผ่าน/ไม่ผ่านได้

# WORKFLOW (ลำดับการทำงาน)
ทำซ้ำตามวงจรต่อไปนี้:
1. GENERATOR: สร้างผลงาน (Iteration 1) หรือแก้เฉพาะเกณฑ์ที่ไม่ผ่านเท่านั้น (Iteration ถัดไป)
2. CRITIC: ระบุผลแต่ละเกณฑ์เป็น PASS หรือ FAIL พร้อมหลักฐานข้อละหนึ่งบรรทัด
3. หากทุกเกณฑ์เป็น PASS ให้หยุด
4. หากยังไม่ผ่านครบ ให้ระบุเกณฑ์ที่ไม่ผ่านแล้วเริ่ม Iteration ถัดไป
// รอบ 1: "หูฟังเสียงใส ใส่สบาย" → C2 ไม่ผ่าน (ไม่มีราคา)  รอบ 2: เติม "ราคา 990 บาท" → ผ่านครบ

# CONSTRAINTS (ข้อห้าม)
- ห้ามเปลี่ยนส่วนที่ผ่านแล้ว
- ห้ามแต่งข้อมูลที่ไม่มีในข้อมูลนำเข้า ให้ระบุว่าเป็นสมมติฐานแทน

# STOP CONDITION (เงื่อนไขหยุด)
หยุดเมื่อ:
- ทุกเกณฑ์เป็น PASS หรือ
- ทำครบ 3 Iteration หรือ
- เกณฑ์เดิมไม่ผ่าน 2 ครั้งติดต่อกันโดยไม่ดีขึ้น (รายงานว่าติดขัด โดยระบุสถานะ blocked)

# OUTPUT FORMAT (รูปแบบผลลัพธ์)
1. ตารางบันทึก Iteration: | Iteration | สิ่งที่เปลี่ยน | C1 | C2 | C3 |
2. ผลงานสุดท้าย
3. ประเด็นที่ยังเหลือหรือสมมติฐาน (ถ้ามี)
```

### จุดออกแบบของ Loop Template

1. แยกผู้สร้างกับผู้ตรวจ
2. กำหนดเกณฑ์ที่ตรวจได้ทีละข้อ
3. รอบถัดไปแก้เฉพาะข้อที่ไม่ผ่าน
4. มีทางออกเมื่อวนแล้วไม่ดีขึ้น

Role คือ Generator + Critic, Workflow คือวงจรซ้ำ, สิ่งที่ต้องกำหนดเพิ่มคือเกณฑ์ผ่านและจำนวนรอบ, Output คือ Iteration Log ใน prompt ของแต่ละชุดเติม C2/C3 ให้ตรวจ PASS/FAIL ได้ และ RUN HARNESS สั่งบันทึก output/trace

### โจทย์ 1 × Loop — จองห้องประชุม

[prompt.md](experiments/1_meeting_room/loop/prompt.md) · [trace.md](experiments/1_meeting_room/loop/trace.md) · [events.md](experiments/1_meeting_room/loop/events.md) · [output.html](experiments/1_meeting_room/loop/output.html) · [response.md](experiments/1_meeting_room/loop/response.md)

Iteration Log จากหน้าร่องรอยในสไลด์:

| Iteration | สิ่งที่เปลี่ยน | C1 | C2 | C3 |
| --- | --- | --- | --- | --- |
| 1 | สร้างเว็บไฟล์เดียว พร้อมจอง/ยกเลิกและสถานะ | PASS ทดลองครบ 5 ฟีเจอร์ | PASS Playwright: errors=0 / requests=0 | PASS แต่ละฟีเจอร์ 1–2 คลิก |

CRITIC ใช้ Playwright จริง ดู [critic_test.py](experiments/1_meeting_room/loop/critic_test.py) และ [critic-results.json](experiments/1_meeting_room/loop/critic-results.json) เปิด output.html เพื่อทดลองเว็บ

สังเกต: trace.md จริงมีคำจีน 取消 (=ยกเลิก) หลุดมา 1 คำ — โมเดลสลับภาษาโดยไม่ตั้งใจ จึงแสดงหลักฐานดิบตามจริง

phase1: input **244,784**, cached **212,096**, output **10,581**, total **255,365** tokens; เวลา **217.0 วินาที**

จำนวนรอบ **1 iterations** ในเฟสแรก ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### โจทย์ 2 × Loop — เบิกค่าใช้จ่าย

[prompt.md](experiments/2_expense_claim/loop/prompt.md) · [trace.md](experiments/2_expense_claim/loop/trace.md) · [events.md](experiments/2_expense_claim/loop/events.md) · [output.md](experiments/2_expense_claim/loop/output.md) · [response.md](experiments/2_expense_claim/loop/response.md)

| Iteration | สิ่งที่เปลี่ยน | C1 | C2 | C3 |
| --- | --- | --- | --- | --- |
| 1 | สร้างเอกสารครบ แยกสมมติฐานและ Open Issues | PASS FR-01–FR-10 และหัวข้อครบ | PASS trace ต้นทาง 9 บรรทัด | PASS Mermaid 4 บล็อก ตรวจแบบสถิต |

Iteration Log ระบุว่า CRITIC ตรวจ Mermaid แบบสถิต ไม่ได้ render จริง จึงต้องอ่านผล E6 จากการตรวจภายหลังประกอบ เปิด [เอกสารที่ render แล้ว](experiments/2_expense_claim/loop/output.render.html) เพื่อดู diagram

phase1: input **174,129**, cached **152,576**, output **14,702**, total **188,831** tokens; เวลา **302.0 วินาที**

จำนวนรอบ **1 iterations** ในเฟสแรก ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### โจทย์ 3 × Loop — ย้ายระบบนัดหมาย

[prompt.md](experiments/3_clinic_migration/loop/prompt.md) · [trace.md](experiments/3_clinic_migration/loop/trace.md) · [events.md](experiments/3_clinic_migration/loop/events.md) · [output.md](experiments/3_clinic_migration/loop/output.md) · [response.md](experiments/3_clinic_migration/loop/response.md) · [prompt-phase2.md](experiments/3_clinic_migration/loop/prompt-phase2.md) · [response-phase2.md](experiments/3_clinic_migration/loop/response-phase2.md)

output.md เป็นฉบับหลังเฟส 2; response.md คือคำตอบเฟสแรก และ trace.md รวมสองเฟส เปิด [เอกสารที่ render แล้ว](experiments/3_clinic_migration/loop/output.render.html) ได้โดยตรง

| Iteration | สิ่งที่เปลี่ยน | C1 | C2 | C3 |
| --- | --- | --- | --- | --- |
| 1 | เฟส 1: สร้างแผน v1.0 ครบทุกส่วน | PASS §2.1–2.6 ครบ | PASS Findings 10 ประเภท | PASS normalization + syntax 3 บล็อก |
| 2 | เฟส 2: ตรวจ v1.0 ตาม C1 ใหม่ ยังไม่แก้ | FAIL ขาด consent / จองเองผ่าน OA | PASS Findings เดิม | PASS ตรวจส่วนเดิมซ้ำ |
| 3 | เฟส 2: เพิ่ม §2.8 และแก้จุดเชื่อมตาม C1 | PASS consent / OA พร้อมส่วนเชื่อม | PASS §2.2 คงเดิม | PASS §2.4 คงเดิม + syntax รวม 4 บล็อก |

ตารางคัดผล C1–C3 ตาม Iteration Log ของสไลด์ เป็นคำรายงานของ CRITIC; ผลสคริปต์ M1 ตรวจจำนวนแถวใน Findings และไม่ได้รับรองว่าแต่ละแถวเป็นคนละประเภท

Change Request ทำให้ C1 จาก FAIL ใน Iteration 2 เป็น PASS ใน Iteration 3 อ่าน “หลักฐานการคงส่วนที่ผ่าน” ใน trace.md ประกอบ

phase1: input **150,108**, cached **121,728**, output **12,446**, total **162,554** tokens; เวลา **251.0 วินาที**

phase2: input **490,035**, cached **433,280**, output **26,413**, total **516,448** tokens; เวลา **297.0 วินาที**

จำนวนรอบ **3 iterations** รวมสองเฟส (นับรหัสไม่ซ้ำ ไม่บวกซ้ำ) ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### ผลเกณฑ์ §5 ของ Loop

C1–C3 เป็นเกณฑ์ของ CRITIC ใน prompt ส่วนตารางต่อไปนี้เป็นผลสคริปต์จาก [tests/experiments-results.json](tests/experiments-results.json) ต้องอ่านวิธีตรวจและหลักฐานประกอบ PASS/FAIL

#### โจทย์ 1 — จองห้องประชุม

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 14 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 0 คลิก: หน้าแรก; สถานะ: 0 คลิก: หน้าแรก (วิธี: heuristic) |
| F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network (วิธี: script) |
| F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 14 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 0 คลิก: หน้าแรก; สถานะ: 0 คลิก: หน้าแรก (วิธี: heuristic) |
| F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source (วิธี: script) |

#### โจทย์ 2 — เบิกค่าใช้จ่าย

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| E1_trace_all_sentences — Traceability ครอบคลุม keyword ต้นทางทั้ง 9 กลุ่ม | PASS | output.md: Traceability; กลุ่ม 1: 336; กลุ่ม 2: 337,342,343; กลุ่ม 3: 338; กลุ่ม 4: 339; กลุ่ม 5: 340; กลุ่ม 6: 341; กลุ่ม 7: 342; กลุ่ม 8: 343; กลุ่ม 9: 344 (วิธี: heuristic) |
| E2_conflict_open_issue — Open Issues มีเกณฑ์ 5,000 และ 10,000 | PASS | output.md:368,368; Open Issues: พบทั้งสองค่า (วิธี: script) |
| E3_no_invented_amounts — ไม่พบตัวเลขวงเงินที่พักที่แต่งเพิ่มใน FR/BR | PASS | output.md:25; สแกนตัวเลข+บาท ห่างจาก ที่พัก/คืน/วงเงิน ไม่เกิน 100 ตัวอักษร; ไม่พบค่านอก 5,000/10,000 (วิธี: heuristic) |
| E4_entity_consistency — ชื่อ participant/entity ใน Sequence/State เทียบกับ ERD | FAIL | output.md:101,227,303; ERD 13 entity; ชื่อไม่พบ: App (ระบบเบิกค่าใช้จ่าย); เทียบชื่อ literal (ตัด _/ไม่สนตัวพิมพ์); participant ที่เป็นระบบ/บทบาทอาจเป็น false positive; ไม่รับรอง attribute/ความหมาย (วิธี: heuristic) |
| E5_state_holder — ชื่อ state หรือ note ระบุผู้ถือเรื่อง | PASS | output.md:306,307,308,309,310,311; ตรวจเฉพาะชื่อ state และ note (วิธี: heuristic) |
| E6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | PASS | output.md:68,101,227,303; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render (วิธี: render) |

#### โจทย์ 3 — ย้ายระบบนัดหมาย

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| M1_five_problem_types — ตาราง Data Quality Findings มีอย่างน้อย 5 แถวปัญหา | PASS | output.md:54,55,56,57,58,59,60,61,62,63; ตาราง Findings แรกมี 10 แถวข้อมูล (ไม่รับรองว่าทุกแถวเป็นคนละประเภท) (วิธี: heuristic) |
| M2_ambiguous_date_flagged — แถววันที่เป้าหมายมีข้อความ flag ความกำกวม | PASS | output.md:23,54; พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย; ไม่ตัดสินการตีความวันที่ (วิธี: script) |
| M3_identity_strategy — หัวข้อ mapping/migration/identity มี normalization และการยืนยัน | PASS | output.md:214,215,251; normalization marker; output.md:213,214,215; confirmation marker ในหัวข้อที่กำหนด (วิธี: heuristic) |
| M4_plan_version_log — บันทึกเวอร์ชันแผนมี v1 และ v2 | FAIL | output.md:289,290; หัวข้อ Plan Version/ชื่อไทย/Plan vN: v1=True, v2=False; v1.1 ไม่นับเป็น v2 (วิธี: script) |
| M5_impact_analysis — เฟส 2 มีคำ Impact และ Reuse หรือคงเดิม | FAIL | Impact: ไม่พบใน output.md + response-phase2.md; Reuse/คงเดิม: output.md:7, output.md:360, output.md:445; ตรวจคำเท่านั้น (วิธี: script) |
| M6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | PASS | output.md:29,69,92,327; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render (วิธี: render) |

### ชุดเสริม loop_claude

ใช้ prompt เดียวกันกับ Loop ของโจทย์ 1 แล้วเปรียบเทียบ CLI เปิด [โฟลเดอร์ loop_claude](experiments/1_meeting_room/loop_claude/)

[prompt.md](experiments/1_meeting_room/loop_claude/prompt.md) · [trace.md](experiments/1_meeting_room/loop_claude/trace.md) · [events.md](experiments/1_meeting_room/loop_claude/events.md) · [output.html](experiments/1_meeting_room/loop_claude/output.html) · [response.md](experiments/1_meeting_room/loop_claude/response.md)

phase1: input **25,501**, cached **91,253**, output **12,209**, total **128,963** tokens; เวลา **145.0 วินาที**

จำนวนรอบ **1 iterations** ในเฟสแรก ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | FAIL | output.html: DOM file://, 1280×800, nav ชั้นแรก 3 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: ไม่พบในเส้นทางที่ตรวจ; สถานะ: 0 คลิก: หน้าแรก (วิธี: heuristic) |
| F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network (วิธี: script) |
| F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | FAIL | output.html: DOM file://, 1280×800, nav ชั้นแรก 3 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: ไม่พบในเส้นทางที่ตรวจ; สถานะ: 0 คลิก: หน้าแรก (วิธี: heuristic) |
| F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source (วิธี: script) |

F1/F3 เป็น **FAIL** เพราะไม่พบการยกเลิกในเส้นทางที่ตัวตรวจสำรวจ จึงยังสรุปไม่ได้ว่าผลงานไม่มีฟังก์ชันนั้นทุกเส้นทาง ต้องเปิดเว็บและตรวจร่องรอยเพิ่มเติม ผลนี้ต่างจากการรายงานผ่านของ CRITIC ใน trace

### จุดสังเกตของ Loop

1. เทียบกับสั่ง “ช่วยทำให้ดีขึ้น” เกณฑ์ที่ตรวจได้ทำให้แต่ละรอบแก้ตรงจุดขึ้นอย่างไร?
2. ทั้ง 3 โจทย์ผ่าน C1–C3 ตั้งแต่ Iteration 1 ตาม trace เป็นเพราะเกณฑ์หลวมหรือ GENERATOR ทำได้ดี จะทดสอบอย่างไร?
3. Iteration 2–3 ของโจทย์ 3 แตะส่วนที่ผ่านแล้วหรือไม่? ใช้หลักฐานการคงส่วนที่ผ่านใน trace ตอบ
4. การตรวจ Mermaid แบบสถิตของโจทย์ 2 เชื่อได้แค่ไหนเมื่อเทียบกับ E6 ที่ render จริงภายหลัง?
5. ถ้าเปลี่ยน C2 เป็น “UI สวย” การตรวจและการตัดสินใจหยุดจะเปลี่ยนอย่างไร?
6. โทเคนและเวลาต่างกันอย่างไรเมื่อแยกโจทย์และเฟสตาม events.md?

## บทที่ 2 Graph Engineering

### Theory: Node · Edge · Dependency · State

เหมือนทำข้าวแกง หุงข้าวกับทำแกงพร้อมกันได้ แต่จัดจานต้องรอทั้งสองเสร็จ หากแกงไหม้ ข้าวที่หุงแล้วยังใช้ได้ Graph แบ่งงานเป็นชิ้นและกำหนดว่าจะส่งผลให้กันอย่างไร

| ส่วนประกอบ | ความหมาย |
| --- | --- |
| Node | งานหนึ่งชิ้นที่มี Task และ Output ชัดเจน |
| Edge | เส้นทางส่งข้อมูลจาก Node หนึ่งไปอีก Node |
| Dependency | งานที่ต้อง DONE ก่อน Node นี้เริ่มได้ |
| State | สถานะงาน TODO → DONE หรือ FAILED |

### Workflow Diagram: จาก Sequential ไป Graph with Loop

![Sequential Graph ทำตามลำดับ](img/04-graph-sequential.png)

Sequential ตามรอยง่ายและรู้ว่าพังที่ Node ไหน ข้อจำกัดคือช้าและไม่ใช้ประโยชน์จากงานขนาน

![Fan-out และ Fan-in แยกทำงานแล้วรวม](img/05-graph-fanout-fanin.png)

Fan-out/Fan-in: N2–N4 ทำงานเป็นอิสระ ไม่เห็นผลของกัน N5 รอให้ DONE ครบก่อนรวมผล

![Conditional Graph เปิดทางตามเงื่อนไข](img/06-graph-conditional.png)

Conditional: เมื่อ N1 พบข้อขัดแย้ง เปิด N1b ก่อน N5 งานและทางเลือกถูกกำหนดไว้ล่วงหน้า แล้วเปิดทางเมื่อเข้าเงื่อนไข

![Graph with Loop ส่ง feedback กลับส่วนที่ไม่ผ่าน](img/07-graph-with-loop.png)

Graph with Loop ใส่วงจร Evaluate → แก้ไว้ใน Node ได้ ภาพแสดง feedback จาก N5 กลับไปส่วนที่ FAIL; DAG ไม่มี cycle ส่วน Graph ที่มี cycle ต้องกำหนดเกณฑ์ผ่าน ขีดจำกัดรอบ และทางออกเมื่อไม่ดีขึ้น

### data contract · Merge Rules · Failure Handling

ผู้ส่งต้องระบุ Node, status, output และ assumptions เพื่อให้ผู้รับตรวจได้ N5 รับเฉพาะผล DONE ที่ครบ contract หาก artifact ขัดแย้งกัน ให้ยกประโยคจาก INPUT มาเป็นหลักฐาน หากข้อมูลไม่พอให้บันทึกประเด็นที่ยังหาข้อสรุปไม่ได้

Node ที่ล้มเหลวลองใหม่ได้ 1 ครั้ง ถ้ายังล้มให้ FAILED แล้วทำต่อเฉพาะงานที่ไม่พึ่งพา Node นั้น พร้อมรายงานสิ่งที่ขาด Node ที่ Dependency ยังไม่ DONE ต้องรอ หยุดเมื่อ N5 DONE หรือไม่มีงานที่ทำต่อได้

Self-consistency ต้องตรวจจากหลักฐาน เช่น ตัวอย่างแนวคิดที่ Sequence มี Entity “Receipt” แต่ ERD ไม่มี ให้กลับไปอ้าง “ต้องตรวจใบเสร็จซ้ำ” เพื่อแก้แบบจำลองให้สอดคล้อง ตัวอย่างนี้อธิบายวิธีคิด ไม่ใช่ข้อสรุปว่าการทดลองจริงพบเหตุการณ์นี้ การใช้เสียงข้างมากแทนหลักฐานยังไม่เพียงพอ

เหมาะเมื่อมีงานหลายส่วนที่แยกทำได้แต่ต้องสอดคล้องกันเมื่อรวม จุดอ่อนคือต้องรู้โครงสร้างงานล่วงหน้าและออกแบบ Dependency ให้เหมาะสม

### Graph Prompt Template

```text
บรรทัดที่ขึ้นต้นด้วย "//" คือคำอธิบายสำหรับผู้เรียน ให้ AI ข้ามบรรทัดเหล่านี้

# ROLE (บทบาท)
คุณเป็นผู้ดำเนินงานตามกราฟ โดยทำงานของแต่ละ Node ในบทบาทผู้ทำงานที่เป็นอิสระจากกัน
จากนั้นทำหน้าที่ MERGER รวมผลลัพธ์ของแต่ละ Node

# GOAL (เป้าหมาย)
สร้างผลงานส่งมอบสุดท้ายโดยทำงานตามกราฟงานด้านล่าง

# INPUT (ข้อมูลนำเข้า)
{{REQUIREMENT}}

# TASK GRAPH (กราฟงาน)
| Node | Task | Depends on | Output |
|------|------|------------|--------|
| N1 | สกัดข้อกำหนด (FR/BR) | - | รายการข้อกำหนด |
| N2 | วาด Use Case Diagram | N1 | แผนภาพ Mermaid |
| N3 | วาด ERD | N1 | แผนภาพ Mermaid |
| N4 | วาด Sequence Diagram | N1 | แผนภาพ Mermaid |
| N5 | ตรวจความสอดคล้องและรวมผล | N2, N3, N4 | เอกสารสุดท้าย |
// N1 ก่อน → N2–N4 พร้อมกัน (fan-out) → N5 รวม (fan-in) — เทียบข้าวแกง: เตรียมวัตถุดิบ / หุงข้าว-ทำแกง-ทำไข่ / จัดจาน

# EXECUTION RULES (กติกาการทำงาน)
1. ทำงานของ Node ได้ก็ต่อเมื่อทุก Node ที่เป็น Dependency ของมันมีสถานะ DONE แล้ว
2. Node ที่อยู่ระดับเดียวกัน (N2, N3, N4) ต้องทำงานเป็นอิสระจากกัน
   ห้ามให้ Node เหล่านี้เห็นผลลัพธ์ของกันและกัน
3. ทุก Node ต้องส่งผลลัพธ์ตาม data contract นี้:
   { "node": "N2", "status": "DONE | FAILED", "output": "...", "assumptions": [] }

# CONDITIONAL EDGE (ทางเลือกตามเงื่อนไข — ไม่บังคับ)
หาก N1 พบข้อกำหนดที่ขัดแย้งกัน ให้ทำงานของ Node N1b "ระบุประเด็นที่ยังหาข้อสรุปไม่ได้" ก่อน N5
// เช่น เจอ 5,000 กับ 10,000 ขัดกัน ให้แตกไป N1b ก่อน

# MERGE RULES (N5) (กติกาการรวมผล)
- รับผลลัพธ์ของ Node เฉพาะเมื่อมีสถานะ DONE และเป็นไปตาม data contract
- หากผลลัพธ์ของแต่ละ Node ขัดแย้งกัน (เช่น มี Entity ใน Sequence Diagram แต่ไม่มีใน ERD)
  ให้ตัดสินโดยใช้หลักฐานจาก INPUT และยกประโยคต้นทางมาอ้างอิง
- หากหลักฐานไม่เพียงพอให้ตัดสิน ห้ามเลือกข้าง ให้ระบุเป็นข้อขัดแย้งที่ยังหาข้อสรุปไม่ได้

# FAILURE HANDLING (การจัดการเมื่องานล้มเหลว)
- หาก Node ทำงานล้มเหลว ให้ลองทำใหม่อีก 1 ครั้ง
- หากล้มเหลวอีก ให้ระบุสถานะ FAILED แล้วทำงานต่อใน Node ที่ไม่ได้ขึ้นกับ Node นั้น
  พร้อมรายงานสิ่งที่ขาดหายไป

# CONSTRAINTS (ข้อห้าม)
- ห้ามแต่งตัวเลขหรือกติกาที่ไม่มีในข้อมูลนำเข้า

# STOP CONDITION (เงื่อนไขหยุด)
หยุดเมื่อ N5 มีสถานะ DONE หรือเมื่อไม่มี Node ที่เหลือสามารถทำงานต่อได้

# OUTPUT FORMAT (รูปแบบผลลัพธ์)
1. Execution trace: | Node | สถานะ | หมายเหตุ |
2. ผลงานส่งมอบสุดท้ายที่รวมแล้ว
3. ข้อขัดแย้งที่พบและวิธีหาข้อสรุปของแต่ละข้อ (พร้อมหลักฐาน)
```

### จุดออกแบบของ Graph Template

1. เขียน Node เป็นตารางพร้อม Dependency
2. กำหนด data contract ระหว่าง Node
3. Node คู่ขนานต้องไม่เห็นผลของกัน
4. Merge ตัดสินด้วยหลักฐานจาก INPUT

Role คือผู้ทำแต่ละ Node + Merger, Workflow คือตาราง Node + Dependency, สิ่งที่ต้องเพิ่มคือ contract และกติกา Merge, Output คือ Execution Trace ตาราง TASK GRAPH ใน Template เป็นตัวอย่างสำหรับโจทย์เบิกค่าใช้จ่าย ส่วน prompt ของโจทย์อื่นปรับงานแต่ละ Node ตามผลลัพธ์ที่ต้องส่ง

### โจทย์ 1 × Graph — จองห้องประชุม

[prompt.md](experiments/1_meeting_room/graph/prompt.md) · [trace.md](experiments/1_meeting_room/graph/trace.md) · [events.md](experiments/1_meeting_room/graph/events.md) · [output.html](experiments/1_meeting_room/graph/output.html) · [response.md](experiments/1_meeting_room/graph/response.md)

N1 วิเคราะห์ → N2 ตรรกะ JS / N3 HTML–CSS / N4 สคริปต์ทดสอบ → N5 รวมเว็บและทดสอบ Execution Trace ต้นฉบับเป็น JSON บรรทัดต่อบรรทัด ตารางนี้คัดจากหน้าร่องรอยของสไลด์:

| Node | สถานะ | หมายเหตุ |
| --- | --- | --- |
| N1 | DONE | N1-contract.md: 5 ฟีเจอร์, 4 หน้าจอ, navigation และ DOM/JS contract; assumptions ว่าง |
| N1b | DONE | N1b-assumptions.md: ห้องตัวอย่าง, สถานะเริ่มต้น, local storage และนิยามคลิกเข้าถึง |
| N2 | DONE | nodes/N2.js; assumptions ว่าง |
| N4 | DONE | nodes/N4-test.py; บันทึกก่อน N3; assumptions ว่าง |
| N3 | DONE | nodes/N3.html; assumptions ว่าง |
| N5_MERGE | MERGED | output.html: รับ N2/N3/N4; ไม่พบ structural conflict; ยังรอตรวจ runtime |
| N5 | DONE | output.html + test-report.md + results.json + response.md; mock-up เก็บในเบราว์เซอร์; ยกเลิกต้องมีรายการก่อน |

N5_MERGE เป็น event ไม่ใช่ Node เพิ่ม เว็บ mock-up เก็บข้อมูลในเบราว์เซอร์ ดูผล Playwright ของ N5 ใน [test-report.md](experiments/1_meeting_room/graph/test-report.md)

phase1: input **590,224**, cached **528,000**, output **8,665**, total **598,889** tokens; เวลา **392.0 วินาที**

จำนวนรอบ **6 nodes** ในเฟสแรก ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### โจทย์ 2 × Graph — เบิกค่าใช้จ่าย

[prompt.md](experiments/2_expense_claim/graph/prompt.md) · [trace.md](experiments/2_expense_claim/graph/trace.md) · [events.md](experiments/2_expense_claim/graph/events.md) · [output.md](experiments/2_expense_claim/graph/output.md) · [response.md](experiments/2_expense_claim/graph/response.md)

N1 สกัดข้อกำหนด → N2 Use Case / N3 ERD / N4 Sequence + State → N5 Traceability และรวม เปิด [เอกสารที่ render แล้ว](experiments/2_expense_claim/graph/output.render.html) เพื่อเทียบ diagram

| Node | สถานะ | หมายเหตุ |
| --- | --- | --- |
| N1 | DONE | สกัด Actors, FR/NFR, BR และประโยคต้นทาง S01–S11 |
| N1b | DONE | C-01: เกณฑ์ 5,000/10,000 ขัดกัน; ไม่เลือกข้าง; เสร็จก่อน N5 |
| N2 | DONE | Use Case จาก N1 เท่านั้น; ใช้ flowchart แทน UML Use Case |
| N3 | DONE | ERD จาก N1; Entity/FK/cardinality เป็นข้อเสนอ |
| N4 | DONE | Sequence + State จาก N1; บัญชีตรวจเอกสารก่อนอนุมัติเป็นสมมติฐาน |
| N5 | DONE | รับ contract ที่ครบและ DONE; ตรวจสอดคล้อง รวม Matrix/Open Issues |

Execution Trace แสดงทั้งผลและสมมติฐานของแต่ละ Node ก่อนรวม ไม่ควรเปลี่ยนสมมติฐานให้กลายเป็นข้อกำหนดที่ผู้ให้สัมภาษณ์ยืนยันแล้ว

phase1: input **832,671**, cached **771,840**, output **20,154**, total **852,825** tokens; เวลา **521.0 วินาที**

จำนวนรอบ **6 nodes** ในเฟสแรก ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### โจทย์ 3 × Graph — ย้ายระบบนัดหมาย

[prompt.md](experiments/3_clinic_migration/graph/prompt.md) · [trace.md](experiments/3_clinic_migration/graph/trace.md) · [events.md](experiments/3_clinic_migration/graph/events.md) · [output.md](experiments/3_clinic_migration/graph/output.md) · [response.md](experiments/3_clinic_migration/graph/response.md) · [prompt-phase2.md](experiments/3_clinic_migration/graph/prompt-phase2.md) · [response-phase2.md](experiments/3_clinic_migration/graph/response-phase2.md)

N1 สำรวจ CSV → N2 As-Is / N3 To-Be + Data Model / N4 Mapping + Migration → N5 Gap + Roll-out และรวม output.md เป็นฉบับหลัง Change Request; response.md เป็นคำตอบเฟสแรก เปิด [เอกสารที่ render แล้ว](experiments/3_clinic_migration/graph/output.render.html)

Execution Trace เฟส 1:

| Node | สถานะ | หมายเหตุ |
| --- | --- | --- |
| N1 | DONE | สำรวจ CSV และจัดทำ Data Quality Findings |
| N1b | DONE | ตรวจหลักฐาน ระบุประเด็นที่ต้องให้มนุษย์ยืนยัน |
| N2 | DONE | As-Is; ทำอิสระจาก N3/N4 |
| N3 | DONE | To-Be + Data Model; ทำอิสระจาก N2/N4 |
| N4 | DONE | Data Mapping + Migration; ทำอิสระจาก N2/N3 |
| N5 | DONE | ตรวจสอดคล้อง รวม Gap, Roll-out และ Plan Version Log |

Change Request เฟส 2: Template สั่งให้ reuse ผล DONE ที่ input ไม่เปลี่ยน ตารางจาก response-phase2.md แสดง Node ที่ AI เลือกรันซ้ำ:

| Node | สถานะ | รันซ้ำ | หมายเหตุ |
| --- | --- | --- | --- |
| N1 | DONE | yes | INPUT เพิ่มข้อกำหนด consent และ LINE self-booking |
| N1b | DONE | yes | ผล N1 เปลี่ยน จึงตรวจข้อกำกวมอีกครั้ง |
| N2 | DONE | yes | ผล N1 เปลี่ยน จึงประเมินผลต่อ As-Is |
| N3 | DONE | yes | ผล N1 เปลี่ยน ต้องเพิ่มกระบวนการและ Data Model |
| N4 | DONE | yes | ผล N1 เปลี่ยน ต้องเพิ่ม mapping และ migration |
| N5 | DONE | yes | ผล N3/N4 เปลี่ยน ต้องรวมและตรวจความสอดคล้องใหม่ |

AI รันซ้ำทุก Node โดย N1b และ N2 ได้ผลเดิมทุกไบต์ตามคำตอบเฟส 2 จึงเป็นกรณีให้พิจารณาว่า Dependency ที่ออกแบบไว้ช่วย reuse ได้เพียงใด

phase1: input **589,489**, cached **552,448**, output **16,693**, total **606,182** tokens; เวลา **492.0 วินาที**

phase2: input **1,819,842**, cached **1,749,888**, output **35,270**, total **1,855,112** tokens; เวลา **687.0 วินาที**

จำนวนรอบ **6 nodes** รวมสองเฟส (นับรหัสไม่ซ้ำ ไม่บวกซ้ำ) ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### ผลเกณฑ์ §5 ของ Graph

ผลจาก [tests/experiments-results.json](tests/experiments-results.json) เกณฑ์และวิธีตรวจเดียวกับบท Loop:

#### โจทย์ 1 — จองห้องประชุม

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 11 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → จองห้อง; สถานะ: 1 คลิก: หน้าแรก → จองห้อง; เส้นทางที่ตรวจไม่สำเร็จ 1, จำกัด candidate=False (วิธี: heuristic) |
| F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network (วิธี: script) |
| F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 11 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → จองห้อง; สถานะ: 1 คลิก: หน้าแรก → จองห้อง; เส้นทางที่ตรวจไม่สำเร็จ 1, จำกัด candidate=False (วิธี: heuristic) |
| F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source (วิธี: script) |

#### โจทย์ 2 — เบิกค่าใช้จ่าย

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| E1_trace_all_sentences — Traceability ครอบคลุม keyword ต้นทางทั้ง 9 กลุ่ม | PASS | output.md: Traceability; กลุ่ม 1: 380; กลุ่ม 2: 381,388,389; กลุ่ม 3: 383; กลุ่ม 4: 384; กลุ่ม 5: 385; กลุ่ม 6: 386,387; กลุ่ม 7: 388; กลุ่ม 8: 389; กลุ่ม 9: 390 (วิธี: heuristic) |
| E2_conflict_open_issue — Open Issues มีเกณฑ์ 5,000 และ 10,000 | PASS | output.md:412,412; Open Issues: พบทั้งสองค่า (วิธี: script) |
| E3_no_invented_amounts — ไม่พบตัวเลขวงเงินที่พักที่แต่งเพิ่มใน FR/BR | PASS | output.md:41; สแกนตัวเลข+บาท ห่างจาก ที่พัก/คืน/วงเงิน ไม่เกิน 100 ตัวอักษร; ไม่พบค่านอก 5,000/10,000 (วิธี: heuristic) |
| E4_entity_consistency — ชื่อ participant/entity ใน Sequence/State เทียบกับ ERD | FAIL | output.md:124,250,316; ERD 10 entity; ชื่อไม่พบ: A (ฝ่ายบัญชี), M (ผู้จัดการฝ่าย), T (หัวหน้าทีม); เทียบชื่อ literal (ตัด _/ไม่สนตัวพิมพ์); participant ที่เป็นระบบ/บทบาทอาจเป็น false positive; ไม่รับรอง attribute/ความหมาย (วิธี: heuristic) |
| E5_state_holder — ชื่อ state หรือ note ระบุผู้ถือเรื่อง | PASS | output.md:319,321,322,324,326,328; ตรวจเฉพาะชื่อ state และ note (วิธี: heuristic) |
| E6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | PASS | output.md:79,124,250,316; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render (วิธี: render) |

#### โจทย์ 3 — ย้ายระบบนัดหมาย

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| M1_five_problem_types — ตาราง Data Quality Findings มีอย่างน้อย 5 แถวปัญหา | PASS | output.md:59,60,61,62,63,64,65,66,67,68,69,70; ตาราง Findings แรกมี 12 แถวข้อมูล (ไม่รับรองว่าทุกแถวเป็นคนละประเภท) (วิธี: heuristic) |
| M2_ambiguous_date_flagged — แถววันที่เป้าหมายมีข้อความ flag ความกำกวม | PASS | output.md:41,68,105,159,1024; พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย; ไม่ตัดสินการตีความวันที่ (วิธี: script) |
| M3_identity_strategy — หัวข้อ mapping/migration/identity มี normalization และการยืนยัน | PASS | output.md:841,901,924; normalization marker; output.md:833,838,839; confirmation marker ในหัวข้อที่กำหนด (วิธี: heuristic) |
| M4_plan_version_log — บันทึกเวอร์ชันแผนมี v1 และ v2 | PASS | output.md:993,994,995; หัวข้อ Plan Version/ชื่อไทย/Plan vN: v1=True, v2=True; v1.1 ไม่นับเป็น v2 (วิธี: script) |
| M5_impact_analysis — เฟส 2 มีคำ Impact และ Reuse หรือคงเดิม | FAIL | Impact: ไม่พบใน output.md + response-phase2.md; Reuse/คงเดิม: output.md:14, output.md:810, output.md:841; ตรวจคำเท่านั้น (วิธี: script) |
| M6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | PASS | output.md:113,175,208,453,492; render_markdown ได้ SVG 5/5 บล็อก; ไม่เขียนไฟล์ render (วิธี: render) |

### จุดสังเกตของ Graph

1. ถ้าให้ N2–N4 เห็นผลของกัน จะเกิดอะไรกับความเป็นอิสระและความสอดคล้อง?
2. ลองเพิ่ม/ลด Node หรือเปลี่ยน Dependency แล้วจุดที่พบความขัดแย้งเปลี่ยนอย่างไร?
3. N1b ถูกเปิดในทั้ง 3 โจทย์หรือไม่ ด้วยเหตุผลอะไร? เทียบ CONDITIONAL EDGE ใน prompt กับ trace
4. เฟส 2 ของโจทย์ 3 รันซ้ำทุก Node สอดคล้องกับกติกา reuse หรือไม่ และควรเปลี่ยน Dependency อย่างไร?
5. Graph ใน CLI เดียวทำขนานจริงหรือทำเป็นลำดับ? เวลาและลำดับ event ใน events.md รองรับข้อสรุปได้เพียงใด?
6. เมื่อเทียบกับ Loop ในโจทย์และเฟสเดียวกัน ผลต่างโทเคนสัมพันธ์กับงานที่ทำอย่างไร?
7. ผล FAIL บอกอะไรและยังบอกอะไรไม่ได้? อ่านวิธีตรวจ หลักฐาน และผลงานจริงก่อนอธิบาย

## บทที่ 3 Dynamic Workflow

### Theory: Planner → Executor → Evaluator → Re-plan

เหมือนวางแผนเที่ยว วัด → ตลาดน้ำ → คาเฟ่ เมื่อฝนตกก็เปลี่ยนตลาดน้ำเป็นพิพิธภัณฑ์ วัดที่ไปแล้วไม่ต้องไปใหม่ และโรงแรมที่จองไว้ยังใช้ได้

PLANNER เขียน Plan v1; EXECUTOR ทำงาน TODO ที่ Dependency เป็น DONE แล้ว; EVALUATOR ตรวจว่าแผนยังเหมาะสมหรือไม่ ถ้ายังเหมาะให้ทำงานต่อ ถ้าไม่เหมาะให้ PLANNER เขียนเวอร์ชันถัดไป

![Dynamic Planner Loop ตรวจและปรับแผนระหว่างทำ](img/08-dynamic-planner-loop.png)

ภาพ Planner Loop: ตรวจแผนหลังทำแต่ละงาน และส่ง Result เมื่อครบ Stop Condition

Static Graph กำหนด Node และ Dependency ล่วงหน้า ส่วน Dynamic เพิ่ม ลด แยก รวม ยกเลิกงาน เปลี่ยนลำดับและ Dependency ระหว่างทำได้ Trigger คือพบงานที่ยังไม่มีในแผน งานทำไม่ได้ตามแผน หรือ NEW INFORMATION เปลี่ยนข้อกำหนด

![Plan Versioning จาก v1 ไป v2 พร้อมการแยกงาน](img/09-plan-versioning.png)

ภาพ Plan Versioning เป็นตัวอย่างแนวคิด: v1 มี A → B → C; v2 แยก B เป็น B1/B2/B3 โดยคง A แล้วส่งต่อ C ผลทดลองจริงอ่านจาก Plan Version Log ด้านล่าง

ทุกเวอร์ชันใหม่ต้องบอก Reason, Changes, Impact analysis และ Reuse ห้ามทำงาน DONE ซ้ำเว้นแต่ Impact ระบุว่ากระทบ ห้ามตัดข้อกำหนดโดยไม่แจ้งเหตุผล และ Re-plan ได้สูงสุด 3 ครั้ง

หยุดเมื่อทุกงาน DONE หรือ DROPPED และ EVALUATOR ยืนยันเป้าหมาย หรือเมื่อถึงขีดจำกัด Re-plan พร้อมรายงานสิ่งที่ยังตัดสินใจไม่ได้ เหมาะเมื่อขอบเขตไม่นิ่ง มีข้อมูลใหม่กลางทาง จุดอ่อนคือซับซ้อนและควบคุมยาก งานขอบเขตนิ่งอาจไม่คุ้มความซับซ้อน

### Dynamic Workflow Prompt Template

```text
บรรทัดที่ขึ้นต้นด้วย "//" คือคำอธิบายสำหรับผู้เรียน ให้ AI ข้ามบรรทัดเหล่านี้

# ROLE (บทบาท)
คุณสวมบทบาทที่แยกจากกัน 3 บทบาท:
- PLANNER: สร้างและปรับปรุงแผน
- EXECUTOR: ทำงานทีละงานและรายงานผลลัพธ์
- EVALUATOR: ตรวจผลลัพธ์และตัดสินว่าแผนยังเหมาะสมหรือไม่

# GOAL (เป้าหมาย)
ส่งมอบผลลัพธ์ตามที่ระบุในข้อมูลนำเข้า โดยปรับแผนเมื่อพบข้อเท็จจริงใหม่

# INPUT (ข้อมูลนำเข้า)
{{REQUIREMENT}}

# NEW INFORMATION (ข้อมูลใหม่)
{{CHANGE_REQUEST_OR_NONE}}
// รอบแรกใส่ NONE พอได้ Plan v1 แล้วค่อยส่ง prompt ต่อพร้อม change request (เช่น PDPA + LINE OA ของโจทย์ 3)

# PLAN FORMAT (รูปแบบแผน)
Plan vN
| งาน | คำอธิบาย | Dependency | สถานะ (TODO / DONE / DROPPED) |
// Plan v1 เที่ยว: T1 วัด (-) → T2 ตลาดน้ำ (T1) → T3 คาเฟ่ (T2)

# WORKFLOW (ลำดับการทำงาน)
1. PLANNER เขียน Plan v1
2. EXECUTOR ทำงานถัดไปที่มีสถานะ TODO และงานที่เป็น Dependency มีสถานะ DONE แล้ว
3. EVALUATOR ตรวจผลลัพธ์แล้วตอบว่า "แผนยังเหมาะสมอยู่หรือไม่?"
4. หากใช่ ให้กลับไปขั้นตอนที่ 2
5. หากไม่ใช่ ให้ PLANNER สร้างแผนเวอร์ชันถัดไป (ดู RE-PLAN RULES) แล้วกลับไปขั้นตอนที่ 2

# RE-PLAN TRIGGERS (เงื่อนไขที่ทำให้ปรับแผน)
ให้ Re-plan เฉพาะเมื่อ:
- ผลลัพธ์ทำให้พบงานที่ยังไม่มีในแผน (เช่น ข้อมูลสกปรกที่ต้องทำความสะอาด) หรือ
- งานหนึ่งไม่สามารถทำได้ตามแผน หรือ
- NEW INFORMATION ทำให้ข้อกำหนดเปลี่ยนไป

# RE-PLAN RULES (กติกาการปรับแผน)
สำหรับแผนเวอร์ชันใหม่ทุกครั้ง ให้เขียน:
- เหตุผลที่เปลี่ยนแผน: เกิดเงื่อนไขใดที่ทำให้ต้องปรับแผน
- สิ่งที่เปลี่ยน: เพิ่ม / ตัด / แยก / รวม / จัดลำดับงานใหม่ หรือเปลี่ยน Dependency
- Impact analysis: งานและผลลัพธ์ใดได้รับผลกระทบ
- Reuse: ผลลัพธ์ใดที่มีสถานะ DONE ยังใช้ได้และเก็บไว้ใช้ต่อ
// Plan v2 เที่ยว: Reason ฝนตก · Changes DROP T2, ADD T2b พิพิธภัณฑ์ (T1), T3 ขึ้นกับ T2b · Impact T3 เลื่อนเวลา · Reuse T1 เก็บไว้

# CONSTRAINTS (ข้อห้าม)
- ห้ามทำงานที่มีสถานะ DONE ซ้ำ เว้นแต่ Impact analysis ระบุว่างานนั้นได้รับผลกระทบ
- ห้ามตัดข้อกำหนดทิ้งโดยไม่แจ้ง งานที่ตัดทิ้งต้องระบุเหตุผล
- ให้ Re-plan ได้สูงสุด 3 ครั้ง หลังจากนั้นให้รายงานสิ่งที่ยังตัดสินใจไม่ได้

# STOP CONDITION (เงื่อนไขหยุด)
หยุดเมื่อทุกงานมีสถานะ DONE หรือ DROPPED และ EVALUATOR ยืนยันว่าบรรลุเป้าหมายแล้ว
หรือเมื่อถึงขีดจำกัดจำนวนครั้งของ Re-plan

# OUTPUT FORMAT (รูปแบบผลลัพธ์)
1. บันทึกเวอร์ชันแผน: v1, v2, ... โดยแต่ละเวอร์ชันระบุเหตุผล สิ่งที่เปลี่ยน ผลกระทบ และ Reuse
2. บันทึกการทำงาน: | ขั้นตอน | งาน | ผลลัพธ์ | การตัดสินของ EVALUATOR |
3. ผลงานส่งมอบสุดท้าย
```

### จุดออกแบบของ Dynamic Template

1. แผนเป็นข้อมูลที่มี version
2. ระบุชัดว่าเหตุการณ์ใดทำให้ Re-plan
3. ทุกครั้งที่เปลี่ยนต้องบอกเหตุผล ผลกระทบ และสิ่งที่ reuse
4. จำกัดจำนวนครั้ง Re-plan

Role คือ Planner + Executor + Evaluator, Workflow คือแผนที่แก้ไขได้, สิ่งที่ต้องเพิ่มคือ Trigger และกติกาเปลี่ยนแผน, Output คือ Plan Version Log ในเฟสแรก NEW INFORMATION เป็น NONE; โจทย์ 3 ส่ง Change Request ผ่าน resume thread เดิม

### โจทย์ 1 × Dynamic — จองห้องประชุม

[prompt.md](experiments/1_meeting_room/dynamic/prompt.md) · [trace.md](experiments/1_meeting_room/dynamic/trace.md) · [events.md](experiments/1_meeting_room/dynamic/events.md) · [output.html](experiments/1_meeting_room/dynamic/output.html) · [response.md](experiments/1_meeting_room/dynamic/response.md)

Plan Version Log:

| Version | Reason | Changes | Reuse |
| --- | --- | --- | --- |
| v1 | แผนเริ่มต้น NEW INFORMATION = NONE | สร้าง T1–T4 | – |

| งาน | ผลลัพธ์ตาม trace | การตัดสินของ EVALUATOR |
| --- | --- | --- |
| T1 | DONE ตรวจไฟล์ กำหนดข้อมูลตัวอย่างและพฤติกรรมระบบ | แผนยังเหมาะสมอยู่ |
| T2 | DONE สร้าง output.html ครบฟังก์ชัน | แผนยังเหมาะสมอยู่ |
| T3 | DONE รัน test_ui.py ด้วย Playwright | แผนยังเหมาะสมอยู่ |
| T4 | DONE บันทึก response.md และหลักฐาน | บรรลุเป้าหมาย; หยุด |

ไม่เกิด Re-plan เพราะ EVALUATOR ตอบว่าแผนยังเหมาะสมทุกขั้น รายละเอียดทดสอบอยู่ใน [test-results.json](experiments/1_meeting_room/dynamic/test-results.json) และ [test_ui.py](experiments/1_meeting_room/dynamic/test_ui.py)

phase1: input **365,708**, cached **328,320**, output **17,927**, total **383,635** tokens; เวลา **400.0 วินาที**

จำนวนรอบ **1 plan_versions** ในเฟสแรก ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### โจทย์ 2 × Dynamic — เบิกค่าใช้จ่าย

[prompt.md](experiments/2_expense_claim/dynamic/prompt.md) · [trace.md](experiments/2_expense_claim/dynamic/trace.md) · [events.md](experiments/2_expense_claim/dynamic/events.md) · [output.md](experiments/2_expense_claim/dynamic/output.md) · [response.md](experiments/2_expense_claim/dynamic/response.md)

เปิด [เอกสารที่ render แล้ว](experiments/2_expense_claim/dynamic/output.render.html) เพื่อดู diagram ประกอบ Plan Version Log:

| Version | Reason | Changes | Reuse |
| --- | --- | --- | --- |
| v1 | แผนเริ่มต้น NEW INFORMATION = NONE | สร้าง T1–T4 | – |

| งาน | ผลลัพธ์ตาม trace | การตัดสินของ EVALUATOR |
| --- | --- | --- |
| T1 | DONE วิเคราะห์ต้นทาง ผู้เกี่ยวข้อง ข้อขัดแย้ง สมมติฐาน | ใช่ |
| T2 | DONE จัดทำ FR / NFR / BR / Use Case | ใช่ |
| T3 | DONE Mermaid และ Traceability Matrix | ใช่ |
| T4 | DONE ตรวจโครงสร้างและส่งมอบเอกสาร | ใช่; บรรลุเป้าหมาย |

trace ระบุว่า AI ไม่พบเครื่องมือ render Mermaid จึงตรวจโครงสร้าง ผลตรวจภายหลัง E6 = PASS ยืนยันการ render ตามวิธีตรวจใน JSON งาน T1–T4 DONE ทั้งหมดและไม่เกิด Re-plan

phase1: input **212,713**, cached **175,232**, output **20,666**, total **233,379** tokens; เวลา **444.0 วินาที**

จำนวนรอบ **1 plan_versions** ในเฟสแรก ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

### โจทย์ 3 × Dynamic — ย้ายระบบนัดหมาย

[prompt.md](experiments/3_clinic_migration/dynamic/prompt.md) · [trace.md](experiments/3_clinic_migration/dynamic/trace.md) · [events.md](experiments/3_clinic_migration/dynamic/events.md) · [output.md](experiments/3_clinic_migration/dynamic/output.md) · [response.md](experiments/3_clinic_migration/dynamic/response.md) · [prompt-phase2.md](experiments/3_clinic_migration/dynamic/prompt-phase2.md) · [response-phase2.md](experiments/3_clinic_migration/dynamic/response-phase2.md)

output.md เป็นฉบับหลังเฟส 2 ส่วน response.md เป็นคำตอบเฟสแรก เปิด [เอกสารที่ render แล้ว](experiments/3_clinic_migration/dynamic/output.render.html)

Plan Version Log v1 → v2 → v3:

| Version | Reason | Changes | Reuse |
| --- | --- | --- | --- |
| v1 | เฟส 1: แผนเริ่มต้น | T1–T6 | – |
| v2 | เฟส 1: พบงานที่ยังไม่มีในแผน จากผล T2 | ADD T2a; T3 → T2a | T1, T2 |
| v3 | เฟส 2: NEW INFORMATION: PDPA + LINE OA | ADD T7–T11 | As-Is / findings / ทะเบียนเดิม |

ตารางคัดจากสไลด์ โดย T3 → T2a หมายถึงปรับ Dependency ของ T3 ให้ขึ้นกับ T2a; Re-plan สะสม 2/3 ครั้ง และไม่มีงาน DROPPED ตาม response-phase2.md

phase1: input **347,232**, cached **305,280**, output **24,817**, total **372,049** tokens; เวลา **555.0 วินาที**

phase2: input **1,168,976**, cached **1,085,568**, output **50,444**, total **1,219,420** tokens; เวลา **550.0 วินาที**

จำนวนรอบ **3 plan_versions** รวมสองเฟส (นับรหัสไม่ซ้ำ ไม่บวกซ้ำ) ที่มา: [tests/experiments-results.json](tests/experiments-results.json) และ events.md ของชุดนี้

Change Request ใช้ NEW INFORMATION ส่งให้ PLANNER สร้างเวอร์ชันใหม่ โดยต้องแสดง Impact และ Reuse:

| Version | Impact analysis | Reuse |
| --- | --- | --- |
| v1 | ครอบคลุมผลงานเดิมทั้งหมด | ยังไม่มีงาน DONE |
| v2 | เพิ่ม T2a เป็นทะเบียนตัดสินข้อมูล; T3–T6 ยังไม่เริ่ม จึงเพิ่มข้อกำหนดให้แต่ละงาน ไม่มี DONE ที่ต้องทำซ้ำ | เก็บ T1 (As-Is/สมมติฐาน) และ T2 (findings) ใช้ต่อทั้งหมด |
| v3 | กระทบบางส่วนของ T1 ขอบเขต, T2 Findings, T2a review gate, T3 To-Be/Model, T4 Mapping/Migration, T5 Gap/Roll-out, T6 ผลตรวจ | As-Is ทั้งหมด, findings/ทะเบียนเดิม, master/ตารางคิว, source lineage, idempotency, single writer, rollback journal |

งานเดิมคง DONE และเพิ่มงาน T7–T11 ซึ่ง DONE ครบในเฟส 2 รายละเอียดเหตุผลและงานที่ใช้ต่ออยู่ใน trace.md และ response-phase2.md

### ผลเกณฑ์ §5 ของ Dynamic

ผลจาก [tests/experiments-results.json](tests/experiments-results.json) ต้องอ่านข้อจำกัดของ heuristic ควบคู่กับ PASS/FAIL:

#### โจทย์ 1 — จองห้องประชุม

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 8 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → การจองของฉัน; สถานะ: 1 คลิก: หน้าแรก → การจองของฉัน (วิธี: heuristic) |
| F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network (วิธี: script) |
| F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 8 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → การจองของฉัน; สถานะ: 1 คลิก: หน้าแรก → การจองของฉัน (วิธี: heuristic) |
| F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source (วิธี: script) |

#### โจทย์ 2 — เบิกค่าใช้จ่าย

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| E1_trace_all_sentences — Traceability ครอบคลุม keyword ต้นทางทั้ง 9 กลุ่ม | PASS | output.md: Traceability; กลุ่ม 1: 495; กลุ่ม 2: 496,503,504,508; กลุ่ม 3: 498; กลุ่ม 4: 499; กลุ่ม 5: 500; กลุ่ม 6: 501,502; กลุ่ม 7: 503; กลุ่ม 8: 504; กลุ่ม 9: 505 (วิธี: heuristic) |
| E2_conflict_open_issue — Open Issues มีเกณฑ์ 5,000 และ 10,000 | PASS | output.md:130,130; Open Issues: พบทั้งสองค่า (วิธี: script) |
| E3_no_invented_amounts — ไม่พบตัวเลขวงเงินที่พักที่แต่งเพิ่มใน FR/BR | PASS | output.md:61; สแกนตัวเลข+บาท ห่างจาก ที่พัก/คืน/วงเงิน ไม่เกิน 100 ตัวอักษร; ไม่พบค่านอก 5,000/10,000 (วิธี: heuristic) |
| E4_entity_consistency — ชื่อ participant/entity ใน Sequence/State เทียบกับ ERD | FAIL | output.md:183,371,450; ERD 15 entity; ชื่อไม่พบ: D (ฐานข้อมูล), S (ระบบเบิกค่าใช้จ่าย); เทียบชื่อ literal (ตัด _/ไม่สนตัวพิมพ์); participant ที่เป็นระบบ/บทบาทอาจเป็น false positive; ไม่รับรอง attribute/ความหมาย (วิธี: heuristic) |
| E5_state_holder — ชื่อ state หรือ note ระบุผู้ถือเรื่อง | PASS | output.md:453,454,455; ตรวจเฉพาะชื่อ state และ note (วิธี: heuristic) |
| E6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | PASS | output.md:149,183,371,450; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render (วิธี: render) |

#### โจทย์ 3 — ย้ายระบบนัดหมาย

| id / เกณฑ์ | ผล | หลักฐานและวิธีตรวจ |
| --- | --- | --- |
| M1_five_problem_types — ตาราง Data Quality Findings มีอย่างน้อย 5 แถวปัญหา | PASS | output.md:199,200,201,202,203,204,205,206,207,208,209,210; ตาราง Findings แรกมี 12 แถวข้อมูล (ไม่รับรองว่าทุกแถวเป็นคนละประเภท) (วิธี: heuristic) |
| M2_ambiguous_date_flagged — แถววันที่เป้าหมายมีข้อความ flag ความกำกวม | PASS | output.md:199; พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย; ไม่ตัดสินการตีความวันที่ (วิธี: script) |
| M3_identity_strategy — หัวข้อ mapping/migration/identity มี normalization และการยืนยัน | PASS | output.md:568,604,619; normalization marker; output.md:565,568,569; confirmation marker ในหัวข้อที่กำหนด (วิธี: heuristic) |
| M4_plan_version_log — บันทึกเวอร์ชันแผนมี v1 และ v2 | PASS | output.md:5,42,22,40; หัวข้อ Plan Version/ชื่อไทย/Plan vN: v1=True, v2=True; v1.1 ไม่นับเป็น v2 (วิธี: script) |
| M5_impact_analysis — เฟส 2 มีคำ Impact และ Reuse หรือคงเดิม | PASS | Impact: output.md:36, output.md:75, output.md:784; Reuse/คงเดิม: output.md:19, output.md:37, output.md:71; ตรวจคำเท่านั้น (วิธี: script) |
| M6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | PASS | output.md:173,264,317,627; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render (วิธี: render) |

### จุดสังเกตของ Dynamic

1. เทียบ v1 กับ v2/v3 ของโจทย์ 3: AI reuse งานเดิมจริงหรือรื้อใหม่? ดู Reuse และสถานะ DONE ที่คงไว้
2. เหตุผลของ v2 อ้างสิ่งที่พบจากผล T2 หรืออ้างลอย ๆ? trace รองรับ Trigger อย่างไร?
3. โจทย์ 1 และ 2 ไม่เกิด Re-plan เพราะไม่มีข้อมูลใหม่หรือ EVALUATOR ตัดสินหลวม? จะออกแบบ Trigger ให้ทดสอบได้อย่างไร?
4. ถ้าใช้ Static Graph กับโจทย์ 3 จะติดตรงไหน? เทียบการรับ Change Request ของบท Graph กับ Plan v3
5. Re-plan ครั้งที่ 2 ใช้โควตา 2/3 แล้ว ถ้ามี Change Request อีกจะเกิดอะไร และเมื่อใดต้องหยุด?
6. เฟส 2 ของโจทย์ 3 ใช้โทเคนมากกว่าเฟสแรก เกิดจาก resume thread หรืองานเพิ่ม? ต้องดูหลักฐานใดใน events.md ก่อนสรุป?

## บทที่ 4 สรุปและเปรียบเทียบ

### ภาพรวม 3 Workflow

![เปรียบเทียบ Loop Graph และ Dynamic Workflow](img/10-three-workflows-compare.png)

ภาพเปรียบเทียบ: Loop ให้ Iteration Log, Graph ให้ Execution Trace, Dynamic ให้ Plan Version Log ใช้ร่องรอยเหล่านี้อธิบายว่าผลงานมาถึงผลสุดท้ายได้อย่างไร

### ตาราง 3 โจทย์ × 3 Workflow

| โจทย์ | Loop | Graph | Dynamic |
| --- | --- | --- | --- |
| 1. จองห้องประชุม | [loop](experiments/1_meeting_room/loop/): 1 iterations; ผ่าน 4/4 | [graph](experiments/1_meeting_room/graph/): 6 nodes; ผ่าน 4/4 | [dynamic](experiments/1_meeting_room/dynamic/): 1 plan_versions; ผ่าน 4/4 |
| 2. เบิกค่าใช้จ่าย | [loop](experiments/2_expense_claim/loop/): 1 iterations; ผ่าน 5/6 | [graph](experiments/2_expense_claim/graph/): 6 nodes; ผ่าน 5/6 | [dynamic](experiments/2_expense_claim/dynamic/): 1 plan_versions; ผ่าน 5/6 |
| 3. ย้ายระบบนัดหมาย | [loop](experiments/3_clinic_migration/loop/): 3 iterations; ผ่าน 4/6 | [graph](experiments/3_clinic_migration/graph/): 6 nodes; ผ่าน 5/6 | [dynamic](experiments/3_clinic_migration/dynamic/): 3 plan_versions; ผ่าน 6/6 |

Workflow ที่คาดว่าเห็นจุดเด่นตามลักษณะโจทย์คือ Loop สำหรับ UI, Graph สำหรับแบบจำลองหลาย artifact และ Dynamic สำหรับขอบเขตที่เปลี่ยนระหว่างทาง แต่ต้องใช้ผลจริงประกอบการตัดสิน ชุดเสริม [loop_claude](experiments/1_meeting_room/loop_claude/) แยกจากตารางหลัก

### โจทย์ 1: เทียบเว็บจริงและผลตรวจ

เปิด [Loop](experiments/1_meeting_room/loop/output.html), [Graph](experiments/1_meeting_room/graph/output.html), [Dynamic](experiments/1_meeting_room/dynamic/output.html) และ [Loop บน Claude Code](experiments/1_meeting_room/loop_claude/output.html) เพื่อทดลองเทียบกัน สไลด์มีเว็บฝังให้คลิกและสลับแท็บได้

| Workflow | รอบ | F1 | F2 | F3 | F4 | total tokens | เวลา (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| loop | 1 iterations | PASS | PASS | PASS | PASS | 255,365 | 217.0 |
| graph | 6 nodes | PASS | PASS | PASS | PASS | 598,889 | 392.0 |
| dynamic | 1 plan_versions | PASS | PASS | PASS | PASS | 383,635 | 400.0 |
| loop_claude | 1 iterations | FAIL | PASS | FAIL | PASS | 128,963 | 145.0 |

Loop บันทึกหยุดเมื่อ CRITIC ผ่านครบใน Iteration แรก; Graph มี N1b และ event N5_MERGE ก่อน N5 DONE; Dynamic มี Plan v1 และไม่เกิด Re-plan ผลสคริปต์ของชุดเสริม F1/F3 FAIL เพราะไม่พบการยกเลิกในเส้นทางที่ตรวจ

### โจทย์ 2: เทียบเอกสารและผลตรวจ

เปิดผลงาน [Loop](experiments/2_expense_claim/loop/output.md), [Graph](experiments/2_expense_claim/graph/output.md) และ [Dynamic](experiments/2_expense_claim/dynamic/output.md) แล้วเทียบ Open Issues และความสอดคล้องของ diagram

| Workflow | รอบ | E1 | E2 | E3 | E4 | E5 | E6 | total tokens | เวลา (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop | 1 iterations | PASS | PASS | PASS | FAIL | PASS | PASS | 188,831 | 302.0 |
| graph | 6 nodes | PASS | PASS | PASS | FAIL | PASS | PASS | 852,825 | 521.0 |
| dynamic | 1 plan_versions | PASS | PASS | PASS | FAIL | PASS | PASS | 233,379 | 444.0 |

ทุก workflow ส่งข้อขัดแย้ง 5,000/10,000 เป็น Open Issue จึงผ่าน E2 ส่วน E4 FAIL ทุกชุดจาก heuristic ที่เทียบชื่อ participant/entity กับ ERD แบบ literal ชื่อระบบหรือบทบาทอาจทำให้เกิด false positive ต้องอ่าน diagram ประกอบก่อนตัดสินความหมาย

### โจทย์ 3: เทียบเอกสารหลัง Change Request

เปิดผลงาน [Loop](experiments/3_clinic_migration/loop/output.md), [Graph](experiments/3_clinic_migration/graph/output.md) และ [Dynamic](experiments/3_clinic_migration/dynamic/output.md) ซึ่งเป็นฉบับหลังเฟส 2 คำตอบก่อน Change Request อยู่ใน response.md ของแต่ละชุด

| Workflow | Prompt เฟส 2 | คำตอบเฟส 2 |
| --- | --- | --- |
| Loop | [prompt-phase2.md](experiments/3_clinic_migration/loop/prompt-phase2.md) | [response-phase2.md](experiments/3_clinic_migration/loop/response-phase2.md) |
| Graph | [prompt-phase2.md](experiments/3_clinic_migration/graph/prompt-phase2.md) | [response-phase2.md](experiments/3_clinic_migration/graph/response-phase2.md) |
| Dynamic | [prompt-phase2.md](experiments/3_clinic_migration/dynamic/prompt-phase2.md) | [response-phase2.md](experiments/3_clinic_migration/dynamic/response-phase2.md) |

### การรับมือ Change Request เดียวกัน

| Workflow | กลไกที่ Template สั่ง | สิ่งที่เกิดจริง | งานที่เพิ่มหรือรันซ้ำ | M4 | M5 |
| --- | --- | --- | --- | --- | --- |
| Loop | CRITIC ตรวจใหม่ แล้วแก้เฉพาะ FAIL | Iteration 2: C1 FAIL; Iteration 3: แก้ C1 → PASS; output เป็น v1.1 | เพิ่ม Iteration 2–3 | FAIL | FAIL |
| Graph | ระบุ Node ที่ต้องรันซ้ำ และ reuse ที่ input ไม่เปลี่ยน | รันซ้ำทุก Node เพราะผล N1 เปลี่ยน; N1b, N2 ได้ผลเดิมทุกไบต์ | N1, N1b, N2, N3, N4, N5 รันซ้ำ | PASS | FAIL |
| Dynamic | NEW INFORMATION → Re-plan พร้อม Impact/Reuse | Plan v3; reuse As-Is/findings เดิม; Re-plan สะสม 2/3 | เพิ่ม T7–T11; งานเดิมคง DONE | PASS | PASS |

ที่มา: trace.md และ response-phase2.md ของแต่ละชุด ผล M4/M5 จาก [tests/experiments-results.json](tests/experiments-results.json) M4 ตรวจ v1 และ v2 โดย v1.1 ไม่นับเป็น v2; M5 ตรวจคำ Impact ร่วมกับ Reuse/คงเดิม ไม่ได้รับรองความหมายทั้งหมด โทเคนและเวลาของเฟส 2 แสดงแยกในตารางถัดไป

### เหมาะเมื่อ / ไม่เหมาะเมื่อ / ร่องรอย

| มิติ | Loop | Graph | Dynamic |
| --- | --- | --- | --- |
| เหมาะเมื่อ | งานชิ้นเดียว เกณฑ์ชัด ปรับปรุงซ้ำได้ | งานหลายส่วน แยกทำได้ ต้องสอดคล้องกัน | ขอบเขตไม่นิ่ง มีข้อมูลใหม่กลางทาง |
| จุดอ่อนและกรณีไม่เหมาะ | แก้ทีละจุด ไม่เห็นภาพรวม; งานที่ไม่มีเกณฑ์ตรวจชัดเจนควรกำหนดเกณฑ์ก่อน | ต้องรู้โครงสร้างงานล่วงหน้า; ขอบเขตที่เปลี่ยนโครงงานบ่อยทำให้ Dependency เดิมไม่พอ | ซับซ้อน ควบคุมยาก ต้องจำกัด Re-plan; งานขอบเขตนิ่งอาจไม่คุ้มความซับซ้อน |
| ร่องรอยที่ได้ | Iteration Log | Execution Trace | Plan Version Log |

### โทเคน เวลา และจำนวนรอบจริงครบ 13 เฟส

ค่าทั้งหมดมาจาก `meta` ใน [tests/experiments-results.json](tests/experiments-results.json) task 1 คือจองห้องประชุม, 2 คือเบิกค่าใช้จ่าย, 3 คือย้ายระบบนัดหมาย

| ชุด / เฟส | engine | รอบ | input | cached | output | total | วินาที |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 / loop / phase1 | codex | 1 iterations | 244,784 | 212,096 | 10,581 | 255,365 | 217.0 |
| 1 / graph / phase1 | codex | 6 nodes | 590,224 | 528,000 | 8,665 | 598,889 | 392.0 |
| 1 / dynamic / phase1 | codex | 1 plan_versions | 365,708 | 328,320 | 17,927 | 383,635 | 400.0 |
| 1 / loop_claude / phase1 | claude | 1 iterations | 25,501 | 91,253 | 12,209 | 128,963 | 145.0 |
| 2 / loop / phase1 | codex | 1 iterations | 174,129 | 152,576 | 14,702 | 188,831 | 302.0 |
| 2 / graph / phase1 | codex | 6 nodes | 832,671 | 771,840 | 20,154 | 852,825 | 521.0 |
| 2 / dynamic / phase1 | codex | 1 plan_versions | 212,713 | 175,232 | 20,666 | 233,379 | 444.0 |
| 3 / loop / phase1 | codex | 3 iterations | 150,108 | 121,728 | 12,446 | 162,554 | 251.0 |
| 3 / loop / phase2 | codex | 3 iterations | 490,035 | 433,280 | 26,413 | 516,448 | 297.0 |
| 3 / graph / phase1 | codex | 6 nodes | 589,489 | 552,448 | 16,693 | 606,182 | 492.0 |
| 3 / graph / phase2 | codex | 6 nodes | 1,819,842 | 1,749,888 | 35,270 | 1,855,112 | 687.0 |
| 3 / dynamic / phase1 | codex | 3 plan_versions | 347,232 | 305,280 | 24,817 | 372,049 | 555.0 |
| 3 / dynamic / phase2 | codex | 3 plan_versions | 1,168,976 | 1,085,568 | 50,444 | 1,219,420 | 550.0 |

วิธีอ่านตาราง:

- Codex: total = input + output โดย cached เป็นส่วนหนึ่งของ input อยู่แล้ว
- Claude: input = input_tokens + cache_creation_input_tokens; total = input + cached + output จาก result.usage ไม่บวก modelUsage หรือ reasoning ซ้ำ
- ตัวเลขนี้ไม่ใช่ยอดบิลทั้งบัญชี และนิยาม input/cached ของแต่ละ CLI ต้องอ่านก่อนเปรียบเทียบ
- “รอบ” นับรหัสไม่ซ้ำใน trace: Loop นับ Iteration, Graph นับ Node ID, Dynamic นับ Plan version จึงไม่ใช่หน่วยงานเดียวกัน
- รอบของโจทย์ 3 เป็นยอดรวมสองเฟสที่แสดงซ้ำในแต่ละแถว ห้ามนำคอลัมน์นี้มาบวก Graph รัน Node เดิมซ้ำได้โดยไม่เพิ่มจำนวน Node ID
- เวลาเป็น duration_s รายเฟส ไม่รวมเวลาพักระหว่างเฟส ชื่อโมเดลของชุด Codex ในข้อมูลผลตรวจเป็น “ไม่มีข้อมูล”; ชุดเสริมบันทึก `claude-fable-5-1`

ผลรวมโทเคนและเวลาของโจทย์ 3 คำนวณจากสองเฟสใน JSON:

| Workflow | total tokens รวม | เวลา (s) รวม |
| --- | --- | --- |
| loop | 679,002 | 548.0 |
| graph | 2,461,294 | 1,179.0 |
| dynamic | 1,591,469 | 1,105.0 |

เฟส 2 ใช้โทเคนมากกว่าเฟสแรกทุก workflow แต่ยังสรุปสาเหตุจากยอดรวมเพียงอย่างเดียวไม่ได้ ให้พิจารณา event และบริบทที่ resume ใน events.md

### สรุปผลเกณฑ์ 3 × 3

| โจทย์ | Loop | Graph | Dynamic |
| --- | --- | --- | --- |
| 1. จองห้องประชุม | ผ่าน 4/4; ไม่มีเกณฑ์ FAIL | ผ่าน 4/4; ไม่มีเกณฑ์ FAIL | ผ่าน 4/4; ไม่มีเกณฑ์ FAIL |
| 2. เบิกค่าใช้จ่าย | ผ่าน 5/6; FAIL: E4 | ผ่าน 5/6; FAIL: E4 | ผ่าน 5/6; FAIL: E4 |
| 3. ย้ายระบบนัดหมาย | ผ่าน 4/6; FAIL: M4, M5 | ผ่าน 5/6; FAIL: M5 | ผ่าน 6/6; ไม่มีเกณฑ์ FAIL |

นับเฉพาะ `pass=true` จำนวนผ่าน/ทั้งหมดไม่ใช่คะแนนรับรองคุณภาพ ผลอาจต่างจาก Workflow ที่คาดว่าเด่น วิธีตรวจและข้อจำกัดอ่านได้ใน [experiments/README.md](experiments/README.md)

F1/F3 ตรวจ keyword ของ feature ในเส้นทาง DOM ที่สำรวจ ไม่ใช่การรับรองทุกพฤติกรรม; E1 ตรวจกลุ่ม keyword ใน Traceability; E4 เทียบชื่อ literal และอาจมี false positive; M1 นับแถว Findings ไม่รับรองว่าทุกแถวเป็นคนละประเภท; M2 ตรวจข้อความ flag; M5 ตรวจคำ Impact/Reuse ส่วน E6/M6 ใช้การ render Mermaid จริง เกณฑ์ไม่มีข้อมูลต้องรายงาน “ไม่มีข้อมูล” ไม่แทนด้วย PASS หรือ FAIL

### คำถามท้ายบท

1. โจทย์ 1 ผ่าน F1–F4 เหมือนกันทั้ง 3 workflow แล้วต่างกันตรงไหนเมื่ออ่านร่องรอยและโทเคน?
2. ทำไม E4 FAIL ทั้ง 3 ชุด เป็นข้อจำกัดของ workflow หรือของเกณฑ์ตรวจ?
3. Graph รันซ้ำทุก Node ในเฟส 2 ทั้งที่ Template สั่ง reuse จะแก้ TASK GRAPH/Dependency อย่างไร?
4. Loop รับ Change Request ได้ แต่ไม่ผ่าน M4 เรื่อง v1 → v2 เป็นข้อเสียเสมอหรือไม่?
5. ถ้าโจทย์เปลี่ยนเป็น “ระบบใหญ่ 10 โมดูล” จะเลือกอะไร และออกแบบเกณฑ์ตรวจอย่างไร?
6. ชุดเสริม loop_claude ได้ F1/F3 FAIL จาก prompt เดียวกัน บอกอะไรเรื่อง prompt กับโมเดล และต้องมีหลักฐานอะไรเพิ่ม?

## ภาคผนวก

### วิธีรันซ้ำด้วย cyolo1 / yolo1

คำสั่งตาม [experiments/README.md](experiments/README.md) ใช้สำเนาโฟลเดอร์ทดลองใหม่และคง prompt ภาษาไทยเดิม รันจากโฟลเดอร์สำเนานั้น เลือกเพียง engine เดียวต่อการรัน ใช้เฉพาะ `cyolo1` และ `yolo1`; yolo1 ทีละ 1 process ส่วน cyolo1 ไม่เกิน 2 jobs พร้อมกัน หากโควตาหมดให้หยุดรอ

```bash
# Codex: เฟสแรก
date -u +%FT%TZ > .start
printf "%s\n" "codex cyolo1" > .engine
cyolo1 exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o response.md "$(cat prompt.md)" < /dev/null > log.jsonl 2> .stderr.txt
printf "exit=%s\n" "$?" > .exit
date -u +%FT%TZ > .end
```

```bash
# Claude: เฟสแรก; รันบัญชีนี้ทีละ process
date -u +%FT%TZ > .start
printf "%s\n" "claude yolo1" > .engine
yolo1 -p --model fable --effort high --strict-mcp-config --output-format stream-json --verbose "$(cat prompt.md)" < /dev/null > log.jsonl 2> .stderr.txt
printf "exit=%s\n" "$?" > .exit
date -u +%FT%TZ > .end
python3 - <<'PY'
import json
from pathlib import Path
rows = [json.loads(line) for line in Path("log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
result = next((r for r in reversed(rows) if r.get("type") == "result"), {})
Path("response.md").write_text(result.get("result", ""), encoding="utf-8")
PY
```

ชื่อโมเดลในตัวอย่างเป็นค่าของ harness ไม่ใช้แทนชื่อโมเดลที่ขาดใน log ของการทดลอง สำหรับเฟส 2 ให้อ่าน thread_id/session_id ของเฟสแรกเป็นตัวแปร SESSION แล้ว resume session เดิมหลังได้รับผลเฟสแรก เก็บ `.start2`, `.end2`, `.exit2`, `.stderr2.txt` แยกจากเฟสแรก เลือกคำสั่งให้ตรง engine:

```bash
# Codex: เฟส 2
cyolo1 exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o response-phase2.md resume "$SESSION" "$(cat prompt-phase2.md)" < /dev/null > log-phase2.jsonl 2> .stderr2.txt
# หรือ Claude: เฟส 2
yolo1 -p --resume "$SESSION" --model fable --effort high --strict-mcp-config --output-format stream-json --verbose "$(cat prompt-phase2.md)" < /dev/null > log-phase2.jsonl 2> .stderr2.txt
```

สำหรับ Claude ให้แยก result เป็น response-phase2.md ด้วยวิธีเดียวกับเฟสแรก โดยเปลี่ยนชื่อไฟล์นำเข้าเป็น log-phase2.jsonl และชื่อไฟล์ผลลัพธ์เป็น response-phase2.md

เมื่อกลับรากโปรเจกต์แล้ว ใช้คำสั่งกับ path ของสำเนาชุดใหม่ แทน `<task>/<workflow>` ก่อนรัน:

```bash
python3 tools/events_from_log.py --help
python3 tools/shoot.py --help
python3 tools/events_from_log.py experiments/<task>/<workflow>
python3 tools/shoot.py experiments/<task>/<workflow>
# ตรวจผลการทดลองตามเกณฑ์; สร้าง JSON และ experiments/README.md ใหม่
python3 tests/check_experiments.py
```

events.md ต้องถอดจาก log จริงด้วยสคริปต์ ส่วน trace/response/output เป็นหลักฐานที่ AI สร้าง เก็บต้นฉบับไว้เพื่อให้ตรวจย้อนกลับได้ การตรวจผลด้วย check_experiments.py ไม่เรียก AI และไม่เขียนทับหลักฐานดิบ

### รายการไฟล์และเครื่องมือ

| ไฟล์หรือโฟลเดอร์ | ใช้ทำอะไร |
| --- | --- |
| [AI_Workflow_Engineering.html](AI_Workflow_Engineering.html) | สไลด์เปิดได้ทันที มี Overview, Copy, diagram และผลงานที่ฝังไว้ |
| [experiments/README.md](experiments/README.md) | ผลทุกชุด นิยามโทเคน เวลา รอบ และวิธีตรวจ |
| [experiments/](experiments/) | Prompt, trace, events, response, output, log และภาพของแต่ละชุด |
| [img/](img/) | ภาพประกอบ PNG, SVG และต้นฉบับ Excalidraw |
| [docs/test-report.md](docs/test-report.md) | ผลตรวจ deck วิธีทดสอบ และข้อจำกัด |
| [tests/results.json](tests/results.json) | จำนวนหน้าและผลทดสอบสไลด์ |
| [tests/experiments-results.json](tests/experiments-results.json) | เวลา โทเคน จำนวนรอบ ผลเกณฑ์และหลักฐานจริง |
| [tests/test_slides.py](tests/test_slides.py) | ตรวจการแสดงผลและพฤติกรรมของสไลด์ด้วย Playwright |
| [tests/check_experiments.py](tests/check_experiments.py) | ตรวจผลการทดลอง และสร้างตารางสรุป |
| [tests/screenshots/](tests/screenshots/) | ภาพตรวจสไลด์และ Overview |
| [tools/events_from_log.py](tools/events_from_log.py) | ถอด events จาก log JSONL |
| [tools/shoot.py](tools/shoot.py) | เปิดผลงานและ capture ด้วย Playwright |
| [tools/render_md.py](tools/render_md.py) | render Markdown และ Mermaid |
| [src/README.md](src/README.md) | สัญญา fragment และวิธี build |
| [src/build_deck.py](src/build_deck.py) | ประกอบสไลด์เป็น HTML ไฟล์เดียว |
| [src/slides/00-intro.html](src/slides/00-intro.html) | ต้นทางบทนำ |
| [src/slides/10-loop.html](src/slides/10-loop.html) | ต้นทาง Loop Engineering |
| [src/slides/20-graph.html](src/slides/20-graph.html) | ต้นทาง Graph Engineering |
| [src/slides/30-dynamic.html](src/slides/30-dynamic.html) | ต้นทาง Dynamic Workflow |
| [src/slides/40-summary.html](src/slides/40-summary.html) | ต้นทางสรุปและเปรียบเทียบ |
| [src/engine/](src/engine/) | ส่วนแสดงผลและควบคุม deck |

บันทึกผู้สอนอยู่ใน [docs/teacher-notes.md](docs/teacher-notes.md)

### วิธี build สไลด์ใหม่

ติดตั้ง Python packages `beautifulsoup4`, `markdown-it-py`, `playwright` และ Chromium ของ Playwright พร้อม Mermaid JavaScript ในเครื่อง ตั้ง `MERMAID_JS` ให้ชี้ไฟล์นั้นได้ คำสั่งจาก [src/README.md](src/README.md) รันจากรากโปรเจกต์:

```bash
python3 src/build_deck.py --slides src/slides --root . --out AI_Workflow_Engineering.html
python3 tests/test_slides.py --html AI_Workflow_Engineering.html --out tests/results.json --shots tests/screenshots
```

ผลตรวจ deck ล่าสุดใน [tests/results.json](tests/results.json): 107 หน้า, ok=true, overflow=0, console_errors=0, copy_ok=true, iframe โหลด 12/12, Mermaid SVG 75, tabs_ok=true รายละเอียดวิธีตรวจอยู่ใน [docs/test-report.md](docs/test-report.md) การโหลด iframe ผ่านไม่ได้รับรองทุกฟังก์ชันของเว็บ และการทดสอบ Copy/แท็บมีขอบเขตตามรายงาน

### รูปแบบฉบับอ่านต่างจากสไลด์อย่างไร

ฉบับนี้เรียงตามบทและลำดับเนื้อหาของสไลด์ รวมหน้าร่องรอยที่ต่อเนื่องเป็นตาราง Markdown และรวมตารางโทเคนทุกเฟสไว้ด้วยกัน รูปใช้ PNG; Template และโจทย์ใช้โค้ดบล็อก; ผลงานที่สไลด์ฝังแบบโต้ตอบใช้ลิงก์ไปไฟล์จริง ตารางที่สไลด์แยกเฟสถูกวางต่อกันให้อ่านได้โดยไม่สลับหน้า เนื้อหาแนวคิดและผลตรวจคงตามต้นทาง
