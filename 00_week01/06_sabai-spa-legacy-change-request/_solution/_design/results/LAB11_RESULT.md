# LAB 11 RESULT · Regression เต็ม + REA เทียบเวอร์ชัน

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 12:40:58 (+07) |
| เวลาจบ | 2026-10-12 13:05 (+07) |
| เวลาที่ใช้ | **~24 นาที** · REA static v2 (docker cp + analyze 49.1 วิ) + pages/cmp-input + compare 12 วิ ≈ 2 นาที · regression รวม 15.2 นาที (reset 0.3 · check-rules 19.0 · golden 1.2 · cr01 5.3 · cr02 4.3 · cr03 3.8 · cr04 2.9 · cr05 3.0 · e2e-cr 3 เบราว์เซอร์ **104.2 วิ** · e2e-legacy `test:all` **768.7 วิ (12.8 นาที)**) · TC-UI-02 webkit `--repeat-each=3` 38 วิ · HAR v2 10 วิ + REA inspect 2.7 วิ · scenario v2 4.1 วิ · เขียนรายงาน/TRACEABILITY/ภาพ ≈ 5 นาที |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `REGRESSION-REPORT.md` · แก้ (ต่อท้าย) `docs/TRACEABILITY.md` `docs/ORACLE-CHANGES.md` · ไฟล์หลักฐาน (ignored) `rea-out/v2/.next/static/` `rea-out/static-v2.json(.log)` `cmp.json` (71 MB) `cmp-out.json(.log)` `journeys-v2.har` `har-api-v2.json(.log)` `scenario-v2.json(.log)` `scenario-v2-final.png` · ไม่แก้โค้ด ไม่แก้เทสต์ · ไม่ commit (พรอมต์ไม่สั่ง) |
| สคริปต์ชั่วคราว | `tools/lab11/`: `regress.ps1` `regress-summary.txt` (UTF-16) `count.mjs` (คัดจาก lab9) `table-shot.mjs` · log `check-rules golden cr01..05 e2e-cr e2e-legacy-all reset tc-ui-02-rerun .log` (UTF-8 แต่ข้อความไทยจาก node เพี้ยนเพราะผ่าน pipeline PS 5.1 · ตัวเลขอ่านได้) · `e2e-cr.json` `e2e-legacy-all.json` · `cmp-sum.txt` `har-api-v1.txt` `har-api-v2.txt` `ids.txt` `scenario-v1-sum.txt` · `lab11-regression.md` `lab11-rea-compare.md` |
| สถานะเว็บตอนจบ | `sabai06-web` image `27c39a2eb077` (build 12:29 = โค้ด `ef47d72` · หลัง build ไม่มีไฟล์ `web/` `db/` เปลี่ยนนอกจาก `web/SPEC.md`) · `/api/health` → `{"ok":true,"db":true}` · เปิดค้าง |
| ข้อมูลทดสอบ | reset ก่อน regression และ **reset อีกครั้งหลัง HAR/scenario** → now `2026-10-10T10:00:00+07:00` |
| พอร์ต | WEB 4100 · DB 5533 · `$env:BASE_URL="http://localhost:4100"` · HAR `http://127.0.0.1:4100` · REA scenario ผ่าน network `sabai06-net` (`http://sabai06-web:3000` ไม่ต้องแก้ scenario) |
| เซสชัน/โหมด | runner (Agent tool) ทำเองในฐานะ Claude Code ของผู้เรียน (mode A) · ไม่ได้เปิด `yolo.cmd` (LAB นี้ไม่มีขั้นที่ต้องพิสูจน์ deny) · CLAUDE.md + `.claude/settings.json` (deny `Edit(e2e-legacy/**)`) **บังคับเอง** — ไม่ได้แก้ `e2e-legacy/` |

## 2. ข้อห้ามที่ทำตาม / จุดที่ทำต่างจากพรอมต์

- ห้ามแก้โค้ด/เทสต์/เปิด `_solution/` `CHANGE-REQUESTS/answers/` → ทำตาม · git ใช้เฉพาะคำสั่งอ่าน (`git diff --stat` `git log` `git show --stat` `git status`)
- พอร์ต 4000 → 4100 ทุกคำสั่ง (รวม HAR `127.0.0.1:4100`)
- **ลำดับ:** ทำข้อ 2 (REA static v1↔v2) ก่อนข้อ 1 เพื่อไม่ให้ REA analyze (CPU หนัก) รันพร้อม e2e 3 เบราว์เซอร์ (กัน flaky webkit) · ข้อ 2b/2c (HAR reset ข้อมูล) ทำหลัง regression เสร็จ
- ข้อ 1: เติม `-- --reporter=list,json` + `PLAYWRIGHT_JSON_OUTPUT_NAME` ให้ทั้ง e2e-cr และ e2e-legacy เพื่อแยก passed / expected-fail / failed (ไม่เปลี่ยนเทสต์) · เพิ่ม `node tests/cr05.mjs` ตามคำว่า "cr01.mjs ถึง cr05.mjs"
- ข้อ 4 "commit baseline" = `4a7908f baseline: ระบบที่รับมอบ`
- **ยอมรับ:** ระหว่างหาหัวข้อ LAB 11 คำสั่ง grep ของ runner พิมพ์บรรทัด "ผลที่คาด/ไปต่อได้เมื่อ" ออกมาโดยไม่ตั้งใจก่อนเริ่มรัน (ไม่ได้ตั้งใจอ่าน) · ตัวเลขทุกตัวด้านล่างมาจากการรันจริง ไม่ได้ปรับตามผลที่คาด

## 3. คำตอบสรุปที่แสดงในแชท

> | ชุด | ผ่าน/ทั้งหมด | เบราว์เซอร์ | เวลา | หมายเหตุ |
> |---|---|---|---|---|
> | check-rules | 90/90 | API | 19.0 วิ | ค่าคาดหวังเดิมไม่แตะ |
> | golden | 62/62 | API | 1.2 วิ | |
> | cr01 / cr02 / cr03 / cr04 / cr05 | 22/22 · 19/19 · 18/18 · 14/14 · 12/12 | API | 5.3 · 4.3 · 3.8 · 2.9 · 3.0 วิ | |
> | e2e-cr | 39: ผ่านจริง 33 · expected-fail 6 · ล้ม 0 | chromium/firefox/webkit 11+2 ต่อตัว | 104.2 วิ | ef = KI-01b KI-02b ×3 |
> | e2e-legacy test:all | 114: ผ่านจริง 106 · ef 7 · ล้ม 1 | api 4+1+ล้ม1 · chromium/firefox/webkit 34+2 | 12.8 นาที | "113 passed · 1 failed" · ล้ม TC-SEC-05 (เดิม) · ef TC-SEC-04 · TC-GC-04 TC-TRN-03 ×3 = baseline |
> | TC-UI-02 webkit ×3 | 1/3 | webkit | 38 วิ | flaky เดิม · ใน test:all รอบนี้ผ่าน |
>
> REA static: pages `/account` ไฟล์เปลี่ยน · `/admin/report` ใหม่ใน v2 · อีก 15 เหมือนเดิม · compare `changed 12 · unknown 711 · added 0` [E ev_ea036036] · route ไฟล์ 25→30 · HAR v2 7 endpoint status/คีย์เดิมทุกตัว [E ev_ba70ee00] vs [E ev_6fbeaec6] · scenario v2 12/12 ฿1,000 [E ev_d627ab35] = รับมอบ [E ev_8dc23d9f] · git diff 66 ไฟล์ โยง CR ได้ (⚠️ 2 แถวเป็นเครื่องมือ/เอกสารคอร์ส) · ค่าคาดหวังเดิม diff ว่าง (golden เป็นไฟล์ใหม่ ไม่ถูกแก้หลังสร้าง)

ตาราง CR × REA (ย่อ · ฉบับเต็มใน `w/REGRESSION-REPORT.md` §3):

| CR | REA static | HAR/scenario | พิสูจน์แทน |
|---|---|---|---|
| CR-01 | changed `account/page` 2 module · route reschedule/reschedule-slots ใหม่ | ไม่เห็น (ไม่ได้กดเลื่อน) | cr01 22/22 · UI 6/6 |
| CR-02 | ไม่เห็น (กฎฝั่งเซิร์ฟเวอร์) | ไม่เห็น (นัดเดี่ยว ฿1,000) | cr02 19/19 · golden 62/62 |
| CR-03 | chunk ร่วม `8561` changed (i18n `DUPLICATE_BOOKING` — รู้จากเปิดไฟล์เอง) | ไม่เห็น | cr03 18/18 · UI 3/3 |
| CR-04 | chunk `8561` changed (`SHOP_CLOSED`) · route `/api/holidays` ใหม่ · `/book` hash เดิม | ไม่เห็น (12 ต.ค.) | cr04 14/14 · UI 6/6 |
| CR-05 | `unknown` (หน้าใหม่ไม่ขึ้น added) · pages "ใหม่ใน v2" · route `/api/admin/report` | ไม่เห็น | cr05 12/12 · UI 6/6 |

## 4. ตัวเลขสำคัญ

| รายการ | ค่า | คำสั่ง |
|---|---|---|
| e2e-legacy `test:all` | 114 · Playwright "1 failed · 113 passed (12.8m)" · passed จริง **106** (api 4 · chromium 34 · firefox 34 · webkit 34) · expected-fail **7** · failed **1** (api TC-SEC-05) · flaky 0 · `stats.expected 113 unexpected 1` | `node tools/lab11/count.mjs e2e-legacy-all.json` |
| e2e-cr | 39 · passed 33 · ef 6 · failed 0 · flaky 0 | `count.mjs e2e-cr.json` |
| TC-UI-02 webkit rerun | 1 passed · 2 failed (repeat-each 3) | `npx playwright test --project=webkit -g "TC-UI-02" --repeat-each=3` |
| static v2 | 37,377,604 B · 49.1 วิ · javascript-module 449 · asset 31 · chunk 26 · endpoint node 12 · unknown 8 · fetch `/api/*` ไม่ซ้ำ 9 (= v1) · coverage partial (semantic unknown 5,611) · [E ev_f54183d0] | `rea-tools summary` |
| compare v1↔v2 | `unchanged 0 · added 0 · removed 0 · changed 12 · unknown 711` · status รวมใน output: matched 431 · unmatched 289 · [E ev_ea036036] · 12 วิ · cmp.json input 71 MB | `rea-tools cmp-sum` |
| changed ที่เป็นโค้ดหน้าเว็บ | `account/page#7177` `#63` · `chunks/8561` (33,805→39,860 B · รหัสใหม่ DUPLICATE_BOOKING SHOP_CLOSED RESCHEDULE_BIRTHDAY/NOT_ALLOWED/SAME/TOO_LATE REPORT_RANGE) · ที่เหลือ = polyfills/main/webpack/framework/_ssgManifest (build id ใหม่) | `cmp-sum` + grep ตัวพิมพ์ใหญ่ใน chunk |
| route ไฟล์ | 25 → 30 (+admin/report · reschedule · reschedule-slots · holidays · test/clock) | `rea-tools endpoints` ×2 + diff |
| HAR v2 | 3,887,100 B · 136 entries (v1 135) · `/api/*` 10 record (37 39 40 41 69 75 77 126 130 131) · 7 endpoint · ตาราง har-api เท่า v1 ทุกช่อง · [E ev_ba70ee00] | `har-records` · `har-api` ×2 + diff |
| scenario v2 | 12/12 · 2,081 ms · ยอด ฿1,000 `data-amount=1000` · png เหมือน v1 ทุก byte (107,054 B) · [E ev_d627ab35] | `scenario-sum` · `cmp` |
| git diff | `4a7908f..HEAD` 66 ไฟล์ +12,827 −43 · `-- check-rules e2e-legacy` ว่าง · `-- tests/golden` 5 ไฟล์ใหม่ · `3bcd8c9..HEAD -- tests/golden` ว่าง | `git diff --stat` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

- e2e-legacy: "113 passed · 1 failed" แต่ผ่านจริง 106 · expected-fail 7 · ล้ม TC-SEC-05 (ล้มตั้งแต่รับมอบ) → เท่า baseline
- `/account` hash `83b95202 → 9f9b905e` (CR-01) · `/admin/report` ใหม่ `4789f8b3` (CR-05) · REA compare ให้หน้านี้เป็น `unknown` ไม่ใช่ `added`
- `/book` hash เดิม `9a898da2` ทั้งที่ CR-04 ปิดการจองวันหยุด → กฎอยู่ฝั่งเซิร์ฟเวอร์ (REA static ไม่เห็น) · พิสูจน์ด้วย cr04 14/14
- `(layout)` hash เดิม `a97cb37b` ทั้งที่ `web/app/layout.tsx` แก้ (เมนู `nav-admin-report`) → layout เป็น async server component ไม่อยู่ใน bundle
- HAR `POST /api/bookings` 201 · body 15 คีย์ เดียวกัน v1 [E ev_6fbeaec6] / v2 [E ev_ba70ee00]
- scenario ฿1,000 · 12/12 [E ev_8dc23d9f] → [E ev_d627ab35]

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบ | เหตุผล |
|---|---|---|
| `rea-out\v2\.next\static` มีอยู่แล้ว ลบไหม | ไม่ต้องถาม — `Test-Path` = False | ยังไม่เคยคัดลอก |
| e2e-legacy แดง 1 (TC-SEC-05) → "ข้อไหนแดงให้หยุด" | **ไม่หยุด** · จดว่าเป็นของเดิม | ล้มตั้งแต่รับมอบ (HANDOVER-CHECK/CLAUDE.md) ไม่ใช่แดงใหม่ · ชุดใหม่ทุกชุดเขียว |
| TC-UI-02 webkit rerun ล้ม 2/3 | ไม่หยุด · จด flaky เดิม | ไฟล์ `/skin` ไม่มี CR แตะ · LAB 9 พิสูจน์บน image ก่อน CR แล้ว · ใน test:all ผ่าน |
| ไฟล์ที่ไม่ใช่ CR (`tools/rea-tools.mjs` `tools/.gitignore` `fast_track/README.md`) | ติด ⚠️ พร้อมคำอธิบาย (commit ของ orchestrator) | ไม่อยู่ในระบบที่ส่งมอบ |
| `tests/golden` อยู่ใน diff baseline..HEAD | ไม่เติมแถวในตารางเปลี่ยนค่า · เติมบันทึกตรวจใต้ตาราง ORACLE-CHANGES | เป็นไฟล์ใหม่ (safety-net) ไม่ใช่การเปลี่ยนค่าเดิม · diff หลังสร้าง = ว่าง |
| TRACEABILITY "ฉบับสมบูรณ์" | ต่อท้ายตารางผล LAB 11 ต่อ CR + ตาราง TC safety-net (CHAR-BOOK-01 KI-* golden) | แถวเดิมไม่มี TC safety-net → "ทุก TC ใหม่มี CR/ที่มา" |

## 7. ข้อสังเกต 👀

- **REA compare ไม่ขึ้น `added` สำหรับหน้าใหม่** (`/admin/report`) — เป็น `unknown` ฝั่งขวาอย่างเดียว · ถ้าอ่านแค่ summary (`added 0`) จะสรุปผิดว่าไม่มีหน้าใหม่ · `pages` (hash ชื่อไฟล์) และ `endpoints` (ชื่อ route) จับได้ชัดกว่า
- chunk ร่วม `8561` (i18n) changed เพราะ 4 CR เติมข้อความ → REA บอกแค่ "เปลี่ยน" แต่ไม่บอกว่าเป็นของ CR ไหน · ต้องเปิดดูสตริงเอง (inference)
- `(layout)` และ `/book` hash เดิมแม้โค้ดที่เกี่ยวข้องถูกแก้ (server component / กฎฝั่งเซิร์ฟเวอร์) — ตัวอย่างดีของ "REA ไม่เห็น ≠ ไม่ได้เปลี่ยน"
- fetch ที่ REA กู้จาก static ยัง 9 เท่าเดิม แม้มี endpoint ใหม่ 4 ตัว → URL ต่อ query/template (กับดัก T13)
- `compare-application-versions` ต้องการ input `cmp.json` 71 MB (ซ้อน static สองก้อน) — ควรเตือนเรื่องพื้นที่
- record-har ใน v2 ได้ B14 เหมือนตอนรับมอบ (reset ก่อนเดิน) · ต้อง reset ซ้ำหลังเก็บหลักฐาน
- ข้อความ "PowerShell NativeCommandError" ใน `rea-out/*.log` = แค่ progress JSON ที่ REA เขียนออก stderr (PS 5.1 ห่อเป็น error) ไม่ใช่ error จริง

## 8. เจอระหว่างทาง (นอก CR)

- ไม่มีบั๊กใหม่ · ของเดิมที่ยังอยู่: TC-SEC-05 (api) ล้ม · TC-UI-02 webkit flaky · KI-01/KI-02 (`test.fail` ใน e2e-cr) ยังเป็นบั๊กเดิมไม่มี CR

## 9. ปัญหาที่เจอ / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| log ที่ผ่าน `*>&1 \| Out-File -Encoding utf8` ใน PS 5.1 ทำข้อความไทยจาก node เพี้ยน (decode เป็น cp874) | อ่านเฉพาะตัวเลข · ผลนับจริงจาก JSON reporter |
| รัน TC-UI-02 rerun ทับ `e2e-legacy/test-report/` ของ `test:all` | ผลนับเก็บไว้แล้วใน `tools/lab11/e2e-legacy-all.json` (ไม่ได้พึ่ง html report) |

## 10. ข้อเสนอแก้พรอมต์

- ข้อ 1: ระบุ `npm run test:all -- --reporter=list,json` (+ `$env:PLAYWRIGHT_JSON_OUTPUT_NAME`) ให้ชัด และบอกว่า TC-SEC-05 (api) ล้มตั้งแต่รับมอบ → "แดง" ในประโยค "ข้อไหนแดงให้หยุด" ควรเขียนว่า "แดงใหม่ที่ baseline ไม่มี" ไม่งั้นผู้เรียนจะหยุดทุกครั้ง · เตือน TC-UI-02 webkit flaky (รันซ้ำเฉพาะตัวก่อนสรุป)
- ข้อ 2: เติม `node tools\rea-tools.mjs endpoints` v1/v2 (เห็น route ใหม่ 5 ไฟล์ ซึ่ง compare ไม่บอก) และเตือนว่าหน้าใหม่อาจเป็น `unknown` ไม่ใช่ `added`
- ข้อ 4: บอกชื่อ commit baseline (`git log --oneline --grep baseline`) และว่ามี commit ที่ไม่ใช่ CR ได้ (เครื่องมือคอร์ส) ให้ติด ⚠️ พร้อมเหตุผล
- ข้อ 5: บอกว่า `tests/golden` เป็นไฟล์ใหม่หลัง baseline → ให้เทียบตั้งแต่ commit ที่สร้าง golden ด้วย (`git log --diff-filter=A -- tests/golden`)
- แนะนำลำดับ: REA static ก่อน/หลัง e2e ได้ แต่ห้ามขนานกับ e2e 3 เบราว์เซอร์ · HAR ต้องหลัง regression (reset ข้อมูล)

## 11. ภาพที่ควรใช้

| ไฟล์ | คำอธิบาย |
|---|---|
| `design/shots/lab11-scenario-v2.png` | ภาพที่ REA ถ่ายเองบนโค้ดหลัง CR (หน้าสรุปการจอง ฿1,000) · คัดจาก `w/rea-out/scenario-v2-final.png` (เหมือน v1 ทุก byte) |
| `design/shots/lab11-regression.png` (+ `.md`) | ตารางผล regression ทุกชุด (render HTML headless 1280 กว้าง) |
| `design/shots/lab11-rea-compare.png` (+ `.md`) | ตาราง CR × REA เห็นไหม + HAR v1↔v2 |

### เทียบกับผลที่คาด

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| `REGRESSION-REPORT.md` · ทุกชุดใหม่เขียว | สร้างแล้ว · cr01–05 + golden + check-rules + e2e-cr เขียวทั้งหมด | ✅ |
| e2e-legacy 114 · "113 passed · 1 failed" · ผ่านจริง 106 · ef 7 (TC-TRN-03 ×3 · TC-GC-04 ×3 · TC-SEC-04 ×1) · failed 1 TC-SEC-05 = baseline | 114 · "113 passed · 1 failed" · 106 · ef 7 ตรงรายชื่อ · failed TC-SEC-05 | ✅ (TC-UI-02 webkit ผ่านรอบนี้ · rerun ×3 ล้ม 2 = flaky เดิม) |
| REA static changed `account/page` (CR-01) · หน้ารายงาน CR-05 อาจเป็น `unknown` · CR-02 CR-03 ไม่เห็น · unknown หลายร้อย | changed account/page ✔ · report = `unknown` ✔ · CR-02 ไม่เห็น ✔ · CR-03 เห็นทางอ้อม (chunk i18n 8561 changed · ตัวกฎไม่เห็น) · unknown 711 | ✅ (CR-03 ละเอียดกว่าที่คาด) |
| HAR v2 endpoint เดิม 7 ตัว status เดิม · อาจมี `/api/holidays` | 7 ตัว status+คีย์เดิมทุกช่อง · **ไม่มี** `/api/holidays` | ✅ |
| scenario v2 12/12 ฿1,000 | 12/12 ฿1,000 | ✅ |
| `pages`: `/account` ไฟล์เปลี่ยน · หน้าใหม่ CR-05 "ใหม่ใน v2" | ตรง | ✅ |
| ทุกไฟล์โยง CR ได้ · diff ค่าคาดหวังเดิมว่าง | web/db ทุกไฟล์โยงได้ · ⚠️ 3 ไฟล์ของคอร์ส (rea-tools.mjs, tools/.gitignore, fast_track/README.md) อธิบายได้ · check-rules/e2e-legacy ว่าง · golden = ไฟล์ใหม่ (diff หลังสร้างว่าง) | ⚠️ ต่างเล็กน้อย (ไฟล์คอร์ส + golden นับใน diff จาก baseline) |
| ไปต่อได้เมื่อ: ตัวเลขจากรอบนี้ · ตาราง CR × REA 5 แถว · HAR [E] ครบ · ไม่มี ⚠️ อธิบายไม่ได้ | ครบ | ✅ |
