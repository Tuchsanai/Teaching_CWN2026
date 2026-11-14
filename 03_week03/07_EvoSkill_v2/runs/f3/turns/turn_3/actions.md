# ตาที่ 3 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-14 21:21 UTC คุณมีเวลาถึง 2026-11-14 21:51 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 3 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v3` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; ls; cat evolver_workspace/* 2>/dev/null | head -100; ls staging skills/*; ls scores; ls reference | head
```

ผลที่ได้:

```
evolver_workspace
reference
scores
skills
solver_workspaces
staging
traces
skills/epoch_0:

skills/epoch_1:
baankafe-money-function

skills/epoch_2:
baankafe-money-function

staging:
baankafe-money-function
epoch_0.json
epoch_1.json
epoch_2.json
baankafe
split.json
```

### ขั้น 2 · Bash

```
cd /evo; ls -R evolver_workspace | head; cat staging/*/SKILL.md; ls staging/*; ls reference/baankafe | head -30; cat reference/split.json | head -30; for i in 0 1 2; do echo $i; cat scores/epoch_$i.json; done; ls scores
```

ผลที่ได้:

```
evolver_workspace:
---
name: baankafe-money-function
description: ใช้เมื่อโจทย์ให้เขียนฟังก์ชันคิดเงิน/ส่วนลด/ค่าส่ง/หารบิล/เงินคืน (หน่วยสตางค์) ลงใน solve.py ของร้าน BaanKafe หรือโจทย์ใดที่ต้องคืนจำนวนเต็มสตางค์ — มีกติกาการปัดเศษ การตรวจ input และนโยบายซ่อนที่ตัวตรวจจะทดสอบแต่โจทย์ไม่ได้เขียนไว้
---

# เขียนฟังก์ชันคิดเงิน BaanKafe ให้ผ่านตัวตรวจ

ตัวตรวจรันเทสต์ 4 กลุ่ม: **normal / boundary / no-drift / reject** โจทย์ (brief) บอกแค่สูตรหลัก
rollout ที่ผ่านมาได้ประมาณ 0.4–0.55 เพราะเขียนแค่สูตรหลักแล้วหยุด (ไม่ validate, ไม่รันทดสอบ, เดาการปัดเศษเอง)
ต้องทำครบทุกข้อด้านล่าง

## 1. โครงไฟล์
- ไฟล์ `solve.py` ในโฟลเดอร์ปัจจุบัน มีฟังก์ชันชื่อและ signature ตรงตามโจทย์เป๊ะ
- ดูแม่แบบที่ `template.py` ในโฟลเดอร์สกิลนี้ (คัดลอกแล้วแก้เฉพาะตัวฟังก์ชัน) — มี helper `half_up`, `round_down`, `need_int`, `need_bool` และ `main()` อ่าน JSON จาก stdin
- ตัวตรวจ import ฟังก์ชันตรง ๆ ได้ และอาจรันเป็น CLI (`{"ok":true,"result":...}` / exit 2 เมื่อ ValueError) จึงควรมีทั้งสองแบบ

## 2. คณิตศาสตร์: ห้าม float
- ใช้ `fractions.Fraction` หรือเลขจำนวนเต็มล้วนตลอดทาง เปอร์เซ็นต์เขียนเป็น `Fraction(95,100)` ไม่ใช่ `0.95`
- **ปัดเศษครั้งเดียวตอนท้ายสุด** ห้ามปัดระหว่างขั้น (เช่น ลด 5% แล้วปัด แล้วลด 10
…(ตัด 4530 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /evo; ls traces; ls traces/epoch_2 | head -3; diff -r skills/epoch_2/baankafe-money-function staging/baankafe-money-function && echo same; ls reference/baankafe/*
```

ผลที่ได้:

```
epoch_0
epoch_1
epoch_2
t1-cafe-bill_s1.jsonl
t1-cafe-bill_s2.jsonl
t1-cafe-bill_s3.jsonl
same
reference/baankafe/answers:
t1-cafe-bill
t2-split-bill
t3-shipping-fee
t4-cashback

reference/baankafe/tasks:
t1-cafe-bill.json
t2-split-bill.json
t3-shipping-fee.json
t4-cashback.json
```

**Agent พูด:** ฉันไม่ได้แก้อะไรใน `/evo/staging/` ชุด `skills_v3` จึงเหมือน `skills_v2` ทุกไฟล์ (ตรวจด้วย `diff -r`)

สกิล `baankafe-money-function` ทำให้ Solver ได้ 1.0 ครบทั้ง 12 rollout ใน epoch 2 คะแนนไต่ขึ้นตามลำดับคือ 0.4–0.55 ใน epoch 0 (ไม่มีสกิล), 0.9 ใน epoch 1 และ 1.0 ใน epoch 2 เมื่อไม่มีจุดพลาดเหลือให้แก้ การเพิ่มกติกาเฉพาะของโจทย์ train เข้าไปมีแต่จะทำให้สกิลเจาะจงเกินและใช้กับโจทย์อื่นไม่ได้

ตอนนี้ยังไม่มีผลของ epoch 3 ให้ดู ใน `/evo/scores/` มีแค่ epoch 0 ถึง 2 และใน `/evo/traces/` ก็มีแค่ epoch 0 ถึง 2 ถ้า epoch 3 มีโจทย์ที่ทำให้คะแนนตก ค่อยกลับมาแก้ในตาถัดไป
