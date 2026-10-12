# REA-FEASIBILITY · ลอง REA กับ "ระบบเดิม" สบายใจ สปา (บท 06)

> ไฟล์ออกแบบสำหรับผู้สอน · รันจริงเมื่อ 12 ต.ค. 2026 บนเครื่อง Windows 11 + Docker Desktop · REA `rea-lab:6.4.0` (`rea --version` = 6.4.0) · Playwright 1.63
> โค้ดที่ใช้ = สำเนา `web/` `db/` ของบทนี้ที่ `C:/t/work/a2/` (ไม่แก้ไฟล์ในบท) · `BUG_MODE=0` · เวลาทดสอบ `TODAY` = 2026-10-10 10:00 (จาก `/api/test/reset`)
> ไฟล์ช่วย + หลักฐานย่ออยู่ใน [`rea-probe/`](rea-probe/) (JSON ทุกไฟล์ < 300 KB)

---

## 1. สรุปผล (อ่านตารางนี้พอ)

| # | ขั้น | คำสั่ง / เครื่องมือ | ผล | เวลา | ใช้ในบท 06? |
|---|---|---|---|---|---|
| 1 | เปิดระบบ | `docker compose up` (db + web) · `GET /api/health` · `POST /api/test/reset` | ✅ db healthy 7 วิ · `next build` 35 วิ (deps cache) · health 200 `{"ok":true,"db":true}` · reset 200 | ~50 วิ | ✅ |
| 2 | Static bundle | `analyze-javascript-application .next/static` → `inspect-analysis-view` | ✅ exit 0 · Evidence 36.8 MB → summary 15 KB · endpoint จาก `fetch` จริง **9/25** route · ชื่อไฟล์ route stub **25/25** | 53 วิ + 7 วิ | ✅ (แผนที่ภาพรวม) |
| 3 | HAR เส้นทางหลัก | `record-har.mjs` (Playwright headless) → `inspect-web-network-capture` | ✅ 135 request · API **7 endpoint / 10 ครั้ง** พร้อม method, query, body keys, status · cookie ถูกปิดค่าอัตโนมัติ | 10 วิ + 3 วิ | ✅ (สำคัญที่สุด) |
| 4 | Trace ฟีเจอร์ | `trace-application-feature` seed `/api/price`, `/api/bookings` | ⚠️ `direction:"both"` = ทั้งกราฟ 510/510 node (ไร้ประโยชน์) · `incoming` = 10–11 node ชี้ถูกว่าเรียกจาก `app/book/page` · seed `/cancel` หาโค้ดที่เรียกไม่เจอ | 7–9 วิ/ครั้ง | ⚠️ ใช้ได้แบบจำกัด |
| 5 | Browser scenario | `capture-browser-scenario` → `host.docker.internal:3261` | ✅ 12 step ผ่านหมด · 1.5 วิ · DOM + screenshot หน้าสรุป ฿1,000 · `completeness: complete` | 3 วิ | ✅ (golden master หน้าจอ) |
| 6 | อ่าน DB | `docker exec … psql -c '\dt'` / `'\d booking'` | ✅ 19 ตาราง · CHECK 51 · FK 25 · EXCLUDE (gist) 2 · REA ไม่อ่าน Postgres | < 1 วิ | ✅ (คู่กับ REA) |
| 7 | เทียบเวอร์ชัน | `compare-application-versions` v1 ↔ v2/v3 | ✅ v3 (GROUP_MAX 6→8 ฝั่งเบราว์เซอร์) **เห็น** module ใน `app/book/page` เปลี่ยน · ❌ v2 (ยกเลิก 24→48 ชม. ฝั่งเซิร์ฟเวอร์) **ไม่เห็นใน .next/static** · ✅ เห็นถ้าเทียบ `.next/server` แต่ปนสัญญาณรบกวน 117 รายการ | build 33 วิ + analyze 51 วิ + compare 14 วิ | ⚠️ สอนเป็นข้อจำกัด |

**ข้อสรุปหลัก**
1. REA ใช้ได้จริงกับ Sabai Spa แต่เห็นได้ **เฉพาะสิ่งที่ส่งไปถึงเบราว์เซอร์** — กฎธุรกิจเกือบทั้งหมดของระบบนี้อยู่ฝั่งเซิร์ฟเวอร์ (`lib/rules/*`, `lib/server/*`) และใน **DB constraint** ซึ่ง REA มองไม่เห็นจาก static bundle
2. ตัวที่คุ้มสุดสำหรับผู้เรียนคือ **HAR + `inspect-web-network-capture`** (ได้สัญญา API จริงพร้อม body) และ **`capture-browser-scenario`** (หลักฐานหน้าจอก่อน/หลังแก้) · static analysis ใช้เป็น "แผนที่หยาบ" 1 รอบพอ
3. REA ต้องจับคู่กับ **การอ่าน repo** (มี source ครบ → skill ของ REA เองก็บอกให้อ่าน repo ปกติ) และ **การอ่าน DB ด้วย psql** — ทั้ง 3 มุมรวมกันจึงได้ภาพครบ (ดูตารางข้อ 3)
4. ข้อควรระวังเชิงปฏิบัติ: พอร์ตที่ Windows จองไว้ (ข้อ 5.1) · HAR ต้องบันทึกผ่าน `127.0.0.1` ไม่ใช่ `localhost` · PowerShell 5.1 `>` เขียนไฟล์เป็น UTF-16 → ให้ REA เขียนไฟล์ในคอนเทนเนอร์เอง

---

## 2. รายละเอียดแต่ละขั้น

### 2.1 เปิดระบบ (ขั้น 1)

| สิ่งที่ทำ | ผล |
|---|---|
| คัดลอก `web/` `db/` → `C:/t/work/a2/` แก้เฉพาะสำเนา: container `a2-sabai-web`/`a2-sabai-db`, network `a2-sabai-net`, volume `a2-sabai-pgdata`, project `a2-sabai-web`/`a2-sabai-db`, `DATABASE_URL=postgres://sabai:sabai@a2-sabai-db:5432/sabai`, db `5461:5432` | ✅ |
| `docker network create a2-sabai-net` · `docker compose -f db/compose.yaml up -d --wait` | ✅ healthy ใน 7 วิ |
| `docker compose -f web/compose.yaml up -d --build --wait` ที่พอร์ต **3061** | ❌ `ports are not available: exposing port TCP 0.0.0.0:3061 … bind: An attempt was made to access a socket in a way forbidden by its access permissions.` (build ผ่านแล้ว 42 วิ, `next build` 35.3 วิ) |
| สาเหตุ: `netsh interface ipv4 show excludedportrange protocol=tcp` → Windows จองช่วง **2970–3069** ไว้ (Hyper-V/WinNAT) | เปลี่ยนเป็น **3261** (นอกช่วงจอง ไม่ชนงานอื่น) → up 6 วิ ✅ |
| `curl http://localhost:3261/api/health` | 200 · `{"ok":true,"db":true}` · 8 ms |
| `curl -X POST http://localhost:3261/api/test/reset` | 200 · `{"ok":true,"now":"2026-10-10T10:00:00+07:00"}` · 180 ms |

> ⚠️ ช่วง 2970–3069 บนเครื่องนี้ **ครอบพอร์ต 3000 ของผู้เรียนด้วย** (ไม่ได้ทดลอง bind 3000 เพราะห้ามใช้ แต่ตาราง excludedportrange ระบุชัด) → ดูข้อ 5.1

### 2.2 Static bundle analysis (ขั้น 2)

```bash
docker cp a2-sabai-web:/app/.next/static v1/.next/static          # 79 ไฟล์ 1.3 MB
docker run --rm -v C:/t/work/a2/v1:/work rea-lab:6.4.0 analyze-javascript-application /work/.next/static --json > ev/rea-static-v1.json
node rea-tools.mjs view ev/rea-static-v1.json ev/view-summary-v1.json
docker run --rm -v C:/t/work/a2:/work rea-lab:6.4.0 inspect-analysis-view /work/ev/view-summary-v1.json --format json > summary-v1.json
```

| ตัวชี้วัด | ค่า |
|---|---|
| exit / เวลา / ขนาด | 0 · 53 วิ · 36.8 MB (summary 15 KB) |
| statistics | relevant_files 54 · parsed 54 · parse_failures 0 · modules 346 · findings 950 |
| graph | node 510 (javascript-module 436, javascript-asset 30, javascript-chunk 25, **endpoint 12**, unknown 6, artifact 1) · edge 1,068 |
| coverage | application `partial` · semantic `partial (truncated)` · semantic unknowns 5,364 |
| วิเคราะห์ไม่ครบ (resource limit) | `framework`, `4bd1b696`, `1255` (worker heap หมด) · `main` (เกิน result budget) · `polyfills` (semantic budget) = chunk ของ React/Next ทั้งหมด ไม่ใช่โค้ดแอป |
| endpoint ที่กู้ได้ | `/api/auth/logout` `/api/price` `/api/auth/login` `/api/bookings` `/api/test/reset` `/api/chat` `/api/courses` `/api/quiz` `/api/giftcards` (9 ตัวจริง) + `a` `b` `c` (ชื่อย่อ minified ใน polyfills = ขยะ) |
| storage | 0 (ตรงกับจริง: แอปไม่ใช้ localStorage/sessionStorage มีแค่ `document.cookie` ภาษา ซึ่ง REA ไม่นับ) |
| ของแถมที่มีประโยชน์ | Next ใส่ stub `chunks/app/api/<route>/route-*.js` ใน static → REA inventory มีชื่อไฟล์ route **ครบ 25/25** (ไม่มี method/พารามิเตอร์) + หน้า `chunks/app/<page>/page-*.js` ครบ 14 หน้า + `_not-found` |

**ทำไมพลาด 7 ตัวที่เบราว์เซอร์เรียกจริง:** ทุกตัวเป็น template literal ที่ minify แล้วเป็น `.concat()` เช่น `fetch("/api/bookings/".concat(t,"/cancel"),{method:"POST"})` ใน `chunks/app/account/page-*.js` → extractor ของ REA เก็บเฉพาะสตริงตายตัว

### 2.3 HAR ของเส้นทางหลัก (ขั้น 3)

สคริปต์ [`rea-probe/record-har.mjs`](rea-probe/record-har.mjs) (Playwright 1.63 headless, context ของตัวเอง ไม่แตะ Chrome ผู้ใช้):
services → จองแบบไม่ล็อกอิน S01 12 ต.ค. 15:00 → ใบสรุปราคา → ยืนยัน → ล็อกอิน `nida@sabai.test` → บัญชี → ยกเลิก B05 → ออก → ล็อกอิน `owner@sabai.test` → `/admin`

| ผลจากสคริปต์ (log จริง) | |
|---|---|
| reset | 200 |
| ยอดใบสรุป | `ยอดสุทธิ: ฿1,000` |
| จองสำเร็จ | `B14` |
| คุณนิดา | ประวัติ 8 รายการ · ปุ่มยกเลิก B06 disabled = `true` (เหลือ 5 ชม.) |
| ยกเลิก B05 | `ยกเลิกแล้ว` (เหลือ 24 ชม. พอดี) |
| admin 12 ต.ค. | 2 แถว |
| เวลา / ไฟล์ | 10 วิ · 135 entries (document 16, static 50, RSC 59, **API 10**) · 3.9 MB |

| ปัญหาที่เจอ | วิธีแก้ |
|---|---|
| บันทึกด้วย `http://localhost:3261` → REA: `HAR schema validation failed: format` ที่ `/log/entries/0/serverIPAddress` (Playwright เขียน `"[::1]"`) | บันทึกผ่าน `http://127.0.0.1:…` → `serverIPAddress: "127.0.0.1"` ผ่าน |
| REA ปิดค่า cookie/Set-Cookie ให้เอง แต่ **รหัสผ่านใน body ของ `/api/auth/login` ยังอยู่** | ใส่ `--sensitive-value Nida@2026 --sensitive-value Owner@2026` → body ถูกแทนเป็น `null` (`reason: explicit-sensitive-value`) |
| Evidence ทั้งไฟล์ 6.2 MB (รวม static/RSC) | เลือกเฉพาะ API ด้วย `--record 37 --record 39 …` (10 ordinal) → 60 KB |

**API inventory (จาก Evidence ของ REA, `node rea-tools.mjs har-api`)**

| endpoint | ครั้ง | status | query | request body keys | response keys (ย่อ) |
|---|---|---|---|---|---|
| `GET /api/slots` | 1 | 200 | service, date, type, people | – | date, service, durationMin, min, max, slots |
| `POST /api/price` | 2 | 200 | – | type, serviceCode, people, date, time, therapists, contactName, contactPhone, redeemBlocks, useBirthday, giftCardCode, hotelCode, distanceKm, coursePurchaseId | gross, discountKind/Pct/Amount, points…, transportFee, total, lines, birthdayAvailable, … (30 key) |
| `POST /api/bookings` | 1 | 201 | – | (เหมือน price) + **quotedTotal** | bookingId, code, status, total, therapistNames, message, detail, quote |
| `POST /api/auth/login` | 2 | 200 | – | (ถูกปิดด้วย sensitive-value) | ok, user |
| `POST /api/bookings/{id}/cancel` | 1 | 200 | – | – | ok, bookingId, code, status |
| `POST /api/auth/logout` | 1 | 200 | – | – | ok |
| `GET /api/admin/bookings` | 2 | 200 | date | – | date, today, bookings |

> ข้อสังเกตเพื่อสอน: หน้า `/services`, `/account`, `/admin` **ไม่เรียก `/api/services`, `/api/me`, `/api/me/bookings`** — Server Component อ่าน DB ผ่าน `lib/server/*` ตรง ๆ แล้วส่งมาเป็น RSC (59 request `?_rsc=`) → HAR เห็นแค่ "API ที่ client component เรียก" เท่านั้น

### 2.4 Trace ฟีเจอร์จอง/ราคา (ขั้น 4)

input: `node rea-tools.mjs trace-input ev/rea-static-v1.json "/api/price" incoming t.json` → `rea trace-application-feature /work/t.json`

| seed (kind / direction) | ผล | อ่านว่า |
|---|---|---|
| string `/api/price` / `both` | 510 node, 1,068 edge, 17 terminal paths (= ทั้งกราฟ) · 2.6 MB | ❌ ไม่ได้อะไร |
| string `/api/price` / `incoming` | 10 node · endpoint `/api/price` ← module `#7037`, `#4518` ใน `chunks/app/book/page-*.js` | ✅ บอกถูกว่าฟีเจอร์ราคาอยู่หน้า `/book` |
| string `/api/bookings` / `incoming` | 11 node · endpoint ← `chunks/app/book/page-*.js` | ✅ |
| string `/api/price` / `outgoing` | 29 node (ส่วนใหญ่เป็น route stub 25 ตัว) | ⚠️ ปน |
| string `/cancel` / `incoming` | 5 node = แค่ไฟล์ stub `api/bookings/[id]/cancel/route` · **ไม่เจอ** `account/page` ที่เรียกจริง | ❌ (template literal) |
| api `/api/price`, route `/book` | 0 match | ❌ seed แบบนี้ไม่ match บน Next bundle |

- seed ที่ใช้ได้: `node-id`, `route`, `string`, `api`, `channel`, `module`, `native-export` · direction: `outgoing` / `incoming` / `both` (ได้จาก error ของ REA)
- seed `string` จับ route stub ที่ไม่เกี่ยวด้วย (เช่น `auth/login/route`, `photos/[id]/route`) เพราะ stub ทุกตัวมีเนื้อไฟล์เหมือนกัน (`route-bec84dfb05562f55.js`) REA จึงรวมเป็น module เดียว
- สิ่งที่ trace **ไม่มีทางเห็น**: สูตรราคา (`lib/rules/pricing.ts`), การจองซ้อน, ส่วนลด — อยู่ฝั่งเซิร์ฟเวอร์ทั้งหมด

### 2.5 `capture-browser-scenario` (ขั้น 5)

ไฟล์ [`rea-probe/scenario-book-quote.json`](rea-probe/scenario-book-quote.json) (ในบทตั้งเป็นพอร์ต 3000; ตอนรันจริงใช้ 3261): services → `service-book-S01` → next → วันที่ 2026-10-12 → รอ `book-slot-15:00` → เลือก → next → ชื่อ/เบอร์ → รอยอด → next → รอ `summary-amount-total` · capture `dom` + `screenshot` + `url` + events `network`, `console`, `page-errors`

| ผล | ค่า |
|---|---|
| exit / เวลา | 0 · wall 3 วิ · `duration_ms` 1,526 |
| step | 12/12 `completed` · `completeness: complete, equality_eligible: true` |
| DOM | มี `data-testid="summary-amount-total" data-amount="1000">฿1,000` |
| screenshot | PNG 107 KB → [`evidence/scenario-book-quote-final.png`](rea-probe/evidence/scenario-book-quote-final.png) (หน้า "4. สรุปก่อนจ่าย" นวดไทย 60 นาที · 12 ต.ค. 15:00–16:00 · ฿1,000) |
| network | 120 event · API: `GET /api/slots…` 200, `POST /api/price` 200 · `request-failed` 5 ตัว = RSC prefetch `net::ERR_ABORTED` (ปกติของ Next ไม่ใช่บั๊ก) |
| console / page error | 0 |

ข้อผิดที่เจอระหว่างเขียน JSON (REA บอกตำแหน่งชัด แก้ตามได้ทันที):
1. `action: "zzz"` → expected `goto, click, fill, press, select_option, check, uncheck, wait_for, wait_for_timeout`
2. `"value": "2026-10-12"` → `invalid_type expected object` → ต้องเป็น `{"source":"literal","value":"2026-10-12"}` (หรือ `"source":"secret"` สำหรับรหัสผ่าน)

### 2.6 มุมมองฐานข้อมูล (ขั้น 6) — REA ไม่ทำ Postgres

```powershell
docker exec sabai-db psql -U sabai -d sabai -c '\dt'
docker exec sabai-db psql -U sabai -d sabai -c '\d booking'
```

| สิ่งที่ได้ | ค่า (จริง) |
|---|---|
| ตาราง | 19: app_setting, birthday_use, body_photo, booking, booking_slot, course_purchase, customer, gift_card, gift_card_txn, herb, hotel, point_txn, review, room, service, service_herb, therapist, therapist_service, waist_measurement |
| constraint | CHECK 51 · FK 25 · EXCLUDE 2 (`booking_room_no_overlap`, `booking_slot_no_overlap` ใช้ gist) · extension `btree_gist` |
| view / trigger / function ของแอป | 0 / 0 / 0 → logic อยู่ใน TypeScript + CHECK constraint |
| แถวหลัง reset | booking 13 · booking_slot 18 · customer 9 · service 9 · therapist 6 · review 17 · `app_setting.test_today = 2026-10-10T10:00:00+07:00` |
| **กฎธุรกิจที่อยู่ใน DB** (จาก `\d booking`) | `booking_type <> 'group' OR party_size BETWEEN 3 AND 6` · `party_size <= 6` · couple ต้อง 2 คน + มีห้อง · `giftcard_paid + other_paid = total_amount` · `points_redeemed % 100 = 0` · `distance_km <= 15.0` · ห้อง/นักบำบัดห้ามซ้อนเวลา (EXCLUDE gist) |

> บทเรียนสำคัญ: CR "รับกลุ่มได้ถึง 8 คน" แก้แค่ `GROUP_MAX` ใน `lib/rules/party.ts` **ไม่พอ** — DB จะปฏิเสธด้วย CHECK `booking_check3`/`booking_party_size_check` → ต้องมี migration ด้วย · REA (และ HAR) ไม่มีทางบอกเรื่องนี้ ต้องอ่าน DB

เครื่องมือเสริมที่แนะนำ (ไม่ได้ทดสอบในงานนี้): `pg_dump --schema-only` สำหรับเก็บ schema เป็นไฟล์ให้ Claude อ่าน · ER diagram จาก DBeaver/pgAdmin

### 2.7 เทียบเวอร์ชัน (ขั้น 7)

สร้าง 2 รุ่นจากสำเนา (diff อยู่ใน `rea-probe/variant-*.diff`) แล้ว `docker build --target build` → `docker cp …/.next/static`

| รุ่น | แก้อะไร | build | ไฟล์ static ที่ต่าง (diff -rq) |
|---|---|---|---|
| v1 | ต้นฉบับ | 35 วิ | – |
| v1b | ต้นฉบับ (ควบคุม) | 6 วิ (cache) | **ไม่มี** (byte-identical เพราะ Docker cache จึงไม่ได้ analyze ซ้ำ) |
| v2 | `CANCEL_MIN_MS` 24 → **48 ชม.** (กฎฝั่งเซิร์ฟเวอร์) | 32 วิ | แค่โฟลเดอร์ build id (`2OXm…` → `pR3T…`) |
| v3 | `GROUP_MAX` 6 → **8** (`checkParty` ถูก import ใน `BookingWizard` = ฝั่งเบราว์เซอร์ด้วย) | 33 วิ | build id + `chunks/app/book/page-*.js` (`if(t>6)` → `if(t>8)`) |

| การเทียบ (`compare-application-versions`) | summary | สิ่งที่ REA ชี้ | สรุป |
|---|---|---|---|
| static v1 → v3 | changed 12 · unknown 557 · added/removed 0 | ✅ module `#7037`, `#4117` ใน `chunks/app/book/page` เปลี่ยน (location+properties) + endpoint `/api/price` `/api/bookings` ย้ายตำแหน่ง + manifest/unknown chunk (สัญญาณรบกวน) | **เห็นการเปลี่ยนจริง** |
| static v1 → v2 | changed 8 · unknown 674 | มีแค่ `_buildManifest`/`_ssgManifest` + chunk ที่ analyze ไม่ครบ 5 ตัว → **ไม่มี module ของแอปเปลี่ยน** | ❌ มองไม่เห็นกฎยกเลิก (ถูกต้อง เพราะไม่ได้อยู่ในเบราว์เซอร์) |
| `.next/server` s1 → s2 (เพิ่มเติม) | changed 117 · unknown 518 · analyze 15/32 วิ · 50 MB ต่อรุ่น · compare 17 วิ | กรองเฉพาะ dimension `content` แล้วไม่ใช่ `*client-reference-manifest*` เหลือ `chunks/1291.js` (โค้ดจริงที่มี `1728e5` = 48 ชม.) + manifest 3 ไฟล์ | ⚠️ เห็นได้ ถ้ามี server build และรู้วิธีกรอง |

**ความไม่นิ่งของ REA:** v2 มีไฟล์ chunk เหมือน v1 ทุกไบต์ (ต่างแค่ชื่อโฟลเดอร์ build id) แต่ผล analyze ต่างกัน — v1: module 436, endpoint 12, unknown 6 · v2: module 550, endpoint 16, unknown 7 (chunk ที่ชน resource limit ไม่เหมือนกันในแต่ละรอบ) → ผลเทียบมี `unknown` หลายร้อยเสมอ ต้องสอนให้อ่านเฉพาะ `changed` ที่เป็นโค้ดแอป

---

## 3. REA เห็น API กี่ตัว เทียบรายการจริง (`app/api/**/route.ts` = 25)

| route จริง | ใครเรียก (จาก source) | REA static endpoint | REA HAR (เส้นทางที่บันทึก) | ชื่อไฟล์ใน static | วิธีที่เห็นแน่ ๆ |
|---|---|---|---|---|---|
| `/api/admin/bookings` | AdminQueue (template) | – | ✅ GET ?date | ✅ | HAR / repo |
| `/api/admin/bookings/[id]/complete` | AdminQueue (template) | – | – (ไม่ได้กดในเส้นทาง) | ✅ | repo |
| `/api/auth/login` | LoginForm | ✅ | ✅ POST | ✅ | |
| `/api/auth/logout` | LogoutButton | ✅ | ✅ POST | ✅ | |
| `/api/bookings` | BookingWizard | ✅ | ✅ POST 201 | ✅ | |
| `/api/bookings/[id]/cancel` | MyBookings (template) | – | ✅ POST | ✅ | HAR / repo |
| `/api/chat` | ChatBox | ✅ | – | ✅ | |
| `/api/courses` | BuyCourseButton | ✅ | – | ✅ | |
| `/api/giftcards` | GiftCardShop | ✅ | – | ✅ | |
| `/api/giftcards/[code]` | GiftCardShop (template) | – | – | ✅ | repo |
| `/api/health` | (healthcheck เท่านั้น) | – | – | ✅ | repo |
| `/api/hotels` | ไม่มี client เรียก | – | – | ✅ | repo |
| `/api/me` | ไม่มี client เรียก | – | – | ✅ | repo |
| `/api/me/bookings` | ไม่มี client เรียก | – | – | ✅ | repo |
| `/api/mood` | MoodPicker (template) | – | – | ✅ | repo |
| `/api/photos/[id]` | `<img src>` จาก `lib/server/customer.ts` | – | – | ✅ | repo |
| `/api/price` | BookingWizard | ✅ | ✅ POST | ✅ | |
| `/api/quiz` | Quiz | ✅ | – | ✅ | |
| `/api/services` | ไม่มี client เรียก | – | – | ✅ | repo |
| `/api/slots` | BookingWizard (template) | – | ✅ GET | ✅ | HAR / repo |
| `/api/test/reset` | AdminQueue | ✅ | (เรียกผ่าน request API ไม่เข้า HAR) | ✅ | |
| `/api/test/today` | ไม่มี client เรียก | – | – | ✅ | repo |
| `/api/therapists` | ไม่มี client เรียก | – | – | ✅ | repo |
| `/api/transport` | TransportCalc (template) | – | – | ✅ | repo |
| `/api/wallet` | ไม่มี client เรียก | – | – | ✅ | repo |

| วิธี | เจอ | % ของ 25 | ได้รายละเอียดอะไร |
|---|---|---|---|
| REA static — endpoint จาก `fetch` | 9 | **36%** (= 9/16 = 56% ของตัวที่ client เรียกจริง) | path + ไฟล์ที่เรียก ไม่มี method/body |
| REA static — ชื่อไฟล์ route stub | 25 | 100% | แค่ชื่อ path (เฉพาะ Next.js App Router) |
| REA HAR (เส้นทางที่บันทึก) | 7 | 28% | method, query, body keys, response keys, status |
| REA static ∪ HAR | 12 | 48% | |
| อ่าน repo (`app/api/**/route.ts`) | 25 | 100% | ทุกอย่าง รวม method ที่ export และกฎ |

---

## 4. ข้อจำกัดที่พบ (สำหรับเขียนในบท)

| # | ข้อจำกัด | ผลต่อผู้เรียน | ทางแก้ |
|---|---|---|---|
| L1 | เห็นแค่โค้ดฝั่งเบราว์เซอร์ · กฎธุรกิจ/ราคา/ยกเลิก/จองซ้อนอยู่ฝั่งเซิร์ฟเวอร์ | REA บอก "อะไรเรียกอะไร" ไม่บอก "คิดยังไง" | อ่าน `lib/rules/*` ใน repo · ทดสอบผ่าน API/HAR |
| L2 | template literal (`.concat`) → endpoint หาย 7 ตัว | เชื่อ endpoint list ของ REA อย่างเดียวไม่ได้ | ใช้ HAR + `grep "fetch("` ใน repo |
| L3 | Server Component อ่าน DB ตรง → 9 route ไม่มีใครเรียกจาก client | HAR ไม่เห็น `/api/services`, `/api/me`, … | อ่าน repo |
| L4 | chunk framework ชน heap/budget ทุกรอบ (5–7 ไฟล์) · ผลไม่นิ่งระหว่างรอบ | `unknown` หลายร้อยใน compare | อ่านเฉพาะ `changed` ที่เป็น `chunks/app/*` |
| L5 | `trace … direction both` = ทั้งกราฟ · seed `api`/`route` ไม่ match | trace ดูเหมือนไม่ทำงาน | ใช้ `string` + `incoming` |
| L6 | Evidence ใหญ่ (static 37 MB, server 50 MB, HAR 6 MB) | Claude อ่านไม่ไหว | `inspect-analysis-view` / `--record` / `rea-tools.mjs` สรุป |
| L7 | HAR `localhost` → `[::1]` ไม่ผ่าน schema | inspect ล้ม | ใช้ `127.0.0.1` |
| L8 | รหัสผ่านใน body ไม่ถูกปิดอัตโนมัติ (cookie ปิดให้) | หลุดลง Evidence | `--sensitive-value` |
| L9 | REA ไม่อ่าน Postgres | ไม่รู้ CHECK/EXCLUDE ที่บังคับกฎ | `docker exec … psql \dt \d` |
| L10 | Windows จองช่วงพอร์ต (เครื่องนี้ 2970–3069 ครอบ 3000) | `docker compose up` ล้ม `bind: … forbidden` | ข้อ 5.1 |
| L11 | image `rea-lab:6.4.0` 2.65 GB · analyze ~50 วิ/รอบ | ช้า/เปลืองดิสก์ | build image ไว้ก่อนเรียน · analyze รอบเดียวแล้วเก็บไฟล์ |

---

## 5. ข้อเสนอ LAB onboarding บท 06 (REA + อ่าน repo + อ่าน DB)

### 5.1 เตรียมเครื่อง (ก่อนเรียน)
- `netsh interface ipv4 show excludedportrange protocol=tcp` — ถ้า 3000 หรือ 5433 อยู่ในช่วง ให้รัน (Admin) `net stop winnat` → `docker compose up` → `net start winnat` (ยังไม่ได้ทดสอบในงานนี้) หรือเปลี่ยนพอร์ตใน compose ของตัวเอง
- `docker build -t rea-lab:6.4.0 <บท 05>/rea` ไว้ล่วงหน้า (2.65 GB)
- `cd _solution/_design/rea-probe; npm i` (ได้ `@playwright/test` 1.63)

### 5.2 ลำดับ LAB (ประมาณ 90–120 นาที)

| LAB | เป้าหมาย | ผู้เรียนทำ / พรอมต์ให้ Claude | เครื่องมือ | ผลงาน |
|---|---|---|---|---|
| 0 | เปิดระบบเดิม | `docker network create sabai-net` → `docker compose -f db/compose.yaml up -d` → `docker compose -f web/compose.yaml up -d --build` → `/api/health` → `POST /api/test/reset` | Docker | ระบบรันที่ 3000 |
| 1 | แผนที่ black-box (15 นาที) | `mkdir rea-in\.next; docker cp sabai-web:/app/.next/static rea-in/.next/static` → `docker run --rm -v "${PWD}:/work" --entrypoint sh rea-lab:6.4.0 -c "rea analyze-javascript-application /work/rea-in/.next/static --json > /work/ev/static.json"` → `node rea-tools.mjs endpoints ev/static.json` | REA static | รายการหน้า + endpoint ที่ "เห็นจากเบราว์เซอร์" |
| 2 | สัญญา API จากการใช้งานจริง (20 นาที) | `node record-har.mjs http://127.0.0.1:3000 ev/journeys.har` → `node rea-tools.mjs har-records ev/journeys.har` (ได้ `--record …` เฉพาะ API) → `rea inspect-web-network-capture /work/ev/journeys.har har --record … --sensitive-value Nida@2026 --sensitive-value Owner@2026` → `node rea-tools.mjs har-api …` | Playwright + REA HAR | ตาราง API inventory (method/body/response) |
| 3 | อ่าน repo เทียบ (20 นาที) | พรอมต์: "อ่าน `web/app/api/**` และ `components/*` สร้างตาราง route ทั้งหมด: method, ใครเรียก, ไฟล์กฎใน `lib/rules` ที่ใช้ · แล้วเทียบกับ `static-endpoints` และ `har-api` บอกว่าตัวไหน REA ไม่เห็นเพราะอะไร" | Claude Code อ่าน repo | ตารางแบบข้อ 3 + CLAUDE.md/CODEBASE-NOTES ของทีม |
| 4 | อ่าน DB (15 นาที) | `docker exec sabai-db psql -U sabai -d sabai -c '\dt'` · `-c '\d booking'` · พรอมต์: "จาก `\d booking` สรุปกฎธุรกิจที่ DB บังคับ เทียบกับ `lib/rules/*` ว่าซ้ำ/ขัดกันตรงไหน" | psql | รายการกฎใน DB vs โค้ด |
| 5 | Impact analysis ของ CR (15 นาที) | เช่น CR "กลุ่มสูงสุด 8 คน": `trace-application-feature` seed `"/api/price"` `incoming` (หน้าไหนเรียก) + `grep GROUP_MAX` + CHECK ใน DB → รายการไฟล์/ตาราง/เทสต์ที่ต้องแตะ | REA trace + repo + DB | ใบ impact (ไฟล์ · migration · เทสต์ถดถอย) |
| 6 | Golden master ก่อนแก้ | `capture-browser-scenario scenario-book-quote.json` (DOM + screenshot) + เก็บ HAR เดิม | REA scenario | หลักฐาน "ก่อน" |
| 7 | แก้ → พิสูจน์ (หลังทำ CR) | rebuild → `docker cp` static ใหม่ → `compare-application-versions` (+ `cmp-sum`) → รัน scenario ซ้ำ เทียบ DOM/ยอด · รันเทสต์ Playwright/`check-rules.mjs` | REA compare + Playwright | CHANGE-REPORT: REA เห็นอะไร / ต้องพิสูจน์ด้วยเทสต์อะไร |

**ประเด็นที่อยากให้ผู้เรียนค้นพบเอง:** (1) REA ไม่เห็นกฎยกเลิก 24 ชม. (v2) แต่เห็น GROUP_MAX (v3) เพราะอะไร · (2) แก้ GROUP_MAX อย่างเดียว DB จะปฏิเสธ (CHECK 3–6) · (3) HAR ไม่เห็น `/api/me` ทั้งที่หน้า account แสดงข้อมูล

---

## 6. ไฟล์ใน `rea-probe/`

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `record-har.mjs` + `package.json` | บันทึก HAR เส้นทางหลัก (ค่าเริ่ม `http://127.0.0.1:3000`) |
| `scenario-book-quote.json` | scenario จองถึงหน้าสรุปราคา สำหรับ `capture-browser-scenario` (`host.docker.internal:3000`) |
| `rea-tools.mjs` | สร้าง input/สรุปผล: `view`, `endpoints`, `trace-input`, `trace-sum`, `cmp-input`, `cmp-sum`, `har-records`, `har-api` |
| `variant-v2-cancel-48h.diff` · `variant-v3-group-max-8.diff` | การแก้ที่ใช้ทดสอบขั้น 7 |
| `evidence/static-v1-inspect-summary.json` (15 KB) · `static-v1-endpoints.md` | ผลขั้น 2 |
| `evidence/har-inspect-api-only.json` (60 KB, ปิดรหัสผ่าน/cookie แล้ว) · `har-api-inventory.md` | ผลขั้น 3 |
| `evidence/trace-summaries.md` | ผลขั้น 4 |
| `evidence/scenario-book-quote.slim.json` · `scenario-book-quote-final.png` | ผลขั้น 5 |
| `evidence/db-dt.txt` · `db-d-booking.txt` · `db-facts.txt` | ผลขั้น 6 |
| `evidence/compare-summaries.md` | ผลขั้น 7 |

เก็บกวาดแล้ว: `docker compose down -v` ทั้ง `a2-sabai-web` / `a2-sabai-db` (ลบ volume `a2-sabai-pgdata`) · `docker network rm a2-sabai-net` · ลบ image `a2-sabai-web:latest`, `a2-sabai-build:v1b/v2/v3` · ไม่แตะ `sabai-net`, `sabai-pgdata` และ container อื่น
