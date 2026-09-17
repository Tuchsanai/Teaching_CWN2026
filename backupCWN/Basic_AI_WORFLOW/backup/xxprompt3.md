# สเปกสื่อการสอน: Loop Engineering · Graph Engineering · Dynamic Workflow


## Workflow
-  ใช้ base_wave_verify_graph.md

---
## 0. ผลลัพธ์ที่ต้องส่ง

| ไฟล์ | เนื้อหา |
| --- | --- |
| `AI_Workflow_Engineering.html` | สไลด์สื่อการสอนภาษาไทย ไฟล์เดียว เปิดได้ทันที |
| `readme.md` | สื่อการสอนภาษาไทยไฟล์เดียว เปิดได้ทันที อ้างอิงจาก AI_Workflow_Engineering.html|
| `experiments/` | ร่องรอยการทดลองจริง (prompt ที่ป้อน, log กระบวนการ, ผลลัพธ์, screenshot) |



### Slide HTML

- ไฟล์เดียว, CSS/JS inline, **ห้าม CDN** · ภาษาไทยกระชับ แบ่งเป็นตอน
- หน้า overview + เลขหน้า + diagram (inline SVG) + code snippet
- ไม่พึ่งเครือข่าย · เลื่อนด้วยลูกศร/คลิก · รูป Excalidraw ฝังเป็น SVG/PNG · โค้ด Template มีปุ่ม copy · ภาษาไทย คำศัพท์เทคนิคภาษาอังกฤษ

**เครื่องมือผลิต:** รูปประกอบทุกรูปวาดด้วย **Excalidraw MCP** · การทดลองรันจริงผ่านเว็บและ capture หน้าจอด้วย **Playwright CLI**

---

## 1. แนวคิดหลักของบทเรียน

**ประโยคเดียวที่สรุปทั้งบทเรียน:** *โจทย์เดิม แต่เปลี่ยนวิธีออกแบบ Workflow → ผลลัพธ์ที่ได้ต่างกัน*

วิธีสอนคือใช้ **โจทย์กลาง 3 ข้อ** (ดูหัวข้อ 5) แล้วให้ AI ทำโจทย์เดิมซ้ำ 3 รอบ ด้วย Workflow คนละแบบ

| รอบ | Workflow | นักศึกษาจะเห็นว่า |
| --- | --- | --- |
| 1 | **Loop** | ทำ → ตรวจ → แก้ วนจนผ่านเกณฑ์ |
| 2 | **Graph** | แตกงานเป็นส่วน ทำขนานกัน แล้วรวมกลับ |
| 3 | **Dynamic** | วางแผนก่อน ทำไปเจออะไรใหม่ก็ปรับแผนได้ |

สิ่งที่ต้องการให้นักศึกษาเปรียบเทียบได้มี 3 ชั้น: **วิธีคิด → วิธีเขียน Prompt → ผลลัพธ์**

**กติกาสำคัญ:** ทุกการทดลองต้องโชว์ *ระหว่างทาง* ด้วย (log ว่า AI คิด/แก้/ปรับอะไรบ้าง) ไม่ใช่โชว์แค่ผลสุดท้าย เพราะความต่างของ Workflow อยู่ที่กระบวนการ ไม่ใช่ที่คำตอบ

### Learning Path (ใช้เป็นรูปแรกของสไลด์)

```text
บทที่ 1 Loop         บทที่ 2 Graph            บทที่ 3 Dynamic           บทที่ 4 สรุป
ทำ-ตรวจ-แก้ วนซ้ำ  → แตกงาน/ทำขนาน/รวม  → วางแผนแล้วปรับได้   → โจทย์แบบไหนใช้อะไร
(ง่าย)                (ปานกลาง)                 (ยาก)                     (เปรียบเทียบ)
```

---

## 2. เป้าหมายการเรียนรู้

จบบทเรียนแล้วนักศึกษาต้องทำสิ่งเหล่านี้ได้

**เข้าใจแนวคิด**

1. อธิบายวงจร Loop (Generate → Evaluate → Improve) และออกแบบเองได้
2. อธิบายส่วนประกอบของ Graph: Node, Edge, State, Dependency
3. ออกแบบ Graph ได้ 3 แบบ: Sequential, Fan-out/Fan-in, Conditional
4. บอกได้ว่า Static Graph กับ Dynamic Workflow ต่างกันตรงไหน
5. ออกแบบโครง Planner–Executor–Evaluator ได้

**ลงมือทำ**

6. เขียน Prompt ควบคุมแต่ละ Workflow แล้วรันจริงบน Codex / Claude Code (รวมถึงลองใช้ skill `cyolo` และ `yolo`)
7. เปรียบเทียบผลจากโจทย์เดียวกันทั้ง 3 Workflow แล้วสรุปได้ว่า *สถานการณ์แบบไหนควรใช้ Workflow แบบใด*

---

## 3. โครงสร้างการสอน (ทุกบทใช้ 5 ขั้นเหมือนกัน)

ทั้ง 3 บทเดินตามแบบแผนเดียวกัน เพื่อให้นักศึกษาคุ้นรูปแบบและเทียบกันข้ามบทได้ง่าย

| ขั้น | ชื่อ | ต้องมีอะไรในสไลด์ |
| --- | --- | --- |
| 1 | **Theory** | แนวคิดคืออะไร · มีส่วนประกอบอะไร · ทำงานอย่างไร · เหมาะกับปัญหาแบบไหน · ข้อดี/ข้อจำกัด · รูป Excalidraw ประกอบ |
| 2 | **Workflow Diagram** | รูป Excalidraw แสดงการไหลของงาน (รายละเอียดในหัวข้อ 6) |
| 3 | **Prompt Template** | Template ครบ 8 ส่วน copy ไปใช้ได้ทันที + อธิบายว่า *ทำไมต้องออกแบบแบบนี้* (หัวข้อ 7) |
| 4 | **ทดลองจริง** | เสียบโจทย์ลงใน `{{REQUIREMENT}}` แล้วรันจริง แสดงผลตามรูปแบบ Prompt → Process → Output (หัวข้อ 4) |
| 5 | **สังเกตผล** | ตารางร่องรอยกระบวนการ + คำถาม "จุดสังเกต" 3–7 ข้อให้นักศึกษาตอบ |

---

## 4. รูปแบบมาตรฐานการแสดงผลการทดลอง

ทุกการทดลองแสดงเป็น **3 กล่องเรียงกัน** เสมอ เพื่อตอบคำถาม "ป้อนอะไร → เกิดอะไร → ได้อะไร"

```text
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│ ① PROMPT ที่ป้อน   [📋] │ → │ ② PROCESS ที่เกิดขึ้น    │ → │ ③ OUTPUT ที่ได้          │
│ Template + โจทย์ ตัวเต็ม │   │ Iteration Log /         │   │ ผลสุดท้าย                │
│ (ห้ามย่อ · กด copy ได้)  │   │ Execution Trace /       │   │ ถ้าเป็นเว็บ → ฝังของจริง │
│                         │   │ Plan Version Log        │   │ ให้เปิดใช้ได้ในสไลด์     │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘
```

| กล่อง | คืออะไร | ข้อกำหนด |
| --- | --- | --- |
| ① Prompt | Template + โจทย์ที่เสียบเข้าไป | **แสดงตัวเต็ม ห้ามย่อ** · มีปุ่ม/icon copy มุมขวาบน กดแล้วได้ทั้งก้อนพร้อมเอาไปรันซ้ำได้ทันที · ถ้ายาวให้กล่อง scroll ได้ ไม่ตัดเนื้อหา |
| ② Process | ร่องรอยระหว่างทาง — Loop ได้ Iteration Log · Graph ได้ Execution Trace · Dynamic ได้ Plan Version Log | **หัวใจของบทเรียน ห้ามตัด และต้องมาจากการรันจริง ห้ามแต่ง** |
| ③ Output | ผลสุดท้าย | **ถ้าเป็นเว็บ ต้องมีของจริงให้ดู** — ฝังหน้าเว็บที่ AI สร้างลงในสไลด์ (iframe/srcdoc) ให้คลิกทดลองได้จริง ไม่ใช่แค่ screenshot · ถ้าเป็นเอกสาร Markdown ให้ render ในสไลด์ (Mermaid ต้อง render ได้) · screenshot ใช้เป็นภาพย่อในสไลด์สรุปเท่านั้น |

**ข้อกำหนดเพิ่มเติม**

- ในสไลด์สรุปของแต่ละโจทย์ ให้วางผล 3 Workflow **เคียงกัน** — ถ้าเป็นเว็บ ให้ฝัง 3 หน้าเว็บจริงเคียงกัน (หรือสลับดูด้วย tab) เพื่อคลิกเทียบได้ทันที
- เก็บหลักฐานทุกชุดที่ `experiments/<โจทย์>/<workflow>/` ประกอบด้วย `prompt.md` (ตัวเต็ม), `trace.md`, `output.*` (ไฟล์เว็บ/เอกสารจริง), `*.png`
- ไฟล์ HTML สไลด์ต้องยังเป็นไฟล์เดียว → ฝังหน้าเว็บผลลัพธ์แบบ inline (srcdoc) ไม่อ้างไฟล์ภายนอก

---

## 5. โจทย์กลาง 3 โจทย์

ทุกโจทย์ให้ AI **วิเคราะห์ Requirement → สร้างโครงสร้างระบบ → สร้างผลลัพธ์ที่ตรวจสอบและเปรียบเทียบได้** และต้องรันครบทั้ง 3 Workflow

| โจทย์ | แนวงาน | ความยากที่ฝังไว้ | Workflow ที่เห็นจุดเด่นชัด |
| --- | --- | --- | --- |
| 1. จองห้องประชุม | Requirement → UI Prototype | feature ตกหล่น, UX ไม่ชัด | **Loop** |
| 2. เบิกค่าใช้จ่าย | สัมภาษณ์ → System Model | ข้อขัดแย้ง, หลาย artifact ต้องสอดคล้อง | **Graph** |
| 3. ย้ายระบบนัดหมาย | As-Is → To-Be + Migration | ข้อมูลสกปรก, ขอบเขตไม่แน่นอน, Change Request | **Dynamic** |

### โจทย์ที่ 1 — ระบบจองห้องประชุม

```text
สร้างเว็บไซต์สำหรับระบบจองห้องประชุม
ระบบต้องสามารถ: แสดงห้องประชุม, ดูเวลาว่าง, จองห้อง, ยกเลิกการจอง, แสดงสถานะการจอง
Output: Web UI Mock-up ที่เปิดและทดลองใช้งานได้
```

**เกณฑ์ตรวจ:** ครบ 5 feature · เปิดใช้งานได้จริง (Playwright เปิดและคลิกทดสอบ) · Navigation ไปถึงทุก feature ได้ภายใน 2 คลิก

### โจทย์ที่ 2 — วิเคราะห์ Requirement ระบบเบิกค่าใช้จ่าย (บันทึกสัมภาษณ์ → System Model)

Input คือบันทึกสัมภาษณ์ดิบ ที่จงใจใส่ข้อขัดแย้งและข้อมูลไม่ครบ

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

**Output:** Markdown ไฟล์เดียว (diagram เป็น Mermaid) ประกอบด้วย Actor/Stakeholder · FR-xx และ NFR · BR-xx · Use Case Diagram · ERD · Sequence Diagram "ยื่นเบิก → อนุมัติ → จ่ายเงิน" · State Diagram ของใบเบิก · Traceability Matrix (ประโยคต้นทาง → FR/BR → Use Case → Entity) · Open Issues

**เกณฑ์ตรวจ**

- ทุกประโยคในบันทึก trace ไป FR/BR ได้อย่างน้อย 1 รายการ
- ตรวจพบข้อขัดแย้งเกณฑ์อนุมัติ (5,000 vs 10,000) และส่งเป็น Open Issue ไม่ตัดสินเอง
- ไม่แต่งตัวเลขวงเงินค่าที่พักขึ้นเอง
- Entity/Attribute ใน Sequence และ State ตรงกับ ERD
- State Diagram ตอบได้ว่า "ค้างอยู่ที่ใคร"
- Mermaid ทุกบล็อก render ได้

**ทำไมเหมาะกับ Graph:** fan-out สร้าง Use Case / ERD / Sequence คู่ขนาน แล้ว fan-in ตรวจความสอดคล้อง ได้ฝึก Conflict Resolution และ Self-consistency ที่อิงหลักฐาน

### โจทย์ที่ 3 — ย้ายระบบนัดหมายคลินิกจาก Google Sheet สู่ระบบกลาง (As-Is → To-Be + Change Request)

บริบท: คลินิกทันตกรรม 3 สาขา ใช้ Google Sheet แยกสาขา ร่วมกับจองผ่าน LINE ต้องการย้ายมาระบบนัดหมายกลาง

```csv
สาขา,วันที่,เวลา,ชื่อคนไข้,เบอร์,หมอ,บริการ,หมายเหตุ
ลาดกระบัง,03/09/2026,10:00,สมชาย ใจดี,081-234-5678,หมอเอ,ขูดหินปูน,
ลาดกระบัง,2026-09-03,10:00,สมชาย ใจดี,0812345678,หมอเอ,ขูดหินปูน,จองซ้ำทางไลน์
บางนา,3 ก.ย. 69,13:30,คุณมาลี,,หมอบี,จัดฟัน,ไม่มีเบอร์ ติดต่อทางไลน์
บางนา,03/09/2026,13:30,วิชัย ศรีสุข,089-111-2222,หมอบี,อุดฟัน,
อ่อนนุช,09/03/2026,09:00,Somchai Jaidee,081 234 5678,หมอเอ,ตรวจฟัน,หมอเอมาช่วยสาขานี้ทุกวันพุธ
```

**ปัญหาที่ซ่อนไว้ (ไม่บอกนักศึกษา — ใส่ในเฉลยของผู้สอนเท่านั้น):** รูปแบบวันที่ปน (dd/mm, ISO, พ.ศ. ย่อ) · จองซ้ำ · คนไข้เดียวกันแต่ชื่อ/เบอร์เขียนต่างกันข้ามสาขา (ไม่มี Patient ID) · หมอบีถูกจองชนเวลา · หมอคนเดียวหลายสาขา · เบอร์โทรขาด · แถว `09/03/2026` กำกวม (หมายเหตุ "วันพุธ" คือหลักฐานว่าเป็น 9 ก.ย. 2026 เพราะ 9 มี.ค. 2026 เป็นวันจันทร์)

**งานรอบแรก:** As-Is Process (Mermaid flowchart) · Data Quality Findings (ปัญหา / แถว / ผลกระทบ) · To-Be Process และ Data Model · Data Mapping + แผน Migration (รวมวิธีจับคู่ตัวตนคนไข้) · Gap Analysis + Roll-out Plan · Plan Version Log

**Change Request** (ปล่อยหลังได้ Plan v1)

```text
เจ้าของคลินิกแจ้งเพิ่ม:
1. ต้องเก็บความยินยอมของคนไข้ตาม PDPA
2. คนไข้ต้องจองคิวเองผ่าน LINE OA ได้
```

**เกณฑ์ตรวจ**

- พบปัญหาข้อมูลอย่างน้อย 5 ประเภท
- แถว `09/03/2026` ถูก flag ว่ากำกวม และตีความโดยอ้างหลักฐาน
- มีกลยุทธ์จับคู่ตัวตนคนไข้ (normalize เบอร์/ชื่อ) พร้อมกรณีที่ต้องให้คนยืนยัน
- Plan Version Log บันทึก v1 → v2 พร้อมเหตุผล
- Impact Analysis ของ Change Request ระบุ artifact ที่กระทบ และ reuse ส่วนที่ไม่กระทบ

**ทำไมเหมาะกับ Dynamic:** ขอบเขตงานรู้ได้หลังตรวจข้อมูล และมี Change Request กลางทาง — Static Graph คาดงาน cleaning ล่วงหน้าไม่ได้ ส่วน Loop วนแก้ทีละจุดโดยไม่วางแผนใหม่

---

## 6. เนื้อหาเฉพาะแต่ละบท

### บทที่ 1 — Loop Engineering

**คำเปรียบ:** นักเรียนส่งการบ้าน ครูตรวจตามเกณฑ์ ไม่ผ่านก็แก้เฉพาะจุดแล้วส่งใหม่ ไม่เกิน 3 ครั้ง

**Diagram**

```text
Requirement → Generate → Evaluate → ผ่าน? ─ใช่→ Result
                 ↑                     └ไม่→ Improve ─┘
```

**Theory ที่ต้องอธิบาย:** วงจร Generate → Evaluate → Improve · ทำไมต้องแยก Generator กับ Critic · เกณฑ์แบบ PASS/FAIL · Stop Condition และทางออกเมื่อวนแล้วไม่ดีขึ้น

**ตัวอย่างผลที่คาดหวัง (โจทย์ 1)**

| Iteration | สิ่งที่เปลี่ยน | ผลตรวจ |
| --- | --- | --- |
| 1 | หน้าเว็บพื้นฐาน | C1 FAIL — ยังไม่มี Cancel Booking |
| 2 | เพิ่ม Cancel | C3 FAIL — Navigation ไม่ชัด |
| 3 | ปรับ Navigation | ผ่านทุกเกณฑ์ → Final Prototype |

**จุดสังเกตให้นักศึกษาตอบ:** เทียบกับสั่ง "ช่วยทำให้ดีขึ้น" เฉย ๆ เกณฑ์ที่ตรวจได้ทำให้แต่ละรอบแก้ตรงจุดขึ้นอย่างไร · รอบ 2 แตะส่วนที่ผ่านแล้วหรือไม่

### บทที่ 2 — Graph Engineering

**คำเปรียบ:** ทำข้าวแกง หุงข้าวกับทำแกงพร้อมกันได้ (fan-out) จัดจานต้องรอทั้งสองเสร็จ (fan-in) แกงไหม้ ข้าวที่หุงแล้วยังใช้ได้

**ลำดับสอน** (เพิ่มความซับซ้อนทีละขั้น): `Sequential → Fan-out/Fan-in → Conditional → Graph with Loop` — วาดรูป Excalidraw แยก 4 รูป

**Diagram**

```text
                 ┌→ Analyze Requirement ─┐          ┌→ Agent A ─┐
Requirement ─────┤                       ├→ Merge   Input ──┼→ Agent B ─┼→ Evaluator → Output
                 └→ Design UI ───────────┘          └→ Agent C ─┘
```

**Theory ที่ต้องอธิบาย:** โครงสร้าง (Node, Edge, Dependency, State) · รูปแบบ Graph (Sequential, Fan-out/in, Static, Conditional, DAG, Graph with Loop) · schema/data contract ระหว่าง Node · เกณฑ์รับงาน/รวมงาน และ Conflict Resolution · Failure Handling · Self-consistency ที่ **ไม่ใช่แค่ Majority Vote** แต่ตรวจจากหลักฐาน

**ตัวอย่างผลที่คาดหวัง (โจทย์ 2)**

| Node | Status | Notes |
| --- | --- | --- |
| N1 | DONE | พบ FR 8 ข้อ BR 5 ข้อ + ขัดแย้ง 5,000/10,000 → เปิด N1b |
| N1b | DONE | Open Issue: เกณฑ์อนุมัติ 2 ระดับไม่ตรงกัน |
| N2, N3, N4 | DONE | ทำคู่ขนาน ไม่เห็นผลกัน |
| N5 | DONE | พบ Entity "Receipt" ใน Sequence แต่ไม่มีใน ERD → แก้โดยอ้างประโยค "ต้องตรวจใบเสร็จซ้ำ" |

**จุดสังเกตให้นักศึกษาตอบ:** ถ้าให้ N2–N4 เห็นผลของกัน จะเกิดอะไร · ลองเพิ่ม/ลด Node หรือเปลี่ยน Dependency แล้วจุดที่พบความขัดแย้งเปลี่ยนอย่างไร

### บทที่ 3 — Dynamic Workflow

**คำเปรียบ:** วางแผนเที่ยว วัด → ตลาดน้ำ → คาเฟ่ ฝนตกก็เปลี่ยนตลาดน้ำเป็นพิพิธภัณฑ์ วัดที่ไปแล้วไม่ต้องไปใหม่ โรงแรมที่จองไว้ยังใช้ได้

**Diagram**

```text
Planner → Create Plan → Executor → Evaluator → Need Re-plan? ─No→ Result
   ↑                                                └Yes────────┘
```

```text
Plan v1: A → B → C          Plan v2 (Evaluator พบว่าต้องแยก B): A → {B1, B2, B3} → C
```

**Theory ที่ต้องอธิบาย:** ต่างจาก Static Graph ตรงที่ Planner ปรับ Workflow ระหว่างทำได้ (เพิ่ม/ลด/แยก/รวม/ยกเลิก Task, เปลี่ยนลำดับ, เปลี่ยน Dependency) · Re-planning + Reason for Change · Dependency Management + Impact Analysis · Reuse Existing Result · Plan Versioning · Constraints ที่ Planner ต้องเคารพ

**ตัวอย่างผลที่คาดหวัง (โจทย์ 3)**

| Version | Reason | Changes | Reuse |
| --- | --- | --- | --- |
| v1 | — | As-Is → Findings → To-Be → Mapping → Gap | — |
| v2 | Findings พบข้อมูลสกปรก 6 ประเภท | ADD "Patient Identity Resolution", SPLIT Mapping เป็น Normalize + Map | As-Is, Findings คงเดิม |
| v3 | Change Request (PDPA + LINE OA) | ADD Consent entity, ADD LINE OA booking flow; To-Be แก้บางส่วน | Findings, Identity Resolution, Migration Plan คงเดิม |

**จุดสังเกตให้นักศึกษาตอบ:** เทียบ v1 กับ v2/v3 ว่า AI reuse งานเดิมจริงหรือรื้อใหม่ · เหตุผลอ้างสิ่งที่พบจริงหรือไม่ · ถ้าใช้ Graph กับโจทย์นี้ จะติดตรงไหน

### บทที่ 4 — เปรียบเทียบและสรุป

สไลด์แสดงตาราง **3 โจทย์ × 3 Workflow** พร้อมผลจริงฝังเคียงกัน (ตามหัวข้อ 4) และสรุปว่าแต่ละ Workflow เหมาะ/ไม่เหมาะกับสถานการณ์ใด

| | Loop | Graph | Dynamic |
| --- | --- | --- | --- |
| เหมาะเมื่อ | งานชิ้นเดียว เกณฑ์ชัด ปรับปรุงซ้ำได้ | งานหลายส่วน แยกทำได้ ต้องสอดคล้องกัน | ขอบเขตไม่นิ่ง มีข้อมูลใหม่กลางทาง |
| จุดอ่อน | ไม่เห็นภาพรวม แก้ทีละจุด | ต้องรู้โครงสร้างงานล่วงหน้า | ซับซ้อน ควบคุมยาก ต้องจำกัด Re-plan |
| ร่องรอยที่ได้ | Iteration Log | Execution Trace | Plan Version Log |

---

## 7. การออกแบบ Prompt Template

สอน **วิธีคิด** — นักศึกษาต้องออกแบบเองได้ ไม่ใช่แค่ copy

### 7.1 Anatomy 8 ส่วน

| ส่วน | คำถามตอนออกแบบ | ตัวอย่าง |
| --- | --- | --- |
| Role | AI สวมบทบาทอะไร กี่บทบาท | "ผู้เขียน" กับ "ผู้ตรวจ" แยกกัน |
| Goal | งานเสร็จหน้าตาเป็นอย่างไร | "ได้หน้าเว็บที่กดจองห้องได้" |
| Input | ข้อมูลอะไรที่เสียบเข้ามา | `{{REQUIREMENT}}` |
| Workflow | ทำอะไรก่อนหลัง อะไรทำพร้อมกัน | Generate → Evaluate → Improve |
| Constraints | ห้ามทำอะไร | "ห้ามแต่งตัวเลขที่โจทย์ไม่ได้ให้" |
| Evaluation Criteria | ตรวจอย่างไรให้ตอบได้ว่าผ่าน/ไม่ผ่าน | "มีปุ่มยกเลิกหรือไม่" แทน "UI ดีไหม" |
| Output Format | ส่งผลรูปแบบไหน | iteration log + ผลสุดท้าย |
| Stop Condition | เมื่อไรต้องหยุด | "ผ่านครบ หรือครบ 3 รอบ" |

> **เกณฑ์ที่ตอบได้แค่ "ผ่าน/ไม่ผ่าน" คือเกณฑ์ที่ดี** — เกณฑ์อย่าง "ดี", "สวย", "ครบถ้วน" ทำให้ AI ให้ตัวเองผ่านเสมอ

### 7.2 อะไรเปลี่ยนเมื่อเปลี่ยน Workflow

| ส่วน | Loop | Graph | Dynamic |
| --- | --- | --- | --- |
| Role | Generator + Critic | ผู้ทำแต่ละ Node + Merger | Planner + Executor + Evaluator |
| Workflow | วงจรซ้ำ | ตาราง Node + Dependency | แผนที่แก้ไขได้ (มี version) |
| ต้องกำหนดเพิ่ม | เกณฑ์ผ่าน, จำนวนรอบ | data contract, กติกา Merge | เงื่อนไข Re-plan, กติกาเปลี่ยนแผน |
| Output | Iteration Log | Execution Trace | Plan Version Log |

**ข้อตกลง:** บรรทัดขึ้นต้นด้วย `//` คือคำอธิบายไทยสำหรับผู้เรียน Template สั่ง AI ให้ข้าม จึง copy ทั้งก้อนได้

### 7.3 Loop Template

**จุดออกแบบ:** (1) แยกผู้สร้างกับผู้ตรวจ — ให้ AI ดูงานตัวเองมักตอบว่าดี (2) เกณฑ์ตรวจได้ทีละข้อ (3) รอบถัดไปแก้เฉพาะข้อที่ไม่ผ่าน (4) มีทางออกเมื่อวนแล้วไม่ดีขึ้น

```text
Lines starting with "//" are notes for human learners. Ignore them.

# ROLE
You play two separate roles:
- GENERATOR: creates or improves the solution.
- CRITIC: checks the solution strictly against the criteria. The critic must not be lenient.

# GOAL
Produce a solution that satisfies every criterion below.

# INPUT
{{REQUIREMENT}}

# CRITERIA (each must be answerable with PASS or FAIL)
C1. Every feature listed in the requirement is present.
C2. {{CRITERION_2}}
C3. {{CRITERION_3}}
// ตัวอย่าง "คำโปรยสินค้า": C1 มีชื่อสินค้า  C2 มีราคา  C3 ไม่เกิน 30 คำ — ทุกข้อตอบผ่าน/ไม่ผ่านได้

# WORKFLOW
Repeat the following cycle:
1. GENERATOR: produce the solution (iteration 1) or fix ONLY the failed criteria (later iterations).
2. CRITIC: mark each criterion PASS or FAIL, with one line of evidence for each.
3. If every criterion is PASS, stop.
4. Otherwise, list the failed criteria and start the next iteration.
// รอบ 1: "หูฟังเสียงใส ใส่สบาย" → C2 ไม่ผ่าน (ไม่มีราคา)  รอบ 2: เติม "ราคา 990 บาท" → ผ่านครบ

# CONSTRAINTS
- Do not change parts that already passed.
- Do not invent information that is not in the input. Mark it as an assumption instead.

# STOP CONDITION
Stop when:
- all criteria PASS, or
- 3 iterations are completed, or
- the same criterion fails 2 times in a row with no improvement (report it as blocked).

# OUTPUT FORMAT
1. Iteration log table: | Iteration | What changed | C1 | C2 | C3 |
2. Final solution
3. Remaining issues or assumptions (if any)
```

### 7.4 Graph Template

**จุดออกแบบ:** (1) เขียน Node เป็นตารางพร้อม Dependency (2) กำหนด data contract ระหว่าง Node (3) Node คู่ขนานต้องไม่เห็นผลของกัน (4) กติกา Merge ตัดสินด้วยหลักฐาน ไม่ใช่เสียงข้างมาก

```text
Lines starting with "//" are notes for human learners. Ignore them.

# ROLE
You are a graph executor. You run each node as an independent worker,
then act as the MERGER that combines node outputs.

# GOAL
Produce the final deliverable by executing the task graph below.

# INPUT
{{REQUIREMENT}}

# TASK GRAPH
| Node | Task                          | Depends on | Output          |
|------|-------------------------------|------------|-----------------|
| N1   | Extract requirements (FR/BR)  | -          | requirement list|
| N2   | Draw use case diagram         | N1         | Mermaid diagram |
| N3   | Draw ERD                      | N1         | Mermaid diagram |
| N4   | Draw sequence diagram         | N1         | Mermaid diagram |
| N5   | Consistency check + merge     | N2, N3, N4 | final document  |
// N1 ก่อน → N2–N4 พร้อมกัน (fan-out) → N5 รวม (fan-in) — เทียบข้าวแกง: เตรียมวัตถุดิบ / หุงข้าว-ทำแกง-ทำไข่ / จัดจาน

# EXECUTION RULES
1. Run a node only after all nodes it depends on are DONE.
2. Nodes at the same level (N2, N3, N4) must work independently.
   Do not let one see another's output.
3. Every node returns this data contract:
   { "node": "N2", "status": "DONE | FAILED", "output": "...", "assumptions": [] }

# CONDITIONAL EDGE (optional)
If N1 finds conflicting requirements, run node N1b "List open issues" before N5.
// เช่น เจอ 5,000 กับ 10,000 ขัดกัน ให้แตกไป N1b ก่อน

# MERGE RULES (N5)
- Accept a node output only if its status is DONE and it follows the data contract.
- If node outputs disagree (e.g., an entity exists in the sequence diagram but not in the ERD),
  resolve using evidence from the INPUT. Quote the source sentence.
- If the evidence cannot settle it, do not choose. List it as an unresolved conflict.

# FAILURE HANDLING
- If a node fails, retry it once.
- If it fails again, mark it FAILED, continue with nodes that do not depend on it,
  and report what is missing.

# CONSTRAINTS
- Do not invent numbers or rules that are not in the input.

# STOP CONDITION
Stop when N5 is DONE, or when no remaining node can run.

# OUTPUT FORMAT
1. Execution trace: | Node | Status | Notes |
2. Final merged deliverable
3. Conflicts found and how each was resolved (with evidence)
```

### 7.5 Dynamic Workflow Template

**จุดออกแบบ:** (1) แผนต้องเป็นข้อมูลที่มี version (2) ระบุชัดว่าเหตุการณ์ใดทำให้ Re-plan (3) ทุกครั้งที่เปลี่ยนต้องบอกเหตุผล ผลกระทบ และสิ่งที่ reuse (4) จำกัดจำนวนครั้ง Re-plan

```text
Lines starting with "//" are notes for human learners. Ignore them.

# ROLE
You play three separate roles:
- PLANNER: creates and revises the plan.
- EXECUTOR: carries out one task at a time and reports results.
- EVALUATOR: checks results and decides whether the plan still fits.

# GOAL
Deliver the result described in the input, adapting the plan when new facts appear.

# INPUT
{{REQUIREMENT}}

# NEW INFORMATION
{{CHANGE_REQUEST_OR_NONE}}
// รอบแรกใส่ NONE พอได้ Plan v1 แล้วค่อยส่ง prompt ต่อพร้อม change request (เช่น PDPA + LINE OA ของโจทย์ 3)

# PLAN FORMAT
Plan vN
| Task | Description | Depends on | Status (TODO / DONE / DROPPED) |
// Plan v1 เที่ยว: T1 วัด (-) → T2 ตลาดน้ำ (T1) → T3 คาเฟ่ (T2)

# WORKFLOW
1. PLANNER writes Plan v1.
2. EXECUTOR runs the next TODO task whose dependencies are DONE.
3. EVALUATOR checks the result and answers: "Does the plan still fit?"
4. If yes, go back to step 2.
5. If no, PLANNER creates the next plan version (see RE-PLAN RULES), then go back to step 2.

# RE-PLAN TRIGGERS
Re-plan only when:
- a result reveals work the plan did not include (e.g., dirty data that needs cleaning), or
- a task cannot be done as planned, or
- NEW INFORMATION changes the requirement.

# RE-PLAN RULES
For every new version, write:
- Reason for change: which trigger happened
- Changes: add / drop / split / merge / reorder tasks, or change dependencies
- Impact analysis: which tasks and results are affected
- Reuse: which DONE results stay valid and are kept
// Plan v2 เที่ยว: Reason ฝนตก · Changes DROP T2, ADD T2b พิพิธภัณฑ์ (T1), T3 ขึ้นกับ T2b · Impact T3 เลื่อนเวลา · Reuse T1 เก็บไว้

# CONSTRAINTS
- Never redo a DONE task unless the impact analysis says it is affected.
- Never silently drop a requirement. A dropped task must state why.
- Maximum 3 re-plans. After that, report what remains undecided.

# STOP CONDITION
Stop when every task is DONE or DROPPED and the EVALUATOR confirms the goal is met,
or when the re-plan limit is reached.

# OUTPUT FORMAT
1. Plan version log: v1, v2, ... each with reason, changes, impact, reuse
2. Execution log: | Step | Task | Result | Evaluator decision |
3. Final deliverable
```