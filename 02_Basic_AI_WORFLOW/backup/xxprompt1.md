# ออกสื่อการสอนและบทเรียน: Loop Engineering, Graph Engineering และ Dynamic Workflow

## 0.รูปแบบสื่อการสอน
   * `README.md` - xxxxx
   * `AI_Workflow_Engineering_SA.html` — สไลด์สื่อการสอนภาษาไทย

## 1. แนวคิดหลัก

- Problem-Based + Prompt-Based Learning บนแกนเดียว:
  โจทย์เดียวกัน → เปลี่ยนวิธีออกแบบ Workflow → สังเกตผลลัพธ์ที่เปลี่ยนไป ใช้โจทย์กลาง 3 โจทย์ รันผ่าน Loop → Graph → Dynamic ตามลำดับ เพื่อให้เห็นความต่างทั้งวิธีคิด วิธี
  ออกแบบ และผลลัพธ์
- ให้ใช้ Excalidraw MCP** วาดรูปประกอบทั้งหมด ในสื่อการสอนเพื่อเพิ่มความเข้าใจ  

## 2. เป้าหมายการเรียนรู้

จบบทเรียนแล้วนักศึกษาสามารถ
1. อธิบายและออกแบบ Loop Workflow
2. อธิบาย Node, Edge, State, Dependency
3. ออกแบบ Sequential, Fan-out/Fan-in และ Conditional Graph
4. แยก Static Graph กับ Dynamic Workflow
5. ออกแบบโครงสร้าง Planner–Executor–Evaluator
6. เขียน Prompt ควบคุมแต่ละ Workflow และทดลองกับ ChatGPT / Codex / Claude Code / AI Agent อื่น
7. เปรียบเทียบผลจากโจทย์เดียวกัน และบอกได้ว่าแต่ละ Workflow เหมาะกับสถานการณ์ใด

## 3. โจทย์กลาง

ทุกโจทย์ให้ AI **วิเคราะห์ Requirement → สร้างโครงสร้างระบบ → สร้างผลลัพธ์ที่ตรวจสอบและเปรียบเทียบได้** และต้องรันครบทั้ง 3 Workflow

| โจทย์ | แนวงาน | ความยากที่ฝังไว้ | Workflow ที่เห็นจุดเด่นชัด |
| --- | --- | --- | --- |
| 1. จองห้องประชุม | Requirement → UI Prototype | feature ตกหล่น, UX ไม่ชัด | Loop |
| 2. เบิกค่าใช้จ่าย | สัมภาษณ์ → System Model | ข้อขัดแย้ง, หลาย artifact ต้องสอดคล้อง | Graph |
| 3. ย้ายระบบนัดหมาย | As-Is → To-Be + Migration | ข้อมูลสกปรก, ขอบเขตไม่แน่นอน, Change Request | Dynamic |

### โจทย์ที่ 1 — ระบบจองห้องประชุม

```text
สร้างเว็บไซต์สำหรับระบบจองห้องประชุม
ระบบต้องสามารถ: แสดงห้องประชุม, ดูเวลาว่าง, จองห้อง, ยกเลิกการจอง, แสดงสถานะการจอง
Output: Web UI Mock-up ที่เปิดและทดลองใช้งานได้
```

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

เหมาะกับ **Graph**: fan-out สร้าง Use Case / ERD / Sequence คู่ขนาน แล้ว fan-in ตรวจความสอดคล้อง ได้ฝึก Conflict Resolution และ Self-consistency ที่อิงหลักฐาน

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

**ปัญหาที่ซ่อนไว้ (ไม่บอกนักศึกษา):** รูปแบบวันที่ปน (dd/mm, ISO, พ.ศ. ย่อ), จองซ้ำ, คนไข้เดียวกันแต่ชื่อ/เบอร์เขียนต่างกันข้ามสาขา (ไม่มี Patient ID), หมอบีถูกจองชนเวลา, หมอคนเดียวหลายสาขา, เบอร์โทรขาด, แถว `09/03/2026` กำกวม (หมายเหตุ "วันพุธ" คือหลักฐานว่าเป็น 9 ก.ย. 2026 เพราะ 9 มี.ค. 2026 เป็นวันจันทร์)

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

เหมาะกับ **Dynamic**: ขอบเขตงานรู้ได้หลังตรวจข้อมูล และมี Change Request กลางทาง — Static Graph คาดงาน cleaning ล่วงหน้าไม่ได้ ส่วน Loop วนแก้ทีละจุดโดยไม่วางแผนใหม่

## 4. โครงสร้างการสอนในแต่ละหัวข้อ (5 ขั้น)

1. **Theory** — แนวคิด องค์ประกอบ วิธีทำงาน เหมาะกับปัญหาแบบใด ข้อดี/ข้อจำกัด
2. **Workflow Diagram** — ภาพการทำงาน (หัวข้อ 5)
3. **Prompt Template** — copy & paste ใช้ได้ทันที ครบ 8 ส่วน (หัวข้อ 6)
4. **ทดลองกับโจทย์จริง** — ใส่โจทย์ใน `{{REQUIREMENT}}` แล้วรัน Experiment 1 Loop → 2 Graph → 3 Dynamic
5. **ดูผลลัพธ์** — แสดงร่องรอยของกระบวนการ ไม่ใช่เฉพาะผลสุดท้าย

## 5. เนื้อหาเฉพาะแต่ละหัวข้อ

### 5.1 Loop Engineering

```text
Requirement → Generate → Evaluate → ผ่าน? ─ใช่→ Result
                 ↑                     └ไม่→ Improve ─┘
```

ตัวอย่างผลที่คาดหวัง (โจทย์ 1): Iteration 1 หน้าเว็บพื้นฐาน → ยังไม่มี Cancel Booking · Iteration 2 เพิ่ม Cancel → Navigation ไม่ชัด · Iteration 3 ปรับ Navigation → ผ่านทุกเกณฑ์ → Final Prototype

จุดสังเกต: วงจร `Generate → Evaluate → Improve → Generate` — Template ดูหัวข้อ 6.3

### 5.2 Graph Engineering

ลำดับสอน (เพิ่มความซับซ้อนทีละขั้น): `Sequential → Fan-out/Fan-in → Conditional → Graph with Loop`

```text
                 ┌→ Analyze Requirement ─┐          ┌→ Agent A ─┐
Requirement ─────┤                       ├→ Merge   Input ──┼→ Agent B ─┼→ Evaluator → Output
                 └→ Design UI ───────────┘          └→ Agent C ─┘
```

แนวคิดที่ต้องอธิบาย: โครงสร้าง (Node, Edge, Dependency, State) · รูปแบบ Graph (Sequential, Fan-out/in, Static, Conditional, DAG, Graph with Loop) · schema ระหว่าง Node · เกณฑ์รับงาน/รวมงาน และ Conflict Resolution · Failure Handling · Self-consistency ที่ **ไม่ใช่แค่ Majority Vote** แต่ตรวจจากหลักฐาน — Template ดูหัวข้อ 6.4

### 5.3 Dynamic Workflow

```text
Planner → Create Plan → Executor → Evaluator → Need Re-plan? ─No→ Result
   ↑                                                └Yes────────┘
```

ต่างจาก Static Graph ตรงที่ Planner ปรับ Workflow ระหว่างทำได้: เพิ่ม/ลด/แยก/รวม/ยกเลิก Task, เปลี่ยนลำดับ, เปลี่ยน Dependency

```text
Plan v1: A → B → C          Plan v2 (Evaluator พบว่าต้องแยก B): A → {B1, B2, B3} → C
```

แนวคิดที่ต้องอธิบาย: Re-planning + Reason for Change · Dependency Management + Impact Analysis · Reuse Existing Result · Plan Versioning · Constraints ที่ Planner ต้องเคารพ — Template ดูหัวข้อ 6.5

## 6. การออกแบบ Prompt Template

สอน **วิธีคิด** — นักศึกษาต้องออกแบบเองได้ ไม่ใช่แค่ copy

### 6.1 Anatomy 8 ส่วน

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

### 6.2 อะไรเปลี่ยนเมื่อเปลี่ยน Workflow

| ส่วน | Loop | Graph | Dynamic |
| --- | --- | --- | --- |
| Role | Generator + Critic | ผู้ทำแต่ละ Node + Merger | Planner + Executor + Evaluator |
| Workflow | วงจรซ้ำ | ตาราง Node + Dependency | แผนที่แก้ไขได้ (มี version) |
| ต้องกำหนดเพิ่ม | เกณฑ์ผ่าน, จำนวนรอบ | data contract, กติกา Merge | เงื่อนไข Re-plan, กติกาเปลี่ยนแผน |
| Output | Iteration Log | Execution Trace | Plan Version Log |

**ข้อตกลง:** บรรทัดขึ้นต้นด้วย `//` คือคำอธิบายไทยสำหรับผู้เรียน Template สั่ง AI ให้ข้าม จึง copy ทั้งก้อนได้

### 6.3 Loop Template

**เปรียบ:** นักเรียนส่งการบ้าน ครูตรวจตามเกณฑ์ ไม่ผ่านก็แก้เฉพาะจุดแล้วส่งใหม่ ไม่เกิน 3 ครั้ง

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

จุดสังเกต: เทียบกับสั่ง "ช่วยทำให้ดีขึ้น" เฉย ๆ — เกณฑ์ที่ตรวจได้ทำให้แต่ละรอบแก้ตรงจุดขึ้นอย่างไร

### 6.4 Graph Template

**เปรียบ:** ทำข้าวแกง หุงข้าวกับทำแกงพร้อมกันได้ (fan-out) จัดจานต้องรอทั้งสองเสร็จ (fan-in) แกงไหม้ ข้าวที่หุงแล้วยังใช้ได้

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

จุดสังเกต: ลองเพิ่ม/ลด Node หรือเปลี่ยน Dependency แล้วดูว่าผลและจุดที่พบความขัดแย้งเปลี่ยนอย่างไร

### 6.5 Dynamic Workflow Template

**เปรียบ:** วางแผนเที่ยว วัด → ตลาดน้ำ → คาเฟ่ ฝนตกก็เปลี่ยนตลาดน้ำเป็นพิพิธภัณฑ์ วัดที่ไปแล้วไม่ต้องไปใหม่ โรงแรมที่จองไว้ยังใช้ได้

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

จุดสังเกต (โจทย์ 3): เทียบ Plan v1 กับ v2 ว่า AI reuse งานเดิมจริงหรือรื้อใหม่ และเหตุผลอ้างสิ่งที่พบจริงหรือไม่



## 8. การผลิตสื่อและหลักฐานการทดลอง (ข้อกำหนดสำหรับ agent)

เครื่องมือหลัก: **Excalidraw MCP** วาดรูปประกอบทั้งหมด · **Playwright CLI** รันการทดลองผ่านเว็บและ capture หน้าจอ
