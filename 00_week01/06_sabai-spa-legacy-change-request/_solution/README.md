# 🔑 เฉลยผู้สอน · บท 06 สบายใจ สปา: รับงานแก้ระบบเดิมด้วย Change Request

> ⚠️ **โฟลเดอร์นี้สำหรับผู้สอนเท่านั้น** มีผลจริงทุก LAB · ทะเบียน CR ปลายทาง · เกณฑ์ตรวจ ([GRADING.md](GRADING.md)) · เฉลย Quiz ([QUIZ.md](QUIZ.md)) · เฉลยข้อสอบ ([EXAM-KEY.md](EXAM-KEY.md)) · เครื่องตรวจ ([grader/README.md](grader/README.md))
> ถ้าแจกงานให้ผู้เรียน ให้ลบหรือย้าย `_solution/` ออกก่อน · 🔒 แถวที่ติด 🔒 เกี่ยวกับข้อสอบชุด B ห้ามคัดลง README ของบทหรือภาพ

ไฟล์ผลงานในนี้มาจาก **การรันพรอมต์ของบทครบ LAB 0–12 หนึ่งรอบ** (12 ต.ค. 2026 · 09:33–13:22) โดยให้ Claude สวมบทผู้เรียน ทำทีละ LAB ตามพรอมต์ใน `_design/PROMPTS.md` · ไม่เปิด `_solution/` และเปิด `CHANGE-REQUESTS/answers/CR-0N-ANSWERS.md` **หลัง**เขียนคำถามถึงร้านเสร็จทุกครั้ง · กติกาการรันอยู่ใน [_design/RUNNER.md](_design/RUNNER.md) · LAB 11–12 รันต่อ 12:40–13:22 และเติมผลแล้ว

- **รันใน sandbox แยก** `C:/t/work/b2run/w/` = สำเนาโฟลเดอร์บทที่เป็น git repo ของตัวเอง (commit ตั้งต้น `d617d68`) · โหมด A: runner ทำเองใน Agent-tool session (cwd ≠ `w/` จึงต้องบังคับ `CLAUDE.md` / `.claude/settings.json` เอง) · เซสชันใหม่จริง 1 ครั้งใน LAB 4 (ทดสอบรั้ว deny)
- **พอร์ต:** รอบจริงรันที่ **เว็บ 4100 · db 5533** (D10 · 4000 ถูกบท 05 ใช้ขนานกัน) ด้วย `$env:WEB_PORT` `$env:DB_PORT` `$env:BASE_URL` · ผู้เรียนใช้ **4000 / 5433** · ไฟล์ที่ runner สร้างใน `w/` เขียนค่าผู้เรียน (4000) อยู่แล้ว
- **ขอบเขตเบราว์เซอร์ (M6):** LAB 6–8, 10 รัน e2e-legacy แบบ `api + chromium` และ e2e-cr chromium · 3 เบราว์เซอร์เต็มเฉพาะ LAB 9 ส่วนที่ 3 (และ LAB 11) · LAB 7–8 ข้อ "spec ใหม่ 3 เบราว์เซอร์" รันแค่ chromium ตามคำสั่ง orchestrator
- **จุด "รอผมอนุมัติ" / "ถามผมก่อน"** runner ตัดสินแทนผู้เรียน แล้วจดในหัวข้อ "ตัดสินแทนผู้เรียน" ของแต่ละ result
- ตัวเลขผลจริงทุกตัวในหน้านี้มาจาก [_design/results/LAB*_RESULT.md](_design/results/) (รหัสผ่านบัญชีทดสอบถูกแทนด้วย `<รหัสทดสอบ>`) · ช่องที่ไม่มีข้อมูลจริงเขียนว่า "ไม่ได้วัดในรอบจริง"

---

## สารบัญ

1. [ผู้เรียนควรมีอะไรเมื่อจบบท](#1-ผู้เรียนควรมีอะไรเมื่อจบบท)
2. [ผลจริงทีละ LAB](#2-ผลจริงทีละ-lab)
3. [ทะเบียน CR ปลายทาง](#3-ทะเบียน-cr-ปลายทาง)
4. [ตาข่ายเดิม: ค่าอ้างอิงตลอดบท (regression baseline)](#4-ตาข่ายเดิม-ค่าอ้างอิงตลอดบท-regression-baseline)
5. [REA เห็นอะไร · ไม่เห็นอะไร](#5-rea-เห็นอะไร--ไม่เห็นอะไร)
6. [ปัญหาที่ยังค้างในระบบ (known issues)](#6-ปัญหาที่ยังค้างในระบบ-known-issues)
7. [เวลาจริงต่อ LAB + ข้อเสนอแก้พรอมต์](#7-เวลาจริงต่อ-lab--ข้อเสนอแก้พรอมต์)
8. [ตรวจงาน · ข้อสอบ · เครื่องตรวจ](#8-ตรวจงาน--ข้อสอบ--เครื่องตรวจ)

---

## 1. ผู้เรียนควรมีอะไรเมื่อจบบท

ตำแหน่งไฟล์ = ตำแหน่งในโฟลเดอร์บท (D13: สถานะปลายทางของ `w/` จะคัดมาไว้ใน `_solution/` ตำแหน่งเดียวกันหลังจบ LAB 12) · จำนวนบรรทัดของไฟล์ใหม่ = `git diff --stat d617d68 ef47d72` ใน `w/` (สถานะหลัง LAB 10)

**คัดแล้ว (หลัง LAB 12 · HEAD `ab04036`):** `git diff --name-only d617d68 ab04036` ใน `w/` = 71 ไฟล์ → คัด **70 ไฟล์** มาไว้ตำแหน่งเดียวกัน (ไม่คัด `fast_track/README.md` = การแก้ของ orchestrator ไม่ใช่งานผู้เรียน) · เอกสารราก 8 (`CLAUDE.md` `HANDOVER-CHECK.md` `SYSTEM-MAP.md` `KNOWN-ISSUES.md` `CHANGE-REPORT.md` `REGRESSION-REPORT.md` `RELEASE-NOTES.md` `UAT-CHECKLIST.md`) · `CHANGE-REQUESTS/REGISTER.md` · `.claude/settings.json` · `docs/` 12 (รวม `impact/CR-01…05`) · `db/init/` 2 + `db/migrations/` 2 · `tests/` 11 (cr01–05 · golden 5 · smoke) · `e2e-cr/` 12 · `web/` 19 · `tools/` 2 · diff ซอร์สทั้งก้อน [web-db-solution.diff](web-db-solution.diff) (`d617d68..ab04036` · 70 ไฟล์ +13,527 −39 · 870 KB · ไม่รวม node_modules/.next/rea-out/fast_track) · ไม่คัด `rea-out/` `backups/` `tools/lab*/` (ignored / ไม่ commit) · ไม่มีไฟล์ใด > 1 MB · ไฟล์เทสต์ใช้บัญชี seed เดียวกับ `e2e-legacy/tests/fixtures.ts` ของบท (ไม่ใช่ความลับจริง) · 🔒 แถว "กดใช้บริการเสร็จก่อนถึงเวลานัด" ใน `RELEASE-NOTES.md` ข้อ 10 และ `docs/SPEC-GAPS.md` G9 ติดคอมเมนต์ 🔒 ไว้แล้ว

| ไฟล์ / โฟลเดอร์ | ได้จาก LAB | เนื้อหาในรอบจริง |
|---|---|---|
| `HANDOVER-CHECK.md` · commit baseline | 1 | 107 บรรทัด 9 หัวข้อ · ตารางข้อที่ล้ม 4 แถว · คำอ้าง 19 ข้อ (H1–H12 บันทึกส่งมอบ + H13–H19 README-LEGACY): ✅ 12 · ❌ 2 · ⚠️ 5 · baseline `4a7908f` |
| `docs/REA-INVENTORY.md` · `rea-out/` (ไม่ commit) | 2 | 119 บรรทัด (18,387 B) · endpoint 25 แถวติดป้าย static/runtime/inference/unknown + `[E ev_…]` ทุกแถว · หน้า 14 · "สิ่งที่ REA ไม่เห็น" 8 ข้อ · คำถาม 8 ข้อ · ค่าที่ล็อกเป็น [E] 9 แถว |
| `SYSTEM-MAP.md` · `docs/SPEC-GAPS.md` | 3 | SYSTEM-MAP 262 บรรทัด: route 25 ไฟล์ / 26 handler · BR-01–20 · DB 19 ตาราง · กับดัก T1–T13 · triangulation 23 แถว (✅ 17 · ⚠️ 6 · ❌ 0) · ตรวจทาน 5 แถว · SPEC-GAPS 35 บรรทัด 13 คำถาม (G1–G13) |
| `CLAUDE.md` · `.claude/settings.json` · `docs/IMPACT-TEMPLATE.md` · `docs/ORACLE-CHANGES.md` | 4 | CLAUDE.md 45 บรรทัด 6 หัวข้อ (กติกาการแก้ 9 ข้อ) · deny 1 กฎ `Edit(e2e-legacy/**)` · แม่แบบ impact 60 บรรทัด · ORACLE-CHANGES 11 บรรทัด **ยังว่างถึง LAB 10** |
| `web/app/api/test/clock/route.ts` + `setTestClock()` ใน `web/lib/server/testmode.ts` | 5 | test seam เลื่อนนาฬิกาโดยไม่ล้างข้อมูล · 404 เมื่อ `ALLOW_TEST_RESET=0` · 422 เมื่อค่าไม่ถูก |
| `tests/golden/` (run.mjs · price.json · slots.json · admin-queue.json · README.md) | 5 | 62 เคส (price 50 · slots 6 · admin-queue 6) · SHA-256 ย่อ `a485c485` / `b5eb12a8` / `255ee583` · README 77 บรรทัด (ต้อง `git add -f`) |
| `e2e-cr/` (config + `char-booking` `known-issues` + spec ของ CR-01/03/04/05) · `KNOWN-ISSUES.md` | 5 · 7–10 | KI-01 บัตรปลอมไม่เตือน · KI-02 เบอร์ `abc` จองได้ · KI-03 owner ยกเลิกผ่าน API ได้ (ไม่มี test.fail) |
| `docs/impact/CR-0N.md` ×5 · `tests/cr0N.mjs` ×5 | 6–10 | impact 126–168 บรรทัด/ฉบับ · cr01 22 เคส · cr02 19 · cr03 18 · cr04 14 · cr05 12 |
| `db/migrations/001_shop_holiday.sql` + `.down.sql` · `docs/MIGRATION-RUNBOOK.md` · `backups/before-cr04.sql` (ไม่ commit) | 8 | migration 23 บรรทัด · down 9 · runbook 77 · สำรอง 52,535 ไบต์ |
| `docs/TRACEABILITY.md` · `CHANGE-REPORT.md` · `CHANGE-REQUESTS/REGISTER.md` | 6–10 | TRACEABILITY 22 บรรทัด · CHANGE-REPORT 266 บรรทัด (ส่วน CR-02 03 04 01 05) · REGISTER แถว CR-01–05 สถานะ "ทดสอบผ่าน (รอ UAT)" |
| โค้ดแอปที่แก้ (`web/` `db/init/`) | 6–10 | ดู [ข้อ 3](#3-ทะเบียน-cr-ปลายทาง) คอลัมน์ diff · รวม `git diff --stat d617d68 ef47d72` = **66 ไฟล์ +12,918 −43** (รวม golden JSON 3 ไฟล์ 8,031 บรรทัด และเอกสาร) |
| `REGRESSION-REPORT.md` · TRACEABILITY ฉบับสมบูรณ์ | 11 | `REGRESSION-REPORT.md` 138 บรรทัด 7 หัวข้อ (ผลทุกชุด · REA v1↔v2 · HAR v2 · scenario v2 · CR × REA 5 แถว · diff 66 ไฟล์โยง CR · ค่าคาดหวังเดิม) · `docs/TRACEABILITY.md` ต่อท้ายผล LAB 11 ต่อ CR + ตาราง TC safety-net · `docs/ORACLE-CHANGES.md` +บันทึกตรวจ (ตารางยังว่าง) · ไม่แก้โค้ด/เทสต์ |
| `tests/smoke.mjs` · `RELEASE-NOTES.md` · `UAT-CHECKLIST.md` · `docs/DEPLOY-RUNBOOK.md` | 12 | `tests/smoke.mjs` 78 บรรทัด 7 ข้อ อ่านอย่างเดียว · `docs/DEPLOY-RUNBOOK.md` 86 บรรทัด (ลำดับ 0–7 · เงื่อนไขถอย 4 · ขั้นถอย R1–R4 · ผลซ้อมจริง · ไม่มี `down -v` นอกจากคำเตือน) · `RELEASE-NOTES.md` 166 บรรทัด (5 CR · รอร้านยืนยัน 7 · ยังไม่แก้ 16) · `UAT-CHECKLIST.md` 95 บรรทัด 31 แถว + ลงชื่อ 4 ช่อง · commit `e768ef9` (2 ไฟล์ +164) · `ab04036` (7 ไฟล์ +454 −5) |

**commit ใน `w/` (ลำดับจริง):** `4a7908f` baseline → `8e2ffc6` CLAUDE.md + รั้ว → `3bcd8c9` safety-net → `4dbcb90`/`d982284` CR-02 → `eb0bf69`/`fe187aa` CR-03 → `d221eda`/`7a2dc24` CR-04 → `8aba74e`/`802f853`/`e54fdc5`/`f4edf7b` CR-01 → `15fb782`/`ef47d72` CR-05 (ระหว่างนั้นมี `a9d58de` `3526f06` ของ orchestrator ไม่ใช่งานผู้เรียน) · ทุก CR มี commit เทสต์แดงก่อน commit แก้

---

## 2. ผลจริงทีละ LAB

| LAB | ผลจริง |
|---|---|
| 0 เช็กเครื่อง | Docker Engine 29.5.2 · Node v26.7.0 · ช่วงพอร์ตที่จอง 23 ช่วง มี **2970–3069** (ครอบ 3000) · 4000/5433 ไม่อยู่ในช่วง · 4000 ไม่ว่างเพราะบท 05 เปิดอยู่ → runner ใช้ 4100/5533 · `mcp doctor` exit 0 (tools 170/170 · 3.4 วิ) · CurrentUser RemoteSigned (Process Bypass มาจากเครื่องมือของ agent) · ไม่มีไฟล์ใดถูกแก้ |
| 1 รับมอบ | check-rules **90/90** (19.8 วิ) · e2e-legacy api+chromium 42 รายการ: Playwright สรุป "41 passed · 1 failed" (4.1 นาที) = ผ่านจริง **38** · expected-fail **3** (TC-SEC-04 · TC-GC-04 · TC-TRN-03) · ล้ม **1** (TC-SEC-05 = เทสต์ล้าสมัย: ได้ 422 `COURSE_UNAVAILABLE` ไม่ใช่ 403/404) · คำอ้าง ❌ 2 ข้อ: H6 "ปิด reset ใน production" (ค่าเริ่ม `ALLOW_TEST_RESET=1` · reset 200) และ H9 "ผ่านหมดยกเว้น 3" · Next 15.5.27 · PG 16.15 · DB 19 ตาราง |
| 2 REA black-box | static bundle 79 ไฟล์ 1,149,873 B · analyze **48.1 วิ** (`ev_11d475e1` · summary `ev_24390574`) · endpoint fetch **9** + เศษ `[[...]]` `[]` `[...]` + `/_next/image` ×2 · route file 25 · หน้า 14 · coverage partial · HAR 135 record → เลือก 10 → **7 endpoint / 10 ครั้ง** (`ev_6fbeaec6`) · scenario ผ่าน network `sabai06-net` **12/12 step · ฿1,000** (`ev_8dc23d9f`) · `grep "ระบบไม่มี"` = 0 |
| 3 แผนที่ระบบ | route 25 ไฟล์ / 26 handler (GET 15 · POST 11) · handler ที่ไม่มีผู้เรียกในเว็บ 8 · BR 20 แถว · DB 19 ตาราง · **CHECK 51 · FK 25 · PK 19 · UNIQUE 10 · EXCLUDE 2** (จาก `pg_constraint` · พรอมต์ไม่ได้สั่ง) · `room_id = 1` 2 ที่ (`booking.ts:290` `:376`) · triangulation 23 แถว ✅ 17 ⚠️ 6 · SPEC-GAPS 13 · ตรวจทาน 5 แถว: ตรง 3 · อ้างไม่ครบ 2 · บรรทัดผิด 0 |
| 4 CLAUDE.md + รั้ว | CLAUDE.md 45 บรรทัด · deny `Edit(e2e-legacy/**)` · เซสชันใหม่ลอง Edit `e2e-legacy/playwright.config.ts` → *"File is in a directory that is denied by your permission settings."* · SHA-256 ก่อน/หลังเท่ากัน · ยืนยันทั้งโหมด `bypassPermissions` (yolo) และ `acceptEdits` (orchestrator ทดสอบเพิ่ม) · commit `8e2ffc6` 8 ไฟล์ +553 |
| 5 ตาข่าย | seam: clock → today 2026-10-10 → 2026-10-12 · นัดยังอยู่ · `ALLOW_TEST_RESET=0` → 404 · golden **62/62 ×2 รอบ** · e2e-cr 3 เบราว์เซอร์ ×2 รอบ: ผ่าน 12 · expected-fail 6 · ล้ม 0 (Playwright บอก "18 passed") · mutant X1 X2 X3 ถูกจับ **ทุกตัว** โดย golden (2/62 · 3/62 · 10/62 ต่าง) และ check-rules (88 · 88 · 83/90) · **e2e-cr จับ 0/3** · commit `3bcd8c9` 16 ไฟล์ +8,681 |
| 6 CR-02 | คำถาม 9 (✅ 5 · ◐ 2 · ❌ 2 → สมมติฐาน A1–A4) · ค่าคาดหวัง 18 แถว `[D:CR-02]` · `cr02` แดง **10/19** → เขียว **19/19** · check-rules 90/90 (diff ว่าง · E26 ฿3,000 · E28 ฿4,500 · E79 ฿6,000) · golden 62/62 · e2e-legacy 38/1/3 = baseline · `pricing.ts` +19 −2 · `booking.ts` +1 |
| 7 CR-03 | ทำซ้ำเรื่องร้องเรียน: 3 คำขอได้ 201 B14 B15 B16 · พร้อมกัน 201 B17 B18 · คำถาม 10 (✅ 5 · ◐ 4 · ❌ 1) · `cr03` แดง **5/16** → เขียว **18/18** (+C17 C18 หลังเจอ TC-BOOK-07) · e2e-legacy รอบแรก 37/**2**/3 (TC-BOOK-07 แดงไม่ตั้งใจ) → ย้ายลำดับการตรวจ → 38/1/3 · `cr03.spec` chromium 0/1 → 1/1 · advisory lock ต่อคน · ไม่มี migration |
| 8 CR-04 | migration ครั้งที่ 1 `CREATE TABLE` · **`INSERT 0 3`** · ครั้งที่ 2 NOTICE `already exists, skipping` · **`INSERT 0 0`** · exit 0 ทั้งคู่ (0.28 / 0.27 วิ) · B14 ยังอยู่ · `th_ok = t` · `cr04` แดง **3/14** → **14/14** · spec chromium 1/2 → 2/2 · reset 2 ครั้ง 200 · ติดตั้งใหม่ 20 ตาราง · image ถอย `sabai06-web:before-cr04` · ส่วน ข (หลังร้าน) ไม่ได้ทำ |
| 9 CR-01 | คำถาม 14 (ค้าง Q5 Q9 Q10 Q13) · `cr01` แดง **0/22** (ทุกเคส 404) → **22/22** · `cr01.spec` 3 เบราว์เซอร์ 0/6 → **6/6** · e2e-cr 3 เบราว์เซอร์ ผ่าน 27 · ef 6 · ล้ม 0 · e2e-legacy `test:all` 114 รายการ (13.4 นาที): ผ่านจริง **105** · ef **7** · ล้ม **2** (TC-SEC-05 เดิม + **TC-UI-02 webkit flaky**) · 14 ไฟล์ +933 −23 · 4 commit |
| 10 CR-05 | ค่าคาดหวังจาก SQL 9 คิวรี × 4 ช่วง **ก่อน**เขียนโค้ด · ก.ย. ยืนยัน/เสร็จ/ยกเลิก 0/3/1 · ยอดขาย 1,900 · ส่วนลดระดับ 100 · แต้ม 19 · ครั้งคอร์ส 2 · ต.ค. 6/1/0 · 1,440 · เดือนเกิด 360 · ยอดนัดยืนยัน 11,130 · 92 วัน 200 / 93 วัน 422 `REPORT_RANGE` · `cr05` แดง **1/12** → **12/12** · spec 3 เบราว์เซอร์ 6/6 · CSV BOM `EF BB BF` 4 แถว · R10 ตั้งนาฬิกา 12 ต.ค. 14:00 ก่อนกดเสร็จ B01 → ยอดขาย 2,440 = Σ คิวหลังร้าน |
| 11 regression เต็ม + REA เทียบเวอร์ชัน | check-rules 90/90 · golden 62/62 · cr01–05 22/19/18/14/12 · e2e-cr 3 เบราว์เซอร์ 39: ผ่าน **33** · ef 6 · ล้ม 0 (104 วิ) · e2e-legacy `test:all` 114: Playwright "113 passed · 1 failed" = ผ่านจริง **106** · ef **7** · ล้ม **1** (TC-SEC-05 เดิม) · 12.8 นาที = baseline · TC-UI-02 webkit ผ่านรอบนี้ แต่ `--repeat-each=3` ล้ม 2/3 (flaky เดิม) · REA static v2 49.1 วิ · compare `changed 12 · unknown 711 · added 0` (`ev_ea036036`) · `/account` hash เปลี่ยน (CR-01) · `/admin/report` ใหม่แต่เป็น `unknown` ไม่ใช่ `added` · `/book` hash เดิมทั้งที่ CR-04 ปิดวันหยุด · route ไฟล์ 25 → 30 · HAR v2 7 endpoint status/คีย์เดิมทุกตัว (`ev_ba70ee00` vs `ev_6fbeaec6`) · scenario v2 12/12 ฿1,000 (`ev_d627ab35`) · CR × REA: เห็น CR-01 CR-05 (และ CR-03/04 ทางอ้อมผ่าน chunk i18n `8561`) · ไม่เห็น CR-02 → พิสูจน์แทนด้วย cr02 + golden |
| 12 ส่งมอบ + ซ้อมถอยกลับ | smoke 7 ข้อ: 7/7 exit 0 → หยุดเว็บ 0/7 exit **1** (`ECONNREFUSED`) → 7/7 exit 0 · สำรอง `before-rollback.sql` 53,469 B · จอง **B14** → `001_shop_holiday.down.sql` (`to_regclass` ว่าง · B14 อยู่) → up ซ้ำ `INSERT 0 3` (B14 อยู่) → DB `down`→`up` ไม่มี `-v` 7.8 วิ (B14 อยู่ · volume อยู่) → cr04 14/14 · ซ้อมทั้งก้อน ~17 วิ · B14 หายหลังขั้น 6 เพราะ cr04 reset ไม่ใช่เพราะถอย · RELEASE-NOTES 5 CR · รอยืนยัน 7 · ยังไม่แก้ 16 · UAT 31 แถว โยง TC 30/31 (ขาด CR-04 ส่วน ข) · REGISTER 5 แถว "รอตรวจรับ (UAT)" · พบ race ใหม่ในกล่องเลื่อนนัด CR-01 (2/4 รอบ · เซิร์ฟเวอร์ปฏิเสธ ไม่มีข้อมูลผิด) |

### หมายเหตุรายละเอียดสำคัญ

- **ความ "ตาบอด" ต่อผลที่คาด:** runner อ่านพรอมต์ด้วยช่วงบรรทัดแล้วเห็นบล็อก "ผลที่คาด" ก่อนรันใน LAB 0–6 และ 8–9 (จดไว้ทุก result) · **LAB 7 และ 10 ตาบอดจริง** · ตัวเลขทุกตัวนับจาก log จริง แต่การเลือกเคสบางเคส (LAB 6 B04/C17 · LAB 9 R6 R7 R13–R15) อาจถูกชี้นำ
- **LAB 1:** `--reporter=list` แทนที่ reporter ใน config → ไม่มี `test-report/html` (`npm run report` ใน README-LEGACY ใช้ไม่ได้) · `x` ใน list = ทั้ง expected-fail และ failed → AI ที่นับ `x` ตรง ๆ ได้ "ล้ม 4" ผิด
- **LAB 2:** static เห็น call แค่ URL ค่าคงที่ · `/api/slots` `/api/admin/bookings?date=` `/api/bookings/{id}/cancel` เห็นจาก HAR เท่านั้น · `--sensitive-value` ตัด body ของ login ทั้งก้อน · `record-har.mjs` จอง B14 + ยกเลิก B05 (ข้อมูลเปลี่ยน)
- **LAB 3:** `\d booking` + `\d booking_slot` อย่างเดียวนับได้ CHECK 23 / FK 6 · หัวไฟล์ schema เขียน "ERD 17 ตาราง" แต่ DB มี 19 · พบ 🔒 X4/G9 (กดใช้บริการเสร็จได้ก่อนเวลานัด = ข้อสอบชุด B ข้อ 5) — ห้ามลง README/ภาพ
- **LAB 4:** `yolo.cmd` ทับโหมดเป็น `bypassPermissions` แต่ deny ยังปฏิเสธ · รั้วไม่กันการอ่านและไม่กัน shell (agent ในเซสชันใหม่ชี้เอง) · `git add -A` รวม SYSTEM-MAP/SPEC-GAPS/REA-INVENTORY ที่ LAB 1–3 ไม่ได้ commit
- **LAB 5:** `.git/info/exclude` บรรทัด `README.md` ไม่มี `/` → `tests/golden/README.md` หายจาก `git add` เงียบ ๆ ต้อง `git add -f` · aria snapshot ที่ Playwright สร้างแปลงยอดเงินเป็น regex (ไม่ล็อกเงินจริง) → เขียน template เอง · KI-01 เป็น "ข้อความวูบ" ~250 ms
- **LAB 6:** C9 (Gold กลุ่ม 3) ยอด ฿2,850 เท่าเดิมแต่ `discountKind` tier → group = เคสที่ "ยอดเท่าเดิมแต่ต้องแดง" · ตาข่ายเดิมทั้งหมดล็อกวันที่ 10 ต.ค. จึงมองไม่เห็น CR-02 เลย
- **LAB 7:** error ของ API ใช้ภาษาจาก cookie `lang` ไม่ใช่ `body.lang` · `errorBody()` เดิมไม่รับตัวแปร → แตะ `http.ts` · TC-BOOK-05 (ดับเบิลแตะ) ผ่านทั้งก่อน/หลัง = เหตุที่ทีมเดิมคิดว่ากันซ้ำแล้ว
- **LAB 8:** ถ้า rebuild เว็บก่อนรัน migration → slots/price/bookings/reset ตอบ 500 · migration ก่อน = เว็บเดิมทำงานต่อได้ (reset 200) · ถอย = เว็บก่อน `down.sql` · แชทต้องเช็กวันหยุดในขั้นเลือกวัน ไม่งั้น ApiError หลุดเป็น 422
- **LAB 9:** กับดัก "นับนัดตัวเอง" 3 จุด (นักบำบัด · ห้องคู่ · BR-21 ของ CR-03) · `canUseCourse()` เดิมต้องเหลือ ≥ 1 → ใช้กับนัดที่กันครั้งแล้วไม่ได้ · `booking.period` GENERATED แต่ `booking_slot.period` ต้อง UPDATE เอง · spec แดงใช้ 301 วิ (รอ timeout 90 วิ)
- **LAB 10:** seed ไม่มีนัดที่วัน UTC ≠ วันไทย (`q_tz` = 0) → เทสต์ seed พิสูจน์เรื่องโซนเวลาได้จำกัด · R12 (แชทไม่รั่ว) ผ่านตั้งแต่ก่อนแก้ → แดง 11/12 ไม่ใช่ 12/12 · ตรวจ CSV ด้วย Node (ไม่มี Excel ใน sandbox)

---

## 3. ทะเบียน CR ปลายทาง

สถานะใน `CHANGE-REQUESTS/REGISTER.md` หลัง LAB 10 · ลำดับในบทเรียงเล็ก → ใหญ่ (กฎ → บั๊ก → schema → ฟีเจอร์ → รายงาน) ไม่ใช่ตามเลข CR

| CR | เรื่อง | LAB | คำถามถึงร้าน | เทสต์ใหม่ แดง → เขียว | commit แดง → แก้ | diff (commit แก้) | สถานะ | ยังค้าง |
|---|---|---|---|---|---|---|---|---|
| CR-02 | ส่วนลดกลุ่มขั้นบันได มีผล 1 พ.ย. 2569 | 6 | 9 (✅ 5 · ◐ 2 · ❌ 2) | `cr02` 10/19 → 19/19 | `4dbcb90` → `d982284` | 7 ไฟล์ +89 −7 · โค้ด `pricing.ts` +19 −2 · `booking.ts` +1 | ทดสอบผ่าน (รอ UAT) | สมมติฐาน ⚠️ A1–A4 (กลุ่ม 2 คน · จองใหม่ใช้อัตราใหม่ · ไม่มีวันสิ้นสุด · แชทไม่เพิ่ม) |
| CR-03 | ลูกค้าโดนจองซ้ำ 2 นัด (ด่วน) | 7 | 10 (✅ 5 · ◐ 4 · ❌ 1) | `cr03` 5/16 → 18/18 · `cr03.spec` 0/1 → 1/1 (chromium) | `eb0bf69` → `fe187aa` | 10 ไฟล์ +145 −17 · โค้ด 4 ไฟล์ ~39 บรรทัด (`booking.ts` +35 · `i18n.ts` +2 · `http.ts` 1 · `chat.ts` 1) | ทดสอบผ่าน (รอ UAT) | Q3 `+66` vs `0` · Q10 จองแทนคนอื่นด้วยเบอร์ตัวเอง |
| CR-04 | วันหยุดร้าน | 8 | 10 | `cr04` 3/14 → 14/14 · `cr04.spec` 1/2 → 2/2 (chromium) | `d221eda` → `7a2dc24` | 17 ไฟล์ +254 −10 · โค้ดเว็บ 6 ไฟล์ +64 · migration 001 + down | ส่วน ก ทดสอบผ่าน (รอ UAT) | **ส่วน ข (หลังร้านเพิ่ม/ลบวันหยุดเอง) ยังไม่ทำ** · Q4 นัดเดิมที่ตรงวันหยุด (ไม่มีใน seed) |
| CR-01 | ลูกค้าเลื่อนนัดเองได้ | 9 | 14 (ค้าง 4) | `cr01` 0/22 → 22/22 · `cr01.spec` 0/6 → 6/6 (3 เบราว์เซอร์) | `8aba74e` → `802f853` · `e54fdc5` → `f4edf7b` | 14 ไฟล์ +933 −23 · โค้ดแอป 8 ไฟล์ · endpoint ใหม่ 2 (`reschedule` · `reschedule-slots`) | ทดสอบผ่าน (รอ UAT) | Q5 นัด "ใครก็ได้" · Q9 เลื่อนไปวันหยุดร้าน (ตัดสินแทน: `SHOP_CLOSED`) · Q10 แพ็กเกจ · Q13 ประวัติการเลื่อน |
| CR-05 | รายงานยอดสำหรับเจ้าของร้าน | 10 | 12 (ตอบตรง 6 · ตัดสินแทน 7) | `cr05` 1/12 → 12/12 · `cr05.spec` 6/6 (3 เบราว์เซอร์ · เขียนหลังทำหน้า) | `15fb782` → `ef47d72` | 13 ไฟล์ +944 −7 · โค้ดเว็บ 6 ไฟล์ · i18n ใหม่ 24 key × 3 ภาษา | ทดสอบผ่าน (รอ UAT) | ข้อที่ตัดสินแทนร้าน Q2 Q4 Q5 Q7 Q9 Q11 |

- ทุก CR: `git diff -- web/scripts/check-rules.mjs tests/golden e2e-legacy` = ว่าง · ไม่มีแถวใหม่ใน `docs/ORACLE-CHANGES.md` · ไม่มี `docker compose down -v`
- คอลัมน์ "ผลตรวจรับ" ใน REGISTER ยังว่าง: หลัง LAB 12 สถานะทั้ง 5 แถว = **รอตรวจรับ (UAT)** + ข้ออ้างอิงใน `UAT-CHECKLIST.md` (1.1–1.6 · 2.1–2.6 · 3.1–3.6 · 4.1–4.6 · 5.1–5.6) + commit hash · คอลัมน์ "ผลตรวจรับ" ยังว่างทั้ง 5 แถว (รอร้านลงชื่อ = ถูกต้อง ผู้เรียนต้องไม่กรอกแทนร้าน)
- **ค่าคาดหวังที่ต้องตรงเป๊ะ** (ร้านยืนยัน ③ หรือ SQL): CR-02 กลุ่ม 3/4/5/6 จอง 1 พ.ย. นัด 5 พ.ย. = ฿2,850 / ฿3,600 / ฿4,250 / ฿5,100 · 31 ต.ค. 23:59 กลุ่ม 3 = ฿3,000 · ใบสรุปข้ามเที่ยงคืน → 409 `PRICE_CHANGED` ฿2,850 · B04 ยัง ฿4,500 · CR-03 ซ้ำนัด B03 → 409 `DUPLICATE_BOOKING` existing B03 · พร้อมกัน `[201, 409]` · CR-04 23 ต.ค. → 422 `SHOP_CLOSED` "วันปิยมหาราช" · 5 ธ.ค. ตอน 10 ต.ค. → `DATE_OUT_OF_RANGE` · CR-01 B05 → 12 ต.ค. 10:00 = 200 ฿760 · 10:01 → 422 `RESCHEDULE_TOO_LATE` · B02 19:00 → 19:30 = 200 · คอร์ส C02 reserved 1 · CR-05 ตามแถว LAB 10 ข้อ 2 (รายละเอียดใน [GRADING.md](GRADING.md))

---

## 4. ตาข่ายเดิม: ค่าอ้างอิงตลอดบท (regression baseline)

ตาข่าย 3 ชั้น: ① `check-rules.mjs` 90 เคส ② `e2e-legacy/` 42 รายการ (api 6 + chromium 36 · 3 เบราว์เซอร์ = 114) ③ golden ที่ผู้เรียนสร้าง (LAB 5) · e2e-legacy เขียนเป็น **ผ่านจริง / ล้ม / expected-fail** (Playwright นับ expected-fail รวมใน "passed")

| จุดเวลา | check-rules | e2e-legacy | golden | e2e-cr | เทสต์ CR |
|---|---|---|---|---|---|
| LAB 1 รับมอบ | 90/90 (19.8 วิ) | api+chromium **38 / 1 / 3** (TC-SEC-05 ล้ม · 4.1 นาที) | — | — | — |
| LAB 5 ตาข่าย | 90/90 (หลังคืน mutant) | ไม่ได้รัน | 62/62 ×2 รอบ | 3 เบราว์เซอร์ ผ่าน 12 · ef 6 ×2 รอบ | mutant: golden 3/3 · check-rules 3/3 · e2e-cr 0/3 |
| LAB 6 CR-02 | 90/90 · diff ว่าง | 38 / 1 / 3 (4.0 นาที) | 62/62 | chromium 4 + ef 2 | cr02 19/19 |
| LAB 7 CR-03 | 90/90 · diff ว่าง | รอบแรก 37 / **2** / 3 (TC-BOOK-07) → รอบสุดท้าย **38 / 1 / 3** | 62/62 | chromium 5 + ef 2 | cr02 19 · cr03 18/18 |
| LAB 8 CR-04 | 90/90 | 38 / 1 / 3 (251 วิ) | 62/62 | chromium 7 + ef 2 | cr02 19 · cr03 18 · cr04 14/14 |
| LAB 9 CR-01 | 90/90 (2 รอบ) | `test:all` 114: **105 / 2 / 7** (TC-SEC-05 + TC-UI-02 webkit) · 13.4 นาที | 62/62 | 3 เบราว์เซอร์ 27 + ef 6 | cr01 22 · cr02 19 · cr03 18 · cr04 14 |
| LAB 10 CR-05 | 90/90 | 38 / 1 / 3 (245 วิ) | 62/62 | chromium 11 + ef 2 | cr01 22 · cr02 19 · cr03 18 · cr04 14 · cr05 12/12 |
| LAB 11 regression เต็ม | 90/90 (19.0 วิ) | `test:all` 114: **106 / 1 / 7** (TC-SEC-05 · 12.8 นาที) · TC-UI-02 webkit ผ่าน (rerun ×3 ล้ม 2) | 62/62 (1.2 วิ) | 3 เบราว์เซอร์ 33 + ef 6 · ล้ม 0 (104 วิ) | cr01 22 · cr02 19 · cr03 18 · cr04 14 · cr05 12 (ทั้งหมดเขียว) |

- **expected-fail ที่ต้องเห็น:** api+chromium = TC-SEC-04 · TC-GC-04 · TC-TRN-03 (3) · `test:all` = TC-SEC-04 ×1 (project api) + TC-GC-04 ×3 + TC-TRN-03 ×3 = 7 · e2e-cr = KI-01b · KI-02b ต่อเบราว์เซอร์
- **ล้มที่เป็นค่าปกติของ baseline:** TC-SEC-05 (เทสต์ล้าสมัย · ห้ามแก้ค่าคาดหวังโดยไม่มี CR)
- **TC-UI-02 webkit (`/skin`) flaky ของเดิม:** `--repeat-each=3` บน image ปัจจุบันล้ม 2/3 · บน image `before-cr04` (ก่อน CR-04 และ CR-01) ที่พอร์ต 4101 ล้ม 1/3 → ไม่ใช่ regression ของ CR · ผลที่คาดของ LESSON-PLAN ("113 passed · 1 failed") ผ่านโดยบังเอิญ
- **"เทสต์เขียว ≠ ไม่มีบั๊ก":** check-rules 90/90 ตั้งแต่รับมอบ ทั้งที่ระบบมีบั๊กจริง (ข้อ 6) · ตาข่ายเดิมมองไม่เห็น CR-02 เลยเพราะล็อกวันที่ 10 ต.ค. — ถ้าเปลี่ยนค่าคงที่ตรง ๆ โดยไม่มีวันมีผล E26/E28/E79 + golden จะแดงทันที (= ตาข่ายกัน "เปลี่ยนเกินวันมีผล")

---

## 5. REA เห็นอะไร · ไม่เห็นอะไร

| คำถาม | REA ตอบได้ไหม | หลักฐานรอบนี้ |
|---|---|---|
| bundle ที่ส่งมอบเรียก API อะไร | ได้บางส่วน (static · coverage partial) | `ev_11d475e1`: fetch 9 ตัวที่ URL เป็นค่าคงที่ · route file 25 (ชื่อไฟล์) · หน้า 14 · statistics: modules 346 · findings 950 · parse_failures 0 · limitations 25 ใน view (`limitation_count` ใน summary = 14 → ต้องบอกว่านับจากไหน) |
| เส้นทางจริงของลูกค้าเรียกอะไร | ได้ เฉพาะเส้นทางที่เดิน (HAR) | `ev_6fbeaec6`: 7 endpoint / 10 ครั้ง · `/api/bookings` 201 + `quotedTotal` · `/api/slots` `/cancel` `/admin/bookings` เห็นจาก HAR เท่านั้น (LAB 3 ยืนยัน: `BookingWizard.tsx:144` ใช้ template literal) · cookie `sabai_session` อายุ 7 วัน |
| ทำไม `/api/me` `/api/me/bookings` `/api/services` ไม่อยู่ใน HAR | ไม่ได้ (browser-only) | หน้าเป็น Server Component อ่านฝั่งเซิร์ฟเวอร์ · LAB 3 นับ handler ที่ไม่มีผู้เรียกในเว็บ 8 ตัว → **หาไม่เจอ ≠ ไม่ได้ใช้** |
| ค่าที่ล็อกเป็น [E] ได้ | ได้ | scenario `ev_8dc23d9f` S01 เดี่ยว 12 ต.ค. 15:00 → ฿1,000 · LAB 5 ใช้เป็น oracle ของ `CHAR-BOOK-01` (`data-amount` 1000 ตรง) |
| กฎฝั่งเซิร์ฟเวอร์ / DB (ส่วนลด · BR-21 · CHECK 51 · EXCLUDE 2) | ไม่ได้ | REA ไม่อ่าน Postgres และไม่เห็นโค้ด server · ใช้อ่าน repo + `pg_constraint` + เทสต์ API แทน (triangulation 23 แถว · ช่อง REA ที่ไม่เห็นเขียน "REA ไม่เห็น" + เหตุผล) |
| ความลับใน HAR | — | `<รหัสทดสอบ>` ไม่อยู่ใน `har-api.json` แต่อยู่ใน `journeys.har` ดิบ 1 จุด → ห้าม commit/ส่งต่อ `.har` |
| v1 ↔ v2 เปลี่ยนตรงหน้าที่ CR แตะไหม | ได้บางส่วน: compare `changed 12 · unknown 711 · added 0` · changed ที่เป็นโค้ดหน้าเว็บ = `account/page` 2 module (CR-01) + chunk ร่วม `8561` (i18n: `DUPLICATE_BOOKING` `SHOP_CLOSED` `RESCHEDULE_*` `REPORT_RANGE` → CR-01/03/04/05 · ต้องเปิดสตริงเอง) · ที่เหลือ = polyfills/main/webpack/framework/build id · หน้าใหม่ `/admin/report` (CR-05) เป็น `unknown` ไม่ขึ้น `added` → ใช้ `pages`/`endpoints` (route 25 → 30) · `/book` และ `(layout)` hash เดิมแม้โค้ดแก้ (กฎฝั่งเซิร์ฟเวอร์/server component) · CR-02 ไม่เห็นเลย = "REA ไม่เห็น ≠ ไม่ได้เปลี่ยน" | static v2 `ev_f54183d0` (37.4 MB · 49.1 วิ · module 449) · compare `ev_ea036036` (input `cmp.json` 71 MB · 12 วิ) |
| HAR v2 + scenario v2 = เส้นทางเดิมไม่เปลี่ยน | ได้: HAR v2 136 entries (v1 135) · `/api/*` 10 ครั้ง · 7 endpoint status + คีย์ body เดิมทุกช่อง · `POST /api/bookings` 201 body 15 คีย์เท่า v1 · ไม่มี `/api/holidays` (เส้นทางเดิมไม่เรียก) · `ev_ba70ee00` vs `ev_6fbeaec6` | ได้: 12/12 step · 2,081 ms · ฿1,000 `data-amount=1000` · png เหมือน v1 ทุก byte · `ev_d627ab35` = `ev_8dc23d9f` (ต้อง reset ข้อมูลหลังเก็บ HAR/scenario) |

---

## 6. ปัญหาที่ยังค้างในระบบ (known issues)

สถานะหลัง LAB 10 · ไม่มี CR สั่งแก้จึงไม่แก้ (ยกเว้นที่ระบุ) · ข้อ "ถามร้าน" ควรอยู่ใน `RELEASE-NOTES.md` ของ LAB 12

| เรื่อง | หลักฐาน | เจอที่ | สถานะ |
|---|---|---|---|
| logout ไม่เพิกถอน session (cookie เดิม `GET /api/me` ยัง 200 · stateless 7 วัน) | TC-SEC-04 (test.fail) · `logout/route.ts:7-8` | LAB 1 · 2 · 3 | ยังไม่แก้ · ผู้รับเหมาเรียก "ไม่กระทบการใช้งาน" |
| รหัส Gift Card ที่ไม่มีจริง หน้าจองไม่เตือน (API 404/422 `GC_NOT_FOUND` · ข้อความวูบ ~250 ms) | TC-GC-04 · KI-01 · `BookingWizard.tsx:182` `:186` `:188` | LAB 1 · 5 | ยังไม่แก้ |
| ติ๊กรถรับส่งไม่ใส่ระยะ/โรงแรม ไปขั้น 4 ได้ | TC-TRN-03 | LAB 1 | ยังไม่แก้ |
| เบอร์ `abc` จองได้ 201 · และ BR-21 (CR-03) ข้ามเพราะไม่มีตัวเลขให้เทียบ → จองซ้ำได้ไม่จำกัด | KI-02 · LAB 7 §8 | LAB 5 · 7 | ยังไม่แก้ · ถามร้านรูปแบบเบอร์ |
| owner ยกเลิกนัดลูกค้าผ่าน API ได้ (หน้า `/admin` ไม่มีปุ่ม · ยังติดกฎ 24 ชม.) | KI-03 · G13 · `booking.ts:465-467` | LAB 3 · 5 | ไม่แน่ใจว่าตั้งใจ → ถามร้าน |
| TC-SEC-05 ล้าสมัย (ได้ 422 `COURSE_UNAVAILABLE` · ข้อความ "เหลือ 0 ครั้งหรือหมดอายุ" ชวนเข้าใจผิด) | LAB 1 | LAB 1 | แดงค้าง · แก้ค่าคาดหวังได้เมื่อมี CR + ORACLE-CHANGES |
| `ALLOW_TEST_RESET` ค่าเริ่ม 1 (compose + `config.ts`) → reset เปิดไม่ต้องล็อกอิน · `/login` โชว์บัญชีทดสอบ · "วันนี้" ค้าง 10 ต.ค. → **อัตรา CR-02 จะไม่มีผลเองถ้าขึ้นจริงด้วยค่าเริ่ม** | H6 ❌ · G7 · T9 | LAB 1 · 3 · 6 | ความเสี่ยงคงค้างใน CHANGE-REPORT |
| ระยะรถปัดทศนิยมก่อนเทียบ: 15.04 กม. รับ ฿300 · 5.04 ฟรี | G4 · `transport.ts:19-22` | LAB 3 | ถามร้าน |
| ฐานแต้มหัก Gift Card ทั้งก้อน (U06 + GCPART ได้ 0 แต้ม) | G5 · `points.ts:29-31` | LAB 3 · 5 | ถามร้าน |
| แพ็กเกจไม่ได้ส่วนลดระดับสมาชิก (SPEC เงียบ) | G6 · `pricing.ts:48` | LAB 3 | ถามร้าน |
| 🔒 กด "ใช้บริการเสร็จ" ได้ก่อนเวลานัด (`completeBooking()` ไม่ตรวจเวลา) | G9 · X4 · `booking.ts:493-501` (LAB 3) / `:534-581` (หลัง CR) | LAB 3 · 10 | 🔒 ข้อสอบชุด B ข้อ 5 · ห้ามลง README/ภาพ · LAB 10 R10 ตั้งนาฬิกาถึงเวลานัดก่อนกด (D12) |
| ช่องจำนวนคน `max={20}` ขณะกฎสูงสุด 6 | X8 · `BookingWizard.tsx:331` | LAB 3 | เซิร์ฟเวอร์ตอบ `GROUP_CALL_SHOP` อยู่แล้ว |
| คิวหลังร้าน join `booking_slot` ไม่กรอง `active` | X9 · `admin.ts:15` | LAB 3 | ไม่ได้ยืนยัน runtime |
| Gift Card หมดอายุ "วันนี้" ยังใช้ได้ (`SABAI-GC-LAST`) | golden `single-S01-U02-GCLAST` | LAB 5 | ถามร้าน |
| error ของ API ไม่สนใจ `body.lang` (ใช้ cookie) | `http.ts:39` | LAB 7 | ของเดิม |
| นัดซ้ำที่มีอยู่แล้วในฐานจริงไม่ถูกตรวจ/รายงาน | CR-03 Q9 นอกขอบเขต | LAB 7 | เสนอรายงาน SQL ให้ร้าน |
| ข้อความร้าน "วันนี้ร้านหยุด (…)" ใช้คำว่า "วันนี้" ทั้งที่ลูกค้าเลือกวันอื่น | CR-04 ② ใช้คำต่อคำ | LAB 8 | ความเสี่ยงใน CHANGE-REPORT |
| CR-04 ส่วน ข (หลังร้านจัดการวันหยุด) | REGISTER | LAB 8 | ยังไม่ทำ · down migration ทำวันหยุดที่ร้านเพิ่มเองหาย |
| TC-UI-02 webkit flaky (`/skin` → `skin-recs` ไม่ขึ้นใน 15 วิ) | `tc-ui-02-rerun.log` · `tc-ui-02-old-image.log` | LAB 9 | ของเดิม · ไม่แก้เทสต์ |
| ปุ่ม "ยกเลิกนัด" ที่ disabled contrast ต่ำ · `myBookings()` ไม่กรอง `active` | LAB 9 §8 | LAB 9 | ของเดิม |
| รายงานไม่มียอดขายบัตรของขวัญ/แพ็กคอร์ส (`gift_card` `course_purchase` ไม่อยู่ใน booking) | LAB 10 §8 | LAB 10 | นอก CR-05 |
| ที่ค้างหลังส่งมอบ | `RELEASE-NOTES.md` "เรื่องที่ยังไม่ได้แก้" 16 ข้อ (ภาษาคน · ผลกระทบ + ข้อเสนอ): ครบ 6 ข้อที่คาด (cookie หลังออกจากระบบ · บัตรปลอมไม่เตือน · เบอร์ไม่ตรวจรูปแบบ · owner ยกเลิกแทน · ปิดโหมดทดสอบ/reset · ติ๊กรถไม่ใส่ระยะ) + ระยะปัดเศษ · แต้มบัตรของขวัญ · แพ็กเกจไม่มีส่วนลดระดับ · ห้องคู่ 1 ห้อง · TC-UI-02 Safari · CR-04 ส่วน ข · เอกสาร 1.0 ไม่ตรง · ใหม่: race กล่องเลื่อนนัด (CR-01) · ข้อ 10 = แถว 🔒 บนสุดของตารางนี้ (ติดคอมเมนต์ 🔒 ในไฟล์แล้ว) · รายงาน CR-05 แสดงรหัสนักบำบัด T01… แทนชื่อ อยู่ใน "รอร้านยืนยัน" | 12 | |

---

## 7. เวลาจริงต่อ LAB + ข้อเสนอแก้พรอมต์

### 7.1 เวลา

จากหัวตาราง "เวลาเริ่ม · จบ · ใช้ไป" ของแต่ละ result (นาฬิกาเครื่อง 12 ต.ค. 2026) · runner (agent) เร็วกว่าผู้เรียนมาก: ไม่ต้องอ่านทวน ไม่รอคน · คอลัมน์ "แผน" = [คาด] จาก `_design/LESSON-PLAN.md` §6

| LAB | เริ่ม | จบ | ใช้ไป | งานเครื่องที่นานที่สุด | แผน [คาด] |
|---|---|---|---|---|---|
| 0 | 09:33 | ~09:36 | ~3 นาที | `mcp doctor` 3.4 วิ | 5 |
| 1 | 09:35 | 09:44 | ~9 นาที | e2e-legacy api+chromium 4.1 นาที · build 8.1 วิ (cache) | 30 |
| 2 | 09:46 | 09:50 | ~4 นาที | analyze 48.1 วิ | 35 |
| 3 | 10:03 | 10:12 | ~9 นาที | psql < 1 วิ/คำสั่ง | 40 |
| 4 | 10:14 | 10:17 | ~3 นาที | เซสชันทดสอบรั้ว 15.2 วิ | 20 |
| 5 | 10:20 | 10:38 | ~18 นาที | e2e-cr 3 เบราว์เซอร์ 68 + 64 วิ · rebuild ต่อ mutant 38–43 วิ | 90 |
| 6 | 10:41 | ~10:58 | ~17 นาที | e2e-legacy 244 วิ · rebuild 39 วิ | 45 |
| 7 | 10:58 | ~11:27 | ~29 นาที | e2e-legacy 252 + 244 วิ (2 รอบเพราะ TC-BOOK-07) | 75 |
| 8 | 11:25 | ~11:42 | ~17 นาที | e2e-legacy 251 วิ · rebuild 41 วิ | 75 |
| 9 | 11:41 | ~12:22 | **~41 นาที** | `test:all` **802 วิ (13.4 นาที)** · spec แดง 301 วิ | 90 |
| 10 | 12:21 | ~12:40 | ~19 นาที | e2e-legacy 245 วิ · rebuild 39 วิ | 60 |
| **รวม 0–10** | 09:33 | 12:40 | **~169 นาที** (ผลรวมแถว) | | 565 |
| 11 | 12:40 | ~13:05 | ~24 นาที | `test:all` **768.7 วิ (12.8 นาที)** · e2e-cr 3 เบราว์เซอร์ 104 วิ · REA analyze v2 49.1 วิ | 55 |
| 12 | 13:05 | ~13:22 | ~17.5 นาที | ซ้อมถอยทั้งก้อน ~17 วิ (DB down→up 7.8 วิ) · ตรวจ UAT บนหน้าเว็บ Playwright 4 รอบ ~1.5 นาที | 35 |
| **รวม 0–12** | 09:33 | 13:22 | **~211 นาที** (ผลรวมแถว · 0–10 169 + 11 ~24 + 12 ~17.5) | | 655 |

> เวลาเครื่องที่ผู้เรียนจะเห็นนานกว่านี้: build แรกของรอบนี้ใช้ cache (8.1 วิ) · `npx playwright install` 1.4 วิ เพราะเบราว์เซอร์อยู่ในแคชจากบท 04/05 · rebuild หลังแก้โค้ดในรอบนี้ 39–51 วิ

### 7.2 ข้อเสนอแก้พรอมต์ (ระดับ H และ M ที่เกิดซ้ำ)

รวมจากหัวข้อ "ข้อเสนอแก้พรอมต์" ของทุก result · ยังไม่ได้ยืนยันว่าปรับลง README ของบทแล้ว (ดู `_design/PROMPT-FIX-LOG.md`)

| LAB | ระดับ | ปัญหา | ข้อเสนอ |
|---|---|---|---|
| 6 7 8 9 10 | **H** | ส่วนที่ 1 อยู่ใน Plan mode แต่สั่ง "ทำ `docs/impact/CR-0N.md`" — Plan mode เขียนไฟล์ไม่ได้ | "เสนอคำถาม + impact ในแผน · หลังผมอนุมัติ (ออก Plan mode) ให้บันทึก `docs/impact/CR-0N.md` เป็นขั้นแรก" |
| 7 8 | **H** | ส่วนที่ 2 สั่ง spec ใหม่ "3 เบราว์เซอร์" ขัดกับ M6 (api + chromium) | เลือกอย่างเดียว · ถ้า 3 เบราว์เซอร์ให้เขียน `--project=` ครบ |
| 2 | **H** | "ใช้เฉพาะคำสั่งข้างล่าง" แต่ไม่มีคำสั่งให้ evidence_id / summary / สถานะ scenario / รายการหน้า | เพิ่มคำสั่งใน `rea-tools.mjs` (`ids` `summary` `scenario-sum` `pages`) |
| 3 | **H** | ผลที่คาด "CHECK 51 · FK 25" ไม่มีขั้นที่ให้ตัวเลขนี้ · "route 25" กำกวม (25 ไฟล์ / 26 handler) | เพิ่มคิวรี `pg_constraint` · ระบุหน่วยนับ |
| 5 | **H** | `.git/info/exclude` `README.md` ไม่ anchor → `tests/golden/README.md` หายจาก commit | เขียน `/README.md` · หรือสั่งตรวจ `git status` ก่อน commit |
| 8 | **H** | NOTICE ครั้งที่ 2 ขึ้นเป็น `NativeCommandError` สีแดงใน PS 5.1 | บอกว่า "ปกติ ดู `$LASTEXITCODE` = 0" หรือ `SET client_min_messages = warning;` |
| 10 | **H** | ส่วนที่ 1 สั่ง `psql -c "<SQL>"` ขัด CLAUDE.md ข้อ 5 (`docker cp` + `-f`) และ SQL หลายคิวรีผ่าน `-c` ใน PowerShell พังง่าย | ใช้ไฟล์ SQL + `-v ON_ERROR_STOP=1 -f` |
| 1 | M | ข้อ 7 ไม่มีกรณี "เป็น repo อยู่แล้ว toplevel = โฟลเดอร์นี้" · `--reporter=list` ทำให้ไม่มีรายงาน html | เพิ่มกรณีที่ 3 · ใช้ `--reporter=list,html` |
| 4 | M | ขอบเขต `git add` ไม่ชัด · "Write(...) ใช้กับไฟล์ไม่ได้" ชวนสับสน | `git add -A` (รวมไฟล์ LAB 2–3) · "กฎ Edit(...) กันทุกเครื่องมือแก้ไฟล์" |
| 6 | M | path template `docs/IMPACT-CR-0N.md` ≠ พรอมต์ `docs/impact/CR-0N.md` · ลำดับ commit / REGISTER | ให้ตรงกัน · อัปเดต REGISTER ก่อน commit |
| 7 | M | impact ไม่ไล่เทสต์เดิมที่ "เจ้าของนัดจองทับนัด seed ของตัวเอง" → TC-BOOK-07 แดง | ถ้าตั้งใจเป็นบทเรียน ให้ใส่ใน "ผลที่คาด" · หรือใบ้ `grep -n "U02\|B02" e2e-legacy/tests` |
| 8 | M | ลำดับ deploy (migrate ก่อน rebuild · ถอย: เว็บก่อน down) อยู่แค่ในลำดับข้อ · ติดตั้งใหม่ตรวจเร็วเกิน | เขียนเป็นข้อความ · เพิ่มขั้นรอ init |
| 9 | M | ไม่มีวิธีแยก passed / expected-fail / failed · TC-UI-02 flaky ไม่มีคำเตือน | `--reporter=list,json` + `PLAYWRIGHT_JSON_OUTPUT_NAME` · เตือนรันซ้ำเฉพาะตัวก่อนสรุป |
| 0–9 | M (RUNNER) | บล็อก "ผลที่คาด" ติดกล่องพรอมต์ → runner อ่านด้วยช่วงบรรทัดเห็นก่อนรัน | แยกด้วยหัวข้อ/เส้นคั่น หรือย้ายไปท้ายไฟล์ |

---

## 8. ตรวจงาน · ข้อสอบ · เครื่องตรวจ

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| [GRADING.md](GRADING.md) | รูบริก 20 ข้อ + วิธีตรวจ · ตรวจทีละ LAB 0–12 · หลักฐานที่ต้องดู · ค่าอ้างอิงจากรอบจริง · คำตอบผิดที่พบบ่อย (TC-BOOK-07 · Plan mode · วันที่จอง ≠ วันนัด · `INSERT 0 3`/`INSERT 0 0` · oracle SQL ก่อนโค้ด · TC-UI-02 flaky) |
| [QUIZ.md](QUIZ.md) | Quiz ทบทวน 10 ข้อ + เฉลย + คำอธิบาย + คำตอบผิดที่พบบ่อย |
| [EXAM-KEY.md](EXAM-KEY.md) | เฉลยและแผนตรวจข้อสอบ ชุด A ([../EXAM.md](../EXAM.md)) + ชุด B ([EXAM-B.md](EXAM-B.md)) · ข้อที่แก้ repo เดิม 6/8 ข้อ = 84/100 คะแนน |
| [grader/README.md](grader/README.md) | เครื่องตรวจอัตโนมัติ (`grade.ps1` → `grade.mjs`) ให้ 84 คะแนน · ผู้สอนกรอกเอง 16 · ใช้ docker network ของผู้สอบแต่ละคน ไม่ใช้พอร์ตเครื่อง |
| `exam-ref/` | diff เฉลยอ้างอิงที่รันจริง (`A-*.diff` `B-*.diff`) · mutant `exam-ref/mutants/` · ฐาน "ใช้งานจริง" `prod-data-A.sql` `prod-data-B.sql` |
| `_design/LESSON-PLAN.md` · `PROMPTS.md` · `RUNNER.md` · `CR-DESIGN.md` · `CODEBASE-NOTES.md` | แผนการสอน · พรอมต์ทุก LAB (ฉบับที่ใช้รัน) · กติกาให้ Claude สวมบทผู้เรียน · ออกแบบ CR · แผนที่โค้ด |
| `_design/ORIGINAL-BUGS-ch04.md` | เฉลยบั๊ก `BUG_MODE` เดิมของบท 04 (ถอดสวิตช์แล้วในบทนี้) |
| `_design/results/LAB0_RESULT.md` … `LAB12_RESULT.md` | คำตอบในแชท · ตัวเลข · ข้อสังเกต · ปัญหา · ตัดสินแทนผู้เรียน — ที่มาของตัวเลขทุกตัวในหน้านี้ · `LAB11_RESULT.md` `LAB12_RESULT.md` (เพิ่มแล้ว · หัวไฟล์จดพอร์ต 4100/5533) |

**คะแนนรูบริกของรอบถ่ายทำ:** ไม่ได้วัดในรอบจริง (ไม่มีผู้ตรวจให้คะแนนใน result) · หลักฐานต่อข้อ 1–16 อยู่ในข้อ 2–4 ของหน้านี้ · ข้อ 17–20: ข้อ 17 `REGRESSION-REPORT.md` §1 แยก 106/1/7 + TC-UI-02 rerun · ข้อ 18 §3 CR × REA 5 แถว + §4 diff 66 ไฟล์ + `docs/TRACEABILITY.md` · ข้อ 19 `RELEASE-NOTES.md` (16 ข้อค้าง) + `UAT-CHECKLIST.md` 31 แถว · ข้อ 20 `docs/DEPLOY-RUNBOOK.md` "ผลซ้อมถอยกลับ" + `tests/smoke.mjs` (exit 1/0) — ทั้ง 4 ข้อมีหลักฐานครบตามเกณฑ์ "ได้ 1" (ดู [GRADING.md](GRADING.md) ข้อ 17–20)

**ข้อ D12:** LAB 10 ส่วนที่ 2 ข้อ 4 ("ตั้งเวลาให้ถึงเวลานัดก่อนกดเสร็จ") คงไว้เป็นทักษะ test seam · ข้อสอบชุด B ข้อ 5 ปรับให้ไม่พึ่งการรู้ข้อนี้อย่างเดียว (ดู EXAM-KEY)
