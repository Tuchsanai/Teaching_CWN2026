# LAB 8 RESULT · CR-04 migration วันหยุดร้าน (ส่วน ก)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 11:25 (นาฬิกาเครื่อง) |
| เวลาจบ | 2026-10-12 ~11:42 |
| เวลาที่ใช้ | ~17 นาที: อ่าน CLAUDE.md/SYSTEM-MAP/CR + คำถาม + เปิดคำตอบ + หลักฐาน + impact ≈ 5 นาที · เขียน `tests/cr04.mjs` + `cr04.spec.ts` + รันแดง ≈ 2 นาที (cr04 4.8 วิ · spec 12.1 วิ) · สำรอง 0.6 วิ · จองนัดใหม่ + migrate ×2 + ตรวจ < 1 นาที (migrate 0.28 / 0.27 วิ) · แก้โค้ด + เอกสาร db/init ≈ 2 นาที · rebuild **41 วิ** · cr04 เขียว 3.5 วิ · reset ×2 · spec เขียว 8.3 วิ · ติดตั้งใหม่ 6 วิ · check-rules **25.9 วิ** · golden 1.4 วิ · cr02 4.6 วิ · cr03 4.2 วิ · e2e-cr chromium **28 วิ** · e2e-legacy api+chromium **251 วิ** · ภาพ + เอกสาร + commit ≈ 3 นาที |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `docs/impact/CR-04.md` · `tests/cr04.mjs` (14 เคส) · `e2e-cr/tests/cr04.spec.ts` (2 เทสต์) · `db/migrations/001_shop_holiday.sql` · `001_shop_holiday.down.sql` · `web/lib/server/holiday.ts` · `web/app/api/holidays/route.ts` · `docs/MIGRATION-RUNBOOK.md` · แก้ `db/init/01-schema.sql` (+8) · `db/init/02-seed.sql` (+6) · `web/lib/server/testmode.ts` (TABLES +`shop_holiday`) · `web/lib/server/booking.ts` (+3) · `web/lib/bot/chat.ts` (+6) · `web/lib/server/http.ts` (+4/−1) · `web/lib/i18n.ts` (+2) · `web/SPEC.md` (1.3) · `docs/TRACEABILITY.md` (+แถว CR-04) · `CHANGE-REPORT.md` (+ส่วน CR-04) · `CHANGE-REQUESTS/REGISTER.md` (แถว CR-04) · ไม่ commit: `backups/before-cr04.sql` (52,535 ไบต์ · อยู่ใน `.git/info/exclude`) · **ไม่แตะ** `web/components/*` `check-rules.mjs` `tests/golden/` `e2e-legacy/` |
| git (w/) | 2 commit ตามพรอมต์: `d221eda` "CR-04 test: แดงก่อนแก้" (3 ไฟล์) → `7a2dc24` "CR-04: วันหยุดร้าน + migration 001" (17 ไฟล์ +254/−10) · `git status --short` = 0 บรรทัด · มีบรรทัด `Co-Authored-By` |
| สคริปต์ชั่วคราว / log | `tools/lab8/`: `questions.md` `book-new.mjs` `book-new.log` `check-001.sql` `migrate-twice.log` `fresh.log` `shot.mjs` `shot.log` `build.log` `cr04-red.log` `cr04-spec-red.log` `cr04-green.log` `cr04-spec-green.log` `check-rules.log` `golden.log` `cr02.log` `cr03.log` `e2e-cr.log` `e2e-legacy.log` · `design/logs/lab8-red.txt` `lab8-green.txt` |
| สถานะเว็บตอนจบ | `sabai06-web` image `sabai06-web:latest` `aac2f24e3cb2` (โค้ด `7a2dc24`) · `/api/health` → `{"ok":true,"db":true}` · เปิดค้างไว้ · image ถอยกลับ `sabai06-web:before-cr04` `199e58b75e1a` · `sabai06-fresh` หยุดแล้ว (`--rm`) |
| ข้อมูลทดสอบ | ทุกชุด reset ท้ายรอบ + ภาพ reset ก่อนถ่าย · ตอนจบ `/api/test/today` → `2026-10-10T10:00:00+07:00` · `shop_holiday` 3 แถว |
| พอร์ตที่ใช้จริง | เว็บ **4100** · db **5533** (`$env:WEB_PORT/DB_PORT` ก่อน `up --build` · `$env:BASE_URL="http://localhost:4100"` ก่อนทุกชุดทดสอบและสคริปต์ node) · ไฟล์ใน w/ ใช้ค่าเริ่ม 4000 |
| คำสั่งเปิดเซสชันและโหมดสิทธิ์ | runner (Agent tool) ทำเองในเซสชันเดียว ไม่ได้เปิด `claude -p` · ส่วนที่ 1 ทำแบบ plan (ไม่แตะโค้ด · เนื้อหา impact เสนอในแผน แล้ว "ออกจาก plan mode" จึงบันทึก `docs/impact/CR-04.md` ตามปัญหาพรอมต์ที่รู้) · ส่วนที่ 2 เทียบเท่า `acceptEdits` · กติกา `w/CLAUDE.md` และ deny `Edit(e2e-legacy/**)` **บังคับเอง** · ส่วนที่ 3 (ทางเลือก) ไม่ได้ทำ |

## 2. ข้อห้ามที่ทำตาม / จุดที่ทำต่างจากพรอมต์

- ไม่เปิด `_solution/` · เปิด `CHANGE-REQUESTS/answers/CR-04-ANSWERS.md` **หลัง**เขียนคำถาม Q1–Q10 (`tools/lab8/questions.md`)
- ไม่มี `docker compose down -v` · ไม่ลบ volume · ไม่แตะ pawpantry05 / exref-* / sabai-* บท 04
- SQL ทุกไฟล์รันด้วย `docker cp` + `psql -v ON_ERROR_STOP=1 -f` (migration + ไฟล์ตรวจ `check-001.sql`) · ไม่ pipe SQL ผ่าน PowerShell · ข้อความไทยตรวจด้วย SQL (`th_ok`) · จองนัดด้วย node
- ไม่แก้ `e2e-legacy/` `check-rules.mjs` `tests/golden/` (`git diff --stat -- web/scripts/check-rules.mjs tests/golden e2e-legacy` = ว่าง) · ไม่มีรายการใหม่ใน `docs/ORACLE-CHANGES.md`
- ใช้ `clock()` (`today` ที่ booking/chat มีอยู่แล้ว) · โค้ดใหม่ไม่มี `new Date()`
- `docker tag` ก่อน rebuild (ข้อ 5)
- git: ใช้ git จริงใน w/ ตาม BRIEF D11 (พรอมต์สั่ง commit เอง)
- พอร์ต 4100/5533 แทน 4000/5433
- **ข้อ 6 "cr04.spec.ts รัน 3 เบราว์เซอร์" → รันเฉพาะ chromium** ตามคำสั่ง orchestrator (CR LAB: api + chromium) · firefox/webkit ไม่ได้รัน
- ⚠️ **การปนเปื้อน:** ตอนอ่านหัวข้อ LAB 8 ใช้ `sed -n 310,358p` ซึ่งเกินกล่อง ```text ไปถึงบรรทัด "ผลที่คาด" / "ไปต่อได้เมื่อ" → เห็นผลที่คาดตั้งแต่ต้น (ผิด RUNNER §2) · ค่าคาดหวังในเทสต์มาจากคำตอบร้าน ② ③ และค่าวัดก่อนแก้ (23 รอบ) ไม่ได้ลอกจากผลที่คาด แต่ตาราง §11 ไม่ได้ "ตาบอด"

## 3. คำตอบสรุปที่แสดงในแชท

**ส่วนที่ 1 (วิเคราะห์ · Plan mode)**

> คำถามถึงร้าน Q1–Q10 (ปิดทั้งวันไหม · ข้อความ/ชื่อ 3 ภาษา · ลำดับ error กับช่วง 30 วัน · นัดเดิมในวันหยุด · UI · ส่วน ข ทันไหม/ใครมีสิทธิ์ · ปีหน้า · แชท · ต่ออายุคอร์ส · downtime) → เปิดคำตอบ: ปิดทั้งวัน · ไม่ต่ออายุ · เกินช่วงบอกช่วงวันก่อน · ส่วน ข ทำทีหลังได้ · ตาราง/API/error/ชื่อ 3 ภาษาตกลงแล้ว
>
> **หลักฐานจาก repo**
> - เพิ่มตารางใน `db/init/01-schema.sql` อย่างเดียว → ฐานที่รันอยู่**ไม่ได้**ตาราง: `db/compose.yaml:18` mount `./init` เป็น `/docker-entrypoint-initdb.d` ซึ่งรันเฉพาะตอน volume ว่าง · volume `sabai06-pgdata` `:17` มีข้อมูลแล้ว
> - seed ของ reset = `db/init/02-seed.sql` → COPY เข้า image ตอน `up --build` (`web/compose.yaml:8-9` additional_contexts · `web/Dockerfile:31` · `SEED_SQL_PATH` `:25`) · อ่านครั้งแรกแล้ว cache (`testmode.ts:17-30`)
> - reset `TRUNCATE` 19 ตารางใน `TABLES` (`testmode.ts:11-15` `:45`) แล้วรัน seed (`:46`) → ตารางใหม่ต้องเติม `TABLES` + แถวใน seed + rebuild · ถ้าเว็บใหม่ขึ้นก่อน migrate → TRUNCATE ตารางที่ไม่มี → 500
>
> | ไฟล์/ตารางที่จะแตะ | เหตุผล | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง |
> |---|---|---|---|
> | `db/migrations/001_shop_holiday.sql` + `.down.sql` | ตารางใหม่บนฐานที่มีข้อมูล · รันซ้ำได้ · ถอยได้ | ซ้อม migrate ×2 + ตรวจ SQL | ไทยเพี้ยนถ้า pipe · รันผิดฐาน |
> | `db/init/01-schema.sql` `02-seed.sql` | เครื่องติดตั้งใหม่ + seed reset | ติดตั้งใหม่ `sabai06-fresh` · reset ×2 · ทุกชุด | seed เก่าใน image (T4) |
> | `web/lib/server/testmode.ts` TABLES | reset ต้องล้างตารางใหม่ (T2) | reset ×2 | reset 500 |
> | `web/lib/server/holiday.ts` (ใหม่) + `booking.ts` `buildQuote()` `availableSlots()` | ปิดรอบ/ราคา/จองทุกแบบรวมคอร์ส · หลังเช็กช่วงวัน | cr04 · check-rules · golden · cr02 · cr03 · e2e | ลำดับ error ผิด |
> | `web/lib/bot/chat.ts` ขั้นเลือกวัน | แชทตอบชื่อวันหยุด | cr04 แชท · e2e-legacy CHAT | ApiError หลุดเป็น 422 |
> | `http.ts` `errorBody()` + `i18n.ts` `err.SHOP_CLOSED` | ข้อความมี `{name}` 3 ภาษา | cr03 (ข้อความ `{code}`) | กระทบ error อื่น |
> | `web/app/api/holidays/route.ts` (ใหม่) | `GET /api/holidays` | cr04 H1 | — |
> | `shop_holiday` (ตาราง) | เก็บวันหยุด | — | ถอย = ข้อมูลวันหยุดหาย |
>
> ค่าคาดหวังใหม่ 14 เคส (H1–H14) + UI 2 · ติดป้าย `[D:CR-04]` ทุกแถว (H4 มี `[E]` 23/23 รอบ) · ลำดับ error: SERVICE → คน → DATE_OUT_OF_RANGE → SHOP_CLOSED → SLOT_INVALID · ส่วน ข: ถามผู้เรียน → ไม่ทำรอบนี้

**ส่วนที่ 2 (ลงมือ ส่วน ก)**

> | ขั้น | คำสั่ง | ผล | เวลา |
> |---|---|---|---|
> | 1 เทสต์แดง | `node tests/cr04.mjs` · `npx playwright test tests/cr04.spec.ts --project=chromium` | **3/14** (ผ่านแค่ H4 H9 H14 ที่ล็อกของเดิม) · UI-1 ล้ม UI-2 ผ่าน → commit `d221eda` | 4.8 วิ · 12.1 วิ |
> | 2 migration | เขียน `001_shop_holiday.sql` (`BEGIN` · `CREATE TABLE IF NOT EXISTS` · `INSERT … ON CONFLICT DO NOTHING` · `COMMIT`) + `.down.sql` | — | — |
> | 3a สำรอง | `pg_dump` → `docker cp` → `backups\before-cr04.sql` | 52,535 ไบต์ | 0.6 วิ |
> | 3b นัดใหม่ | reset → node จอง S01 2026-10-20 14:00 ไม่ล็อกอิน | 201 **B14** (booking 14 แถว) | < 1 วิ |
> | 3c migrate ครั้งที่ 1 | `docker cp` + `psql -v ON_ERROR_STOP=1 -f /tmp/001.sql` | `CREATE TABLE` · `INSERT 0 3` · exit 0 | 0.28 วิ |
> | 3d migrate ครั้งที่ 2 | คำสั่งเดิม | NOTICE `already exists, skipping` · `INSERT 0 0` · exit 0 | 0.27 วิ |
> | 3e ตรวจ | `check-001.sql` ด้วย `psql -f` | count **3** · `th_ok` **t** · `zh_ok` t · B14 confirmed อยู่ · booking 14 / customer 9 · เว็บเดิม reset 200 และ shop_holiday ยัง 3 | < 1 วิ |
> | 4 โค้ด | db/init · TABLES · holiday.ts · booking.ts · chat.ts · http.ts · i18n · `/api/holidays` | — | — |
> | 5 tag + rebuild | `docker tag sabai06-web:latest sabai06-web:before-cr04` · `up -d --build --wait` | exit 0 · health ok · latest `aac2f24e3cb2` / before-cr04 `199e58b75e1a` | 41 วิ |
> | 6 พิสูจน์ | `node tests/cr04.mjs` · reset ×2 · cr04.spec chromium · `docker run … sabai06-fresh` | **14/14** · 200 · 200 · **2/2** · fresh 20 ตาราง `shop_holiday` 3 แถว th_ok t → `docker stop` | 3.5 วิ · 8.3 วิ · 6 วิ |
> | 7 regression | check-rules · golden · cr02 · cr03 · e2e-cr chromium · e2e-legacy | **90/90** (diff ว่าง) · **62/62** · **19/19** · **18/18** · **7 + expected-fail 2** · ผ่านจริง **38** / ล้ม **1** (TC-SEC-05 เดิม) / test.fail **3** = baseline | 26 · 1.4 · 4.6 · 4.2 · 28 · 251 วิ |
> | 8 เอกสาร + commit | MIGRATION-RUNBOOK · TRACEABILITY · CHANGE-REPORT · SPEC 1.3 · REGISTER | commit `7a2dc24` (17 ไฟล์) | — |

## 4. ตัวเลขสำคัญ

| ตัวเลข | ค่า | คำสั่งที่ใช้นับ |
|---|---|---|
| เคส cr04 | 14 (H1–H14) · แดง 3/14 → เขียว 14/14 | บรรทัดสรุป `CR-04: ผ่าน …` ใน `cr04-red.log` / `cr04-green.log` |
| UI e2e-cr cr04 | 2 · แดง 1 ล้ม/1 ผ่าน → 2/2 (chromium) | `cr04-spec-*.log` |
| migration | 2 ครั้ง exit 0 · `INSERT 0 3` → `INSERT 0 0` · 0.28/0.27 วิ | `tools/lab8/migrate-twice.log` |
| แถววันหยุด | 3 · `th_ok = t` | `check-001.sql` |
| ข้อมูลเดิม | booking 14 ก่อน = 14 หลัง · customer 9 · B14 อยู่ | `migrate-twice.log` |
| สำรอง | 52,535 ไบต์ | `(Get-Item backups\before-cr04.sql).Length` |
| ตารางใน DB | 19 → 20 (fresh `\dt` 20 rows) | `fresh.log` |
| rebuild | 41 วิ | `build.log` + Get-Date |
| check-rules | 90/90 | `check-rules.log` |
| golden / cr02 / cr03 | 62/62 · 19/19 · 18/18 | logs |
| e2e-cr chromium | 9 passed = ผ่านจริง 7 + expected-fail 2 (KI-01 KI-02 `x`) · failed 0 · flaky 0 | `grep -E "\[chromium\]" e2e-cr.log` |
| e2e-legacy api+chromium | สรุป Playwright 41 passed / 1 failed → ผ่านจริง **38** · expected-fail **3** (TC-SEC-04 TC-GC-04 TC-TRN-03) · failed **1** (TC-SEC-05 เดิม) · flaky 0 · 4.2 นาที | `grep -cE "^\s+ok " e2e-legacy.log` = 38 · `grep -E "^\s+x " …` |
| diff ไฟล์ commit แก้ | 17 ไฟล์ +254/−10 (โค้ด web 6 ไฟล์ +64) | `git show --stat HEAD` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

| รหัส | แถว |
|---|---|
| H2 `[D:CR-04] ③1` | `GET /api/slots?service=S01&date=2026-10-23` → 422 `SHOP_CLOSED` "วันนี้ร้านหยุด (วันปิยมหาราช) กรุณาเลือกวันอื่น" (ก่อนแก้ 200 · 23 รอบ) |
| H9 `[D:CR-04] ③3` | 5 ธ.ค. ตอนวันนี้ 10 ต.ค. → `DATE_OUT_OF_RANGE` (ไม่ใช่ SHOP_CLOSED) |
| H10 `[D:CR-04] ① ข้อ 3` | reset now 2026-11-10 → slots 5 ธ.ค. → `SHOP_CLOSED` (วันพ่อแห่งชาติ) |
| H8 `[D:CR-04]` CR | U01 จองคอร์ส K01 23 ต.ค. → 422 `SHOP_CLOSED` (ก่อนแก้จองได้) |
| H12 `[D:CR-04] ②` | แชท "จองนวดไทย 60" → "2026-10-23" → ตอบข้อความร้านหยุด + ถามวันใหม่ · state ยัง `date` |
| migrate ×2 | ครั้งที่ 2: NOTICE `relation "shop_holiday" already exists, skipping` · `INSERT 0 0` · exit 0 · B14 ยังอยู่ |

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| รอบนี้ทำส่วน ข (หลังร้าน) ไหม (ส่วนที่ 1 ข้อ 1 "ถามผมก่อน") | **ไม่ทำ · ทำส่วน ก เท่านั้น** | CR ใช้คำว่า "ถ้าเป็นไปได้" · คำตอบร้าน ① ข้อ 4 ยอมให้ทำส่วน ก ก่อน · กำหนดส่ง 23 ต.ค. · ส่วนที่ 3 ของ LAB เป็นทางเลือก |
| อนุมัติแผน (ส่วนที่ 1 ข้อ 5) | อนุมัติ | มีตาราง impact ไฟล์ × เทสต์ × หลักฐาน grep · ตอบคำถามข้อ 2 ด้วยไฟล์:บรรทัด · มีลำดับ error · ค่าคาดหวัง 14 เคสติดป้ายครบ · มีขั้นซ้อม + ถอยกลับ + ข้อมูลที่หาย |
| นัดเดิมที่ตรงวันหยุด (Q4 ไม่มีคำตอบ) | ไม่แตะ · รายงานว่าไม่มี | seed/ฐานไม่มีนัด 23 ต.ค. 5 ธ.ค. 31 ธ.ค. (grep seed) |
| ข้อความใน UI | ไม่แก้ component | `BookingWizard.tsx:144-148` แสดง error ของ `/api/slots` อยู่แล้ว (`ErrorBox`) → แก้น้อยที่สุด |
| `GET /api/holidays` รูปแบบ | `{holidays:[{date,name,nameTh,nameEn,nameZh}]}` | คำตอบ ② บอกแค่ "รายการเรียงตามวันที่" |
| ถอยกลับ | เว็บก่อน DB | เว็บรุ่นใหม่อ่าน/TRUNCATE ตารางนี้ → down ก่อน = 500 |

## 7. ข้อสังเกต 👀

- **PowerShell 5.1 ห่อ NOTICE ของ psql เป็น error สีแดง** ตอนรัน migration ครั้งที่ 2 (`docker : psql:/tmp/001.sql:14: NOTICE: relation "shop_holiday" already exists, skipping` + `NativeCommandError`) ทั้งที่ exit 0 — ผู้เรียน/Agent อาจตีความว่า "รันซ้ำแล้วพัง" (เกิดเพราะใช้ `2>&1` เก็บ log · ถ้าไม่ redirect ก็ยังขึ้นบนจอเป็นสีแดงใน PS 5.1)
- กับดักลำดับ deploy ที่พรอมต์ไม่ได้พูดตรง ๆ: ถ้า rebuild เว็บก่อนรัน migration → `/api/slots` `/api/price` `/api/bookings` และ reset ตอบ 500 (ตารางไม่มี) · กลับกัน migration ก่อน = เว็บเดิมทำงานต่อได้ (ทดสอบแล้ว reset 200)
- reset ล้าง "ข้อมูลจริง" ด้วย — ขั้นซ้อม "ฐานที่มีข้อมูลแบบระบบจริง" ต้อง reset ก่อนจองนัดใหม่ ตามพรอมต์ · สำรองจึงต้องทำก่อน reset (พรอมต์เรียงถูกแล้ว)
- ข้อความของร้าน "วันนี้ร้านหยุด (…)" ใช้คำว่า "วันนี้" ทั้งที่ลูกค้าเลือกวันอื่น — ใช้คำต่อคำตาม ② แล้วจดเป็นความเสี่ยงใน CHANGE-REPORT
- `errorBody()` เดิมเติมตัวแปรข้อความเฉพาะ `existing → {code}` → ต้องขยายให้รับ `{name}` (จุดเดียวที่แตะโค้ดร่วมของทุก error · cr03 ยังผ่าน)
- แชท: ถ้าแค่เพิ่ม assert ใน `availableSlots()` แชทจะได้ ApiError จาก `freeTimes` → `/api/chat` ตอบ 422 แทนคำตอบบอท · ต้องเช็กวันหยุดในขั้นเลือกวันก่อน
- ติดตั้งใหม่: `docker run -d` คืนทันที · `pg_isready` อาจผ่านระหว่าง init (เซิร์ฟเวอร์ชั่วคราว) → runner วนถามจน `SELECT count(*) FROM shop_holiday` ได้ตัวเลข (6 วิ)

## 8. เจอระหว่างทาง (นอก CR)

- ไม่มีบั๊กใหม่ของระบบเดิม · (ข้อสังเกต: `/api/holidays` เปิดสาธารณะไม่ต้องล็อกอิน — ตั้งใจ เพราะลูกค้าต้องเห็นวันหยุด)

## 9. ปัญหาที่เจอ / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| NOTICE ครั้งที่ 2 ขึ้นเป็น `NativeCommandError` | ตรวจ `$LASTEXITCODE` (= 0) และ `INSERT 0 0` · จดใน runbook ว่าเป็นปกติ |
| อ่าน PROMPTS เกินกล่อง text (เห็นผลที่คาด) | จดการปนเปื้อนในข้อ 2 |
| ไม่มี `node_modules` ของ web บน host → typecheck ล่วงหน้าไม่ได้ | ใช้ `next build` ใน `up --build` เป็นตัวตรวจ (ผ่านครั้งแรก) |

## 10. ข้อเสนอแก้พรอมต์

1. **(H)** ส่วนที่ 2 ข้อ 3: เพิ่ม "ครั้งที่ 2 จะขึ้น NOTICE `already exists, skipping` (PowerShell อาจแสดงเป็นตัวแดง) = ปกติ ให้ดู `$LASTEXITCODE` = 0" — หรือใส่ `SET client_min_messages = warning;` ในไฟล์ migration
2. **(H)** ส่วนที่ 2 ข้อ 6 "รัน 3 เบราว์เซอร์" ขัดกับแผน runner (CR LAB = api + chromium) และ RUNNER §3.7 → เลือกอย่างเดียว (เสนอ chromium ใน LAB 8 · 3 เบราว์เซอร์ไว้ LAB 11)
3. **(M)** ข้อ 5/8: ระบุลำดับ "migrate ก่อน rebuild · ถอย: เว็บก่อน down.sql" เป็นข้อความในพรอมต์ (ตอนนี้ถูกเพราะเรียงข้อเท่านั้น) และให้ runbook มีหัวข้อ "ลำดับ"
4. **(M)** ข้อ 6 ติดตั้งใหม่: เพิ่มขั้นรอ init เสร็จ เช่น `docker exec sabai06-fresh sh -c 'until psql -U sabai -d sabai -tAc "select 1 from shop_holiday limit 1" >/dev/null 2>&1; do sleep 1; done'` ก่อนตรวจ ไม่งั้นตรวจเร็วเกินได้ "relation does not exist"
5. **(L)** ส่วนที่ 1 ข้อ 3 "ทุกช่องทางที่จองได้" — ใส่คำใบ้ว่าแชทเรียก `availableSlots()` ผ่าน `freeTimes` (ApiError จะหลุด) ถ้าต้องการให้ผู้เรียนเห็นกับดักนี้
6. **(L)** ข้อความร้าน "วันนี้ร้านหยุด" ใน CR-04-ANSWERS ② อาจปรับเป็น "วันที่เลือกร้านหยุด" (ถ้าไม่ได้ตั้งใจเป็นจุดสอน)

## 11. ภาพที่ควรใช้ + เทียบกับผลที่คาด

| ไฟล์ | คำอธิบาย |
|---|---|
| `design/shots/lab8-shop-closed.png` | `/book` ไม่ล็อกอิน นวดไทย 60 ขั้น 2 เลือก 23/10/2026 → กล่องแดง "วันนี้ร้านหยุด (วันปิยมหาราช) กรุณาเลือกวันอื่น" ปุ่มถัดไปปิด (1280×800 headless · reset ก่อนถ่าย) |
| `design/shots/lab8-migration-twice.txt` | log จริงของ migrate 2 ครั้ง + ตรวจ (count 3 · th_ok t · B14 อยู่ · เว็บเดิม reset 200) |

(⚠️ เห็นผลที่คาดก่อนรันโดยไม่ตั้งใจ — ดูข้อ 2)

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| `GET /api/holidays` 3 แถว | 200 · 3 แถวเรียงวันที่ · ชื่อ 3 ภาษาตรง (H1) | ✅ |
| slots S01 23 ต.ค. → 422 `SHOP_CLOSED` มี "วันปิยมหาราช" | ✅ th/en/zh (H2 H3) | ✅ |
| 22 และ 24 ต.ค. → 200 · 23 รอบ | 200 · 23 รอบ ว่าง 23 ทั้งคู่ (H4) | ✅ |
| price/bookings 23 ต.ค. ทุกแบบ 422 | single/couple/group/package/course → 422 SHOP_CLOSED (H5–H8) | ✅ |
| 5 ธ.ค. ตอนนี้ → `DATE_OUT_OF_RANGE` | ✅ slots + price (H9) | ✅ |
| ที่ now 10 พ.ย. → `SHOP_CLOSED` | ✅ วันพ่อแห่งชาติ (H10) · เพิ่ม 31 ธ.ค. ที่ now 1 ธ.ค. (H11) | ✅ |
| migration 2 ครั้งไม่ error นัดใหม่อยู่ | exit 0 ทั้งคู่ · B14 อยู่ | ✅ |
| `th_ok = t` | t | ✅ |
| reset 2 ครั้ง 200 | 200 · 200 | ✅ |
| check-rules 90/90 | 90/90 | ✅ |
| ติดตั้งใหม่มีตาราง | 20 ตาราง · shop_holiday 3 แถว | ✅ |
| กับดักลืม TABLES → reset 500 | ไม่เกิด (เติม TABLES ตั้งแต่แผน · T2 อยู่ใน CLAUDE.md) | — (ไม่ได้ลองพลาด) |
| ส่วน ข: 14 ต.ค. → 409 `HAS_BOOKINGS` · 15 ต.ค. → 201 | ไม่ได้ทำส่วน ข (ตัดสินแทนผู้เรียน) | — |
| ไปต่อได้เมื่อ: RUNBOOK + `backups/before-cr04.sql` (ไม่ commit) + image `before-cr04` | มีครบ · backups ถูก exclude | ✅ |
