# REVIEW-README-A · รีวิว README-PART-A บท 06 (RW6A · 12 ต.ค. 2026)

เทียบกับ: `LESSON-PLAN.md` §1–6, §8, §12 · `IMAGES-REVIEW-06.md` · `CR-DESIGN.md` §2 · `CODEBASE-NOTES.md` §7 · `EXAM-DRAFT.md` (ส่วนผู้สอน §3) · `PROMPTS.md` · บท 05 `STYLE-GUIDE.md` `REA-THEORY.md` `LESSON-PLAN.md` `README-PART-B.md` · โฟลเดอร์ `img/` ทั้งสองบท · `web/compose.yaml` `db/compose.yaml` `tools/rea.ps1` · `CHANGE-REQUESTS/*`
หมายเหตุ: `05_…/_solution/_design/README-PART-A.md` **ยังไม่มีไฟล์** (ตรวจ 12 ต.ค. 2026) → ตรวจความตรงของศัพท์/ป้ายกับ `05/LESSON-PLAN.md` §3, `REA-THEORY.md` §3.2 §4.2 และ `05/README-PART-B.md` แทน · `IMAGES-NOTES.md` ของบท 06 ไม่มี

## สรุป

แก้ใน `README-PART-A.md` 8 จุด · ไม่แก้ (นอกขอบเขต/ตั้งใจ) 4 จุด · ไม่พบเฉลยรั่ว

| # | ประเด็น | ผลตรวจ / สิ่งที่เจอ | แก้แล้ว? |
|---|---|---|---|
| 1 | 🎓 ครบ 6 ข้อตามแผน §5 | ข้อ 1–6 มีครบ · ทุกข้อมีรูป concept + ตาราง 3–4 คอลัมน์ (หัวมี emoji) + blockquote กับดัก · กล่อง 🔁 ทบทวนบท 05 อยู่ข้อ 2, 3, 6 (ไม่สอนซ้ำ) | ✅ ผ่าน |
| 2 | ไดอะแกรม 5 ไฟล์ยังเป็น `IMAGE-TODO` ทั้งที่ไฟล์มีแล้วใน `img/` (`overview-5-phases.png` `three-eyes-db.png` `safe-change-loop.png` `traceability-chain.png` `lab-flow.png` · 2560 px · 324–481 KB) | วางรูปทั้ง 5 ตรงตำแหน่งตามแผน พร้อม alt สไตล์บ้าน (หัวเรื่อง + ทุกกล่องตามลำดับ + แถบล่าง · ข้อความถอดจาก `diagrams/*.html` และเปิดดู PNG `three-eyes-db` `safe-change-loop` เทียบแล้วตรง) · `safe-change-loop.png` วางใต้บรรทัด "วงจรแก้ 1 CR" คู่กับตาราง ①–⑧ · อัปเดตคอมเมนต์หัวไฟล์ | ✅ แก้แล้ว |
| 3 | `site-admin-queue.png` (แผน §12 #52 · 🧰) ไม่มีไฟล์ และไม่มีตำแหน่งใน PART-A | ใส่คอมเมนต์ `IMAGE-TODO` ใต้ตาราง "2 กล่อง + REA" · ต้องถ่ายจากรอบ RUNNER | ✅ วางตำแหน่ง (รอไฟล์) |
| 4 | ลิงก์รูปทั้งหมด | 27 ลิงก์ (บท 06 23 · บท 05 4) มีไฟล์จริงครบ 27/27 (path นับจากรากบท = ตำแหน่ง README.md) | ✅ ผ่าน |
| 5 | ตัวชี้ "อ่าน 🎓 ของบท 05 ข้อ 1–4" (2 ที่) | 🎓 ของบท 05 มี 8 ข้อ: 3 ตา = ข้อ 3 · หลักฐาน/หาไม่เจอ ≠ ไม่มี = ข้อ 4 · ป้าย [E]/characterization = **ข้อ 7** → "1–4" ขาดป้าย [E] | ✅ แก้เป็น "ข้อ 3, 4 และ 7" ทั้ง 2 ที่ |
| 6 | ศัพท์/ป้ายให้ตรงบท 05 | บท 05 ใช้ authority **🔵 static · 🟢 runtime · 🟡 inference · ⚪ unknown** · "**[E] ขัด [D] = ผู้ต้องสงสัยบั๊ก · [D] ชนะ**" · "กฎธุรกิจยังต้องมี [D]/[R]" · triangulation = "≥ 2 มุมยืนยันกัน" → กล่องทบทวนเดิมไม่มี emoji authority และไม่มี "[D] ชนะ" | ✅ แก้กล่อง 🔁 ข้อ 2 + blockquote ใต้ตารางป้าย ("· [D] ชนะ") · "หาไม่เจอ ≠ ไม่มี" `[E ev_xxxxxxxx]` ตรงบท 05 อยู่แล้ว |
| 7 | 🧰 กติกา PowerShell ข้อ 6: `curl.exe --data-binary @file.json` | ทดสอบใน PowerShell 5.1 จริง: `@file.json` ไม่ครอบ quote → ParserError *"The splatting operator '@' cannot be used…"* | ✅ แก้เป็น `'@file.json'` + เหตุผล · ⚠️ **`PROMPTS.md` บรรทัด 17, 152, 518 และ PART-B ที่คัดจากนั้นยังเป็น `@file.json` ไม่มี quote** → ต้องแก้ใน PART-B/PROMPTS (นอกขอบเขตงานนี้) |
| 8 | 🧰 ข้อเท็จจริงพอร์ต/ชื่อ | 4000/5433 · `sabai06-web` `sabai06-db` `sabai06-net` `sabai06-pgdata` · `http://sabai06-web:3000` ผ่าน network · HAR `127.0.0.1:4000` ตรง compose จริงและ BRIEF D5 D7 D8 · ExecutionPolicy `Restricted` + `-NoProfile -ExecutionPolicy Bypass -File` ตรง PROMPTS/rea.ps1 · `-Out` แทน `>` (BOM) ตรง rea.ps1 · `docker cp` + `psql -f` · ตรวจไทยด้วย SQL `t` · Node 22.18+ · rea-lab 2.65 GB | ✅ ผ่าน |
| 9 | เฉลยรั่ว: บั๊ก L1–L8 · กับดัก reset/`TABLES` · คำตอบข้อสอบ · mutant | grep `TABLES testmode room_id completeBooking cancelBooking cookie logout Gift GC_NOT abc owner ALLOW_TEST S03 E39 E40 E88 M1–M9 X1–X3 L1–L8 S4 กดเสร็จ ค่ารถ โรงแรม BUG_MODE flags` ใน README-PART-A = 0 (นอกคอมเมนต์หัวไฟล์) · L1 ปรากฏเฉพาะในรูป "เรื่องร้องเรียน CR-03" ซึ่งอยู่ในหนังสือ CR ที่ผู้เรียนเห็นอยู่แล้ว · "รายการตายตัว" เป็นคำใบ้กว้างตามแผน M9 · "ทำไม init ไม่พอ → หาเองใน LAB 8" ไม่เฉลย | ✅ ผ่าน |
| 10 | ตัวอย่าง `CHECK party_size <= 6` / กลุ่ม 8 คน | มาจากแผน §5 ข้อ 2 [รันจริง:A2] · ไม่ใช่ข้อสอบ (EXAM-DRAFT ไม่มีงานเปลี่ยนขนาดกลุ่ม) | ✅ เก็บไว้ |
| 11 | `traceability-chain.png` / `concept-15` แสดง "BR-21" (ชื่อที่มาจาก `answers/CR-03-ANSWERS.md`) และแถว CR-02 5%/10%/15% | ตัวเลข CR-02 อยู่ในหนังสือ CR-02 เอง · BR-21 เป็นแค่รหัสกฎ ไม่ใช่วิธีแก้ · แผน §12 กำหนดไว้เอง | ➖ ไม่แก้ (ยอมรับได้) |
| 12 | ตารางเส้นทาง 🔍/✏️ | 0–3 🔍 · 4–10 ✏️ · 11 🔍 · 12 ✏️ = **8/12 ✏️** ตรงแผน §6 (≥ ครึ่ง) · anchor 13 ตัวตรงหัว LAB ใน `README-PART-B.md` (คำนวณแบบ GitHub slug) · ไฟล์ที่ได้ตรงแผน · ⏱️ เป็น `⏳` + คอมเมนต์ RESULT รอรอบจริง (ถูกต้องตาม BRIEF ข้อ 7) | ✅ ผ่าน |
| 13 | สไตล์บ้าน | ชื่อบทลงท้าย (Copy & Paste) · ย่อหน้าแรกมี "คัดลอกพรอมต์ → …" · ประโยคหลักตัวหนาในคำพูดและอยู่ในแถบล่างไดอะแกรม · ตาราง 📦 คอลัมน์บทนี้ตัวหนา · ค.ศ. ในเนื้อความ + หมายเหตุ "2569 = 2026" · เงิน ฿ มี comma · ช่วงใช้ `–` · ไม่มี em dash ในเนื้อความ (มีแค่ `—` เป็นช่องว่างในตาราง 📦 ซึ่งเป็นแบบบท 04) · ใช้ "เรา" | ✅ ผ่าน |
| 14 | `three-eyes-db.png` subtitle เขียน "3 ตาจากบท 05 (REA · อ่าน repo · เอกสาร)" | ไม่ตรงนิยาม 3 ตาของบท 05 (black-box · grey-box REA · white-box) ที่กล่องทบทวนใช้ · ในเนื้อ README ไม่กระทบ แต่ภาพขัดกันเล็กน้อย | ❌ ไม่แก้ (ไฟล์ภาพ) → เสนอแก้ `diagrams/three-eyes-db.html` เป็น "3 ตาจากบท 05 (เดินเว็บ · REA · อ่าน repo) + ตาที่ 4 คือฐานข้อมูล" แล้ว render ใหม่ |
| 15 | บท 05 `README-PART-B.md` บรรทัด 119 นิยาม "black = REA ดูของที่ build" ขัดกับภาพ `concept-03-black-white-grey-box.jpg` (grey-box = REA) | บท 06 ยึดตามภาพ (grey-box = REA) | ❌ นอกขอบเขต · แจ้งผู้ดูแลบท 05 |

## ไฟล์ที่แก้
- `_solution/_design/README-PART-A.md` (เท่านั้น)
