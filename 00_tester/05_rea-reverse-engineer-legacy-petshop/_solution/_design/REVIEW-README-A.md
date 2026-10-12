# REVIEW-README-A · ตรวจ `README-PART-A.md` (ผู้ตรวจ RW5A · 12 ต.ค. 2026)

> เทียบกับ `LESSON-PLAN.md` · `REA-THEORY.md` · `METHODS.md` · `REA-FEASIBILITY.md` · `PREP-LOG.md` · `STYLE-GUIDE.md` · `IMAGES-NOTES.md` · `IMAGES-REVIEW-05.md` · `img/` (36 ไฟล์)
> ตรวจบนเครื่องจริง (อ่านอย่างเดียว): `docker image ls rea-lab` = `rea-lab:6.4.0` **2.65GB** · Docker 29.5.2 · Node v26.7.0 · `netsh … excludedportrange` = มี `2970–3069` และ `3070–3169` (มี 3000) · 4000 ไม่อยู่ในช่วงที่จอง
> สำเนาก่อนแก้: scratchpad ของ RW5A (`README-PART-A.orig.md`)

## สรุป

| ด้าน | ผล |
|---|---|
| (1) ครบทุกแนวคิดที่ผู้สอนสั่ง | ✅ 18 หัวข้อ ครบ: Chikofsky & Cross · static/dynamic · black/white/grey · REA หรืออ่าน repo · Evidence + 4 ถัง + หาไม่เจอ ≠ ไม่มี · digest · graph + trace · passive/driven/HAR · เทียบเวอร์ชัน · obligation → oracle · [E] กับ [D][R][A][O] · จริยธรรม · ขีดจำกัด · REA architecture · characterization · safety net · impact · แดง → เขียว · ทุกหัวข้อมี **รูป + ตาราง + blockquote กับดัก** + LAB ที่ได้ใช้ |
| (2) รูป | แก้แล้ว: IMG-TODO 6 จุดใส่รูปจริงครบ · ทุกลิงก์รูปมีไฟล์จริง (28 รูป) · ไม่มีรูปซ้ำภายใน Part A |
| (3) ข้อเท็จจริง 🧰 | ✅ ถูกหลังแก้ 4 จุดเล็ก |
| (4) เฉลยรั่ว | ✅ grep `1,049 1049 orders.ts PP-231 /orders/[id] >= FREE_SHIPPING_MIN SummaryRows` = 0 · Quiz มีแค่คอลัมน์คำถาม · ตัวอย่างเงินเป็นค่าสมมติ |
| (5) ตารางเส้นทาง | ✅ ตรง LESSON-PLAN §2: 🔍 = LAB 0 1 2 3 9 · ✏️ = LAB 4 5 6 7 8 10 (6/10 ≥ ครึ่ง) · มีช่อง ⏱️ แบบ `<!-- RESULT:LABn:time -->` ครบ 11 แถว · anchor LAB 0–10 ตรงหัวข้อใน Part B ทุกตัว |
| (6) สไตล์ | ✅ ไม่มี em dash · ใช้ "เรา" · emoji เป็นป้าย · ประโยคหลักตัวหนาในเครื่องหมายคำพูด |
| (7) ความยาว | ⚠️ 520 บรรทัด / 110 KB (ส่วน 🎓 ~380 บรรทัด) ยาวกว่าบท 04 แต่ผู้สอนสั่งให้ทฤษฎีแน่น · ทุกหัวข้อเป็นรูป → ตาราง → กับดัก อ่านไล่ได้เร็ว + มีสารบัญกลุ่มหัวข้อ · ไม่ตัด |

## รายการที่พบ

| # | จุด | พบอะไร | แก้แล้ว? |
|---|---|---|---|
| 1 | 🧭 · 🎓4 · 🎓5 · 🎓11 · 🎓18 · 🗺️ | `<!-- IMG-TODO -->` 6 จุด ทั้งที่ไดอะแกรมมีแล้วใน `img/` | ✅ ใส่ `overview-5-phases.png` `when-rea.png` `evidence-4-buckets.png` `oracle-badges-e.png` `safe-change-loop.png` `lab-flow.png` พร้อม alt จาก `IMAGES-NOTES.md` (เปิดดู 3 รูปหลักแล้ว ข้อความใน alt ตรงกับภาพ) |
| 2 | 🎓18 | ใช้ `concept-22-red-then-green.jpg` ซ้ำกับ LAB 8 ใน Part B | ✅ เอาออก ใช้ `safe-change-loop.png` (ไดอะแกรม 8 ขั้นตรงกับตารางของหัวข้อพอดี) |
| 3 | 🎓3 triangulation | บอกว่า REA trace เห็น `POST /api/orders` แต่ static trace ไม่รู้ method · และตัวอย่างใช้แค่ 2 ตา | ✅ เปลี่ยนเป็น 3 ตา: REA เห็น `/api/orders` · repo เจอ `CheckoutForm.tsx:73` · HAR เห็น `POST /api/orders` 201 (ตาม REA-FEASIBILITY §HAR) |
| 4 | 🎓5 authority | เขียนเหมือนค่า `authority` ของ REA มีแค่ static/runtime/inference/unknown แต่ใน REA จริงเป็นค่าละเอียด (`ast-static-analysis` `controlled-replay` …) และแยก `state` กับ `confidence` | ✅ เพิ่มย่อหน้าบอกว่า 4 ถังคือ "การรวบเพื่อสอน" + คอลัมน์ "authority จริงใน REA (ตัวอย่าง)" ตาม REA-THEORY §3.2 |
| 5 | 🎓6 | "hash ต่างทั้งหมด" ไม่แม่น | ✅ "ต่างโดยสิ้นเชิง (ดูจาก hash ไม่ออกว่าต่างมากหรือน้อย)" |
| 6 | 🎓8 | ไม่ได้บอกว่าทำไมต้องใช้ seed `string` | ✅ เพิ่มในกับดัก: seed `api` = Electron API · `route`/`api` กับ `/api/coupons/validate` ได้ no-match (REA-FEASIBILITY) |
| 7 | 🎓11 ป้าย | ตาราง 📦 บอก `[D][R][E][O]` แต่ 🎓11 มีแถว [A] โดยไม่บอกสถานะ (ภาพ `oracle-badges-e.png` บอก "[E] แทน [A]") · ขาดกติกา REA-THEORY §4.2 ข้อ 3 และคำอธิบาย [E] ต่างจาก [O] | ✅ แถว [A] = "คำอ้าง … บทนี้ไม่ใช้เป็นผลที่คาดหวัง ต้องยืนยันด้วย [E] หรือถาม [D] ก่อน" · เพิ่มกติกา "[E] ต่างจาก [O]" และ "TC กฎธุรกิจต้องมี [D]/[R] · มีแค่ [E] → `[E-ยังไม่ยืนยัน]`" |
| 8 | 🎓13 | แถว "ผลขนาดเล็ก" อ่านแล้วไม่เข้าใจ | ✅ "ผลที่เล็กพอให้ AI อ่านตรง ๆ" (54 MB จริงตาม PREP-LOG) |
| 9 | 🎓14 | "rea.ps1 mount รากบท" แต่สคริปต์ mount **โฟลเดอร์ปัจจุบัน** (`Get-Location`) | ✅ "mount โฟลเดอร์ปัจจุบัน → ต้องรันจากรากบท" |
| 10 | 🧰 ExecutionPolicy | ไม่ได้บอกกรณีองค์กรล็อกด้วย Group Policy (`-ExecutionPolicy Bypass` ถูก GPO ทับ) | ✅ เพิ่มในช่อง "ตรวจยังไง": แถว MachinePolicy/UserPolicy ต้อง `Undefined` ไม่งั้นแจ้งผู้ดูแลเครื่อง |
| 11 | 🧰 ปิดเว็บบทอื่น | บอกให้ปิดบท 02–04 ด้วยเหตุผลพอร์ต 4000 (ซึ่งมีแค่บท 06 ที่ชน) | ✅ "ปิดบท 06 (พอร์ต 4000) · บท 02–04 ไม่ชน แต่ปิดช่วยประหยัดแรม" |
| 12 | 🧰 tree | `.gitignore` ขาด `playwright-report/` · ไม่มี `fast_track/` ที่อยู่ในบทจริง | ✅ เติมทั้งสอง |
| 13 | 🧰 ข้อเท็จจริงอื่น | port 4000 / ช่วงจอง 2970–3069 3070–3169 · `docker build -t rea-lab:6.4.0 rea` (Dockerfile อยู่ `rea/`) · ~2.65 GB · ข้อความ error bind · `-NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out …` · `>` ของ PS 5.1 = UTF-16/BOM · Git Bash แปลง `/work` · `pawpantry05` / `pawpantry05_default` / `http://petshop:3000` · e2e-legacy 10 ไฟล์ 40 test · `npm run test:all` 3 เบราว์เซอร์ | ✅ ตรงของจริงทั้งหมด ไม่ต้องแก้ |
| 14 | 🎓 ความถูกต้องทฤษฎี | Chikofsky & Cross 6 คำ (RE = examination ไม่ใช่ change) · Dijkstra/Rice · static vs runtime · 7 คลาส source-to-bundle + modified = 0 / ไฟล์ที่แก้เป็น `unknown` (PREP-LOG: `duplicated · unknown · unknown · duplicated`) · compare-versions ส่วนใหญ่ `unknown` (1,447/1,669) · fail-closed · HAR `--sensitive-value` · จริยธรรม (พ.ร.บ.คอมพิวเตอร์ PDPA EULA) · ขีดจำกัด | ✅ ตรง REA-THEORY / PREP-LOG |
| 15 | Part B ข้อ 5 LAB 2 (บรรทัด 119) + 📖 | (ตามคำสั่ง coordinator) พรอมต์เขียน "black = REA ดูของที่ build" ขัดกับ Part A และ `three-eyes.png` · คำศัพท์ grey-box = "ผสมสองแบบ" | ✅ แก้ Part B: "white = อ่านโค้ด · grey = REA ส่องของที่ build · black = เปิดเว็บ/HAR ดูจากข้างนอก" · 📖 grey-box = "ส่องของที่ส่งมอบหรือรันอยู่ด้วย REA แต่ยังทดสอบจากข้างนอก" · ⚠️ **`PROMPTS.md:128` ยังเป็นข้อความเดิม** (ไม่ได้แก้เพราะอาจเป็นฉบับที่ RUNNER กำลังใช้) ให้ผู้ดูแล PROMPTS แก้ให้ตรงก่อนรอบรันถัดไป หรือจดความต่างใน `_solution` §7 |
| 16 | ลำดับเลข concept | Part A ใช้ `concept-12` หลัง `concept-15` (หัวข้อ 15) ผิดกฎ STYLE-GUIDE 4.1 "เรียงตามลำดับที่ปรากฏ" | ❌ ไม่แก้ (เปลี่ยนชื่อไฟล์กระทบ Part B / IMAGES-*) · เล็กน้อย |
| 17 | รูปซ้ำข้าม Part | Part B ใช้ `concept-09` `concept-10` (รูป 🎓8–9 ของ Part A) และ Part A ใช้ `concept-18` `concept-23` (รูป LAB 4 / LAB 9 ของ Part B) | ❌ ไม่แก้ในรอบนี้ · แนะนำผู้รวม README ตัดรูปซ้ำฝั่งใดฝั่งหนึ่ง (LESSON-PLAN §8.1 ให้ 09/10 อยู่ 🎓 · 18/23 อยู่ LAB) |
| 18 | 🎓16 ตาราง "เทสต์เขียวไม่ได้บอก" | แถว "ตรวจที่ค่าขอบไหน · ตรวจแค่หน้าจอ หรือตรวจถึงผลที่ระบบบันทึก" ใกล้เคียงคำใบ้ BUG-01 | ❌ คงไว้ · เป็นคำตอบทั่วไปของ Quiz 10 ตาม LESSON-PLAN §3.1 (ส่วนเฉพาะบทอยู่ `_solution/QUIZ.md` เท่านั้น) ไม่ชี้ไฟล์/ยอด |
