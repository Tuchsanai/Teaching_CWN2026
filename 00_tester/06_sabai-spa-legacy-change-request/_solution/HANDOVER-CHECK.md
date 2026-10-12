# HANDOVER-CHECK · ตรวจรับมอบระบบ "สบายใจ สปา"

วันที่ตรวจ 12 ต.ค. 2026 · ทุกตัวเลขมาจากคำสั่งที่รันจริงใน PowerShell จากโฟลเดอร์บท · ไม่ได้แก้ไฟล์ใน `web/` `db/` `e2e-legacy/` · ไม่ได้เปิด `_solution/` และ `CHANGE-REQUESTS/answers/`

## 1. เวอร์ชัน

| ส่วน | เวอร์ชัน | ที่มา |
|---|---|---|
| Next.js | 15.5.27 (React 19.1.1 · pg 8.16.3) | `web/package.json` |
| PostgreSQL | 16.15 on x86_64-pc-linux-musl (Alpine) | `docker exec sabai06-db psql -U sabai -d sabai -tAc "SELECT version()"` |
| Node ใน container เว็บ | v22.23.3 | `docker exec sabai06-web node -v` |
| Playwright (e2e-legacy) | 1.63.0 | `e2e-legacy/node_modules/@playwright/test/package.json` |
| เอกสาร `web/SPEC.md` | ฉบับ 1.0 · ก.ย. 2569 (439 บรรทัด) | หัวไฟล์ |

## 2. container และพอร์ต

| container | image | พอร์ต host → container | สถานะ |
|---|---|---|---|
| `sabai06-web` | `sabai06-web:latest` | **4100** → 3000 | healthy |
| `sabai06-db` | `postgres:16-alpine` | **5533** → 5432 | healthy |

- network `sabai06-net` (external · สร้างด้วย `docker network create sabai06-net`) · volume `sabai06-pgdata`
- ค่าเริ่มใน compose คือ `${WEB_PORT:-4000}` และ `${DB_PORT:-5433}` · เครื่องนี้ 4000 มีงานอื่นใช้อยู่ จึงตั้ง `$env:WEB_PORT="4100"` `$env:DB_PORT="5533"` ก่อน `docker compose up` และ `$env:BASE_URL="http://localhost:4100"` ก่อนรันชุดตรวจ (เครื่องทั่วไปใช้ 4000/5433 ตามบันทึกส่งมอบ)

## 3. เวลาเปิดระบบ

| ขั้น | เวลา |
|---|---|
| `docker network create sabai06-net` | 0.2 วิ |
| `docker compose -f db/compose.yaml up -d --wait` (สร้าง volume ใหม่ + init schema/seed) | 6.3 วิ |
| `docker compose -f web/compose.yaml up -d --build --wait` | 8.1 วิ (ทุก layer `CACHED` เพราะ image เคย build บนเครื่องนี้แล้ว · build ครั้งแรกจริงจะนานกว่านี้มาก) |
| รวม | ~15 วิ |

ตรวจหลังเปิด
- `GET /api/health` → `{"ok":true,"db":true}` ✅
- `POST /api/test/reset` → **200** `{"ok":true,"now":"2026-10-10T10:00:00+07:00"}` (นาฬิการะบบถูกล็อกเป็น 10 ต.ค. 2026 10:00)

## 4. ผลชุดตรวจที่ส่งมอบ 2 ชั้น

| ชุดตรวจ | ผ่าน | ล้ม | คาดว่าล้ม | เวลา |
|---|---|---|---|---|
| ชั้น 1 `node web/scripts/check-rules.mjs` | 90 / 90 | 0 | 0 | 19.8 วิ |
| ชั้น 2 `npx playwright test --reporter=list` (api + chromium · 42 รายการ = api 6 + chromium 36) | **38** (ผ่านจริง) | **1** (TC-SEC-05) | **3** (TC-SEC-04 · TC-GC-04 · TC-TRN-03) | 4.1 นาที (248 วิ รวมเปิด npx) |

- บรรทัดสรุปของ Playwright คือ `41 passed (4.1m)` · `1 failed` → ใน 41 นั้นมี 3 ข้อที่ติด `test.fail(true, 'KNOWN-ISSUE: …')` ซึ่ง "ล้มตามที่คาด" จึงถูกนับเป็น passed · ผ่านจริง = 41 − 3 = 38
- แยก project: api 6 ข้อ = ผ่านจริง 4 (TC-BOOK-06 TC-SEC-01 TC-SEC-02 TC-SEC-03) · คาดว่าล้ม 1 (TC-SEC-04) · ล้ม 1 (TC-SEC-05) · chromium 36 ข้อ = ผ่านจริง 34 · คาดว่าล้ม 2 (TC-GC-04 TC-TRN-03) · ล้ม 0
- `npm install` 2.4 วิ (5 แพ็กเกจ) · `npx playwright install chromium firefox webkit` 1.4 วิ (มีเบราว์เซอร์ในเครื่องแล้ว)
- หมายเหตุ: `--reporter=list` แทนที่ reporter ใน config ทั้งหมด จึงไม่มีรายงาน html (`test-report/html`) รอบนี้ · log API รายข้ออยู่ที่ `e2e-legacy/test-report/logs/`

## 5. ตารางข้อที่ล้มหรือติด test.fail

| TC | ผล | สิ่งที่เทสต์คาด | สิ่งที่ระบบทำจริง (หลักฐาน) | จำแนก |
|---|---|---|---|---|
| TC-SEC-05 (api) | ❌ ล้ม | U04 จองแบบคอร์สด้วย `coursePurchaseId` ของ U01 → 403/404 | ได้ **422** `COURSE_UNAVAILABLE` "ใช้คอร์สนี้ไม่ได้ (เหลือ 0 ครั้งหรือหมดอายุ)" (`test-report/logs/TC-SEC-05.log`) · ขั้นอื่นผ่าน: ยกเลิก B05 ของคนอื่น → 403 · B05 ยัง confirmed · คอร์ส C01 ยัง "เหลือ 7 จาก 11 ครั้ง" · 20 ต.ค. 11:00 ไม่มีนัดใหม่ · โค้ด `web/lib/server/booking.ts:120-133` หา `course_purchase WHERE customer_id = <ผู้ล็อกอิน> AND id = $2` ไม่เจอจึงตอบ 422 | **เทสต์ล้าสมัย** (ระบบปฏิเสธจริงและไม่มีข้อมูลรั่ว แค่ status เป็น 422 ไม่ใช่ 403/404) · ข้อสังเกต: ข้อความ "เหลือ 0 ครั้ง" ชวนเข้าใจผิดเมื่อคอร์สเป็นของคนอื่น |
| TC-SEC-04 (api) | ⚠️ คาดว่าล้ม (ล้มจริง) | logout แล้วใช้ cookie เดิม `GET /api/me` → 401 | logout ตอบ 200 แต่ cookie เดิมยังได้ **200** พร้อมข้อมูลคุณนิดา (`test-report/logs/TC-SEC-04.log`) | **บั๊กของระบบ** (session ไม่ถูกเพิกถอน · ความปลอดภัย) |
| TC-GC-04 (chromium) | ⚠️ คาดว่าล้ม (ล้มจริง) | ใส่รหัสบัตร `XXXX` แล้วกด "ใช้บัตรนี้" → มี `book-giftcard-error` | ไม่มี element `book-giftcard-error` (error-context.md) · ใบสรุปไม่มีบรรทัด Gift Card และยอด ฿1,000 (ขั้นนี้ผ่าน) · โค้ด: รหัสที่ไม่มีจริง API โยน 422 `GC_NOT_FOUND` (`booking.ts:168`) แต่หน้าจอแสดงกล่องเตือนจาก `quote.giftCardError` เท่านั้น (`BookingWizard.tsx:512`) ซึ่งตั้งแค่ `GC_EXPIRED`/`GC_EMPTY` | **บั๊กของระบบ** (ผู้ใช้ไม่รู้ว่ารหัสบัตรใช้ไม่ได้) |
| TC-TRN-03 (chromium) | ⚠️ คาดว่าล้ม (ล้มจริง) | ติ๊กรถรับส่งแต่ไม่ใส่ระยะ/โรงแรม กด "ถัดไป" → ต้องอยู่ขั้น 3 และมีข้อความเตือน | ไปถึงขั้น 4 (`data-step="4"` · มี `book-summary`) และไม่มีข้อความเรื่องระยะ/โรงแรม (error-context.md) | **บั๊กของระบบ** (ไม่บังคับกรอกข้อมูลรถรับส่ง) |

## 6. คำอ้างของผู้รับเหมา vs ผลจริง

H1–H12 จาก `CHANGE-REQUESTS/00-HANDOVER-MEMO.md` · H13–H19 จาก `e2e-legacy/README-LEGACY.md`

| # | คำอ้าง | ผลจริง | สถานะ |
|---|---|---|---|
| H1 | ส่งมอบเว็บ Next.js + TypeScript · DB PostgreSQL 16 · `db/init/01-schema.sql` `02-seed.sql` | Next.js 15.5.27 · PostgreSQL 16.15 · มีไฟล์ init ทั้ง 2 | ✅ |
| H2 | `web/SPEC.md` ฉบับ 1.0 เป็นปัจจุบัน ตรงกับระบบทุกข้อ | ยังไม่ได้เทียบ · SPEC อ้าง REQUIREMENTS.md / DESIGN.md / TEST-DATA.md ที่ไม่ได้ส่งมอบมา | ⚠️ ตรวจได้โดยเทียบ SPEC ทีละหัวข้อกับโค้ด + พฤติกรรมจริง (สำรวจ black-box ด้วย REA และให้ Agent อ่าน repo + DB) |
| H3 | ชุดตรวจกฎร้าน 90 เคส | 90 ข้อ (E01–E90) | ✅ |
| H4 | ชุดทดสอบหน้าเว็บ Playwright 42 เคส | 42 รายการ (api 6 + chromium 36) | ✅ |
| H5 | เปิดระบบด้วย 3 คำสั่ง → เว็บ :4000 · DB :5433 | 3 คำสั่งเปิดได้ healthy ใน ~15 วิ · ค่าเริ่ม compose = 4000/5433 (เครื่องนี้ใช้ 4100/5533 ผ่าน env เพราะ 4000 ไม่ว่าง) | ✅ |
| H6 | `POST /api/test/reset` ในการใช้งานจริงปิดไว้แล้ว (`ALLOW_TEST_RESET=0`) | ค่าที่ส่งมอบ **เปิดอยู่**: `web/compose.yaml` `ALLOW_TEST_RESET: ${ALLOW_TEST_RESET:-1}` และ `web/lib/config.ts` ค่าเริ่ม `"1"` · reset ตอบ **200** | ❌ (ไม่มีไฟล์ไหนตั้ง 0 · ถ้าขึ้นจริงด้วยไฟล์ชุดนี้ ใครก็ล้างข้อมูลได้) |
| H7 | บัญชีทดสอบแสดงที่หน้าเข้าสู่ระบบเฉพาะโหมดทดสอบ | โหมดทดสอบ (`ALLOW_TEST_RESET=1`) หน้า `/login` แสดงรหัสผ่านบัญชีทดสอบ (`Nida@2026` `Owner@2026`) · `config.ts` บอกว่า flag เดียวกันคุมการแสดง | ⚠️ ต้องเปิดเว็บด้วย `ALLOW_TEST_RESET=0` แล้วเปิด `/login` ดูว่าซ่อนจริง |
| H8 | ชุดตรวจกฎร้านผ่าน 90/90 | 90/90 · 19.8 วิ | ✅ |
| H9 | ชุดทดสอบหน้าเว็บผ่านทั้งหมด ยกเว้น 3 เคส KNOWN-ISSUE | ล้มเพิ่ม 1 ข้อ **TC-SEC-05** (นอก 3 ข้อ KNOWN-ISSUE) · README-LEGACY ของผู้รับเหมาเองก็เขียนว่า "TC-SEC-05 แดงค้าง" = เอกสาร 2 ฉบับขัดกันเอง | ❌ |
| H10 | รองรับการจองพร้อมกันหลายคน ไม่มีการจองซ้อน | TC-BOOK-06 (ยิง 2 คำขอพร้อมกัน รอบ/นักบำบัดเดียวกัน) ผ่าน · TC-BOOK-05 (กดยืนยันซ้ำ) ผ่าน · เห็นใน `booking.ts` ว่ามี `FOR UPDATE` บางจุด | ⚠️ ผ่านแค่ 2 คำขอ 1 รอบ · ตรวจให้จริงต้องอ่านโค้ดทั้งเส้นทางจอง (transaction / lock / constraint ใน DB) + ยิงพร้อมกันหลายคำขอหลายรอบ |
| H11 | ห้อง Couple Suite มี 1 ห้อง | ตาราง `room` มี 1 แถว `Couple Suite` capacity 2 | ✅ |
| H12 | แชทบอทจองได้เฉพาะบริการเดี่ยว 1 คน | ไม่มี TC ใน e2e-legacy ที่ทดสอบ `/chat` | ⚠️ ต้องลองจองผ่าน `/chat` (หรือ REA) ด้วยกลุ่ม/คู่ แล้วดูว่าปฏิเสธ |
| H13 | Playwright 1.63.0 · 12 ไฟล์ · 42 TC (UI 36 · API 6) | 1.63.0 · 12 ไฟล์ `*.spec.ts` · 36 + 6 | ✅ |
| H14 | `check-rules.mjs` 90/90 ~20 วินาที | 90/90 · 19.8 วิ | ✅ |
| H15 | `npx playwright test` (api + chromium) 41 passed · 1 failed ~4 นาที | 41 passed · 1 failed · 4.1 นาที | ✅ |
| H16 | `npm run test:all` 113 passed · 1 failed ~13 นาที | ยังไม่ได้รัน (3 เบราว์เซอร์) | ⚠️ ตรวจด้วย `npm run test:all` (~13 นาที รันแบบ background) |
| H17 | 3 ข้อติด `test.fail` (KNOWN-ISSUE) นับเป็น passed | 3 ข้อ: TC-SEC-04 TC-GC-04 TC-TRN-03 ล้มจริงทั้งหมด จึงนับเป็น passed | ✅ (แต่ 3 ข้อนี้เป็นบั๊กจริง ไม่ใช่ "ไม่กระทบการใช้งาน" ตามบันทึกส่งมอบ · TC-SEC-04 เป็นช่องโหว่ session) |
| H18 | TC-SEC-05 แดงค้าง ยังไม่ได้ดู | แดงจริง · ดูแล้ว = เทสต์ล้าสมัย (422 แทน 403/404 · ระบบปฏิเสธถูก) | ✅ |
| H19 | เอกสารอ้างอิงในคอมเมนต์ (TEST-PLAN / TEST-DATA / BR-xx) ไม่ได้ส่งมอบมา | ไม่มีไฟล์เหล่านี้ในโฟลเดอร์ · `tests/fixtures.ts` และ `web/SPEC.md` ยังอ้างถึง | ✅ |

สรุป: ✅ 12 · ❌ 2 (H6 H9) · ⚠️ 5 (H2 H7 H10 H12 H16)

## 7. baseline (git)

- `git rev-parse --show-toplevel` → โฟลเดอร์นี้เอง (เป็น repo อยู่แล้ว มี commit ตั้งต้น `d617d68 starting folder (chapter 06)` · ไม่ได้อยู่ใน repo อื่น) → ไม่ต้อง `git init`
- เพิ่มบรรทัดใน `.git/info/exclude`: `_solution/ img/ README.md EXAM.md rea-out/ backups/ node_modules/ test-results/ test-report/ playwright-report/` (กันไฟล์ผลรันเข้า commit ต่อจากนี้ · `img/` `EXAM.md` ถูก track ไปแล้วตั้งแต่ commit ตั้งต้น exclude จึงไม่มีผลกับสองตัวนี้)
- commit baseline: ดูหัวข้อ 8

## 8. commit baseline

| รายการ | ค่า |
|---|---|
| commit | `4a7908f` · `baseline: ระบบที่รับมอบ` (ต่อจาก `d617d68 starting folder (chapter 06)`) |
| ไฟล์ใน commit นี้ | 1 ไฟล์ (`HANDOVER-CHECK.md` ฉบับก่อนเติมหัวข้อนี้) · ไฟล์ระบบที่รับมอบถูก track แล้วตั้งแต่ `d617d68` |
| ไฟล์ที่ track ทั้งหมดหลัง baseline | 212 ไฟล์ (`git ls-files`) |
| สถานะหลัง commit | สะอาด ยกเว้นหัวข้อ 8 นี้ที่เติมทีหลัง (commit id อยู่ในไฟล์ที่ commit ไปแล้วไม่ได้) |

## 9. สรุป

| ชุดตรวจ | ผ่าน | ล้ม | คาดว่าล้ม | เวลา |
|---|---|---|---|---|
| check-rules (ชั้น 1) | 90 | 0 | 0 | 19.8 วิ |
| e2e-legacy api + chromium (ชั้น 2) | 38 | 1 (TC-SEC-05) | 3 (TC-SEC-04 TC-GC-04 TC-TRN-03) | 4.1 นาที |
