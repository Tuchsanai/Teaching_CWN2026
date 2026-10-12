# REGRESSION-REPORT · ตรวจรับหลังแก้ CR-01 ถึง CR-05

วันที่รัน 12 ต.ค. 2026 (12:41–13:03) · โค้ด = HEAD `ef47d72` (image `sabai06-web` build 12:29 · หลัง build ไม่มีไฟล์ใน `web/` `db/` เปลี่ยนนอกจาก `web/SPEC.md`) · reset ก่อนรัน (`now` = 2026-10-10T10:00+07:00)
ทุกตัวเลขมาจากการรันรอบนี้ · ไม่ได้แก้โค้ดหรือเทสต์ · ไม่ได้เปิด `_solution/`
เครื่องนี้รันที่พอร์ต **4100** (`$env:BASE_URL="http://localhost:4100"` · HAR ใช้ `http://127.0.0.1:4100`) เพราะ 4000 มีงานอื่นใช้

## 1. ผลรันทุกชุด

| ชุด | ผ่าน/ทั้งหมด | เบราว์เซอร์ | เวลา | หมายเหตุ |
|---|---|---|---|---|
| `web/scripts/check-rules.mjs` (กฎร้านเดิม) | **90/90** | — (API) | 19.0 วิ | ค่าที่คาดหวังเดิม ไม่แตะ |
| `tests/golden/run.mjs` (golden master) | **62/62** | — (API) | 1.2 วิ | price + slots 6/6 + admin-queue 6/6 |
| `tests/cr01.mjs` เลื่อนนัด | **22/22** | — (API) | 5.3 วิ | |
| `tests/cr02.mjs` ส่วนลดกลุ่มขั้นบันได | **19/19** | — (API) | 4.3 วิ | |
| `tests/cr03.mjs` กันจองซ้ำ | **18/18** | — (API) | 3.8 วิ | |
| `tests/cr04.mjs` วันหยุดร้าน | **14/14** | — (API) | 2.9 วิ | |
| `tests/cr05.mjs` รายงานยอด + CSV | **12/12** | — (API) | 3.0 วิ | |
| `e2e-cr` (ชุดของทีม) | 39 รายการ: ผ่านจริง **33** · expected-fail **6** · ล้ม 0 · flaky 0 | chromium 11+2 · firefox 11+2 · webkit 11+2 | 104.2 วิ | บรรทัดสรุป Playwright "39 passed (1.7m)" · expected-fail = KI-01b KI-02b (`test.fail` บั๊กเดิมที่ยังไม่มี CR) ×3 |
| `e2e-legacy` `npm run test:all` (ชุดเดิม) | 114 รายการ: ผ่านจริง **106** · expected-fail **7** · ล้ม **1** · flaky 0 | api 4+1+ล้ม 1 · chromium 34+2 · firefox 34+2 · webkit 34+2 | 768.7 วิ (12.8 นาที) | บรรทัดสรุป "**113 passed · 1 failed**" · ล้ม = TC-SEC-05 (api) = ล้มตั้งแต่รับมอบ (HANDOVER-CHECK) · expected-fail = TC-SEC-04 (api) · TC-GC-04 TC-TRN-03 ×3 = baseline เท่าเดิม |
| `e2e-legacy` TC-UI-02 webkit รันซ้ำ `--repeat-each=3` | 1/3 (ล้ม 2) | webkit | 38 วิ | ใน `test:all` รอบนี้ **ผ่าน** · flaky เดิมของหน้า `/skin` (พิสูจน์แล้วบน image ก่อน CR ตอน CR-01) · ไม่ใช่ไฟล์ที่ CR ใดแตะ → ไม่นับเป็นแดงใหม่ |

แยก passed / expected-fail / failed จาก JSON reporter (`--reporter=list,json`) เพราะบรรทัดสรุปของ Playwright นับ `test.fail` ที่ล้มตามคาดรวมใน passed
**สรุป: ไม่มีแดงใหม่** · ชุดใหม่ทุกชุดเขียว · ชุดเดิมเท่า baseline ตอนรับมอบ (ล้ม TC-SEC-05 ตัวเดียว · `test.fail` 7)

## 2. REA เทียบ bundle ที่ส่งมอบ v1 (รับมอบ) ↔ v2 (หลัง CR)

| ขั้น | ผล | ป้าย |
|---|---|---|
| `docker cp sabai06-web:/app/.next/static rea-out\v2\.next\static` | (`rea-out\v2\.next\static` ยังไม่มีมาก่อน จึงไม่ต้องลบ) | — |
| `analyze-javascript-application` v2 | 49.1 วิ · 37,377,604 B · coverage partial · module 449 · endpoint node 12 · unknown 8 | [E ev_f54183d0] (v1 = [E ev_11d475e1]) |
| `compare-application-versions` | 12 วิ · summary `unchanged 0 · added 0 · removed 0 · changed 12 · unknown 711` · coverage partial | [E ev_ea036036] |

### 2.1 หน้า (route) จาก hash ในชื่อไฟล์ (`rea-tools pages`)

| route | v1 hash | v2 hash | สถานะ |
|---|---|---|---|
| `/account` | 83b95202 | 9f9b905e | **ไฟล์เปลี่ยน** |
| `/admin/report` | - | 4789f8b3 | **ใหม่ใน v2** |
| อีก 15 รายการ (`(layout)` `/` `/_not-found` `/admin` `/book` `/chat` `/giftcard` `/login` `/package` `/quiz` `/services` `/skin` `/therapists` `/transport` `/wallet`) | เท่าเดิม | เท่าเดิม | เหมือนเดิม |

hash ต่าง = ไฟล์ใน bundle เปลี่ยน แต่ไม่บอกว่าเปลี่ยนตรงไหน · hash เท่า = โค้ดฝั่งเบราว์เซอร์ของหน้านั้นไม่เปลี่ยน (ไม่ได้บอกอะไรเรื่องฝั่งเซิร์ฟเวอร์)

### 2.2 รายการ `changed` 12 ตัว (`rea-tools cmp-sum`) · อ่านเฉพาะโค้ดหน้าเว็บ

| node | มิติที่เปลี่ยน | อ่านว่า |
|---|---|---|
| `chunks/app/account/page-…#7177` และ `#63` | content, location, properties | โค้ดหน้า `/account` เปลี่ยน → CR-01 |
| `chunks/8561-…#8561` (33,805 → 39,860 B) | content, location, properties | chunk ร่วมที่หลายหน้าใช้ (`/account` `/admin` `/book` `/chat` ฯลฯ) · ไล่ดูเองพบว่าเป็นข้อความ i18n: v2 มีรหัส error ใหม่ `DUPLICATE_BOOKING` (CR-03) `SHOP_CLOSED` (CR-04) `RESCHEDULE_*` 4 ตัว (CR-01) `REPORT_RANGE` (CR-05) — REA บอกแค่ว่า "เปลี่ยน" ส่วนชื่อ CR มาจากการเปิดอ่านไฟล์ (inference) |
| `polyfills` `main` `webpack` `framework` `4bd1b696` `1255` (unknown/asset) · `_ssgManifest.js` | properties / location | build id ใหม่ (`jZbQKIWK…`) · ชื่อไฟล์เดิม → สัญญาณจากการ build ใหม่ ไม่ใช่โค้ดหน้าเว็บ |

- หน้าใหม่ `/admin/report` (CR-05) **ไม่ขึ้นเป็น `added`** แต่เป็น `unknown` (มีเฉพาะฝั่งขวา) เพราะ coverage partial · `unknown` 711 ตัว **ห้ามสรุปว่าไม่เปลี่ยน**
- route ฝั่งเซิร์ฟเวอร์จากชื่อไฟล์ `chunks/app/api/**/route-*.js` (`rea-tools endpoints`): v1 25 → v2 **30** · ใหม่ `/api/admin/report` (CR-05) `/api/bookings/[id]/reschedule` `/api/bookings/[id]/reschedule-slots` (CR-01) `/api/holidays` (CR-04) `/api/test/clock` (seam ทดสอบ · safety-net ไม่ใช่ CR) · เห็นแค่ชื่อไฟล์ ไม่เห็นกฎข้างใน
- fetch ที่ REA กู้ได้จาก static ยัง **9** endpoint เท่า v1 [E ev_f54183d0] · `/api/admin/report?…` ในหน้า report เป็น URL ต่อ query (template) → REA ไม่นับ (กับดัก T13)

## 2b. สัญญา API เส้นทางเดิม (HAR ชุดเดียวกับตอนรับมอบ)

`record-har.mjs http://127.0.0.1:4100` 10 วิ (reset → จองได้ B14 · /account 8 นัด · ปุ่มยกเลิก B06 disabled · ยกเลิก B05 · หลังร้าน 12 ต.ค. 2 แถว) · HAR v2 136 entries (v1 135) · `/api/*` 10 record → `inspect-web-network-capture` 2.7 วิ

| endpoint | v1 (status · query/body/response keys) [E ev_6fbeaec6] | v2 [E ev_ba70ee00] | เหมือนเดิม/เปลี่ยน | CR ที่อนุญาตให้เปลี่ยน |
|---|---|---|---|---|
| `GET /api/slots` | 1 ครั้ง · 200 · query service, date, type, people · res date, service, durationMin, min, max, slots | 1 ครั้ง · 200 · คีย์เดียวกันทุกตัว | เหมือนเดิม | — (CR-04 ปิดเฉพาะวันหยุด · เส้นทางนี้ 12 ต.ค.) |
| `POST /api/price` | 2 ครั้ง · 200 · body 14 คีย์ · res 30 คีย์ | 2 ครั้ง · 200 · body 14 คีย์ · res 30 คีย์ เดียวกัน | เหมือนเดิม | CR-02 (ยอดกลุ่มตั้งแต่ 1 พ.ย. · เส้นทางนี้นัดเดี่ยว) |
| `POST /api/bookings` | 1 ครั้ง · **201** · body 15 คีย์ (+quotedTotal) · res 10 คีย์ | 1 ครั้ง · **201** · คีย์เดียวกัน | เหมือนเดิม | CR-03 (409 เฉพาะคนเดียวกันเวลาทับ) · CR-04 (422 วันหยุด) |
| `POST /api/auth/login` | 2 ครั้ง · 200 · res ok, user | 2 ครั้ง · 200 · เดียวกัน | เหมือนเดิม | — |
| `POST /api/bookings/{id}/cancel` | 1 ครั้ง · 200 · res ok, bookingId, code, status | 1 ครั้ง · 200 · เดียวกัน | เหมือนเดิม | — |
| `POST /api/auth/logout` | 1 ครั้ง · 200 · res ok | 1 ครั้ง · 200 · เดียวกัน | เหมือนเดิม | — |
| `GET /api/admin/bookings` | 2 ครั้ง · 200 · query date · res date, today, bookings | 2 ครั้ง · 200 · เดียวกัน | เหมือนเดิม | — (CR-05 เพิ่ม endpoint ใหม่ ไม่แตะตัวนี้) |

ตาราง `har-api` v1 กับ v2 ตรงกันทุกช่อง (`diff` หลังตัด evidence id = ไม่มีบรรทัดต่าง) · ไม่มี endpoint ใหม่ในเส้นทางนี้ (หน้าจองไม่ได้เรียก `/api/holidays` · ไม่ได้เปิดกล่องเลื่อนนัด) → **[E ev_ba70ee00] สัญญา API ของเส้นทางเดิมไม่เปลี่ยน**

## 2c. REA ขับหน้าจองเดิมซ้ำบนโค้ดใหม่ (`capture-browser-scenario` · network `sabai06-net`)

| | รับมอบ (docs/REA-INVENTORY.md) | v2 (รอบนี้) | ตรงไหม |
|---|---|---|---|
| step | 12/12 completed [E ev_8dc23d9f] | **12/12** completed · 2,081 ms · completeness complete [E ev_d627ab35] | ✔ |
| API ที่เรียก | `GET /api/slots?service=S01&date=2026-10-12&type=single&people=1` 200 · `POST /api/price` 200 | เดียวกันทั้ง 2 ตัว status เดียวกัน | ✔ |
| ยอดหน้าสรุป (นวดไทย 60 นาที · 12 ต.ค. 15:00–16:00) | "ยอดสุทธิ: ฿1,000" `data-amount=1000` | "ยอดสุทธิ: ฿1,000" `data-amount=1000` | ✔ (นัดเดี่ยว ไม่โดน CR-02) |
| ภาพสุดท้าย | `rea-out/scenario-final.png` | `rea-out/scenario-v2-final.png` (ไฟล์เหมือนกันทุก byte) | ✔ |

## 3. CR × "REA เห็นไหม"

| CR | ส่วนที่ควรเปลี่ยนใน bundle (หน้าไหน) | REA static เห็นไหม | HAR/scenario เห็นไหม | ถ้าไม่เห็นเพราะอะไร | เทสต์ไหนพิสูจน์แทน |
|---|---|---|---|---|---|
| CR-01 เลื่อนนัด | `/account` (`MyBookings.tsx` กล่องเลื่อนนัด) · i18n `RESCHEDULE_*` · route ใหม่ reschedule / reschedule-slots | **changed** (`account/page` 2 module · chunk ร่วม 8561) · route ใหม่ 2 ไฟล์จากชื่อไฟล์ | ไม่เห็น · HAR เปิด `/account` แต่ไม่ได้กดเลื่อน → endpoint เดิม 7 ตัวเท่าเดิม | เส้นทาง HAR ไม่ได้เดินฟีเจอร์ใหม่ · static ไม่บอกว่าเปลี่ยนอะไร | `tests/cr01.mjs` 22/22 · `e2e-cr` CR01-UI-1/2 (3 เบราว์เซอร์) |
| CR-02 ส่วนลดกลุ่ม | ไม่มี (กฎราคาอยู่ฝั่งเซิร์ฟเวอร์ `web/lib/rules/pricing.ts` · `/package` `/book` hash เดิม) | **ไม่เห็น** (ไม่มี node changed ที่เกี่ยว) | ไม่เห็น · scenario/HAR เป็นนัดเดี่ยว 12 ต.ค. ยอด ฿1,000 เท่าเดิม | static วิเคราะห์แค่โค้ดฝั่งเบราว์เซอร์ · ส่วนลดใหม่มีผลกับกลุ่ม ≥ 3 คนที่จองตั้งแต่ 1 พ.ย. ซึ่งเส้นทางไม่ได้เดิน | `tests/cr02.mjs` 19/19 · golden price 62/62 · check-rules 90/90 |
| CR-03 กันจองซ้ำ | ข้อความ `DUPLICATE_BOOKING` ใน i18n (chunk ร่วม) · กฎอยู่ฝั่งเซิร์ฟเวอร์ `booking.ts` | **changed** เฉพาะ chunk ร่วม 8561 (ไม่บอกว่าเป็น CR-03 · รู้จากการเปิดอ่านเอง) · ตัวกฎไม่เห็น | ไม่เห็น · HAR จองครั้งเดียวด้วยเบอร์ที่ไม่ซ้ำ → 201 เหมือนเดิม | กฎฝั่งเซิร์ฟเวอร์ · เส้นทางไม่ได้จองซ้ำ | `tests/cr03.mjs` 18/18 · `e2e-cr` CR03-UI-1 |
| CR-04 วันหยุดร้าน | i18n `SHOP_CLOSED` · route ใหม่ `/api/holidays` · `/book` hash เดิม (หน้าจองไม่ได้เปลี่ยนฝั่งเบราว์เซอร์) | **changed** chunk ร่วม 8561 · route `/api/holidays` จากชื่อไฟล์ (`unknown` ในการเทียบ) | ไม่เห็น · scenario/HAR ใช้ 12 ต.ค. (ไม่ใช่วันหยุด) · ไม่มีการเรียก `/api/holidays` | กฎฝั่งเซิร์ฟเวอร์ + ตาราง DB (`shop_holiday` migration 001) · เส้นทางไม่ได้เลือก 23 ต.ค. | `tests/cr04.mjs` 14/14 · `e2e-cr` CR04-UI-1/2 · migration ซ้อม (MIGRATION-RUNBOOK) |
| CR-05 รายงานยอด | หน้าใหม่ `/admin/report` · route `/api/admin/report` · i18n `REPORT_RANGE` · เมนูใน `layout.tsx` | **unknown** (หน้าใหม่มีฝั่งขวาอย่างเดียว ไม่ขึ้น `added`) · `pages` = "ใหม่ใน v2" · route ใหม่จากชื่อไฟล์ · chunk 8561 changed · `(layout)` hash **เดิม** ทั้งที่ `layout.tsx` แก้ (layout เป็น server component → ไม่อยู่ใน bundle) | ไม่เห็น · HAR เปิด `/admin` (คิว) ไม่ได้เปิดรายงาน · `/api/admin/bookings` เท่าเดิม | coverage partial · เส้นทางไม่ได้เดินหน้าใหม่ · URL ต่อ query → fetch ไม่ถูกกู้ | `tests/cr05.mjs` 12/12 · `e2e-cr` CR05-UI-1/2 (3 เบราว์เซอร์) |

"REA ไม่เห็น" ≠ "ไม่ได้เปลี่ยน" · CR-02 CR-03 CR-04 เปลี่ยนกฎฝั่งเซิร์ฟเวอร์ที่ bundle ไม่มี → หลักฐานว่าทำตามที่ขอคือเทสต์ API · REA ใช้เป็นหลักฐานอีกด้านว่า **ของเดิมที่ลูกค้าเห็นไม่ขยับ** (หน้า 15 หน้า hash เดิม · HAR 7 endpoint เดิม · scenario ฿1,000 เดิม)

## 4. ทุกไฟล์ใน `git diff --stat 4a7908f..HEAD` (baseline: ระบบที่รับมอบ → HEAD) โยงกับ CR

66 ไฟล์ · +12,827 / −43

| ไฟล์ | CR / ที่มา |
|---|---|
| `web/lib/rules/pricing.ts` | CR-02 |
| `web/lib/server/booking.ts` | CR-02 (1) · CR-03 (35) · CR-04 (3) · CR-01 (164) |
| `web/lib/server/http.ts` | CR-03 · CR-04 · CR-01 (แม็ปรหัส error → HTTP status) |
| `web/lib/i18n.ts` | CR-03 · CR-04 · CR-01 · CR-05 (ข้อความ 3 ภาษา) |
| `web/lib/bot/chat.ts` | CR-03 · CR-04 (ข้อความ error ในแชท) |
| `web/lib/server/holiday.ts` · `web/app/api/holidays/route.ts` | CR-04 |
| `db/migrations/001_shop_holiday.sql` · `001_shop_holiday.down.sql` · `db/init/01-schema.sql` · `db/init/02-seed.sql` | CR-04 (migration + ให้ติดตั้งใหม่/reset ตรงกับ migration) |
| `web/lib/server/testmode.ts` | safety-net (seam นาฬิกา `3bcd8c9`) · CR-04 (เติม `shop_holiday` ใน `TABLES` · กับดัก T2) |
| `web/app/api/test/clock/route.ts` | safety-net (seam ทดสอบ · เปิดเฉพาะ `ALLOW_TEST_RESET=1`) — ไม่ใช่ CR แต่เป็นเครื่องมือทดสอบที่ CR-01/CR-02 ใช้ |
| `web/app/api/bookings/[id]/reschedule/route.ts` · `reschedule-slots/route.ts` · `web/components/MyBookings.tsx` · `web/lib/server/customer.ts` | CR-01 |
| `web/app/admin/report/page.tsx` · `web/app/api/admin/report/route.ts` · `web/components/AdminReport.tsx` · `web/lib/server/admin.ts` · `web/app/layout.tsx` (เมนูรายงาน) | CR-05 |
| `web/SPEC.md` | CR-02 · CR-03 · CR-04 · CR-01 · CR-05 (อัปเดตเอกสารเก่าตามกฎใหม่) |
| `tests/cr01.mjs`…`cr05.mjs` · `e2e-cr/tests/cr01/03/04/05.spec.ts` | CR-01 … CR-05 (เทสต์ใหม่) |
| `docs/impact/CR-01.md`…`CR-05.md` · `CHANGE-REPORT.md` · `CHANGE-REQUESTS/REGISTER.md` · `docs/TRACEABILITY.md` | CR-01 … CR-05 (เอกสารงาน) |
| `docs/MIGRATION-RUNBOOK.md` | CR-04 |
| `tests/golden/*` (5 ไฟล์) · `e2e-cr/` ตั้งต้น (`playwright.config.ts` `global-setup.ts` `fixtures.ts` `tsconfig.json` `package*.json`) · `e2e-cr/tests/char-booking.spec.ts` · `e2e-cr/tests/known-issues.spec.ts` · `KNOWN-ISSUES.md` | safety-net ก่อนแก้ CR (`3bcd8c9`) · ใช้เป็น regression ของทุก CR |
| `CLAUDE.md` · `.claude/settings.json` · `SYSTEM-MAP.md` · `HANDOVER-CHECK.md` · `docs/IMPACT-TEMPLATE.md` `ORACLE-CHANGES.md` `REA-INVENTORY.md` `SPEC-GAPS.md` | รับมอบ/เตรียมงาน (`8e2ffc6`) · ไม่แตะระบบ |
| `tools/rea-tools.mjs` · `tools/.gitignore` | ⚠️ ไม่ใช่ CR · อัปเดตเครื่องมือของคอร์ส (`a9d58de` "orchestrator: rea-tools subcommands") · ไม่อยู่ในระบบที่ส่งมอบ |
| `fast_track/README.md` | ⚠️ ไม่ใช่ CR · เอกสารคอร์ส (`3526f06` "orchestrator: sync fast_track README") · ไม่อยู่ในระบบที่ส่งมอบ |

ไฟล์ใน `web/` และ `db/` ทุกไฟล์โยง CR ได้ (ยกเว้น seam ทดสอบ 2 ไฟล์ที่มีที่มาเป็น safety-net) · ⚠️ 2 แถวอธิบายได้ (เครื่องมือ/เอกสารของคอร์ส)

## 5. ค่าที่คาดหวังเดิม

| คำสั่ง | ผล |
|---|---|
| `git diff --stat 4a7908f..HEAD -- web/scripts/check-rules.mjs e2e-legacy` | **ว่าง** |
| `git diff --stat 4a7908f..HEAD -- tests/golden` | 5 ไฟล์ +8,297 (ไฟล์ใหม่ทั้งหมด สร้างใน `3bcd8c9` จากพฤติกรรมเดิม [E]) · ไม่ใช่การเปลี่ยนค่าเดิม |
| `git diff --stat 3bcd8c9..HEAD -- tests/golden web/scripts/check-rules.mjs e2e-legacy` | **ว่าง** (golden ไม่ถูกแก้หลังสร้าง แม้ CR-02 เปลี่ยนราคา เพราะ golden ล็อกวันที่ก่อน 1 พ.ย.) |

→ ไม่มีค่าที่คาดหวังเดิมเปลี่ยน · `docs/ORACLE-CHANGES.md` ตารางว่างถูกต้อง (เติมบันทึกการตรวจรอบนี้แล้ว)

## 6. TRACEABILITY

`docs/TRACEABILITY.md` เติมแล้ว: ทุก CR (01–05) มี BR และ TC ที่ผ่านรอบนี้ · เทสต์ใหม่ทุกตัวมี CR หรือระบุว่าเป็น safety-net (CHAR-BOOK-01 · KI-01a/b KI-02a/b KI-03a · golden) · คอลัมน์ผล LAB 11 อ้างตัวเลขข้อ 1

## 7. ข้อสังเกต / ค้าง

- TC-SEC-05 (api) ล้มตั้งแต่รับมอบ ยังไม่มี CR แก้ · TC-UI-02 webkit flaky (ผ่านใน `test:all` รอบนี้ · รันซ้ำ 1/3)
- `record-har.mjs` reset และเปลี่ยนข้อมูล (B14 · B05 ยกเลิก) → reset กลับหลังเก็บหลักฐานแล้ว
- ค้างจาก CR (ไม่ใช่ regression): CR-04 ส่วน ข (หลังร้านเพิ่ม/ลบวันหยุดเอง) ยังไม่ทำ · คำถามที่ตัดสินแทนร้านรอ UAT ตาม `CHANGE-REQUESTS/REGISTER.md`
