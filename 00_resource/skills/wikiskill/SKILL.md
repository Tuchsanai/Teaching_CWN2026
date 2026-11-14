---
name: wikiskill
description: ปรับชุดสกิลของ Agent อัตโนมัติด้วยวงรอบ WikiSkill (arXiv:2608.27454) ที่มี wiki คั่นกลางระหว่าง Trace กับสกิล — รัน Trial ด้วย skill-optimizer สรุป Trace ลง wiki เสนอแก้สกิลทีละ 1 ตัว แล้วรับเฉพาะเมื่อ Validation ดีกว่า R_best ใช้เมื่อผู้ใช้ขอ "รัน WikiSkill", "ปรับสกิลด้วย wiki", "สร้างสกิลจากศูนย์ด้วย Trace", ขอดูสถานะหรือทำวงรอบต่อจากที่ค้าง หรือสั่ง /wikiskill
---

# wikiskill

วงรอบปรับสกิลที่เริ่มจากชุดสกิลว่าง แล้วให้โมเดล 2 บทบาททำงานแทนคน: **Wiki Maintainer** สรุป Trace เป็นความรู้ และ **Skill Proposer** เขียนสกิลจากความรู้นั้น โปรแกรมเป็นผู้ตัดสินด้วย Validation

```text
raw/    Trace ของ Training      เขียนครั้งเดียว ไม่แก้
wiki/   ความรู้ที่สรุปจาก Trace   สะสมทุกรอบ ไม่ถูกย้อนกลับ
skills/ ชุดสกิลที่ใช้งาน          เปลี่ยนเมื่อผ่าน gate เท่านั้น
```

## ใช้เมื่อไร

- มีโฟลเดอร์งาน `<work>` แบบ skill-optimizer (มี `suite/suite.json` ที่แบ่งโจทย์เป็น `train` และ `val`) และต้องการให้ระบบค้นหาสกิลเองจาก Trace
- ต้องการทำวงรอบต่อจากขั้นที่ค้าง ดูสถานะ หรืออ่านว่า wiki กับสกิลของ workspace หนึ่งมาจากไหน
- ต้องการเทียบผลแบบมี wiki กับไม่มี wiki (`--no-wiki`)

ไม่ใช้เมื่อ: ต้องการแก้สกิลด้วยมือทีละรุ่น (ใช้ `skill-optimizer` ของบท 05) หรือยังไม่มีชุดโจทย์กับตัวตรวจ

## ตารางคำสั่ง

รูปแบบ: `python3 scripts/wikiskill.py <คำสั่ง> <work> --ws <ชื่อ workspace>` · 1 การรัน = 1 workspace = `<work>/runs/<ws>/`

| คำสั่ง | Algorithm 1 | ทำอะไร | เรียกโมเดล |
|---|---|---|---|
| `init` | บรรทัด 2 | สร้าง workspace: ชุดสกิลว่าง wiki ว่าง (มี `state.json` แล้ว = exit 1) | ไม่ |
| `baseline` | บรรทัด 3 | วัด Validation ด้วยชุดสกิลว่าง → `R_best` | เรียก (Trial) |
| `rollout` | บรรทัด 8 | Agent ทำโจทย์ Training ด้วยชุดสกิลปัจจุบัน → `raw/iter-NN/` | เรียก (Trial) |
| `maintain` | บรรทัด 9–10 | สุ่ม Trace แล้วให้ Wiki Maintainer สรุปลง `wiki/` | เรียก 1 ครั้ง |
| `propose` | บรรทัด 11–12 | Skill Proposer เสนอแก้สกิล 1 ตัว → `history/iter-NN/candidate/` | เรียก 1 เซสชัน |
| `gate` | บรรทัด 13–19 | วัด Validation ของชุดที่เสนอ → รับ หรือ ย้อนกลับ · จดลง `wiki/skill-impact.md` | เรียก (Trial) |
| `loop` | บรรทัด 3–20 | ทำต่อจากขั้นที่ค้างจนวงรอบหยุด แล้วพิมพ์ `status` (`--iters N` แทนค่าของ `init`) | เรียก |
| `status` | – | ตารางสรุปทุกรอบจาก `state.json` | ไม่ |

ตัวเลือกของ `init`: `--accounts yolo1,yolo2` (ต้องระบุ) · `--iters 8` · `--reps 3` · `--par 6` · `--model sonnet` · `--effort medium` · `--opt-model sonnet` · `--opt-effort high` · `--task-desc "…"` · `--no-wiki` · `--skillopt <path ของ skillopt.py>`

## ขั้นตอน

1. **ตรวจของที่ป้อนเข้า** `<work>/suite/suite.json` ต้องมีโจทย์ชุด `train` และ `val` และตัวตรวจรันได้ · หา `skillopt.py` ของ skill-optimizer ให้พบ (ค่าเริ่มต้น `../skill-optimizer/scripts/skillopt.py` นับจากโฟลเดอร์ของสกิลนี้)
2. **ยืนยันกับผู้ใช้ก่อนเริ่ม** บัญชีที่ใช้ จำนวนรอบ จำนวนรอบต่อโจทย์ และคำอธิบายงาน (`--task-desc`) เพราะทุกขั้นที่เรียกโมเดลมีค่าใช้จ่าย
3. **สร้าง workspace**

   ```bash
   python3 scripts/wikiskill.py init <work> --ws w1 --accounts yolo1,yolo2 --task-desc "<งานที่ Agent ทำ>"
   ```
4. **รันวงรอบ** ทั้งหมดในคำสั่งเดียว หรือทีละขั้นเมื่อต้องการดูผลระหว่างทาง

   ```bash
   python3 scripts/wikiskill.py loop <work> --ws w1
   # หรือ: baseline → rollout → maintain → propose → gate → rollout → …
   ```
   คำสั่งที่ถูกเรียกผิดลำดับจะบอกขั้นถัดไปแล้ว exit 1 โดยไม่เรียกโมเดล · ถ้าขั้นใดล้มกลางทาง แก้สาเหตุแล้วสั่ง `loop` ซ้ำได้ ขั้นที่เสร็จแล้วไม่ถูกทำใหม่
5. **อ่านผล** `status` แล้วเปิดตามลำดับ: `wiki/skill-impact.md` (เสนออะไร ได้ผลอย่างไร) → `wiki/index.md` → หน้า pattern ที่เกี่ยวข้อง → `skills/<ชื่อ>/SKILL.md` และ `PURPOSE.md`
6. **รายงานผู้ใช้** ตาราง `status` · สกิลที่ได้ · pattern ที่พบ · รอบที่ถูกปฏิเสธและเหตุผล · ค่าใช้จ่ายรวม
7. **วัดผลสุดท้าย (ถ้าต้องการ)** ชุดสกิลของ workspace วัดด้วย skill-optimizer ได้โดยตรง: `python3 <skillopt.py> run <work> --label w1 --split test`

รายละเอียดของไฟล์ที่แต่ละคำสั่งเขียน: [`references/workspace.md`](references/workspace.md) · ที่มาของแต่ละส่วนเทียบกับเปเปอร์: [`references/source.md`](references/source.md)

## ข้อห้าม

- ห้ามแก้ไฟล์ใน `raw/` · Trace เป็นหลักฐานที่ใช้ตรวจการตีความของ wiki
- ห้ามแก้หรือลบไฟล์ใน `wiki/` ด้วยมือระหว่างวงรอบ และห้ามย้อน wiki กลับเมื่อข้อเสนอถูกปฏิเสธ · `wiki/skill-impact.md` เขียนโดยโปรแกรมเท่านั้น
- ห้ามแก้ `skills/` ของ workspace ด้วยมือ และห้ามคัดลอก `candidate/skills/` ไปใช้เอง · สกิลเปลี่ยนได้ทางเดียวคือผ่าน `gate`
- ห้ามแก้ `state.json` เพื่อข้ามขั้นหรือเปลี่ยนคะแนน
- ห้ามให้ Agent ที่ทำโจทย์เห็น `wiki/` หรือ `raw/` (อย่าคัดลอกเข้า sandbox หรือใส่ในสกิล)
- ห้ามใส่คำตอบของโจทย์ ค่าที่ตัวตรวจคาด หรือ trace id ลงในสกิล
- ห้ามเปิดโจทย์หรือผลรายข้อของชุด Validation ให้ Maintainer หรือ Proposer เห็น · ชุดนี้ใช้ตัดสินเท่านั้น
- ห้ามเปลี่ยนเกณฑ์ของ gate (รับเมื่อ Validation **มากกว่า** R_best เท่านั้น เท่ากัน = ไม่รับ)
- ห้ามรันสอง workspace ชื่อเดียวกันพร้อมกัน และห้ามรัน `init` ทับ workspace เดิม (ใช้ชื่อใหม่)
