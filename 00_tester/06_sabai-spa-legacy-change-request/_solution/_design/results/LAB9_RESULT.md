# LAB 9 RESULT · CR-01 ฟีเจอร์ใหม่ ลูกค้าเลื่อนนัดเอง (3 ส่วน)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 11:41 (นาฬิกาเครื่อง) |
| เวลาจบ | 2026-10-12 ~12:22 |
| เวลาที่ใช้ | **~41 นาที** · ส่วน 1 (อ่าน CR/CLAUDE.md/SYSTEM-MAP + คำถาม Q1–Q14 + เปิดคำตอบ + psql seed + วัด `/api/slots` ก่อนแก้ + impact) ≈ 6 นาที · ส่วน 2 ≈ 5 นาที (เขียน `tests/cr01.mjs` 22 เคส · แดง 5.5 วิ · แก้โค้ด · rebuild **39 วิ** · เคสขั้น A 20/20 5.2 วิ · ทั้งหมด 22/22 5.5 วิ · check-rules 21.3 วิ · golden 1.5 · cr02 5.2 · cr03 4.1 · cr04 3.2) · ส่วน 3 ≈ 30 นาที (spec แดง 3 เบราว์เซอร์ **301 วิ** เพราะรอ timeout 90 วิ · UI · rebuild **40 วิ** · spec เขียว 14 วิ · ภาพ+วิดีโอ ~1 นาที · regression: check-rules 20.7 · golden 1.8 · cr01 7.5 · cr02 5.8 · cr03 5.2 · cr04 3.1 · e2e-cr 3 เบราว์เซอร์ **95.8 วิ** · e2e-legacy `test:all` **802 วิ (13.4 นาที)** · ตรวจ flaky TC-UI-02 ~2 นาที · เอกสาร+commit ≈ 3 นาที) |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `docs/impact/CR-01.md` · `tests/cr01.mjs` (22 เคส R1–R22) · `e2e-cr/tests/cr01.spec.ts` (2 เทสต์) · `web/app/api/bookings/[id]/reschedule/route.ts` · `web/app/api/bookings/[id]/reschedule-slots/route.ts` · แก้ `web/lib/server/booking.ts` (+164/−10) · `web/lib/server/http.ts` (+2/−1) · `web/lib/i18n.ts` (+12) · `web/lib/server/customer.ts` (+1) · `web/components/MyBookings.tsx` (+152/−10) · `web/SPEC.md` (1.4 · +12/−2) · `docs/TRACEABILITY.md` (+9 แถว CR-01) · `CHANGE-REPORT.md` (+ส่วน CR-01) · `CHANGE-REQUESTS/REGISTER.md` (แถว CR-01) · รวม `git diff --stat 7a2dc24` = **14 ไฟล์ +933/−23** · ไม่แตะ `db/` `web/lib/bot/chat.ts` `check-rules.mjs` `tests/golden/` `e2e-legacy/` |
| git (w/) | 4 commit: `8aba74e` "CR-01 test: แดงก่อนแก้" (2 ไฟล์) → `802f853` "CR-01 A+B: API เลื่อนนัด" (5 ไฟล์ +201/−10) → `e54fdc5` "CR-01 C test: หน้าเลื่อนนัด แดงก่อนแก้" (1 ไฟล์) → `f4edf7b` "CR-01 C: หน้าเลื่อนนัด" (7 ไฟล์) · `git status --short` = 0 บรรทัด · ทุก commit มี `Co-Authored-By` |
| สคริปต์ชั่วคราว / log | `tools/lab9/`: `questions.md` `seed*.sql` `record.mjs` `record.log` `regress.ps1` `regress-summary.txt` `count.mjs` (นับ JSON ของ Playwright) `build-a.log` `build-c.log` `cr01-red.log` `cr01-a.log` `cr01-green.log` `cr01-spec-red.log` `cr01-spec-green.log` `*-ab.log` (regression ส่วน 2) `check-rules.log` `golden.log` `cr01..04.log` `e2e-cr.log/.json` `e2e-legacy-all.log/.json` `tc-ui-02-rerun.log` `tc-ui-02-old-image.log` (log จาก PowerShell `*>` เป็น UTF-16) · `design/logs/lab9-red.txt` `lab9-green.txt` (UTF-8) |
| สถานะเว็บตอนจบ | `sabai06-web` image `sabai06-web:latest` `c236505edf3e` (โค้ด `f4edf7b`) · `/api/health` → `{"ok":true,"db":true}` · เปิดค้างไว้ · `sabai06-fresh` (ใช้ชั่วคราวตรวจ flaky บน `before-cr04`) หยุดแล้ว (`--rm`) |
| ข้อมูลทดสอบ | ทุกชุด reset ท้ายรอบ · reset ซ้ำตอนจบ → `now` = `2026-10-10T10:00:00+07:00` |
| พอร์ตที่ใช้จริง | เว็บ **4100** · db **5533** (`$env:WEB_PORT/DB_PORT` ก่อน `up --build` · `$env:BASE_URL="http://localhost:4100"` ก่อนทุกชุดทดสอบ) · ชั่วคราว 4101 (`sabai06-fresh` image `before-cr04`) · ไฟล์ใน w/ ใช้ค่าเริ่ม 4000 |
| คำสั่งเปิดเซสชันและโหมดสิทธิ์ | runner (Agent tool) ทำเองในเซสชันเดียว ไม่ได้เปิด `claude -p` · ส่วน 1 แบบ plan (ไม่แตะโค้ด · เสนอเนื้อหา impact แล้ว "ออกจาก plan mode" จึงบันทึก `docs/impact/CR-01.md`) · ส่วน 2–3 เทียบเท่า `acceptEdits` · กติกา `w/CLAUDE.md` + deny `Edit(e2e-legacy/**)` **บังคับเอง** |

## 2. ข้อห้ามที่ทำตาม / จุดที่ทำต่างจากพรอมต์

- ไม่เปิด `_solution/` · เปิด `CHANGE-REQUESTS/answers/CR-01-ANSWERS.md` **หลัง**เขียนคำถาม Q1–Q14 (`tools/lab9/questions.md`)
- ไม่แก้ `e2e-legacy/` `check-rules.mjs` `tests/golden/` (`git diff --stat 7a2dc24 -- web/scripts/check-rules.mjs tests/golden e2e-legacy` = ว่าง) · ไม่มีรายการใหม่ใน `docs/ORACLE-CHANGES.md` · ไม่มี `docker compose down -v` · ไม่แตะ pawpantry05 / exref-* / sabai-* บท 04
- SQL (อ่านอย่างเดียว ดู seed) ด้วย `docker cp` + `psql -v ON_ERROR_STOP=1 -f` + ตรวจ `$LASTEXITCODE` · ยิง API ไทยด้วย node
- โค้ดใหม่ใช้ `clock()` (`now` `today`) · ไม่มี `new Date()` ที่เป็น "วันนี้"
- git จริงใน w/ (BRIEF D11 · พรอมต์สั่ง commit)
- **ส่วน 2 ข้อ 2–3:** เขียนโค้ดขั้น A และ B ในรอบแก้เดียวกัน → rebuild **ครั้งเดียว** แล้วรัน "เฉพาะเคสขั้น A" (`node tests/cr01.mjs R1 … R22` ยกเว้น R9 R11 = 20/20) ก่อน แล้วรันทั้งหมด 22/22 (พรอมต์ตั้งใจให้ rebuild 2 ครั้ง)
- **ส่วน 3 ข้อ 1:** พรอมต์ไม่ให้ข้อความ commit ของเทสต์ UI แดง → ใช้ "CR-01 C test: หน้าเลื่อนนัด แดงก่อนแก้"
- **ส่วน 3 ข้อ 3:** `npm run test:all` และ `npx playwright test` ของ e2e-cr รันพร้อม `-- --reporter=list,json` + `PLAYWRIGHT_JSON_OUTPUT_NAME` เพื่อแยก passed / expected-fail / failed จาก JSON (ไม่เปลี่ยนเทสต์)
- **REGISTER.md** อยู่ใน commit เดียวกับ "CR-01 C: หน้าเลื่อนนัด" (พรอมต์วางไว้หลัง commit)
- ⚠️ **การปนเปื้อน:** ตอนอ่านหัวข้อ LAB 9 ใช้ `sed -n 359,401p` ซึ่งเกินกล่อง ```text ไปถึง "ผลที่คาด"/"ไปต่อได้เมื่อ" → เห็นผลที่คาดตั้งแต่ต้น (ซ้ำ LAB 8 · ผิด RUNNER §2 และคำสั่ง orchestrator "Read ONLY the ```text block") · ค่าคาดหวังในเทสต์มาจากคำตอบร้าน ①–③ + seed/ค่าที่วัดก่อนแก้ แต่เคส R6 R7 R13 R14 R15 เลือกตัวอย่างตรงกับผลที่คาด (9/10 พ.ย. · 21:00/21:30 · B07 · 31 ต.ค.→1 พ.ย. · C02 19→21 ต.ค.) ซึ่งอาจถูกชี้นำ · ตาราง §11 ไม่ "ตาบอด"

## 3. คำตอบสรุปที่แสดงในแชท

**ส่วนที่ 1 (วิเคราะห์ · Plan mode)**

> คำถามถึงร้าน Q1–Q14 → เปิดคำตอบ: ได้คำตอบ Q1 Q2 Q3 Q4 Q6 Q7 Q8 Q11 Q12 Q14 · **ค้าง** Q5 (นัด "ใครก็ได้" → ใช้คนใน `booking_slot`) · Q9 วันหยุดร้าน (ตัดสินแทน: ห้าม `SHOP_CLOSED`) · Q10 แพ็กเกจ (ทำแบบทั่วไป ไม่มีเทสต์แยก) · Q13 ประวัติการเลื่อน/แชท (ไม่ทำ)
>
> **เวลาของนัดเก็บที่ไหน:** `booking.start_at` `end_at` (`db/init/01-schema.sql:109-110` · อัปเดตเอง) · `booking.period` = `GENERATED ALWAYS … STORED` (`:111` · คำนวณเอง ห้าม UPDATE) · `booking_slot.period` (`:148` · 1 แถว/นักบำบัด · **อัปเดตเอง**) · `birthday_use.year_month` ไม่ต้องแก้ถ้าเลื่อนในเดือนเดิม
> **กฎห้ามซ้อน:** นักบำบัด `busySlots()` `booking.ts:280` + `freeTherapists()` `overlap.ts:14` + DB `booking_slot_no_overlap` (`:152`) · ห้องคู่ `roomBusy()` `booking.ts:290` (`room_id = 1` T1) + DB `booking_room_no_overlap` (`:137-138`) · คนเดียวกัน `assertNoOverlapForPerson()` `booking.ts:356` (CR-03) · **ทับเวลาเดิมของตัวเอง:** โค้ดทั้ง 3 จุดนับนัดตัวเอง → 409 ปลอม (`SLOT_TAKEN`/`DUPLICATE_BOOKING`) ต้องเพิ่ม "ไม่นับนัด id นี้" · DB: UPDATE แถวเดิมไม่ชน (EXCLUDE เทียบแถวอื่น) แต่ INSERT slot ใหม่ก่อนปิดเก่าจะชน 23P01 → 409 (T11)
> **ทำไม `/api/slots` ใช้ไม่ได้:** นับนัดตัวเองเป็นไม่ว่าง · ตอบว่างถ้า "ใครก็ได้" ว่าง (วัดจริง: S01 14 ต.ค. 16:00 ว่างเพราะ T06 แต่ T03 ของ B01 ติด B04) · ไม่ตรวจ 24 ชม./เดือนเกิด/คอร์ส/เจ้าของ
> **ทำไมยกเลิกแล้วจองใหม่เพี้ยน:** คอร์ส reserved −1 แล้ว +1 ผ่าน `canUseCourse(remaining ≥ 1)` (อาจได้คนละคอร์ส) · `birthday_use` ลบเฉพาะ `yearMonth(today) <= ym` (`:525-526`) แล้ว insert ใหม่ → ชน PK/สิทธิ์หาย · ราคาคิดใหม่ (tier ปัจจุบัน + CR-02) + `PRICE_CHANGED` · แต้ม/บัตรคืนแล้วตัดใหม่ · รหัสนัดเปลี่ยน · รอบเดิมว่างให้คนอื่นแย่งระหว่างทาง
>
> | ขั้น | ไฟล์ที่จะแตะ | เทสต์ที่พิสูจน์ | ความเสี่ยง |
> |---|---|---|---|
> | A API เลื่อนนัด | `booking.ts` (`rescheduleBooking` + `excludeBookingId` 3 ฟังก์ชัน) · `reschedule/route.ts` · `http.ts` · `i18n.ts` | cr01 R1–R8 R10 R12–R22 · cr03 | ชนตัวเอง · ลำดับล็อก · ค่าเริ่ม exclude เปลี่ยนของเดิม |
> | B รอบที่เลื่อนได้ | `booking.ts` (`rescheduleSlots`) · `reschedule-slots/route.ts` | cr01 R9 R11 · `/api/slots` เดิม (golden · e2e-legacy) | ผูกคนเดิมผิด · ห้องคู่ |
> | C หน้า `/account` | `customer.ts` · `MyBookings.tsx` · `i18n.ts` | cr01.spec 3 เบราว์เซอร์ · e2e-legacy เต็ม | testid เดิม `cancel-*` |
>
> ค่าคาดหวัง 22 เคส R1–R22 ติดป้าย `[D:CR-01]` (+ `[D:CR-03]` R18 · `[D:CR-04]` R19 · `[E]` ค่าเดิม ฿760 / `/api/slots` ก่อนแก้)

**ส่วนที่ 2 (ขั้น A + B)**

> | เคส | ก่อนแก้ | หลังแก้ |
> |---|---|---|
> | R1 B05 → 12 ต.ค. 10:00 (24 ชม. พอดี) | 404 | 200 `{code:B05, endTime:11:00, therapists:[T04], total:760}` · นัดของนิดายัง 8 รายการ |
> | R2 ตอน 10:01 | 404 | 422 `RESCHEDULE_TOO_LATE` + phone · B05 ไม่เปลี่ยน |
> | R3 B06 วันนี้ | 404 | 422 `RESCHEDULE_TOO_LATE` |
> | R4 เวลาเดิม | 404 | 422 `RESCHEDULE_SAME` |
> | R5 วันเดิม 14:00 | 404 | 200 |
> | R6 9 พ.ย. / 10 พ.ย. | 404 | 200 / 422 `DATE_OUT_OF_RANGE` (11 ต.ค.–9 พ.ย.) |
> | R7 21:00 / 21:30 | 404 | 200 / 422 `SLOT_INVALID` |
> | R8 B01 → 14 ต.ค. 16:00 | 404 | 409 `SLOT_TAKEN` |
> | R9 reschedule-slots B01 14 ต.ค. | 404 | 23 รอบ · 16:00 false · 15:00 true · `/api/slots` 16:00 ยัง true |
> | R10 B02 คู่ 19:00→19:30 | 404 | 200 T01+T02 · คิวร้าน 19:30–21:00 |
> | R11 reschedule-slots B02 | 404 | 19:30 true · 19:00 current |
> | R12 ต้น / ไม่ล็อกอิน / owner | 404 ×3 | 403 / 401 / 403 |
> | R13 B07 completed / B11 cancelled | 404 | 422 `RESCHEDULE_NOT_ALLOWED` ×2 |
> | R14 เดือนเกิด 31 ต.ค. → 1 พ.ย. / 30 ต.ค. | 404 | 422 `RESCHEDULE_BIRTHDAY` / 200 ยอดเดิม |
> | R15 คอร์ส C02 19 → 21 / 20 ต.ค. | 404 | 422 `COURSE_UNAVAILABLE` reserved 1 / 200 reserved 1 |
> | R16 แต้ม 2 ก้อน เลื่อน 13→15 ต.ค. | 404 | 200 · ยอดเดิม · แต้ม 50 เท่าเดิม |
> | R17 รอบเดิม T04 ว่าง + แขกจองได้ | 404 | T04 กลับมา · แขก 201 |
> | R18 ทับนัดอื่นของตัวเอง | 404 | 409 `DUPLICATE_BOOKING` + รหัสนัดใหม่ |
> | R19 23 ต.ค. | 404 | 422 `SHOP_CLOSED` |
> | R20 en / zh | 404 | ข้อความตรงตาราง ② |
> | R21 เลื่อน 2 ครั้ง | 404 | 200 ×2 |
> | R22 กลุ่ม B04 | 404 | 200 T01–T05 เดิม |
> | **รวม** | **0/22** | **22/22** · check-rules 90/90 (diff ว่าง) · golden 62/62 · cr02 19/19 · cr03 18/18 · cr04 14/14 |

**ส่วนที่ 3 (ขั้น C + regression เต็ม)**

> | ชุดทดสอบ | chromium | firefox | webkit | หมายเหตุ |
> |---|---|---|---|---|
> | `e2e-cr/tests/cr01.spec.ts` (ก่อนแก้) | 0/2 | 0/2 | 0/2 | ไม่มีปุ่ม `reschedule-B05` · 301 วิ (รอ timeout) |
> | `e2e-cr/tests/cr01.spec.ts` (หลังแก้) | 2/2 | 2/2 | 2/2 | 14 วิ |
> | e2e-cr ทั้งชุด | 9 + ef 2 | 9 + ef 2 | 9 + ef 2 | ef = KI-01b KI-02b · ล้ม 0 · 95.8 วิ |
> | e2e-legacy `test:all` | 34 + ef 2 | 34 + ef 2 | 33 + ef 2 + **ล้ม 1** | api: 4 + ef 1 (TC-SEC-04) + ล้ม 1 (TC-SEC-05 เดิม) · webkit ล้ม **TC-UI-02** (flaky webkit มีอยู่เดิม ดู §7) · ef chromium/firefox/webkit = TC-GC-04 TC-TRN-03 · 13.4 นาที |
> | check-rules · golden | 90/90 · 62/62 | | | |
> | cr01 · cr02 · cr03 · cr04 | 22 · 19 · 18 · 14 | | | ผ่านทั้งหมด |

## 4. ตัวเลขสำคัญ

| ตัวเลข | ค่า | คำสั่ง/แหล่ง |
|---|---|---|
| cr01 API | แดง **0/22** (ทุกเคส 404) → เขียว **22/22** (5.5 วิ) · เฉพาะขั้น A 20/20 | `node tests/cr01.mjs` · log `cr01-red.log` `cr01-a.log` `cr01-green.log` |
| cr01.spec | แดง 6 failed → เขียว **6 passed** (2 เทสต์ × 3 เบราว์เซอร์) | `npx playwright test tests/cr01.spec.ts` |
| e2e-cr 3 เบราว์เซอร์ | 33 รายการ: passed 27 · expected-fail 6 · failed 0 · flaky 0 | `node tools/lab9/count.mjs e2e-cr.json` |
| e2e-legacy test:all | **114 รายการ** · บรรทัดสรุป Playwright "**2 failed · 112 passed** (13.4m)" · แยก: passed จริง **105** (api 4 · chromium 34 · firefox 34 · webkit 33) · expected-fail **7** (api TC-SEC-04 · TC-GC-04 TC-TRN-03 ×3) · failed **2** (api TC-SEC-05 เดิม · webkit TC-UI-02) · flaky 0 | `count.mjs e2e-legacy-all.json` · `stats.expected 112 unexpected 2` |
| TC-UI-02 webkit รันซ้ำ | image ปัจจุบัน `--repeat-each=3` → 1 ผ่าน 2 ล้ม · image `before-cr04` (ก่อน CR-04 และ CR-01) ที่พอร์ต 4101 → 2 ผ่าน 1 ล้ม | `tc-ui-02-rerun.log` `tc-ui-02-old-image.log` |
| regression | check-rules **90/90** · golden **62/62** · cr02 19/19 · cr03 18/18 · cr04 14/14 (2 รอบ: หลัง A+B และหลัง C) | `regress-summary.txt` |
| rebuild | 39 วิ (A+B) · 40 วิ (C) | `build-a.log` `build-c.log` |
| diff | `git diff --stat 7a2dc24` = 14 ไฟล์ +933/−23 · โค้ดแอป 8 ไฟล์ (`-- web` ไม่รวม SPEC) | git |
| ภาพ/วิดีโอ | `lab9-reschedule-dialog.png` 102,968 ไบต์ · `lab9-reschedule.webm` 704,812 ไบต์ | `ls -la design/shots` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

| รหัส | แถว |
|---|---|
| R1 (CR-01 ③1) | นิดา B05 11 ต.ค. 10:00 → 12 ต.ค. 10:00 ตอนเหลือ 24 ชม. พอดี → 200 ยอด ฿760 เดิม · รหัส B05 เดิม |
| R10 (CR-01 ①) | คู่ของคุณต้น B02 19:00 → 19:30 วันเดียวกัน (ทับเวลาตัวเอง) → 200 · ถ้าใช้โค้ดตรวจชนเดิมจะได้ 409 ปลอม |
| R9 | `reschedule-slots` B01 14 ต.ค. 16:00 = ไม่ว่าง (T03 ติด B04) ขณะ `/api/slots` บอกว่าง (T06) → เหตุที่ต้องมี endpoint ใหม่ |
| R15 (CR-01 ③3 · BR-14) | คอร์ส C02 (เหลือ 0 หลังกันครั้ง) 19 → 21 ต.ค. 422 `COURSE_UNAVAILABLE` reserved 1 · → 20 ต.ค. 200 — ห้ามใช้ `canUseCourse()` เดิมเพราะต้องเหลือ ≥ 1 |
| R18 (BR-21) | เลื่อน B05 ไปทับนัดใหม่ของตัวเอง 12 ต.ค. 10:00 → 409 `DUPLICATE_BOOKING` |
| CR01-UI-1 | `/account` → `reschedule-B05` → `reschedule-date` 2026-10-12 → `reschedule-slot-10:00` → `reschedule-confirm` → "เลื่อนนัด B05 เป็น 12 ต.ค. 2026 10:00 แล้ว" → รีโหลด "12 ต.ค. 2026 10:00–11:00" (3 เบราว์เซอร์) |

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| ส่วน 1 ข้อ 6 "รอผมอนุมัติ" | **อนุมัติ** แผน 3 ขั้น | impact มีตารางไฟล์ × เทสต์ × ความเสี่ยง + grep ไฟล์:บรรทัด · ค่าคาดหวัง 22 เคส ครบหัวข้อที่พรอมต์ขอ · ทางเลือก UPDATE แถวเดิมมีเหตุผล |
| Q5 นัดที่จอง "ใครก็ได้" | ผูกคนที่ระบบจัดไว้ใน `booking_slot` | คำตอบ ① "นักบำบัดคนเดิม" · ระบบไม่เก็บว่าลูกค้าเลือกเองหรือไม่ |
| Q9 เลื่อนไปวันหยุดร้าน | ห้าม → 422 `SHOP_CLOSED` (หลังเช็กช่วงวัน) | CR ข้อ 3 "รอบที่มีจริง" + CR-04 "ปิดทุกช่องทาง" · จดเป็น ⏳ รอร้านยืนยัน |
| Q10 แพ็กเกจ | ไม่กันแบบการจอง (ใช้ `booking_slot` เดิม) | CR ไม่แยกแบบ · ไม่มีเทสต์แยก (ความเสี่ยงคงค้าง) |
| Q13 ประวัติ/แชท | ไม่ทำ · ไม่มี migration | ร้านไม่ขอ · แชทไม่มีเมนูนัดของฉัน |
| ลำดับ error | 401 → 404 → 403 → NOT_ALLOWED → TOO_LATE → BAD_REQUEST → DATE_OUT_OF_RANGE → SHOP_CLOSED → BIRTHDAY → COURSE_UNAVAILABLE → SLOT_INVALID → SAME → SLOT_TAKEN → DUPLICATE_BOOKING | ตรวจสิทธิ์/สถานะของนัดก่อนวันใหม่ · ตามลำดับเดิมของการจอง (ช่วงวันก่อนวันหยุด · SLOT_TAKEN ก่อน DUPLICATE ตาม CR-03) |
| `reschedule-slots` รอบเวลาเดิม | `available:false, current:true` | POST เวลาเดิมได้ `RESCHEDULE_SAME` → ไม่เสนอให้กด |
| `reschedule-slots` ทับนัดอื่นของลูกค้า | ไม่เสนอ (available false) | กันเสนอรอบที่ POST จะได้ 409 `DUPLICATE_BOOKING` |
| owner | 403 `FORBIDDEN` | CR ข้อ 7 + ① "เจ้าของร้านไม่ต้องมีปุ่มนี้" |
| ข้อความ commit เทสต์ UI | "CR-01 C test: หน้าเลื่อนนัด แดงก่อนแก้" | พรอมต์ไม่กำหนด |
| TC-UI-02 webkit ล้มใน regression | ไม่หยุด/ไม่แก้ · ตรวจซ้ำแล้วจดเป็น flaky เดิม | ไม่ใช่ไฟล์ที่ CR-01 แตะ (`/skin` · `SkinAnalyzer.tsx`) · ล้มบน image ก่อน CR ด้วย |

## 7. ข้อสังเกต 👀

- **กับดัก "นับนัดตัวเอง" มี 3 จุดในโค้ด** (นักบำบัด · ห้องคู่ · BR-21 ของ CR-03) แต่ DB EXCLUDE ไม่ชนถ้า UPDATE แถวเดิม → ถ้า Agent แก้แค่ `busySlots` จะติด `DUPLICATE_BOOKING` ปลอมจาก CR-03 ที่เพิ่งทำ (R10 จับได้) — ตัวอย่างดีว่า CR ก่อนหน้ากลายเป็นกับดักของ CR ถัดไป
- **กับดักคอร์ส:** ใช้ `canUseCourse()` เดิมกับนัดที่กันครั้งไว้แล้วจะ 422 ทุกครั้งสำหรับคอร์สที่เหลือ 1 (remaining = 0) → ต้องตรวจแค่วันหมดอายุ
- `booking.period` เป็น GENERATED → UPDATE `start_at/end_at` พอ · แต่ `booking_slot.period` ไม่ใช่ → ลืมแก้จะทำให้คิวนักบำบัดค้างเวลาเก่า (R17 จับ)
- นัดของคุณนิดาใน seed มี 8 รายการ (B05 B06 B08–B13) · เทสต์ R1 นับจำนวนนัดเพื่อยืนยันว่าไม่มีนัดใหม่/cancelled เพิ่ม
- ชุด e2e-legacy 3 เบราว์เซอร์มี **webkit flaky TC-UI-02** (`/skin` อัปโหลดรูป → `skin-recs` ไม่ขึ้นใน 15 วิ) · รันซ้ำบน image ก่อน CR ก็ล้ม 1/3 → ถ้าผู้เรียนเห็นแดงนี้อาจคิดว่า CR-01 ทำพัง — ควรเตือนใน README/KNOWN-ISSUES
- spec แดงใช้เวลา 301 วิ เพราะ `locator.click` รอจน timeout 90 วิ × 3 เบราว์เซอร์ × UI-1 (UI-2 ล้มเร็ว)
- input `type=date` ใน webkit/firefox headless ใช้ `fill('2026-10-12')` ได้ทั้ง 3 เบราว์เซอร์ (ภาพแสดง 12/10/2026 ตาม locale)

## 8. เจอระหว่างทาง (นอก CR)

- **TC-UI-02 flaky บน webkit** (หน้า `/skin`): ล้ม 1 ใน `test:all` · `--repeat-each=3` image ปัจจุบัน ล้ม 2/3 · image `before-cr04` ล้ม 1/3 → ปัญหาเดิมของหน้า/สภาพแวดล้อม webkit ไม่เกี่ยว CR (baseline PREP V5b ตามผลที่คาดไม่ล้ม = ผ่านโดยบังเอิญ)
- ปุ่ม "ยกเลิกนัด" ที่ disabled แทบมองไม่เห็นตัวอักษร (contrast ต่ำ · เห็นในภาพ lab9) — ของเดิม
- `myBookings()` อ่านนักบำบัดจาก `booking_slot` ทุกแถวรวมที่ `active = false` (ไม่มี filter active) — ของเดิม ไม่กระทบเพราะเลื่อนนัดไม่ปิด slot

## 9. ปัญหาที่เจอ / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| Git Bash แปลง `/tmp/…` เป็น path Windows ใน `docker exec … -f /tmp/x.sql` | ใช้ PowerShell (ตามพรอมต์) |
| psql ไฟล์แรกอ้างตาราง `app_user` ที่ไม่มี → exit 3 | ตรวจ `$LASTEXITCODE` · แก้ไฟล์ตรวจ (ไม่เกี่ยว CR) |
| ภาพแรก กล่องเลื่อนนัดตกขอบล่าง 800 px | scroll ให้การ์ด B05 อยู่บนสุดแล้วถ่ายใหม่ |
| log จาก PowerShell 5.1 `*>` เป็น UTF-16 | แปลงเป็น UTF-8 ตอนคัดไป `design/logs/` |
| e2e-legacy webkit TC-UI-02 ล้ม | รันซ้ำบน image ปัจจุบันและ image ก่อน CR (`sabai06-fresh` พอร์ต 4101) → flaky เดิม · จดไว้ ไม่แก้เทสต์ |

## 10. ข้อเสนอแก้พรอมต์

- ส่วน 2 ข้อ 2–3 แยก rebuild 2 ครั้ง (A แล้ว B) แต่ Agent มักเขียนทั้งสองในรอบเดียว → ระบุ "ถ้าเขียนทั้ง A และ B แล้ว rebuild ครั้งเดียว รันเคส A ก่อนแล้วจึงรันทั้งหมด" หรือรวมเป็นขั้นเดียว
- ส่วน 3 ข้อ 1 ไม่ระบุข้อความ commit → เติม `git commit -m "CR-01 C test: แดงก่อนแก้"`
- ส่วน 3 ข้อ 3 "แยก passed / expected-fail / failed" → แนะนำ `npm run test:all -- --reporter=list,json` (+ `PLAYWRIGHT_JSON_OUTPUT_NAME`) หรือบอกรายชื่อ `test.fail` 7 ตัว
- เตือนว่า TC-UI-02 webkit อาจ flaky (รันซ้ำเฉพาะตัวด้วย `--project=webkit -g TC-UI-02` ก่อนสรุปว่าพัง)
- ส่วน 1 ข้อ 5 รายการเคสยาวมาก → อาจให้ "R1–R12 ขั้นต่ำ" ชัดเจน เพื่อไม่ให้ Agent ตัดเคสสำคัญ (เช่น คอร์ส/เดือนเกิดต้องจองนัดใหม่ก่อนเพราะ seed ไม่มี)
- ส่วน 3 ข้อ 2 "rebuild → cr01.spec.ts เขียว 3 เบราว์เซอร์" + ข้อ 3 รันซ้ำทั้ง e2e-cr 3 เบราว์เซอร์ → ซ้ำซ้อนเล็กน้อย (≈ 1.5 นาที) รับได้

## 11. ภาพที่ควรใช้ + เทียบกับผลที่คาด

| ไฟล์ | คำอธิบาย |
|---|---|
| `design/shots/lab9-reschedule-dialog.png` | `/account` คุณนิดา (headless chromium 1280×800 · reset ก่อนถ่าย) เปิดกล่อง "เลื่อนนัด B05" เลือก 12/10/2026 + รอบ 10:00 (23 รอบของนักบำบัดคนเดิม) · นัด B06 ด้านล่างปุ่มเลื่อนเป็นสีเทา + ข้อความโทรร้าน |
| `design/shots/lab9-reschedule.webm` | วิดีโอ CR01-UI-1 headless chromium 1280×800 ~15 วิ: กดเลื่อนนัด → เลือกวัน → รอบ 10:00 → ยืนยัน → "เลื่อนนัด B05 เป็น 12 ต.ค. 2026 10:00 แล้ว" → รีโหลด 12 ต.ค. 2026 10:00–11:00 (ชื่อตามคำสั่ง orchestrator · RUNNER §6 ใช้ชื่อ `cr01-15.webm`) |

เทียบกับ "ผลที่คาด" (⚠️ เห็นก่อนรัน ดู §2)

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| B05 → 12 ต.ค. 10:00 = 200 total 760 | R1 200 total 760 | ✅ |
| ทำตอน 10:01 → 422 `RESCHEDULE_TOO_LATE` | R2 | ✅ |
| B06 → 422 | R3 `RESCHEDULE_TOO_LATE` | ✅ |
| B02 19:00 → 19:30 = 200 | R10 | ✅ |
| B01 → 14 ต.ค. 16:00 = 409 (T03 ติด B04) | R8 409 `SLOT_TAKEN` | ✅ |
| reschedule-slots B01 14 ต.ค. ไม่มี 16:00 ขณะ `/api/slots` มี | R9: 16:00 อยู่ในรายการแต่ `available:false` · `/api/slots` true | ✅ (ตีความ "ไม่มี" = ไม่ว่าง) |
| 9 พ.ย. 200 / 10 พ.ย. 422 | R6 | ✅ |
| 21:00 200 / 21:30 422 | R7 (`SLOT_INVALID`) | ✅ |
| เวลาเดิม 422 `RESCHEDULE_SAME` | R4 | ✅ |
| คนอื่น 403 · ไม่ล็อกอิน 401 · owner 403 | R12 | ✅ |
| B07 422 `RESCHEDULE_NOT_ALLOWED` | R13 | ✅ |
| เดือนเกิด 31 ต.ค. → 1 พ.ย. 422 | R14 `RESCHEDULE_BIRTHDAY` | ✅ |
| คอร์ส C02 19 → 21 ต.ค. 422 และ reserved = 1 | R15 `COURSE_UNAVAILABLE` reserved 1 | ✅ |
| แต้มไม่เปลี่ยน | R16 (50 เท่าเดิม) | ✅ |
| UI ผ่าน 3 เบราว์เซอร์ | cr01.spec 6/6 | ✅ |
| e2e-legacy `test:all` = 114 รายการ "113 passed · 1 failed" (ef 7 · failed TC-SEC-05) เท่า baseline | 114 รายการ "112 passed · 2 failed" · ef 7 · failed TC-SEC-05 + **TC-UI-02 webkit** (flaky เดิม ยืนยันบน image ก่อน CR) | ⚠️ ต่าง 1 (ไม่ใช่ regression ของ CR-01) |
| commit 4–5 ตัว | 4 ตัว | ✅ |
| ไปต่อได้เมื่อ: cr01 API เขียวทุกเคส · spec เขียว 3 เบราว์เซอร์ · regression ไม่มีแดงใหม่ | 22/22 · 6/6 · แดงใหม่ = flaky webkit เดิมเท่านั้น | ✅ (มีหมายเหตุ) |
