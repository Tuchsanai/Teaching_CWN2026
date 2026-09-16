


โจทย์: 

update เนื้อหาด้าน ทฤษฏี AI_Workflow_Engineering_SA.html  อยากให้มีการสอน ทฤษฏี ทั่วไปก่อน ก่อน ที่จะเข้าไปถึง LAB

ยังขาดเนื้อหาเชิง theory อย่างละเอียด แบบทั่วไปของ

| หัวข้อ | เนื้อหาที่ต้องครอบคลุม |
| --- | --- |
| Loop Engineering | สร้าง–ตรวจ–แก้–ตรวจซ้ำ บทบาทผู้สร้าง/ผู้ตรวจ เกณฑ์ประเมิน Retry กับการแก้ตาม Feedback เงื่อนไขหยุด เพดานรอบ/เวลา/งบ การป้องกันวนไม่คืบหน้า และตรวจผลกระทบต่อส่วนที่เคยถูกต้อง |
| Graph Engineering | Node, Edge, Dependency, State, Sequential, Fan-out/Fan-in, Static/Conditional Graph, DAG กับกราฟที่มี Loop, รูปแบบข้อมูลส่งต่อ เกณฑ์รับ/รวมงาน การแก้ข้อขัดแย้งและงานล้มเหลว รวมถึง Self-consistency ที่ตรวจด้วยหลักฐาน ไม่ยึดเสียงส่วนใหญ่เสมอ |
| Dynamic Workflow | Planner–Executor–Evaluator ขอบเขตตัดสินใจ การเพิ่ม/แยก/ยกเลิก/จัดลำดับงานและ Dependency ใหม่ การวิเคราะห์ผลกระทบ ใช้ซ้ำผลงานเดิม และบันทึกแผนแต่ละเวอร์ชันพร้อมเหตุผลและข้อจำกัด |

ตัวอย่าง ให้ดูเป็น idea 

"""
ได้ครับ ด้านล่างเป็น **เนื้อหาทฤษฎีแบบพื้นฐาน** เน้นให้ผู้เรียนเข้าใจ “หลักการทำงาน” ของ Workflow ก่อน โดยไม่ผูกกับกรณีศึกษาทางธุรกิจ และใช้ตัวอย่างเล็ก ๆ ที่ตามได้ง่าย

# พื้นฐาน AI Workflow Engineering

AI Workflow Engineering คือการออกแบบกระบวนการให้ AI หรือระบบหลายส่วนทำงานร่วมกันอย่างเป็นขั้นตอน แทนที่จะใช้ Prompt เพียงครั้งเดียวแล้วจบ

แนวคิดสามารถมองเป็นลำดับพัฒนาการได้ดังนี้

```text
Single Step
    ↓
Loop
    ↓
Graph
    ↓
Dynamic Workflow
```

แต่ละระดับเพิ่มความสามารถในการควบคุม ตรวจสอบ และปรับตัวของระบบ

---

# 1. Loop Engineering

## 1.1 แนวคิดพื้นฐาน

Loop Engineering คือการออกแบบให้ระบบไม่ได้ยอมรับผลลัพธ์ครั้งแรกทันที แต่มีวงจร

```text
สร้าง
  ↓
ตรวจ
  ↓
ผ่าน? ── Yes ──> จบ
  │
  No
  ↓
แก้ไข
  ↓
ตรวจอีกครั้ง
```

แนวคิดสำคัญคือ

```text
Generate → Evaluate → Improve → Evaluate → ...
```

จุดประสงค์ของ Loop ไม่ใช่ทำงานเดิมซ้ำ ๆ แต่คือ

> ให้ผลลัพธ์ในแต่ละรอบดีขึ้นจากข้อมูลที่ได้จากรอบก่อนหน้า

---

## 1.2 บทบาท Creator และ Evaluator

Loop มักแบ่งบทบาทออกเป็นอย่างน้อย 2 ส่วน

### Creator

มีหน้าที่สร้างหรือแก้ไขผลลัพธ์

```text
Input
 ↓
Creator
 ↓
Output
```

### Evaluator

มีหน้าที่ตรวจผลลัพธ์ตามเกณฑ์ที่กำหนดไว้

```text
Output
 ↓
Evaluator
 ↓
Pass / Fail + Feedback
```

จากนั้น Feedback จะถูกส่งกลับไปยัง Creator

```text
Creator
   ↓
Output
   ↓
Evaluator
   ↓
Feedback
   ↓
Creator
```

Creator และ Evaluator อาจเป็นโมเดลเดียวกัน หรือคนละ Agent / Model ก็ได้

---

# 1.3 Evaluation Criteria

Evaluator ต้องมีเกณฑ์ในการตัดสิน

ตัวอย่างเช่น ถ้าให้ระบบสร้างข้อความสรุป อาจกำหนดว่า

```text
1. ความถูกต้อง
2. ความครบถ้วน
3. ความชัดเจน
4. ไม่ขัดแย้งกับข้อมูลต้นฉบับ
```

สามารถกำหนดเป็นคะแนนได้ เช่น

```text
Accuracy      ≥ 8/10
Completeness  ≥ 8/10
Clarity       ≥ 7/10
```

ระบบจบ Loop เมื่อผ่านเกณฑ์ทั้งหมด

---

# 1.4 Retry กับ Feedback-based Revision

สองแนวคิดนี้แตกต่างกัน

### Retry

คือการลองใหม่โดยไม่ได้ใช้ข้อมูลจากความผิดพลาดครั้งก่อน

```text
Attempt 1
   ↓ Fail
Attempt 2
   ↓ Fail
Attempt 3
```

ตัวอย่าง

```text
สร้างคำตอบใหม่อีกครั้ง
```

### Feedback-based Revision

คือการนำข้อผิดพลาดจากรอบก่อนมาใช้ในการแก้ไข

```text
Attempt 1
 ↓
Evaluation
 ↓
"ขาดหัวข้อ B"
 ↓
Revision
 ↓
Attempt 2
```

ดังนั้นโดยทั่วไป

```text
Retry
```

ให้ข้อมูลน้อยกว่า

```text
Evaluate → Feedback → Revise
```

---

# 1.5 Stop Condition

Loop ต้องมีเงื่อนไขหยุดเสมอ

เงื่อนไขพื้นฐานคือ

```text
ผ่านเกณฑ์
```

แต่ระบบจริงควรมีเงื่อนไขอื่นร่วมด้วย เช่น

```text
ผ่านเกณฑ์
OR
ครบจำนวนรอบสูงสุด
OR
เกินเวลาที่กำหนด
OR
เกินงบประมาณ
```

เช่น

```text
max_iterations = 5
```

หมายความว่าถึงแม้ผลลัพธ์ยังไม่สมบูรณ์ ระบบก็จะไม่ทำงานเกิน 5 รอบ

---

# 1.6 Budget ของ Loop

คำว่า Budget ไม่ได้หมายถึงเงินเท่านั้น แต่รวมถึงทรัพยากรต่าง ๆ เช่น

```text
Iteration Budget
Token Budget
Time Budget
Cost Budget
```

ตัวอย่าง

```text
Maximum iterations = 5
Maximum tokens      = 20,000
Maximum time        = 60 seconds
```

เป้าหมายคือป้องกันระบบพยายามแก้ปัญหาอย่างไม่สิ้นสุด

---

# 1.7 ปัญหา Loop ไม่คืบหน้า

บางครั้งระบบอาจวนแบบนี้

```text
Version 1
 ↓
Version 2
 ↓
Version 3
 ↓
Version 4
```

แต่คุณภาพแทบไม่เปลี่ยน

เรียกว่า

```text
Non-progress Loop
```

จึงควรตรวจว่าแต่ละรอบมี Improvement หรือไม่

ตัวอย่าง

```text
Score

Round 1 = 6.1
Round 2 = 6.2
Round 3 = 6.2
Round 4 = 6.2
```

อาจกำหนดเงื่อนไขว่า

```text
ถ้าไม่ดีขึ้น 2–3 รอบ
→ หยุด
```

หรือเปลี่ยนวิธีแก้ปัญหา

---

# 1.8 Regression

อีกปัญหาหนึ่งคือ

> แก้ส่วนที่ผิด แต่ทำส่วนที่เคยถูกต้องให้เสีย

ตัวอย่าง

Version 1

```text
A ✓
B ✗
C ✓
```

หลังแก้ B

```text
A ✗
B ✓
C ✓
```

ดังนั้น Evaluator ไม่ควรตรวจเฉพาะสิ่งที่เพิ่งแก้ แต่ต้องตรวจ

```text
New Requirement
+
Previously Correct Requirements
```

หลักการนี้เรียกว่า Regression Checking

---

# 1.9 สรุป Loop Engineering

แนวคิดหลักคือ

```text
Create
  ↓
Evaluate
  ↓
Feedback
  ↓
Revise
  ↓
Evaluate
```

พร้อมควบคุม

```text
Quality
Iterations
Time
Cost
Progress
Regression
```

Loop เหมาะกับปัญหาที่คำตอบสามารถค่อย ๆ ปรับปรุงได้

---

# 2. Graph Engineering

เมื่อ Workflow ซับซ้อนขึ้น การมี Loop เพียงเส้นเดียวอาจไม่เพียงพอ

Graph Engineering มอง Workflow เป็น

```text
Node + Edge + State + Dependency
```

---

# 2.1 Node

Node คือหน่วยงานหนึ่งใน Workflow

อาจเป็น

```text
Task
Agent
Tool
Model
Function
Evaluator
```

ตัวอย่าง

```text
[Read]
[Analyze]
[Check]
[Summarize]
```

---

# 2.2 Edge

Edge คือความสัมพันธ์หรือเส้นทางการทำงานระหว่าง Node

```text
[A] → [B]
```

หมายถึง

```text
เมื่อ A ทำงานเสร็จ
จึงไป B
```

Edge อาจส่งข้อมูลไปพร้อมกันด้วย

```text
A
 │ result
 ↓
B
```

---

# 2.3 Dependency

Dependency ระบุว่า Task หนึ่งต้องรออะไร

ตัวอย่าง

```text
A ──┐
    ├──> C
B ──┘
```

C ต้องรอทั้ง

```text
A และ B
```

ดังนั้น Dependency ของ C คือ

```text
C depends on A, B
```

---

# 2.4 State

State คือข้อมูลที่ Workflow เก็บไว้ระหว่างการทำงาน

ตัวอย่าง

```text
state = {
    input,
    intermediate_result,
    score,
    feedback,
    status
}
```

แต่ละ Node สามารถ

```text
Read State
Modify State
Create New State
```

ได้

Graph จึงไม่ได้เป็นเพียงเส้นเชื่อม Task แต่เป็น

```text
Graph + Shared/Transferred State
```

---

# 2.5 Sequential Graph

รูปแบบง่ายที่สุด

```text
A → B → C → D
```

ทุกงานทำตามลำดับ

ตัวอย่างง่าย ๆ

```text
รับข้อความ
   ↓
แยกประโยค
   ↓
ตรวจภาษา
   ↓
สรุป
```

ข้อดีคือเข้าใจง่าย แต่ทำงานคู่ขนานไม่ได้

---

# 2.6 Fan-out

Fan-out คือการแตกงานหนึ่งออกเป็นหลายงาน

```text
       ┌→ B
A ─────┼→ C
       └→ D
```

B, C และ D สามารถทำงานพร้อมกันได้หากไม่มี Dependency ต่อกัน

เช่น

```text
Document
   ↓
 ┌───────────────┐
 ↓       ↓       ↓
Check A Check B Check C
```

ข้อดีคือเพิ่ม Parallelism

---

# 2.7 Fan-in

Fan-in คือการรวมผลจากหลาย Node

```text
B ──┐
C ──┼──> E
D ──┘
```

E ทำหน้าที่ Aggregator

เช่น

```text
Analysis A
Analysis B
Analysis C
    ↓
Combine
```

---

# 2.8 Fan-out + Fan-in

รูปแบบที่พบบ่อยคือ

```text
        ┌→ B ─┐
A ──────┼→ C ─┼→ E
        └→ D ─┘
```

หรือ

```text
Split
 ↓
Parallel Work
 ↓
Merge
```

---

# 2.9 Static Graph

Static Graph คือโครงสร้างของ Workflow ถูกกำหนดก่อนเริ่มทำงาน

```text
A → B → C → D
```

หรือ

```text
     ┌→ B ─┐
A ───┤     ├→ D
     └→ C ─┘
```

ไม่ว่าข้อมูลเข้าเป็นอย่างไร โครงสร้างหลักยังเหมือนเดิม

---

# 2.10 Conditional Graph

Conditional Graph สามารถเลือกเส้นทางตาม State

```text
          ┌→ B
A → Check ┤
          └→ C
```

เช่น

```text
if score >= 8:
    → Accept
else:
    → Revise
```

Graph จึงสามารถมี Branch ได้

```text
         Pass → Finish
        /
Check
        \
         Fail → Revise
```

---

# 2.11 DAG

DAG ย่อมาจาก

```text
Directed Acyclic Graph
```

คือ Graph ที่มีทิศทางและไม่มีวงจรย้อนกลับ

ตัวอย่าง

```text
A → B → D
 \→ C ↗
```

แต่ไม่สามารถมี

```text
A → B → C
↑       ↓
└───────┘
```

เพราะเกิด Cycle

DAG เหมาะกับงานที่ Dependency ชัดเจนและแต่ละ Task ควรจบเพียงครั้งเดียว

---

# 2.12 Graph ที่มี Loop

บาง Workflow ต้องสามารถย้อนกลับได้

```text
Generate
   ↓
Check
   ↓
 Fail
   ↓
Revise
   │
   └────→ Check
```

Graph แบบนี้ไม่ใช่ DAG เพราะมี Cycle

สามารถมองได้ว่า

```text
Graph Engineering
+
Loop Engineering
```

ทำงานร่วมกัน

---

# 2.13 รูปแบบข้อมูลระหว่าง Node

Node ต้องตกลงรูปแบบข้อมูลที่ส่งต่อกัน

เช่น Node A ส่ง

```text
{
  "answer": "...",
  "confidence": 0.85
}
```

Node B จึงต้องรู้ว่า Input Format คืออะไร

แนวคิดนี้คล้าย Contract

```text
Node A Output Contract
        ↓
Node B Input Contract
```

หาก Contract ไม่ชัด Graph จะเปราะบางมาก

---

# 2.14 Acceptance Criteria

ก่อนรวมงานควรกำหนดว่า Output ของแต่ละ Node ต้องผ่านอะไร

เช่น

```text
Node B

status = success
score >= 0.8
required_fields != null
```

จากนั้นจึงอนุญาตให้ส่งต่อไปยัง Node ถัดไป

---

# 2.15 Merge Conflict

เมื่อหลาย Node ให้ผลต่างกัน อาจเกิด Conflict

ตัวอย่าง

```text
Agent A → X
Agent B → Y
Agent C → X
```

วิธีง่ายที่สุดคือ Majority Vote

```text
X ชนะ 2 ต่อ 1
```

แต่ Majority ไม่ได้แปลว่าถูกต้องเสมอ

---

# 2.16 Self-consistency แบบมีหลักฐาน

แทนที่จะถามว่า

```text
คำตอบไหนมีคนเลือกมากที่สุด?
```

ควรถามว่า

```text
คำตอบไหนมีเหตุผลหรือหลักฐานสนับสนุนดีที่สุด?
```

ตัวอย่าง

```text
Agent A → X + Evidence A
Agent B → Y + Evidence B
Agent C → X + Evidence C
```

จากนั้น Evaluator ตรวจ

```text
Evidence quality
Logical consistency
Constraint satisfaction
```

จึงอาจเกิดกรณี

```text
A + C เลือก X
B เลือก Y

แต่ Evidence ของ B แข็งแรงกว่า

→ เลือก Y
```

ดังนั้น

> Self-consistency ที่ดีไม่ควรเท่ากับ Majority Voting อย่างเดียว

---

# 2.17 Failure Handling

Graph ต้องกำหนดว่าจะทำอย่างไรเมื่อ Node ล้มเหลว

เช่น

```text
Node B Failed
```

ตัวเลือกอาจเป็น

```text
Retry B
Skip B
Use fallback
Route to another Node
Stop workflow
```

เช่น

```text
A → B → C
    │
    Fail
    ↓
  Retry
```

หรือ

```text
A → B
    │ Fail
    ↓
    D
```

---

# 2.18 สรุป Graph Engineering

Graph Engineering เพิ่มความสามารถจาก Loop ด้วยการรองรับ

```text
Multiple Tasks
Dependencies
Parallelism
Branching
Aggregation
State
Failure Handling
```

องค์ประกอบหลักคือ

```text
Node
Edge
Dependency
State
Condition
Fan-out
Fan-in
```

---

# 3. Dynamic Workflow

Graph ทั่วไปมักออกแบบโครงสร้างไว้ล่วงหน้า

แต่บางปัญหาเราไม่รู้ตั้งแต่ต้นว่า

```text
ต้องมีกี่ Task
ต้องทำ Task อะไร
ต้องทำลำดับใด
```

จึงเกิดแนวคิด Dynamic Workflow

---

# 3.1 Static กับ Dynamic Workflow

Static Workflow

```text
A → B → C → D
```

โครงสร้างถูกกำหนดไว้ก่อน

Dynamic Workflow

```text
Problem
   ↓
Planner
   ↓
สร้าง Workflow ตามสถานการณ์
```

เช่นครั้งหนึ่งอาจสร้าง

```text
A → B → C
```

แต่อีกครั้งอาจเป็น

```text
A
├→ B
├→ C
└→ D
    ↓
    E
```

---

# 3.2 Planner–Executor–Evaluator

โครงสร้างพื้นฐานคือ

```text
Planner
   ↓
Executor
   ↓
Evaluator
```

### Planner

ตัดสินใจว่า

```text
ต้องทำอะไร
ทำลำดับใด
งานไหนขึ้นกับงานไหน
```

### Executor

ทำ Task ตามแผน

### Evaluator

ตรวจว่า

```text
ผลถูกต้องหรือไม่
งานครบหรือไม่
แผนยังเหมาะสมหรือไม่
```

---

# 3.3 Workflow ขั้นพื้นฐาน

```text
Problem
   ↓
Planner
   ↓
Plan
   ↓
Executor
   ↓
Result
   ↓
Evaluator
```

หากผ่าน

```text
Finish
```

หากไม่ผ่าน

```text
Re-plan
```

จึงกลายเป็น

```text
Planner
   ↓
Executor
   ↓
Evaluator
   │
   └──── Re-plan
```

---

# 3.4 ขอบเขตการตัดสินใจของ Planner

Planner ไม่ควรมีอำนาจแบบไร้ขอบเขต

ควรกำหนดว่า Planner สามารถทำอะไรได้บ้าง เช่น

```text
เพิ่ม Task
ลบ Task
แบ่ง Task
รวม Task
เปลี่ยนลำดับ
เพิ่ม Dependency
ลบ Dependency
```

แต่บางอย่างอาจห้าม เช่น

```text
ห้ามเพิ่ม Task เกิน 10 งาน
ห้ามใช้งบเกินกำหนด
ห้ามเปลี่ยน Objective หลัก
```

แนวคิดนี้เรียกว่า Planning Constraints

---

# 3.5 เพิ่ม Task

สมมติแผนเริ่มต้นคือ

```text
A → B → C
```

หลังทำ A พบข้อมูลใหม่

Planner อาจตัดสินใจเพิ่ม X

```text
A → X → B → C
```

นี่คือ Dynamic Expansion

---

# 3.6 Split Task

Task ใหญ่สามารถแบ่งเป็น Task เล็ก

เดิม

```text
A → B → C
```

พบว่า B ซับซ้อนเกินไป

จึงเปลี่ยนเป็น

```text
A
↓
B1
├→ B2
└→ B3
 ↓
B4
↓
C
```

---

# 3.7 Cancel Task

บาง Task อาจไม่จำเป็นอีกต่อไป

เดิม

```text
A → B → C → D
```

หลัง A พบว่า C ไม่จำเป็น

กลายเป็น

```text
A → B → D
```

นี่ช่วยลด Cost และเวลา

---

# 3.8 Reordering

Planner สามารถเปลี่ยนลำดับงาน

เดิม

```text
A → B → C
```

แต่พบว่า C ควรมาก่อน B

```text
A → C → B
```

อย่างไรก็ตามต้องตรวจ Dependency ก่อนเสมอ

---

# 3.9 Dynamic Dependency

เดิม

```text
A
├→ B
└→ C
```

หลังวิเคราะห์พบว่า C ต้องใช้ผลจาก B

ต้องเปลี่ยนเป็น

```text
A → B → C
```

ดังนั้น Dynamic Workflow ไม่ได้เปลี่ยนแค่ Task แต่สามารถเปลี่ยน

```text
Graph Structure
```

ได้ด้วย

---

# 3.10 Impact Analysis

ก่อนเปลี่ยนแผนควรถามว่า

```text
การเปลี่ยนนี้กระทบอะไร?
```

เช่น

เดิม

```text
A → B → C → D
```

ถ้าเปลี่ยน B

อาจต้องพิจารณา

```text
C ใช้ Output ของ B หรือไม่?
D ใช้ผลจาก B ทางอ้อมหรือไม่?
```

สามารถมองเป็น

```text
Changed Node
     ↓
Downstream Dependencies
```

นี่คือ Impact Analysis

---

# 3.11 Reuse Existing Work

Dynamic Workflow ไม่ควรเริ่มใหม่ทุกครั้ง

สมมติ

```text
A ✓
B ✓
C ✗
D ยังไม่ทำ
```

หลัง Re-plan ควรใช้

```text
A และ B เดิม
```

ถ้ายังถูกต้อง

แทนที่จะ

```text
Run A again
Run B again
```

หลักการคือ

> Re-plan เฉพาะส่วนที่จำเป็น

---

# 3.12 Plan Versioning

ทุกครั้งที่เปลี่ยนแผนควรเก็บ Version

เช่น

```text
Plan v1

A → B → C
```

หลังพบปัญหา

```text
Plan v2

A → B1 → B2 → C
```

และควรบันทึก

```text
เหตุผลที่เปลี่ยน
สิ่งที่ค้นพบใหม่
ข้อจำกัด
Task ที่ reuse
Task ที่ยกเลิก
```

ตัวอย่าง

```text
Plan v2

Reason:
B มีขอบเขตกว้างเกินไป

Change:
Split B into B1 and B2

Reuse:
A

Constraint:
Maximum 6 tasks
```

---

# 3.13 Planner ไม่จำเป็นต้องสร้างแผนใหม่ทั้งหมด

Dynamic Workflow ที่ดีมักใช้แนวคิด

```text
Plan → Execute → Observe → Patch Plan
```

มากกว่า

```text
Plan → Fail → Delete Everything → Plan Again
```

เรียกว่า Incremental Re-planning

---

# 3.14 Dynamic Workflow กับ Loop

Dynamic Workflow เองก็คือ Loop ระดับสูง

```text
Plan
 ↓
Execute
 ↓
Evaluate
 ↓
Re-plan
 ↓
Execute
```

จึงสามารถมองความสัมพันธ์ได้ว่า

```text
Loop Engineering
      ↓
ควบคุมการปรับผลลัพธ์

Graph Engineering
      ↓
ควบคุมโครงสร้างงาน

Dynamic Workflow
      ↓
ปรับโครงสร้างงานระหว่าง Runtime
```

---

# ภาพรวมทั้ง 3 แนวคิด

```text
                    AI Workflow Engineering

                           │
             ┌─────────────┼─────────────┐
             │             │             │
            Loop          Graph        Dynamic
             │             │             │
        Improve Result   Organize     Adapt Plan
                         Tasks
```

หรือมองเป็นพัฒนาการ

```text
Single Step

Input → Output


Loop

Generate
   ↓
Evaluate
   ↓
Revise
   ↺


Graph

        ┌→ Task B ─┐
Task A ─┤          ├→ Task E
        └→ Task C ─┘


Dynamic Workflow

Problem
   ↓
Planner
   ↓
Dynamic Graph
   ↓
Execute
   ↓
Evaluate
   ↓
Re-plan
   ↺
```

ความแตกต่างที่สำคัญคือ

| แนวคิด                | คำถามหลัก                                         |
| --------------------- | ------------------------------------------------- |
| **Loop Engineering**  | จะทำให้ผลลัพธ์ดีขึ้นเรื่อย ๆ อย่างไร              |
| **Graph Engineering** | จะจัดโครงสร้างงานและ Dependency อย่างไร           |
| **Dynamic Workflow**  | จะเปลี่ยนแผนและโครงสร้างงานระหว่างการทำงานอย่างไร |

ถ้ามองในเชิงความซับซ้อน จะได้ประมาณนี้

```text
Single Prompt
    ↓
Loop
    ↓
Sequential Graph
    ↓
Fan-out / Fan-in
    ↓
Conditional Graph
    ↓
Graph + Loop
    ↓
Dynamic Workflow
    ↓
Re-planning Workflow
```

โครงสร้างนี้เหมาะใช้เป็น **Theory ก่อนเข้าสู่ LAB** เพราะผู้เรียนจะเห็นชัดว่าแต่ละแนวคิดไม่ได้แทนที่ของเดิม แต่เพิ่มความสามารถขึ้นทีละระดับ.

"""



## 1. โครงสร้างไฟล์

สร้างโฟลเดอร์ `AI_Workflow_Engineering_for_SA/` ประกอบด้วย:

- `README.md` — ภาพรวม เป้าหมาย การเตรียมเครื่อง และวิธีเรียน
- `AI_Workflow_Engineering_SA.html` — สไลด์ภาษาไทย
- `001_LAB_<ชื่อกิจกรรม>/` ถึง `00x_LAB_<ชื่อกิจกรรม>/` วางโดยตรง ไม่สร้าง `LAB/` ครอบ

แต่ละ LAB มี:
- `README.md` — คู่มือทีละขั้น พร้อม Prompt ตัวอย่างผล และจุดตรวจ

ใช้ชื่อไฟล์ตรงกับคู่มือและ Relative links ที่เปิดได้จริง



ข้อกำหนด:
- ใช้ Placeholder แทนข้อมูลบุคคล บัญชี และ Token จริง
- สร้างแผนภาพด้วย **Excalidraw MCP** เก็บทั้งไฟล์แก้ไขได้และไฟล์แสดงผล
- ทดสอบสไลด์และ UI ด้วย **Playwright CLI** พร้อมภาพหน้าจอและผลจริง

