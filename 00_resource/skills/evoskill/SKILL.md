---
name: evoskill
description: รันวงรอบ EvoSkill v2 เพื่อให้ Agent เขียนชุดสกิลเองจากผลการทำโจทย์ของ benchmark (Benchmark Adaptor เตรียมสนาม · Solver ทำโจทย์ · Evolver เขียนสกิลในเซสชันเดียวตลอดการรัน) ใช้เมื่อผู้ใช้ขอ "รัน EvoSkill", "ให้ Evolver เขียนสกิล", "skill evolution", ดูผลหรือความแกว่งของการรัน (status · noise) วัดชุดสกิลกับ Test Set หรือส่งออกผลของการรัน
---

# evoskill

เครื่องมือ 1 ไฟล์ `scripts/evoskill.py` ที่ควบคุมการรันแบบ EvoSkill v2 (arXiv:2610.25931) ตั้งแต่เตรียม benchmark จนวัด Test Set · คุณ (AI ที่อ่านไฟล์นี้) เป็นผู้กดรันคำสั่งและรายงานผล **ผู้เขียนสกิลคือ Evolver ไม่ใช่คุณ**

## ใช้เมื่อไร

| ใช้ | ไม่ใช้ |
|---|---|
| มี benchmark (โจทย์ + ตัวตรวจ + การแบ่งชุด) และอยากได้ชุดสกิลที่ Agent เขียนเอง | อยากแก้สกิลที่มีอยู่ทีละรุ่นแล้วตัดสินด้วยประตูรับ → ใช้ `skill-optimizer` ของบท 05 |
| อ่านผลของการรันที่เก็บไว้ (`status` `noise`) | โจทย์ยังไม่มีตัวตรวจที่ผู้ใช้ตรวจแล้ว |

## สิ่งที่ต้องมีก่อนเริ่ม

`<work>/bench/` ต้องมี `instruction.md` (มีบรรทัด `<E> epochs · <N> samples per task`) · `data/<data root>/` · `split.json` · `benchmark_grader.py` · `solver_prompt.txt` และต้องมี `skillopt.py` ของบท 05 (รัน rollout ของ Solver) · โครงของไฟล์ทั้งหมดอยู่ใน [references/workspace.md](references/workspace.md)

## คำสั่ง

รูปแบบ: `python3 scripts/evoskill.py <คำสั่ง> <work> --run <ชื่อ>` · 1 การรัน = โฟลเดอร์ `<work>/runs/<ชื่อ>/`

| คำสั่ง | ทำอะไร | เรียกโมเดล |
|---|---|---|
| `init --accounts a,b` | สร้างการรัน อ่านขนาดของการรันจากคำสั่งของผู้ใช้ | ไม่ |
| `adapt` | Benchmark Adaptor 1 เซสชัน → plug-in + `reference/` → ล็อกด้วย hash → ตรวจการรั่ว | เรียก |
| `audit` | ตรวจการรั่วใน `reference/` ซ้ำ (exit 0 สะอาด · 1 รั่ว) | ไม่ |
| `base` | epoch 0: Solver ทำทุกชุดโดยไม่มีสกิล | เรียก |
| `turn` | Evolver 1 ตา → `skills_vK` (รับเสมอ) | เรียก |
| `rollout` | Solver ทำ Validation และ Training ด้วย `skills_vK` | เรียก |
| `test` | วัดชุดของ epoch สุดท้ายกับ Test Set 1 ครั้ง | เรียก |
| `run [--stop-after adapt\|base\|turn\|rollout]` | ทำทุกขั้นที่เหลือ (ทำต่อจากที่ค้างได้) แล้วพิมพ์ `status` | เรียก |
| `status` | ตารางสรุปของการรัน | ไม่ |
| `noise` | ความแกว่งของ rollout และผลของประตูรับแบบวัดครั้งเดียว | ไม่ |
| `eval --label L --skills v1\|none\|<โฟลเดอร์> --split train\|val\|test\|all [--model M]` | วัดชุดสกิลใดก็ได้เป็น leg ชื่อ `L` | เรียก |
| `export --to <โฟลเดอร์>` | สำเนาของการรันที่ตัด trace ดิบและรายละเอียดของ Validation | ไม่ |

ตัวเลือกของ `init`: `--instruction <ไฟล์>` · `--solver-model/--solver-effort` (sonnet/medium) · `--evolver-model/--evolver-effort` (sonnet/high) · `--adaptor-model` (sonnet) · `--par` (6) · `--turn-minutes` (30) · `--fresh-session` · `--skillopt <path>`

## ขั้นตอน

1. **ตรวจของที่ผู้ใช้ส่ง** ตัวตรวจต้องผ่านการตรวจของผู้ใช้ก่อน (เช่น ให้เฉลยอ้างอิงเต็มคะแนน) แล้วจึง `init`
2. **`run --stop-after adapt`** แล้วเปิด `setup/audit.md` และ `turns/adaptor/actions.md` ดูว่า `reference/` มีอะไร ก่อนใช้โทเคนกับ rollout
3. **`run`** ทำต่อจนจบ: `base` → (`turn` → `rollout`) × E → `test` · ถูกหยุดกลางทางให้สั่ง `run` ซ้ำ leg ที่เสร็จแล้วไม่รันใหม่ · leg ที่หยุดด้วย "Solver ไม่ได้ทำงาน" (เช่น บัญชีติดลิมิต) ยังไม่ถูกบันทึก ให้แก้บัญชีหรือรอพ้นลิมิตแล้วสั่งคำสั่งเดิมซ้ำ ห้ามข้าม
4. **รายงาน** ด้วยผลของ `status` และ `noise` ตามที่พิมพ์ · อธิบายสิ่งที่ Evolver ทำจาก `turns/turn_K/actions.md`
5. **`export`** เมื่อต้องเก็บผลลงเครื่องหรือส่งต่อ

## ข้อห้าม

- ห้ามแก้ไฟล์ใน `setup/` `reference/` `skills_v*/` `evo/` และ `state.json` ด้วยมือ (โปรแกรมหยุดเมื่อ hash ของ `setup/` ไม่ตรง)
- ห้ามเขียนหรือแก้สกิลแทน Evolver และห้ามเลือกชุดสกิลของ epoch อื่นไปวัด Test แทน epoch สุดท้าย
- ห้ามส่งผลรายข้อของตัวตรวจ (`grade.json` → `checks`) ของ Validation หรือ Test ให้ Evolver และห้ามวางไว้ใน `evo/`
- ห้ามใช้ `EVOSKILL_NO_ISOLATION=1` กับการรันที่วัดผลจริง (ใช้กับ Agent จำลองเท่านั้น)
- ห้ามแก้ `prompts/` ระหว่างการรัน: Evolver ต้องได้ system prompt ชุดเดียวกันทุกตา
- ห้ามรัน `test` ซ้ำเพื่อเลือกผลที่ดีกว่า: Test Set วัดครั้งเดียว

## อ่านเพิ่ม

- [references/workspace.md](references/workspace.md) โครงของ 1 การรัน ไฟล์ที่แต่ละคำสั่งอ่านและเขียน การแยกเครื่อง และวิธีทดสอบด้วย Agent จำลอง
- [references/source.md](references/source.md) ส่วนของสกิลนี้มาจากข้อไหนของเปเปอร์ และต่างตรงไหน
