# REVIEW-README-B · ตรวจ `README-PART-B.md` (LAB 0–10 → ไฟล์ในบทนี้)

> ผู้ตรวจ RW5B · 12 ต.ค. 2026 · เทียบกับ `PROMPTS.md` `LESSON-PLAN.md` `STYLE-GUIDE.md` `PREP-LOG.md` `IMAGES-NOTES.md` `IMAGES-REVIEW-05.md` และ `img/` (36 ไฟล์)
> วิธีตรวจ: สคริปต์ Node ดึงบล็อก ```` ```text ```` / ```` ```json ```` จากทั้ง 2 ไฟล์มาเทียบแบบ byte (หลัง normalize CRLF · ทั้งสองไฟล์เป็น LF อยู่แล้ว) · สคริปต์ slug แบบ github-slugger (ตัดทุกอักขระที่ไม่ใช่ letter/mark/number/`-`/space) ตรวจลิงก์ `](#…)` ของ PART-A + PART-B รวมกัน · `test -f` ทุกลิงก์รูป · grep คำเฉลยนอกบล็อกโค้ด · เปิดดูรูป concept-10 · 17 · 22 · 23 เทียบ alt

## สรุป

| ข้อ | ผล | แก้แล้ว? |
|---|---|---|
| 1 พรอมต์ตรง PROMPTS.md | 14/14 บล็อก (LAB 0–10 + LAB 9 ส่วน 2 + MCP json + MCP text) ตรงทุกไบต์ · ไม่มี drift | ไม่ต้องแก้ |
| 2 ลิงก์รูป · alt | 12/12 ลิงก์ `img/` มีไฟล์จริง · 18 รูปผลจริงเป็น placeholder `RESULT:LABn:img <ชื่อ>` ชื่อตรง LESSON-PLAN §8.3 · alt 2 รูปขึ้นต้นด้วย "ภาพ…" ผิดกฎ STYLE §4.3 | ✅ แก้แล้ว |
| 3 ลำดับแม่แบบ LAB | ทุก LAB = 🎯 → รูป → 💬 → ✅ → 👀 → ✔️ ครบ · ป้าย 🔍/✏️ ตรง LESSON-PLAN §2 (🔍 0 1 2 3 9 · ✏️ 4 5 6 7 8 10) | ไม่ต้องแก้ |
| 4 placeholder ผลจริง | 46 จุด `<!-- RESULT:LABn:… -->` ครบทุก LAB (summary + ตาราง + img) · ไม่พบตัวเลขแต่งนอกพรอมต์ (ตัวเลขที่มี เช่น "40 test" มาจาก PREP-LOG #7) | ไม่ต้องแก้ |
| 5 เฉลยรั่ว | grep `1,049` `1049` `orders.ts` `PP-231` `pricing.ts` `>=` `SummaryRows` `useAddToCart` `฿269/฿239/฿950` นอกบล็อกโค้ด = 0 (เจอแค่ ฿1,500 ในตารางคำตอบร้าน CR-01 = ข้อมูลโจทย์) · ฿999/฿1,049 อยู่เฉพาะในข้อความลูกค้าในพรอมต์ LAB 5 (ตามแบบ) · blockquote LAB 6/8/10 ใช้คำถามนำแทนชื่อไฟล์ใน 🧑 ของ PROMPTS | ไม่ต้องแก้ |
| 6 anchor | PART-A มีลิงก์ `#…` 29 จุด (ตารางเส้นทาง LAB 0–10 ฯลฯ) → resolve ครบ 0 broken · PART-B ไม่มีลิงก์ anchor ของตัวเอง | ไม่ต้องแก้ |
| 7 ข้อเท็จจริงจาก PREP-LOG | `pawpantry05` / `pawpantry05_default` ครบทุกจุด · 127.0.0.1 สำหรับ HAR และ "file node" ใน LAB 2 **ยังไม่มี** · แถว login `(redacted)` ยังไม่มี | ✅ แก้แล้ว |

## รายการที่พบ

| # | ที่ | พบอะไร | แก้แล้ว? |
|---|---|---|---|
| F1 | LAB 3 alt `concept-10` | ขึ้นต้น "ภาพ 3 ช่อง…" (STYLE §4.3 ห้ามขึ้นต้นด้วย "ภาพ") | ✅ → "การ์ตูน 3 ช่อง…" (เนื้อ alt เดิมตรงกับรูป ตรวจแล้ว) |
| F2 | LAB 8 alt `concept-22` | ขึ้นต้น "ภาพเล่าเรื่องซ้ายไปขวา…" | ✅ → "เล่าเรื่องจากซ้ายไปขวา…" |
| F3 | LAB 2 👀 | ไม่มีเรื่อง PREP-LOG §3.3: build นี้ REA ชนเพดานผลของ chunk ใหญ่ → node_kinds อาจขาด endpoint/storage แต่ `rea-summarize` รวม fact จาก file node มาให้ (คอลัมน์ "ที่มา" = `file node`) | ✅ เติมท้าย bullet "หาไม่เจอ ≠ ไม่มี" (ไม่เพิ่ม bullet ใหม่ · คง 5 bullet) + เติมคำแนะนำใน placeholder `LAB2:table-rea` ให้แยกบอกตัวที่มาจาก file node |
| F4 | LAB 3 👀 | ไม่มีเรื่อง HAR ใช้ `127.0.0.1:4000` (PREP-LOG §3.2 · BRIEF D7) | ✅ เติมท้าย bullet URL `petshop:3000` (บอกเหตุผล IPv6 `[::1]` และว่า `record-har.mjs` แปลงให้เอง) |
| F5 | LAB 3 👀 + placeholder | แถว `POST /api/auth/login` ใน `--md` จะเป็น `(redacted)` ทั้ง 2 คอลัมน์ (PREP-LOG §3.1) ผู้เรียนอาจเข้าใจว่า "ไม่มี body" | ✅ เติมใน bullet ⚠️ `.har` + placeholder `LAB3:table-api` (และให้จด base URL จาก `har-steps.json`) |
| F6 | ถ้าเจอปัญหา · แถว "4000 อยู่ในช่วงที่จอง" | `--base http://localhost:4100` (ใช้ได้เพราะสคริปต์แปลงเอง แต่ไม่ตรง D7 "HAR ใช้ 127.0.0.1") | ✅ → `--base http://127.0.0.1:4100` |
| F7 | ถ้าเจอปัญหา | ไม่มีแถวสำหรับ `HAR schema validation failed … serverIPAddress` (เกิดจริงตอน PREP · เสี่ยงเมื่อ agent บันทึก HAR เองด้วย `localhost` เช่น `out\bug01.har` ใน LAB 5) | ✅ เพิ่ม 1 แถว (พรอมต์สั่งเช็ก `[::1]` · บันทึกใหม่ด้วย 127.0.0.1 · ห้ามแก้ HAR ด้วยมือ · บอกสาเหตุก่อน) |
| F8 | ไฟล์ในบทนี้ · บรรทัด `rea/` | ขาด `package.json` (PREP-LOG #12 · LAB 0 สั่ง `npm install` ในโฟลเดอร์ rea) | ✅ เติม `package.json` |
| F9 | ถ้าเจอปัญหา | ตารางมี 16 แถว (เดิม 15 + F7) เกินแนว STYLE §1 แถว 9 "8–14 แถว" | ❌ ไม่แก้ · ทุกแถวเป็นปัญหาที่เกิดจริงหรือเสี่ยงจริงในบทนี้ · ผู้รวม README ตัดได้ถ้าต้องการ (ตัวเลือก: รวม "Firefox / WebKit เปิดไม่ขึ้น" เข้ากับ "test ล้มบางข้อ") |
| F10 | รูป concept ซ้ำระหว่าง PART-A กับ PART-B | `concept-09` `concept-10` (PART-A 🎓6 + PART-B LAB 2/3) · `concept-18` `concept-22` `concept-23` (PART-A + PART-B LAB 4/8/9) → README รวมจะมีรูปเดียวกัน 2 ครั้ง · LESSON-PLAN §8.1 กำหนด 18/22/23 ให้ LAB และ 09/10 ให้ 🎓6 | ❌ ไม่แก้ (อยู่นอกขอบเขต PART-B / ต้องตัดสินตอนรวม) · ข้อเสนอ: ลบ 18/22/23 ออกจาก PART-A · ตัดสินว่า 09/10 จะอยู่ 🎓6 หรือ LAB 2/3 ที่เดียว |
| F11 | PART-A `IMG-TODO` | PART-A ยังเขียนว่า `overview-5-phases` `when-rea` `evidence-4-buckets` `oracle-badges-e` `safe-change-loop` `lab-flow` "ยังไม่ได้สร้าง" แต่ไฟล์มีใน `img/` แล้วพร้อม alt ใน `IMAGES-NOTES.md` | ❌ ไม่แก้ (PART-A) · แจ้งผู้รวม · `safe-change-loop.png` (LESSON-PLAN ใช้ที่ LAB 5) PART-A จองที่ไว้แล้ว จึงไม่ใส่ซ้ำใน PART-B |
| F12 | ชื่อ GIF | `gif-bug-BUG-01.gif` `gif-TC-GIFT-02.gif` ไม่ตรงรูป `gif-bug-TC-<MOD>-NN` ของ STYLE §4.1 แต่ตรง LESSON-PLAN §8.3 | ไม่แก้ (ตาม LESSON-PLAN · BUG-01 ไม่ใช่ TC) |
| F13 | alt รูป concept อื่น | เทียบกับ `IMAGES-REVIEW-05.md` และเปิดดู concept-17 · 23: alt บรรยายครบรวมข้อความในภาพ (เช่น `app.py:120` `เดา?` `ส่งมอบได้`) · ไม่มี em dash นอกหัวรูป · ไม่มีจุดจบ | ไม่ต้องแก้ |
| F14 | PROMPTS LAB 2 🎯 | PREP-LOG §3.3 แนะนำให้เติมใน PROMPTS ว่า node_kinds อาจมี endpoint 7 ไม่มี storage · PROMPTS ยังไม่เติม (ไม่กระทบ README เพราะ 🎯 ไม่อยู่ใน README) | ❌ นอกขอบเขต · แจ้งเจ้าของ PROMPTS |

## ตรวจซ้ำหลังแก้

- บล็อกพรอมต์ 14/14 ยังตรง PROMPTS.md ทุกไบต์ (ไม่ได้แตะในบล็อก)
- anchor PART-A + PART-B: 29 ลิงก์ 0 broken
- ลิงก์รูป 12/12 มีไฟล์ · placeholder `RESULT:` 46 จุด
