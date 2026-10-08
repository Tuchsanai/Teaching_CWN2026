บทบาท: QA architect + prompt engineer
อ่าน BRIEF.md ในโฟลเดอร์นี้ README/TEST-PLAN/CLAUDE.md ของบท 02 และไฟล์ใน 02/e2e (playwright.config.ts, reporters/tester-report.ts, tests/fixtures.ts) แล้วเขียนไฟล์ yolo1-prompts.md (ไฟล์เดียว ห้ามแก้ไฟล์อื่น) ให้มี "ร่างพรอมต์" ภาษาไทยพร้อม copy สำหรับทุก LAB หลังได้ requirement แล้ว:
A. พรอมต์ LAB "ให้ Claude เขียน BUILD-PROMPT.md" (พรอมต์ที่สร้างพรอมต์): ต้องสั่งให้ BUILD-PROMPT ครอบคลุม Next.js (App Router, TypeScript) + PostgreSQL ด้วย docker compose 2 service, รูปจาก assets/, ดีไซน์ว้าว, rule-based AI, data-testid, /api/health, /api/test/reset, seed, BUG_MODE=1 ฝังบั๊ก 3 จุด (ระบุให้ Claude เลือกบั๊กที่ test ควรจับได้ เช่น ส่วนลดสมาชิกผิด, จองซ้อนได้, wallet ไม่ลดจำนวนครั้ง), healthcheck, Windows-friendly, และให้เขียน SPEC.md (testid + ข้อความ error) คู่กัน
B. พรอมต์ LAB สร้างเว็บ (วางเนื้อหา BUILD-PROMPT.md) — สั้นมาก
C. พรอมต์ LAB เดินดูเว็บด้วย Playwright MCP
D. พรอมต์ LAB สร้าง TEST-PLAN.md (โยง TC ↔ FR/BR, P1/P2/P3, ~30 test case, เทคนิค happy/negative/boundary/state/API, entry/exit criteria)
E. พรอมต์ LAB เขียน + รัน Playwright test 3 เบราว์เซอร์ (สร้างโปรเจกต์ e2e จากศูนย์ รวม reporter ที่ทำ GIF+MP4 ด้วย ffmpeg และ TEST-REPORT.md แบบ tester เหมือนบท 02) — แยกเป็น 2 พรอมต์ถ้ายาวเกิน
F. พรอมต์ LAB จับบั๊ก BUG_MODE=1 และพรอมต์เขียน test ใหม่จากภาษาคน
G. ตาราง "ถ้าเจอปัญหา คัดลอกพรอมต์นี้" 6–8 ข้อ
H. ความเสี่ยงที่ "from scratch" จะพังบน Windows (เช่น port ชน, Postgres ยังไม่พร้อม, ffmpeg ไม่มี, test flaky เพราะเวลา/วันที่, เบราว์เซอร์ WebKit) และวิธีเขียนพรอมต์ป้องกัน
หลักการพรอมต์: สั้น, เป็นขั้น, "ทำไม่ได้ให้หยุดแล้วบอก", "ห้ามแก้ test ให้ผ่าน", ขอผลเป็นตาราง เขียนกระชับ ไม่เกิน ~400 บรรทัด
