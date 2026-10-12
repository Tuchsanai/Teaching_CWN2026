# CODEBASE-NOTES · ระบบเดิม "สบายใจ สปา" (บท 06)

> สำหรับผู้สอน/ผู้ออกแบบบท · อ่านจาก `06_sabai-spa-legacy-change-request/web` + `db` (คัดลอกจาก `04/_solution`) และเอกสารบท 04
> ตัวเลขที่มีป้าย **[รันจริง]** มาจากการรันบนสำเนาที่ `C:/t/work/a6/` เมื่อ 12 ต.ค. 2026 · ที่เหลือมาจากการอ่านโค้ด

---

## 0. สรุปสั้น

| หัวข้อ | ค่า |
|---|---|
| สแตก | Next.js **15.5.27** App Router + TypeScript 5.9 · PostgreSQL 16-alpine · `pg` 8.16 (SQL ตรง ไม่มี ORM) · bcryptjs · Node 22 (image) |
| ขนาด | `lib/` 32 ไฟล์ .ts · `app/api` 25 route · หน้า 14 หน้า · `components/` 22 ไฟล์ · schema 19 ตาราง |
| กฎร้าน | BR-01–20 เป็นฟังก์ชันบริสุทธิ์ใน `lib/rules/*` (เงินเป็น **สตางค์** integer) · ราคาที่บันทึกคิดที่เซิร์ฟเวอร์เสมอ |
| ชุดตรวจที่มีมาแล้ว | `web/scripts/check-rules.mjs` E01–E90 **ผ่าน 90/90** ที่ `BUG_MODE=0` · **80/90** ที่ `BUG_MODE=1` [รันจริง ~20 วินาที/รอบ] |
| e2e เดิม | อยู่ในบท 04 (`04/_solution/e2e`) 42 TC (Playwright 1.63) **ไม่ได้คัดลอกมาบท 06** |
| จุดอ่อนหลักสำหรับบท 06 | `lib/flags.ts` + `data-bug-mode` + SPEC บอกตำแหน่งบั๊กตรง ๆ (ดู CR-DESIGN §2) · มีบั๊กจริงที่ไม่ผูก flag อย่างน้อย 6 ตัว (§7) |

---

## 1. สถาปัตยกรรม: 2 compose project บน network ภายนอกเดียวกัน

```
docker network sabai-net (external, สร้างเอง)
├─ project "sabai-db"  (db/compose.yaml)
│   └─ container sabai-db   postgres:16-alpine  host 5433 → 5432
│       volume sabai-pgdata (named) · ./init → /docker-entrypoint-initdb.d (01-schema.sql, 02-seed.sql)
│       ⚠ init รันเฉพาะตอน volume ว่าง → แก้ schema ภายหลังต้องมี migration เอง หรือ down -v
└─ project "sabai-web" (web/compose.yaml)
    └─ container sabai-web  image sabai-web:latest  host 3000 → 3000
        Dockerfile 3 stage (deps → build `next build` → run standalone, USER node)
        additional_contexts dbinit=../db/init → คัดลอก 02-seed.sql ไป /app/sql/02-seed.sql (ใช้ตอน /api/test/reset)
        healthcheck: fetch /api/health ต้องได้ db:true
```

| env (web) | ค่าเริ่มต้นใน compose | ใช้ที่ |
|---|---|---|
| `DATABASE_URL` | `postgres://sabai:sabai@sabai-db:5432/sabai` | `lib/db.ts` (fallback นอก docker = `localhost:5433`) |
| `BUG_MODE` | `${BUG_MODE:-0}` | `lib/flags.ts` เท่านั้น |
| `ALLOW_TEST_RESET` | `${ALLOW_TEST_RESET:-1}` | `flags.allowTestReset` → `/api/test/*`, นาฬิกา, บัญชีทดสอบหน้า login, ปุ่มรีเซ็ต /admin |
| `SESSION_SECRET` | `sabai-jai-local-session-secret-2026` | `lib/session.ts` (HMAC-SHA256) |
| `TODAY` | ว่าง | `lib/clock.ts` (ดู §5 — ค่านี้แทบไม่ถูกใช้) |
| `SEED_SQL_PATH`, `PHOTO_DIR`, `TZ` | ตั้งใน Dockerfile | reset / รูป before-after / เวลาไทย |

ชั้นของโค้ด (ทิศทาง import ลงล่างอย่างเดียว):

| ชั้น | ไฟล์ | หน้าที่ |
|---|---|---|
| หน้า (RSC + client) | `app/*/page.tsx`, `components/*.tsx` | UI · ไม่คิดเงินเอง ยกเว้น `PackageCalc` (คูณ ฿2,900 × คน ฝั่ง client — กฎซ้ำ BR-19) และ `BookingWizard` เรียก `checkParty()` ฝั่ง client |
| route | `app/api/**/route.ts` | แปลง request → เรียก `lib/server/*` ผ่าน `handle()` (`ApiError` → JSON `{error,message}` ตามภาษา cookie `lang`; pg `23P01` → 409 `SLOT_TAKEN`) |
| service | `lib/server/booking.ts` (หลัก 26 KB), `customer.ts`, `catalog.ts`, `store.ts`, `admin.ts`, `testmode.ts`, `http.ts` | ตรวจกฎ + SQL + transaction (`withTx`) |
| กฎ | `lib/rules/*.ts` (ไฟล์ละ BR) + `index.ts` re-export | ฟังก์ชันบริสุทธิ์ |
| bot | `lib/bot/chat.ts`, `mood.ts`, `quiz.ts` | กฎตายตัว (NFR-15) · แชทจองผ่าน `buildQuote`/`createBooking` ตัวเดียวกับเว็บ (FR-26) |
| infra | `lib/db.ts`, `clock.ts`, `flags.ts`, `session.ts`, `i18n.ts` (39 KB, 3 ภาษา), `money.ts` | |

---

## 2. ตาราง DB (19 ตาราง · `db/init/01-schema.sql`)

| ตาราง | คีย์/ข้อจำกัดสำคัญ | seed |
|---|---|---|
| `customer` | email UNIQUE · `role` customer/owner · `lifetime_spend` NUMERIC · `points_balance` ≥ 0 | 9 แถว (U01–U08 + owner id 9) |
| `therapist` | code UNIQUE · `active` | T01–T06 |
| `therapist_service` | PK (therapist, service) | 33 คู่ (ใครทำบริการไหนได้) |
| `service` | kind single/package/course · `duration_min` · `price` · `includes_transport` | S01–S07, P01 (120 นาที ฿2,900), K01 (คอร์ส ฿15,000) |
| `herb`, `service_herb` | sort_order | 14 สมุนไพร |
| `room` | capacity | **1 แถว** Couple Suite (โค้ดผูก `room_id = 1` ตายตัว ดู §7) |
| `hotel` | distance_km NUMERIC(4,1) | H01–H06 (2.0 / 5.0 / 5.1 / 12.0 / 15.0 / 15.1) |
| `course_purchase` | `used + reserved ≤ total` · expires ≥ purchased | C01–C04 |
| `booking` | `period` = GENERATED tstzrange `[start,end)` · CHECK ตามแบบจอง · `giftcard_paid + other_paid = total_amount` · **EXCLUDE `booking_room_no_overlap`** (ห้องเดียวกันห้ามซ้อน ยกเว้น cancelled) | B01–B13 |
| `booking_slot` | UNIQUE (booking, therapist) · **EXCLUDE `booking_slot_no_overlap`** (นักบำบัดซ้อนไม่ได้ เมื่อ active) | 18 แถว |
| `review` | stars 1–5 · booking_id NULL ได้ | 17 รีวิว (T04 ไม่มีรีวิว) |
| `waist_measurement` | booking_id UNIQUE | 4 จุดของ C01 |
| `body_photo` | phase before/after · storage_key (ไฟล์ใน `private/photos`) | 2 |
| `gift_card` | face 500–10000 จำนวนเต็ม · `expires_on = purchased_on + 365` (CHECK) | GC01–GC05 |
| `gift_card_txn` | amount ≠ 0 (ลบ = ใช้, บวก = คืน) | 3 |
| `point_txn` | reason earn/redeem/refund/opening · ผลรวม = `points_balance` | 6 |
| `birthday_use` | PK (customer, year_month) = BR-13 ครั้งเดียว/เดือน | U05 202610 |
| `app_setting` | key/value | `test_today = 2026-10-10T10:00:00+07:00` |

ข้อมูล seed ต่อเดือน (ตามวันนัด เวลาไทย) **[รันจริง: SQL บน seed]**

| เดือน | สถานะ | จำนวน | Σ total | Σ ส่วนลด % | Σ แต้มที่ให้ |
|---|---|---|---|---|---|
| 2026-08 | completed | 2 (คอร์ส B08 B09) | ฿0 | ฿0 | 0 |
| 2026-09 | completed / cancelled | 3 (B10 B12 คอร์ส, B13 ฿1,900) / 1 (B11) | ฿1,900 | ฿100 (tier) | 19 |
| 2026-10 | completed | 1 (B07 ฿1,440 birthday) | ฿1,440 | ฿360 | 14 |
| 2026-10 | confirmed | 6 (B06 B05 B01 B03 B04 B02) | ฿11,130 | ฿870 | 0 |

นับนัดต่อนักบำบัด (completed/confirmed): T01 2/2 · T02 0/3 · T03 1/2 · T04 0/2 · T05 3/1 · T06 0/1 [รันจริง]

---

## 3. กฎร้าน (BR) → ไฟล์ / ฟังก์ชัน / จุดเรียกใช้

| BR | กฎ | ฟังก์ชันกฎ | ถูกเรียกจาก | ป้องกันซ้ำใน DB |
|---|---|---|---|---|
| BR-01 | 10:00–22:00 ทุก 30 นาที จบ ≤ 22:00 | `rules/slots.ts` `buildSlots()`, `isValidStartTime()`, `fitsDay()` (private) | `availableSlots()`, `buildQuote()` · ข้อความเวลาเปิดซ้ำใน `i18n.ts` (`footer.hours`, `home.subtitle`) และ `bot/chat.ts` บรรทัด 64–66 | — |
| BR-02 | นักบำบัด 1 คิว/เวลา `[start,end)` | `rules/overlap.ts` `overlaps()`, `freeTherapists()` (เรียง id น้อย → D7) | `availableSlots()`, `createBooking()` + `busySlots()` | EXCLUDE `booking_slot_no_overlap` |
| BR-03 | จอง +1 ถึง +30 วัน | `rules/dates.ts` `isBookableDate()`, `bookableRange()` | `availableSlots()`, `buildQuote()`, `app/book/page.tsx` (min/max) | — |
| BR-04 | คู่ 2 คนพอดี · Couple Suite 1 คู่ | `rules/party.ts` `checkParty()` | `buildQuote()`, `createBooking()` + `roomBusy()` (**`room_id = 1` hardcode**) · client `BookingWizard.next1()` | EXCLUDE `booking_room_no_overlap` + CHECK couple |
| BR-05 | กลุ่ม 3–6 · 7+ โทรร้าน | `checkParty()` | เหมือน BR-04 · `createBooking()` ตรวจนักบำบัดพอ | CHECK party_size 1–6 |
| BR-06 | กลุ่ม ≥ 4 ลด 10% (ไม่ใช้กับแพ็กเกจ) | `rules/pricing.ts` `bestPercent()` (`GROUP_DISCOUNT_MIN_PEOPLE`, `GROUP_PCT`) | `calcPrice()` | — |
| BR-07 | ยกเลิกเองเมื่อเหลือ ≥ 24 ชม. | `rules/cancel.ts` `canCancel()` | `cancelBooking()`, `myBookings()` (ปุ่ม) | — |
| BR-08 | เฉลี่ยทศนิยม 1 ปัดครึ่งขึ้น · กรอง ≥ 4.5 | `rules/rating.ts` `ratingTenths()`, `passesRatingFilter()` | `catalog.listTherapists()` | — |
| BR-09 | แต้ม = floor(ฐาน ÷ 100) | `rules/points.ts` `pointsFor()`, `earnBase()` (**flag `loyaltyBasis`**) | `calcPrice()` (แต้มที่จะได้) + `completeBooking()` (ให้จริง) | — |
| BR-10 | 100 แต้ม = ฿50 เป็นก้อน ไม่ติดลบ | `redeemPoints()`, `maxRedeemBlocks()` | `calcPrice()`, `buildQuote()` (`POINTS_NOT_ENOUGH`) | CHECK `points_redeemed % 100 = 0` |
| BR-11/12 | Silver/Gold/Platinum · "อีก ฿X" | `rules/tier.ts` `tierOf()`, `nextTier()`, `TIER_PCT` | `buildQuote()`, `customer.tierInfo()` | — |
| BR-13 | เดือนเกิด 20% 1 ครั้ง/เดือน ตามวันนัด | `rules/birthday.ts` `birthdayEligible()` | `buildQuote()`, `createBooking()` (insert), `cancelBooking()` (คืนสิทธิ์ถ้ายังไม่เลยเดือน D4) | PK `birthday_use` |
| BR-14 | คอร์ส 11 ครั้ง 180 วัน | `rules/course.ts` | `buildQuote()` (เลือกคอร์สหมดก่อน), `createBooking()` reserved+1, `cancelBooking()` reserved−1, `completeBooking()` used+1 · `store.buyCourse()` | CHECK used+reserved ≤ total |
| BR-15/16 | Gift Card ฿500–10,000 · 365 วัน | `rules/giftcard.ts` | `store.buyGiftCard()`, `giftCardInfo()`, `buildQuote()`, `createBooking()`/`cancelBooking()` (txn) | CHECK face/expiry |
| BR-17/18 | ≤ 5 กม. ฟรี · ≤ 15 กม. ฿300/คัน · คันละ 4 | `rules/transport.ts` `transportQuote()`, `vehiclesFor()` | `calcPrice()`, `/api/transport` · ข้อความ `i18n transport.rule` | CHECK distance ≤ 15.0 |
| BR-19 | แพ็กเกจ ฿2,900 × คน รถรวมแล้ว | `calcPrice()` type package + `transportQuote(..., true)` | **ซ้ำฝั่ง client** `components/PackageCalc.tsx` (คำนวณเอง) | — |
| BR-20 | ลำดับ: เต็ม → % สูงสุด 1 อัน → แต้ม → รถ → Gift Card · สรุป = เก็บจริง | `calcPrice()` (**วนตาม flag `priceSteps`**) | `buildQuote()` · `createBooking()` เทียบ `quotedTotal` → 409 `PRICE_CHANGED` | — |

สมมติฐาน (A1–A20 ใน REQUIREMENTS §5) ที่ยัง "รอร้านตอบ" = แหล่ง Change Request ตามธรรมชาติ เช่น A2 วันหยุดนักขัตฤกษ์, A4 Couple Suite เต็ม, A16 ส่วนลดซ้อน

---

## 4. จุด flag / BUG_MODE ทั้งหมด

ทุกจุดอ่านผ่าน `lib/flags.ts` (getter อ่าน `process.env` ทุกครั้ง)

| flag | `BUG_MODE=0` | `BUG_MODE=1` | ผู้ใช้ | เคสที่ล้มเมื่อเปิด [รันจริง] |
|---|---|---|---|---|
| `closingBufferMin` | 0 | 1 นาที | `rules/slots.ts` `fitsDay()` | E05 E07 E09 E20 |
| `priceSteps` | `["percent","points"]` | `["points","percent"]` | `rules/pricing.ts` `calcPrice()` | E87 E88 E89 |
| `loyaltyBasis` | `"net"` | `"list"` | `rules/points.ts` `earnBase()` | E39 E40 E50 (E88 ด้วย) |
| `bugMode` | "0" | "1" | `app/layout.tsx` → `<html data-bug-mode>` · `check-rules.mjs` อ่านค่านี้แล้วตั้ง `process.env.BUG_MODE` ให้ unit test · ch04 `e2e/global-setup.ts` + `build-report.mjs` แสดงป้ายโหมด | — |
| `allowTestReset` | env `ALLOW_TEST_RESET` (ค่าเริ่ม "1") | | `/api/test/reset`, `/api/test/today` (404 เมื่อปิด), `clock.ts`, `login/page.tsx` (บัญชีทดสอบ), `admin/page.tsx` (ปุ่มรีเซ็ต) | — |

ผลรัน check-rules [รันจริง]: `BUG_MODE=0` **ผ่าน 90/90** · `BUG_MODE=1` **ผ่าน 80/90** ล้ม E05, E07, E09, E20, E39, E40, E50, E87, E88, E89 (ตรงกับ `ORIGINAL-BUGS-ch04.md`)

ช่องทางที่ทำให้หาบั๊กเจอโดยไม่ต้องทดสอบ (สำคัญต่อบท 06 ที่ให้ Agent อ่าน repo): `grep BUG_MODE` → `flags.ts` มีคอมเมนต์บอกเรื่อง 3 บรรทัด · SPEC §2 เขียนว่า "`1` = เปิดบั๊กที่ตั้งใจใส่ 3 ตัว (เฉลยใน `BUGS.md`)" · หน้าเว็บมี `data-bug-mode` → ข้อเสนอแก้ใน CR-DESIGN §2

---

## 5. Test hooks

| hook | ทำอะไร | หมายเหตุสำหรับบท 06 |
|---|---|---|
| `POST /api/test/reset {now?}` | `LOCK TABLE booking` → `TRUNCATE <19 ตาราง> RESTART IDENTITY CASCADE` → รัน `02-seed.sql` ทั้งไฟล์ → ตั้ง `app_setting.test_today` = now (ค่าเริ่ม `2026-10-10T10:00:00+07:00`) ใน transaction เดียว | **รายชื่อตารางเขียนตายตัวใน `lib/server/testmode.ts` `TABLES`** → เพิ่มตารางใหม่แล้วลืมใส่ = seed INSERT ชน PK → reset 500 → ทุกเทสต์ล้ม (กับดักของ CR ที่มี migration) · seed ต้องอยู่ในไฟล์ `02-seed.sql` ไฟล์เดียว (`SEED_SQL_PATH`) |
| `GET /api/test/today` | `{now, today}` จาก `clock()` | ไม่ต้องล็อกอิน |
| นาฬิกา `lib/clock.ts` | ลำดับ: `app_setting.test_today` (เมื่อ `ALLOW_TEST_RESET=1`) → env `TODAY` → เวลาจริง | seed **ใส่ test_today เสมอ** → ตอน `ALLOW_TEST_RESET=1` env `TODAY` ไม่มีผล · ตอน `=0` (โปรดักชัน) ถ้ามีคนตั้ง `TODAY` ไว้ นาฬิกาโปรดักชันจะค้าง · **ไม่มี hook "เลื่อนนาฬิกาโดยไม่ล้างข้อมูล"** → ทดสอบ "จองวันนี้ แล้วกดเสร็จวันนัด" ต้องแก้ `app_setting` ตรงด้วย SQL |
| `ALLOW_TEST_RESET=0` | ปิดทุก hook + ซ่อนบัญชีทดสอบ/ปุ่มรีเซ็ต | compose ตั้งค่าเริ่มเป็น `1` → "ระบบจริง" ที่ deploy ด้วย compose นี้เปิด reset ไว้โดยไม่ต้องล็อกอิน (ขัด A20/NFR-14 "ซ่อนในโหมดใช้งานจริง") |
| `<html data-ready="true|false">` | `components/ReadyFlag.tsx` ตั้งเมื่อ hydrate เสร็จ | ใช้รอใน Playwright |

---

## 6. ชุดตรวจที่มีอยู่

### 6.1 `web/scripts/check-rules.mjs` (42 KB · ESM · Node ≥ 22.18 เพราะ import `.ts` ตรง)

| ส่วน | รายละเอียด |
|---|---|
| ขอบเขต | E01–E90 จาก TEST-DATA.md (BR-01–20 + NFR-12/17) · 90 เคส |
| วิธี | ก่อนทุกเคส `reset(now)` · client จำ cookie เอง · `quoteAndBook()` = `/api/price` → `/api/bookings` ด้วย `quotedTotal` → อ่านยอดจาก `/api/admin/bookings` (owner) สะสมไว้ตรวจ **E90** (สรุป = db ทุกการจอง ต้อง ≥ 15 การจอง) |
| unit | เคส `{unit:true}` เรียก `R.calcPrice/pointsFor/redeemPoints/...` จาก `lib/rules/index.ts` ตรง (ผูกกับ **signature ของ `calcPrice` input object**) |
| ผูกกับ flag | อ่าน `data-bug-mode` จาก `/` แล้วตั้ง `process.env.BUG_MODE` ก่อน import กฎ |
| ข้อห้ามในไฟล์ | "ค่าที่คาดหวังมาจาก TEST-DATA.md / REQUIREMENTS.md (ห้ามแก้ให้ตรงกับโค้ด)" |
| พฤติกรรมที่เทสต์พึ่งพา (สำคัญเวลาแก้บั๊ก) | E39/E40 กด "ใช้บริการเสร็จ" B05 (นัด 11 ต.ค.) ขณะ today = 10 ต.ค. · E88 จองนัด 16 ต.ค. แล้วกดเสร็จทันที → **ถ้าแก้ให้กดเสร็จได้เฉพาะเมื่อถึงเวลานัด เคสเหล่านี้ต้องเปลี่ยน setup** |
| เวลา | ~20 วินาที/รอบ [รันจริง] |
| วันที่ที่เคสใช้ | 10-10 ถึง 10-21, 10-24, 10-31, 11-01, 11-02, 11-09, 11-10 (+ 2027 สำหรับวันหมดอายุ) · **ไม่ใช้ 10-22, 10-23** · บริการ S03 ไม่ถูกใช้เลย |

### 6.2 e2e Playwright บท 04 (`04/_solution/e2e`) — ไม่มีในโฟลเดอร์บท 06

| ไฟล์ | TC |
|---|---|
| book.spec / book.api.spec | BOOK-01–10 (BOOK-06 = API กดพร้อมกัน) |
| price / transport / member | PRICE-01–06 · TRN-01–03 · MEM-01–04 |
| course / cancel / giftcard | CRS-01–03 · CXL-01–03 · GC-01–04 |
| therapist / i18n / ui / security.api | TH-01 · I18N-01 · UI-01–02 · SEC-01–05 |

config: project `api` + chromium/firefox/webkit · `workers: 1` (ฐานข้อมูลร่วม + นาฬิการ่วม) · th-TH · Asia/Bangkok · reset ก่อนทุก test · ผลบท 04 โหมดปกติล้ม 4/42 (TRN-03, GC-04, SEC-04 = เว็บผิด · SEC-05 = แผนผิด) · โหมดบั๊กล้ม 9/42 (เอกสาร BUG-HUNT.md บท 04 — ไม่ได้รันซ้ำในงานนี้)
→ บท 06 ควรคัดลอก e2e มาเป็น "ชุด regression ที่ผู้รับเหมาเดิมส่งมอบ" (ดู CR-DESIGN §3)

---

## 7. บั๊ก/จุดเสี่ยงจริงที่ไม่ผูก flag (มีแม้ `BUG_MODE=0`)

ยิง API บนสำเนา [รันจริง: `C:/t/work/a6/probe/probe.mjs`, reset ก่อนแต่ละข้อ, today = 10 ต.ค. 10:00]

| # | อาการ | หลักฐาน | ต้นเหตุ (ไฟล์) | ใช้ทำอะไรในบท 06 |
|---|---|---|---|---|
| L1 | คนเดียวกันส่งคำขอจองเดิมซ้ำได้หลายนัด | guest ส่ง S01 20 ต.ค. 14:00 เดิม 3 ครั้ง → 201 ทั้ง 3 (B14 T01, B15 T02, B16) | `createBooking()` ไม่มีกฎ "นัดซ้ำของคนเดียวกัน" · ระบบจัดนักบำบัดคนถัดไปให้ | **CR-03** (เรื่องร้องเรียน) · UI กดสองครั้งไม่ซ้ำเพราะ `disabled={busy}` (TC-BOOK-05 บท 04 ผ่าน) แต่ API/แชท/เน็ตหลุดซ้ำได้ |
| L2 | ร้านกด "ใช้บริการเสร็จ" นัดในอนาคตได้ → ลูกค้าได้แต้ม/ยอดสะสมก่อนมา | B02 (นัด 17 ต.ค.) กดเสร็จวันที่ 10 → 200 · U02 แต้ม 0 → 25 · ยอดสะสม ฿30,000 → ฿32,520 | `completeBooking()` ไม่ตรวจเวลา | ข้อสอบชุด B (แก้แล้ว E39/E40/E88 ต้องเปลี่ยน setup) |
| L3 | logout แล้ว cookie เดิมยังใช้ได้ | `/api/me` ด้วย cookie เดิม → 200 "คุณนิดา" | session HMAC แบบ stateless ไม่มีรายการเพิกถอน (`lib/session.ts`) · logout แค่ลบ cookie | งานเสริม/ข้อสอบ (ต้องมีตาราง session → migration) |
| L4 | ติ๊ก "ต้องการรถ" แต่ไม่เลือกโรงแรม/ไม่ใส่ระยะ ไปขั้น 4 ได้ ไม่มีบรรทัดค่ารถ | TC-TRN-03 บท 04 (อ่านโค้ด: `body()` ส่ง `hotelCode/distanceKm = null` เมื่อว่าง · `next3()` ไม่ตรวจ) | `components/BookingWizard.tsx` | ข้อสอบชุด A (UI + Playwright) |
| L5 | ใส่รหัส Gift Card ที่ไม่มี → ไม่มีข้อความ | API ตอบ 422 `GC_NOT_FOUND` [รันจริง] แต่ wizard `setGcCode("")` → คิดราคาใหม่สำเร็จ → `setQuoteErr(null)` ข้อความหายทันที | `BookingWizard.tsx` บรรทัด ~188 | LAB characterization (บันทึกเป็น known issue) |
| L6 | เบอร์โทรผู้จองไม่ตรวจรูปแบบ | guest `contactPhone: "abc"` → 201 B14 | `createBooking()` ตรวจแค่ไม่ว่าง | ใช้ร่วมกับ CR-03 (normalize เบอร์) |
| L7 | owner ยกเลิกนัดของลูกค้าได้ (ยังติดกฎ 24 ชม.) | owner ยกเลิก B02 → 200 | `cancelBooking()` `session.role !== "owner"` | SPEC ไม่ได้เขียน (§8) |
| L8 | test hooks เปิดโดยไม่ต้องล็อกอิน | `GET /api/test/today` → 200 | compose ค่าเริ่ม `ALLOW_TEST_RESET=1` | เรื่องคุยใน release/UAT |

จุด "กับดัก regression" (ไม่ใช่บั๊ก แต่ CR มักพังตรงนี้):

| กับดัก | ที่อยู่ | CR ที่โดน |
|---|---|---|
| `room_id = 1` เขียนตายตัว 2 ที่ (`roomBusy()` WHERE และ `roomId = 1` ใน `createBooking()`) | `lib/server/booking.ts` | เพิ่มห้องคู่ |
| `TABLES` ของ reset เขียนตายตัว + seed ไฟล์เดียว + init รันเฉพาะ volume ว่าง | `testmode.ts`, Dockerfile, `db/compose.yaml` | ทุก CR ที่มีตารางใหม่ (CR-04) |
| ข้อความกฎซ้ำในข้อความแสดงผล (เวลาเปิด, ค่ารถ, 100 แต้ม = ฿50, 180 วัน, 20%) | `lib/i18n.ts`, `lib/bot/chat.ts`, `lib/bot/quiz.ts` | เปลี่ยนตัวเลขกฎ |
| แพ็กเกจคิดราคาซ้ำฝั่ง client | `components/PackageCalc.tsx` | เปลี่ยนราคาแพ็กเกจ |
| `bestPercent()`/`calcPrice()` ถูก unit test เรียกด้วย object input | `check-rules.mjs` E45 E50 E71 | เพิ่ม parameter ให้ `calcPrice` (CR-02) |
| บอทแนะนำบริการด้วยรหัสตายตัว (S03 ใช้ 6 ที่ใน mood/quiz/chat/skin) | `lib/bot/*`, `SkinAnalyzer.tsx` | ปิดบริการชั่วคราว |
| แชทจองผ่าน `availableSlots`/`createBooking` → error ใหม่ไปโผล่ในแชทผ่าน `errorBody()` ต้องมีคีย์ i18n ครบ 3 ภาษา | `lib/bot/chat.ts` 257–297 | ทุก CR ที่เพิ่ม error code |

---

## 8. SPEC (AI เขียน) ไม่ตรงกับโค้ด

| # | SPEC บอก | โค้ดจริง | ผล |
|---|---|---|---|
| S1 | §1, §2: "เฉลยใน `BUGS.md`" · ค่า `BUG_MODE` | บท 06 ไม่มี `web/BUGS.md` (ย้ายไป `_solution/_design/ORIGINAL-BUGS-ch04.md`) | อ้างไฟล์ที่ไม่มี + บอกว่ามีบั๊กฝัง |
| S2 | §6 cancel: "403 (นัดคนอื่น)" | owner ยกเลิกนัดคนอื่นได้ 200 (L7) | ไม่ได้บันทึกสิทธิ์ owner |
| S3 | §6 logout "→ ออกจากระบบ" | ลบ cookie ฝั่งเบราว์เซอร์อย่างเดียว token ใช้ได้ถึง 7 วัน (L3) | ความปลอดภัย |
| S4 | §6 complete: ไม่กล่าวถึงเวลา · D11 "ให้แต้มตอนร้านกดเสร็จ (หลังใช้บริการ)" | กดเสร็จนัดอนาคตได้ (L2) | ช่องว่างของสเปก |
| S5 | §2 `TODAY` "ใช้เมื่อไม่มี app_setting.test_today" | seed ใส่ test_today เสมอ → ตอน `ALLOW_TEST_RESET=1` ไม่มีทางใช้ `TODAY` | อ่านแล้วเข้าใจผิดได้ |
| S6 | §8 `book-giftcard-error` แสดง error บัตร · §5 `GC_NOT_FOUND` 422 | API ตอบถูก แต่หน้าจองไม่แสดง (L5) | UI ไม่ตรงสเปก |
| S7 | §6 response `/api/giftcards/:code`, `/api/me/bookings`, `/api/wallet`, `/api/admin/bookings` | โค้ดคืน field เกิน: `channel` · `serviceCode,type,people,dateLabel` · `courseId` ใน waist/photos · `serviceCode,statusLabel` | เล็กน้อย (เกิน ไม่ขาด) |
| S8 | §4 BR-04 "`roomBusy()`" | ไม่บอกว่า `room_id = 1` ตายตัว | ซ่อนข้อจำกัด "ห้องเดียว" |
| S9 | ตาราง env: `ALLOW_TEST_RESET` ค่าเริ่ม `1` | REQUIREMENTS A20/NFR-14 ให้ "ซ่อนในโหมดใช้งานจริง" | สเปกกับความต้องการขัดกันเอง (L8) |
| S10 | §4 สมมติฐาน "แชทจองได้เฉพาะบริการเดี่ยว 1 คน" | ตรง (`chat.ts` บังคับ `type: "single"`) | ✅ |

---

## 9. หมายเหตุสภาพแวดล้อม (เจอระหว่างรัน)

- พอร์ต host **3066 ใช้ไม่ได้บนเครื่องนี้**: อยู่ในช่วงที่ Windows สงวน (`netsh interface ipv4 show excludedportrange protocol=tcp` → 2970–3069, 3070–3169) → `bind: forbidden` · วิธีที่ใช้แทน: ไม่ map พอร์ตเว็บ แล้วรัน `check-rules.mjs` จาก container `node:22-alpine` ที่อยู่ใน network เดียวกัน (`BASE_URL=http://a6-sabai-web:3000`) · DB map 5466 ได้
- ใช้ชื่อ compose project / container / volume / network แยก (`a6-*`) เพื่อไม่ชน `sabai-*` และ `a2-sabai-*` ที่มีอยู่บนเครื่อง · ปิดและลบ container/volume/network ของตัวเองแล้ว
- ข้อเสนอสำหรับเครื่องมือของผู้สอน (ตรวจข้อสอบหลายคน): ใช้รูปแบบเดียวกัน — compose project ต่อคน ไม่เปิดพอร์ต host รันชุดตรวจใน container (ดู EXAM-BLUEPRINT §4)
