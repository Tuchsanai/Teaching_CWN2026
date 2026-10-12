# LAB 1 RESULT · รับมอบระบบ (บท 06 สบายใจ สปา)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 09:35:30 |
| เวลาจบ (งานตามพรอมต์) | 09:44:06 · เขียน result เสร็จ ~09:50 |
| เวลาที่ใช้ | ~9 นาที ตามพรอมต์ (อ่านบันทึก 1 นาที + เปิดระบบ 15 วิ + check-rules 20 วิ + e2e-legacy 4.1 นาที + อ่านเทสต์/จำแนก/เขียน HANDOVER-CHECK ~3 นาที) · รวมเขียน result ~15 นาที |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `HANDOVER-CHECK.md` · แก้ `.git/info/exclude` (+10 บรรทัด) · สร้าง `e2e-legacy/node_modules/` `e2e-legacy/test-report/` (ignored) · git commit `4a7908f` |
| สคริปต์ชั่วคราว | `tools/lab1/shot-admin.cjs` · `tools/lab1/shot-admin-1012.cjs` (ถ่ายภาพหลังร้าน) |
| log | `design/logs/lab1-web-build.txt` `lab1-check-rules.txt` `lab1-npm-install.txt` `lab1-pw-install.txt` `lab1-e2e-legacy.txt` |
| สถานะเว็บตอนจบ | `sabai06-web` + `sabai06-db` เปิดค้าง healthy · `/api/health` → `{"ok":true,"db":true}` |
| ข้อมูลทดสอบ | reset ครั้งสุดท้าย now = `2026-10-10T10:00:00+07:00` (ค่าเริ่ม) · ระหว่างถ่ายภาพเคย reset เป็น 12 ต.ค. แล้วคืนค่าเริ่มแล้ว |
| พอร์ตที่ใช้จริง | เว็บ **4100**→3000 · db **5533**→5432 (D10) · ผู้เรียนเห็น **4000 / 5433** → เวลาเขียน README แปลง `localhost:4100` → `localhost:4000`, `5533` → `5433` |
| เซสชัน / โหมดสิทธิ์ | runner (Agent tool) ทำแทนเซสชันใหม่ของผู้เรียน · โหมด A · เครื่องมือ PowerShell สำหรับคำสั่งในพรอมต์ · ไม่ได้เปิด `claude -p`/`yolo.cmd` (LAB นี้ไม่ต้องทดสอบรั้ว) · ยังไม่มี `w/CLAUDE.md` และ `w/.claude/settings.json` (สร้างใน LAB 4) จึงบังคับเฉพาะข้อห้ามในพรอมต์เอง |

## 2. ข้อห้ามที่ทำตาม และจุดที่ทำต่างจากพรอมต์

- ไม่แก้ไฟล์ใน `web/` `db/` `e2e-legacy/` (ยืนยัน: `git status --short` หลัง commit เหลือแค่ ` M HANDOVER-CHECK.md`) · ไม่เปิด `_solution/` (ไม่มีใน w/) และ `CHANGE-REQUESTS/answers/` · ไม่แก้เทสต์
- **พอร์ต:** `$env:WEB_PORT="4100"; $env:DB_PORT="5533"` ก่อน `docker compose up` ทั้ง 2 ไฟล์ · `$env:BASE_URL="http://localhost:4100"` ก่อน check-rules และ playwright · แทน `http://localhost:4000/api/...` ด้วย `:4100` ในการตรวจ health/reset · ไม่แตะ `pawpantry05` (4000) และ `exref-*`
- **git:** ใช้ git จริงตาม D11 (w/ เป็น repo ที่ orchestrator init + commit `d617d68` ไว้แล้ว · พรอมต์สั่ง commit เอง) · ไม่ใช้ snapshot ตาราง RUNNER §4
  - `git rev-parse --show-toplevel` = `C:/t/work/b2run/w` (โฟลเดอร์นี้เอง) → ไม่เข้าเงื่อนไข "ชี้ไปโฟลเดอร์อื่น" และไม่เข้า "ยังไม่เป็น repo" → ไม่ `git init` · ยังเพิ่ม 10 บรรทัดใน `.git/info/exclude` (ดูข้อ 6)
  - `git add -A` + `git commit -m "baseline: ระบบที่รับมอบ"` → `4a7908f` · 1 ไฟล์ (`HANDOVER-CHECK.md`) เพราะไฟล์ระบบถูก commit ไปแล้วใน `d617d68` · tracked รวม 212 ไฟล์
- build: พรอมต์ให้รันแบบ background/timeout ยาว → ใช้ timeout 10 นาที แต่เสร็จใน 8.1 วิ เพราะ layer CACHED ทั้งหมด

## 3. คำตอบสรุปที่แสดงในแชท

> | ชุดตรวจ | ผ่าน | ล้ม | คาดว่าล้ม | เวลา |
> |---|---|---|---|---|
> | check-rules (ชั้น 1) `node web/scripts/check-rules.mjs` | 90 | 0 | 0 | 19.8 วิ |
> | e2e-legacy api + chromium (ชั้น 2) `npx playwright test --reporter=list` | 38 | 1 (TC-SEC-05) | 3 (TC-SEC-04 · TC-GC-04 · TC-TRN-03) | 4.1 นาที |
>
> - บรรทัดสรุปของ Playwright คือ `1 failed` · `41 passed (4.1m)` → 41 รวม expected-fail 3 ข้อ ผ่านจริง 38
> - ข้อที่ล้ม/ติด test.fail: TC-SEC-05 = เทสต์ล้าสมัย (ระบบปฏิเสธด้วย 422 COURSE_UNAVAILABLE ไม่ใช่ 403/404) · TC-SEC-04 = บั๊ก (logout แล้ว cookie เดิมยังได้ 200) · TC-GC-04 = บั๊ก (รหัสบัตรมั่วไม่มีข้อความเตือน) · TC-TRN-03 = บั๊ก (ติ๊กรถแต่ไม่ใส่ระยะ/โรงแรมยังไปขั้น 4 ได้)
> - คำอ้าง 19 ข้อ (H1–H12 บันทึกส่งมอบ · H13–H19 README-LEGACY): ✅ 12 · ❌ 2 (H6 reset ปิดใน production → ค่าที่ส่งมอบเปิดอยู่ ตอบ 200 · H9 ผ่านหมดยกเว้น 3 → TC-SEC-05 ล้มเพิ่ม และ README-LEGACY เองก็บอกว่าแดงค้าง) · ⚠️ 5 (H2 SPEC ตรงทุกข้อ · H7 ซ่อนบัญชีทดสอบ · H10 จองพร้อมกัน · H12 แชทบอท · H16 test:all 3 เบราว์เซอร์)
> - เวอร์ชัน: Next.js 15.5.27 · PostgreSQL 16.15 · Node ใน container v22.23.3 · Playwright 1.63.0
> - เปิดระบบ: network 0.2 วิ + db 6.3 วิ + web 8.1 วิ (cached) · health `{"ok":true,"db":true}` · reset 200 now 2026-10-10 10:00
> - baseline: `4a7908f baseline: ระบบที่รับมอบ` (1 ไฟล์ · repo มี commit ตั้งต้น `d617d68` อยู่แล้ว · tracked 212 ไฟล์)

รายละเอียดเต็มอยู่ใน `w/HANDOVER-CHECK.md` (9 หัวข้อ · ตารางข้อที่ล้ม 4 แถว · ตารางคำอ้าง 19 แถว)

## 4. ตัวเลขสำคัญ (คำสั่งที่ใช้นับ)

| ตัวเลข | ค่า | คำสั่ง/แหล่ง |
|---|---|---|
| check-rules | 90/90 · 19.8 วิ · exit 0 | `node web/scripts/check-rules.mjs` บรรทัดท้าย `ผ่าน 90 / 90 ข้อ` |
| e2e-legacy รายการทั้งหมด | 42 (api 6 · chromium 36) | `Running 42 tests using 1 worker` |
| e2e-legacy ผ่านจริง | 38 (api 4 · chromium 34) | บรรทัด `ok` ใน `lab1-e2e-legacy.txt` |
| e2e-legacy expected-fail | 3 (TC-SEC-04 api · TC-GC-04 · TC-TRN-03 chromium) | บรรทัด `x` + `grep -rn "test.fail" e2e-legacy/tests` = 3 |
| e2e-legacy failed | 1 (TC-SEC-05 api) | `1 failed` |
| e2e-legacy flaky | 0 | retries 0 |
| e2e-legacy เวลา | 4.1 นาที (คำสั่งรวม 248.1 วิ) | บรรทัดสรุป |
| npm install / playwright install | 2.4 วิ (5 แพ็กเกจ) / 1.4 วิ (เบราว์เซอร์มีในเครื่องแล้ว) | `Measure` ใน PowerShell |
| เปิดระบบ | network 0.2 วิ · db 6.3 วิ · web 8.1 วิ (13 step `CACHED`) | `lab1-web-build.txt` |
| เวอร์ชัน | Next 15.5.27 · PG 16.15 · Node (container) v22.23.3 · Playwright 1.63.0 | package.json / `SELECT version()` / `node -v` |
| ตาราง DB | 19 ตาราง · `room` 1 แถว (Couple Suite cap 2) | `\dt` · `select * from room` |
| คำอ้าง | 19 ข้อ · ✅ 12 ❌ 2 ⚠️ 5 | ตารางใน HANDOVER-CHECK.md |
| git | `4a7908f` · 1 ไฟล์ · tracked 212 | `git show --stat` · `git ls-files \| wc -l` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

| รหัส | แถว |
|---|---|
| TC-SEC-05 | U04 จองคอร์สด้วย C01 ของ U01 → ได้ 422 `COURSE_UNAVAILABLE` "ใช้คอร์สนี้ไม่ได้ (เหลือ 0 ครั้งหรือหมดอายุ)" ไม่ใช่ 403/404 · ระบบไม่สร้างนัด คอร์สยังเหลือ 7 จาก 11 → **เทสต์ล้าสมัย** |
| TC-SEC-04 | logout → 200 แต่ cookie เดิม `GET /api/me` → 200 ข้อมูลคุณนิดา → **บั๊ก** (session ไม่ถูกเพิกถอน) · บันทึกส่งมอบเรียกว่า "ไม่กระทบการใช้งาน" |
| TC-GC-04 | รหัส `XXXX` → API โยน 422 `GC_NOT_FOUND` (`booking.ts:168`) แต่หน้าจองแสดงเตือนจาก `quote.giftCardError` (ตั้งเฉพาะ EXPIRED/EMPTY) → ไม่มี `book-giftcard-error` → **บั๊ก** |
| TC-TRN-03 | ติ๊กรถรับส่ง ไม่ใส่ระยะ/โรงแรม กด "ถัดไป" → ไป `data-step="4"` → **บั๊ก** |
| H6 | "ในการใช้งานจริงปิด reset แล้ว (`ALLOW_TEST_RESET=0`)" ↔ `web/compose.yaml` `${ALLOW_TEST_RESET:-1}` + `config.ts` ค่าเริ่ม "1" + reset ตอบ 200 → ❌ |
| H9 | "ผ่านทั้งหมดยกเว้น 3 KNOWN-ISSUE" ↔ TC-SEC-05 ล้มเพิ่ม · README-LEGACY เขียนเองว่า "TC-SEC-05 แดงค้าง ยังไม่ได้ดู" → ❌ เอกสาร 2 ฉบับขัดกัน |

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| ข้อ 7: repo มีอยู่แล้วและ toplevel = โฟลเดอร์นี้ (ไม่เข้าเงื่อนไขไหนในพรอมต์) | ไม่ `git init` · ไม่หยุดถาม · ไปต่อ `git add -A` + commit | เงื่อนไข "หยุดแล้วบอกผมก่อน" ใช้เฉพาะเมื่อชี้ไปโฟลเดอร์**อื่น** · โฟลเดอร์นี้เป็น repo ของบทเอง (D11) ปลอดภัย |
| ข้อ 7: เพิ่มบรรทัด exclude ไหม ทั้งที่พรอมต์ผูกไว้กับกรณี init | เพิ่ม 10 บรรทัด | ไม่มีผลเสีย และกัน `rea-out/` `backups/` `playwright-report/` ที่ LAB ถัดไปสร้างไม่ให้หลุดเข้า commit · `img/` `EXAM.md` track ไปแล้วจึงไม่มีผล (จดใน HANDOVER-CHECK) |
| ลำดับ commit กับ HANDOVER-CHECK.md | เขียน HANDOVER-CHECK ก่อน → commit (จึงมี 1 ไฟล์ใน commit) → เติมหัวข้อ 8 (commit id) ทีหลัง ทิ้งเป็น modified | tree สะอาดอยู่แล้ว ถ้า commit ก่อนเขียนจะได้ "nothing to commit" · commit id ใส่ในไฟล์ที่ commit ไปแล้วไม่ได้ |
| แยกคำอ้างจาก README-LEGACY ด้วยไหม | ใช่ ต่อเลขเป็น H13–H19 | พรอมต์ข้อ 0 บอกว่า README-LEGACY "เป็นคำอ้างของผู้รับเหมาเหมือนกัน" |
| H10 (จองพร้อมกัน) ให้ ✅ จาก TC-BOOK-06 ไหม | ⚠️ | TC ยิงแค่ 2 คำขอ 1 รอบ ไม่พอรับรอง "หลายคน" · ระบุวิธีตรวจต่อ |
| TC-SEC-05 จำแนก | เทสต์ล้าสมัย (+ หมายเหตุข้อความชวนเข้าใจผิด) | ทุกขั้นที่ตรวจผลกระทบผ่าน (ไม่มีนัดใหม่ คอร์สไม่ลด B05 ไม่ถูกยกเลิก) · โค้ด query กรอง `customer_id` ของผู้ล็อกอิน |

## 7. ข้อสังเกต 👀

- พรอมต์สั่ง `npx playwright test --reporter=list` → **แทนที่** reporter ใน config ทั้งชุด จึงไม่มี `test-report/html` · README-LEGACY บอก `npm run report` ไว้ ผู้เรียนที่ลองเปิดรายงานจะเจอ error (log รายข้อใน `test-report/logs/` ยังมี)
- สัญลักษณ์ใน list reporter: expected-fail กับ failed แสดงเป็น `x` เหมือนกัน (ข้อ 5, 6, 25, 40) · ต้องเทียบกับ `test.fail` ในไฟล์เทสต์ หรือดูรายการ `1 failed` ท้ายผล จึงแยกได้ — AI ที่นับ `x` ตรง ๆ จะได้ "ล้ม 4" ผิด
- build "ครั้งแรก" บนเครื่องนี้ไม่ใช่ครั้งแรกจริง (image `sabai06-web:latest` จาก PREP อยู่แล้ว 28 นาที) → 8.1 วิ ไม่ใช่เวลาที่ผู้เรียนจะเห็น (ใช้ตัวเลขจาก PREP/A2 แทน)
- `npx playwright install` 1.4 วิ เพราะเบราว์เซอร์ 1.63.0 มีในแคชเครื่องแล้ว (บท 04/05) · เครื่องผู้เรียนใหม่จะดาวน์โหลดหลายร้อย MB
- PowerShell 5.1 แสดง `npm notice` เป็น `NativeCommandError` สีแดงเมื่อ redirect `*>` — ไม่ใช่ error จริง (exit 0) · AI อาจตีความว่าติดตั้งล้ม
- หน้า `/admin` เปิดมาเป็นคิว **พรุ่งนี้** (`initialDate = addDays(today, 1)` ใน `web/app/admin/page.tsx`) · ถ่าย "/admin 12 ต.ค." ต้องระบุว่าหมายถึงวันระบบหรือวันในตัวเลือก (ดูข้อ 11)
- SPEC.md อ้าง REQUIREMENTS.md / DESIGN.md / TEST-DATA.md ที่ไม่ได้ส่งมอบ — สมจริงแบบ legacy

## 8. เจอระหว่างทาง (นอก CR)

- TC-SEC-04: logout ไม่เพิกถอน session (cookie เดิมยังเรียก `/api/me` ได้ 200) — ช่องโหว่ความปลอดภัยที่ผู้รับเหมาติดป้าย KNOWN-ISSUE ว่า "ไม่กระทบการใช้งาน"
- TC-GC-04: รหัส Gift Card ที่ไม่มีจริง → `/api/price` 422 `GC_NOT_FOUND` แต่ UI ไม่แสดงข้อความ (กล่องเตือนอ่านจาก `quote.giftCardError` เท่านั้น)
- TC-TRN-03: ไม่บังคับกรอกระยะทาง/โรงแรมเมื่อติ๊กรถรับส่ง
- TC-SEC-05 (ข้างเคียง): ใช้คอร์สของคนอื่นได้ข้อความ "เหลือ 0 ครั้งหรือหมดอายุ" ซึ่งไม่จริงสำหรับผู้ใช้คนนั้น (ควรเป็น "ไม่พบคอร์ส") — ไม่ใช่ช่องโหว่
- `ALLOW_TEST_RESET` ค่าเริ่ม = 1 ทั้งใน compose และ `web/lib/config.ts` → ถ้าขึ้นระบบจริงด้วยไฟล์ชุดนี้ `/api/test/reset` เปิด + หน้า `/login` โชว์รหัสผ่านบัญชีทดสอบ + ปุ่ม "รีเซ็ตข้อมูลทดสอบ" ในหลังร้าน

## 9. ปัญหาที่เจอ / วิธีแก้

- 4000 ถูก `pawpantry05` ใช้ (คาดไว้ตาม D10) → ใช้ 4100/5533 ผ่าน env ไม่มีปัญหาอื่น · compose รองรับ `${WEB_PORT}` `${DB_PORT}` อยู่แล้ว
- ข้อ 7 เจอ "nothing to commit" ได้ถ้า commit ก่อนเขียน HANDOVER-CHECK.md (tree สะอาดเพราะ orchestrator commit ตั้งต้นไว้) → เขียนไฟล์ก่อนแล้วจึง commit
- ตอนอ่านหัวข้อ LAB 1 ใน PROMPTS.md ช่วงบรรทัดที่อ่านติด "ผลที่คาด" มาด้วยก่อนเริ่มรัน (ผิด RUNNER §2 เล็กน้อย เหมือน LAB 0) · ตัวเลขทุกตัวมาจากคำสั่งจริง ไม่ได้ปรับตามผลที่คาด · การจำแนก/การนับ H ทำตามหลักฐานของตัวเอง (เลข H ต่างจากผลที่คาดเพราะแยกคำอ้างละเอียดกว่า)

## 10. ข้อเสนอแก้พรอมต์

- **ข้อ 7 (สำคัญ):** เพิ่มกรณีที่ 3 "ถ้าเป็น repo อยู่แล้วและ toplevel = โฟลเดอร์นี้ ให้ข้าม init แต่ยังเพิ่มบรรทัด exclude · ถ้า `git status` สะอาด ให้ใช้ commit ล่าสุดเป็น baseline (บอก id) หรือ commit HANDOVER-CHECK.md เป็น baseline" · และบอกลำดับ "เขียน HANDOVER-CHECK.md ก่อน commit แล้วจด commit id ในแชท/ไฟล์ทีหลัง" เพื่อไม่ให้ AI งงเรื่อง id ในไฟล์ที่ commit ไปแล้ว
- **ข้อ 4:** ตัด `--reporter=list` ออก (config มี `list` อยู่แล้ว) หรือใช้ `--reporter=list,html` เพื่อให้ `npm run report` ใน README-LEGACY ใช้ได้ · เพิ่ม "ข้อที่แสดง `x` อาจเป็นคาดว่าล้ม ให้เทียบกับ `test.fail` ในไฟล์"
- **ข้อ 0:** บอกให้ใช้เลข H ต่อเนื่องสำหรับ README-LEGACY (หรือแยก L1…) เพื่อให้ตารางคำอ้างของผู้เรียนเทียบกับ README ได้ (ผลที่คาดใช้ H1–H6 แต่บันทึกส่งมอบแตกได้ ≥12 ข้อ)
- **ข้อ 1:** หมายเหตุว่า "ถ้า build เสร็จเร็วมาก (CACHED) แปลว่าเคย build แล้ว" ไม่ใช่ปัญหา
- (ทางเลือก) ข้อ 2: ระบุว่าถ้าพอร์ตไม่ใช่ 4000 ให้ตั้ง `$env:WEB_PORT` / `$env:BASE_URL` (อยู่ใน compose และ check-rules อยู่แล้ว แต่พรอมต์ไม่บอก)

## 11. ภาพที่ควรใช้

- `design/shots/site-admin-queue.png` — `/admin` หลัง reset now = 12 ต.ค. 2026 10:00 ล็อกอินเจ้าของร้าน · headless 1280×800 · ค่าเริ่มของหน้าแสดงคิว **13/10/2026** (พรุ่งนี้): B03 คุณสมชาย นวดไทย 90 นาที T06 พี่ดวงใจ ฿1,400 ยืนยัน
- `design/shots/site-admin-queue-date1012.png` — เหมือนกันแต่ `?date=2026-10-12`: B01 คุณฝน นวดไทย 60 นาที T03 พี่บุญมี ฿1,000 ยืนยัน (ใช้ภาพนี้ถ้า IMAGES หมายถึงคิววันที่ 12)

### เทียบกับผลที่คาด

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| มี `HANDOVER-CHECK.md` | มี (9 หัวข้อ) | ✅ |
| check-rules 90/90 ~20 วิ (รันจากราก) | 90/90 · 19.8 วิ · รันจากราก `node web/scripts/check-rules.mjs` | ✅ |
| e2e-legacy 42 รายการ (api 6 + chromium 36) | 42 (6 + 36) | ✅ |
| บรรทัดสรุป "41 passed · 1 failed" | `41 passed (4.1m)` · `1 failed` | ✅ |
| expected-fail 3 (TC-TRN-03 TC-GC-04 TC-SEC-04) → ผ่านจริง 38 | 3 ข้อเดียวกัน · ผ่านจริง 38 | ✅ |
| ล้ม 1 (TC-SEC-05) | TC-SEC-05 | ✅ |
| TC-SEC-05 จำแนก = เทสต์ล้าสมัย (ปฏิเสธแล้ว แค่ 422) | เทสต์ล้าสมัย · 422 COURSE_UNAVAILABLE | ✅ |
| build ~42 วิ (ครั้งแรกนานกว่า) | 8.1 วิ (CACHED จาก PREP) | ⚠️ วัดไม่ได้ในรอบนี้ |
| H1 ✅ | H1 (stack/ไฟล์) ✅ | ✅ (เลข H ต่างกัน ดูหมายเหตุ) |
| H2 ❌ (เอกสารขัดกันเอง TC-SEC-05) | ประเด็นเดียวกัน = **H9** ❌ | ✅ เนื้อหาตรง เลขต่าง |
| H3 ⚠️ (ตรวจได้เมื่ออ่านโค้ด) | ไม่แน่ใจว่าตรงกับข้อไหน · ⚠️ ที่ต้องอ่านโค้ด = H2 (SPEC) และ H10 (จองพร้อมกัน) | ⚠️ ตรงเชิงสาระ |
| H4 ❌ (reset ตอบ 200) | **H6** ❌ (compose/config ค่าเริ่ม 1 · reset 200) | ✅ เนื้อหาตรง เลขต่าง |
| H5 ⚠️ · H6 ⚠️ | ⚠️ อีก 3 ข้อ: H7 (ซ่อนบัญชีทดสอบ) H12 (แชทบอท) H16 (test:all) | ✅ เชิงสาระ |
| commit baseline 1 ตัว | `4a7908f` 1 ตัว (1 ไฟล์ เพราะ repo มี commit ตั้งต้นแล้ว) | ✅ |
| ไปต่อได้: health db:true · ตัวเลข 2 ชั้น · TC-SEC-05 จำแนก · มี commit baseline | ครบ | ✅ |

หมายเหตุเลข H: ผลที่คาดแตกบันทึกส่งมอบเป็น 6 ข้อ · รอบนี้แตกเป็น 12 ข้อ (+7 จาก README-LEGACY) จึงเลขไม่ตรงกัน แต่ ❌ ทั้ง 2 ข้อ (reset เปิดอยู่ · TC-SEC-05/เอกสารขัดกัน) ตรงกับผลที่คาด · README ควรอ้างคำอ้างด้วยเนื้อหา ไม่ใช่เลข H หรือพรอมต์ควรกำหนดวิธีแตกข้อ
