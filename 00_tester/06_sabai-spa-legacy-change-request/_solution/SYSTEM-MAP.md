# SYSTEM-MAP · สบายใจ สปา (ระบบเดิมที่รับมอบ)

> แผนที่ระบบสำหรับทีมใหม่ · ทุกแถวอ้าง `ไฟล์:บรรทัด` (path นับจากรากโฟลเดอร์บท) หรือชื่อ constraint ที่เปิดดูจริง
> ป้ายแหล่ง: **[source]** = โค้ดใน repo · **[DB]** = ผล psql จากฐานที่รันอยู่ · **[E ev_xxxxxxxx]** = Evidence ของ REA ใน `docs/REA-INVENTORY.md` · **[SPEC §]** = `web/SPEC.md` (เอกสารเก่า ฉบับ 1.0 ก.ย. 2569)
> ไม่ได้แก้โค้ด · ไม่ได้เปิด `_solution/` และ `CHANGE-REQUESTS/answers/` · คำถามที่ SPEC กับโค้ดไม่ตรงกันอยู่ใน `docs/SPEC-GAPS.md`

---

## 1. สถาปัตยกรรม

```
เบราว์เซอร์ ──http://localhost:${WEB_PORT:-4000}──▶ [sabai06-web : Next.js standalone :3000] ──postgres://sabai06-db:5432──▶ [sabai06-db : postgres:16-alpine]
                                                         │  network ภายนอก (external) sabai06-net  │
psql/เครื่องมือบน host ──localhost:${DB_PORT:-5433}────────────────────────────────────────────────▶┘
```

| เรื่อง | ค่า | อ้าง |
|---|---|---|
| compose project เว็บ | `name: sabai06-web` · service/container `sabai06-web` · image `sabai06-web:latest` · `restart: unless-stopped` | `web/compose.yaml:1` `:4` `:10-12` |
| build เว็บ | context `web/` + `additional_contexts: dbinit: ../db/init` (ดึง seed เข้า image) | `web/compose.yaml:5-9` |
| พอร์ตเว็บ | `"${WEB_PORT:-4000}:3000"` (ใน container 3000 เสมอ) | `web/compose.yaml:14` · `web/Dockerfile:22` |
| healthcheck เว็บ | `fetch http://127.0.0.1:3000/api/health` ต้องได้ `db:true` · ทุก 10 วิ retries 12 | `web/compose.yaml:24-29` |
| compose project ฐานข้อมูล | `name: sabai06-db` · container `sabai06-db` · `postgres:16-alpine` | `db/compose.yaml:1` `:4-6` |
| พอร์ต db | `"${DB_PORT:-5433}:5432"` | `db/compose.yaml:15` |
| volume | `sabai06-pgdata` (ชื่อคงที่) → `/var/lib/postgresql/data` | `db/compose.yaml:17` `:27-29` |
| init SQL | `./init` → `/docker-entrypoint-initdb.d` (ro) · รันเฉพาะตอน volume ว่าง | `db/compose.yaml:18` |
| healthcheck db | `pg_isready -U sabai -d sabai` | `db/compose.yaml:21-25` |
| network | `sabai06-net` **external: true** ทั้ง 2 project → ต้อง `docker network create sabai06-net` ก่อน `up` | `web/compose.yaml:22-23` `:31-33` · `db/compose.yaml:19-20` `:31-33` |
| Dockerfile | 3 stage `deps` (npm ci --ignore-scripts) → `build` (`npx next build` ไม่ต่อ db) → `run` (node:22-alpine + tzdata, `USER node`, `node server.js`) | `web/Dockerfile:5-8` `:10-15` `:17-34` |
| seed ใน image | `COPY --from=dbinit 02-seed.sql ./sql/02-seed.sql` | `web/Dockerfile:31` |
| สแตก | Next 15.5.27 · react 19.1.1 · pg 8.16.3 (SQL ตรง ไม่มี ORM) · `output: "standalone"` | `web/package.json:15-17` · `web/next.config.ts:4` · `web/lib/db.ts:1` |

### env ที่มีผล

| ตัวแปร | ตั้งที่ | ค่าเริ่มต้น | ผล | อ้างฝั่งโค้ด |
|---|---|---|---|---|
| `DATABASE_URL` | compose | `postgres://sabai:sabai@sabai06-db:5432/sabai` | ที่ต่อ db (ไม่มี env → `localhost:5433`) | `web/compose.yaml:16` · `web/lib/db.ts:11` |
| `ALLOW_TEST_RESET` | compose | `1` (ทั้ง compose และโค้ด) | เปิด `/api/test/*` · นาฬิกาอ่าน `app_setting.test_today` · บัญชีทดสอบหน้า login · ปุ่มรีเซ็ต /admin | `web/compose.yaml:19` · `web/lib/config.ts:4-5` |
| `SESSION_SECRET` | compose | `sabai-jai-local-session-secret-2026` (โค้ด fallback `sabai-dev-secret-change-me`) | กุญแจ HMAC cookie `sabai_session` | `web/compose.yaml:20` · `web/lib/session.ts:13-14` |
| `TODAY` | compose | ว่าง | นาฬิกาสำรอง (ลำดับ 2) | `web/compose.yaml:21` · `web/lib/clock.ts:27-30` |
| `TZ` | compose / Dockerfile | `Asia/Bangkok` | โซนเวลา container (โค้ดคิด +7 เองอีกชั้น) | `web/compose.yaml:18` · `web/Dockerfile:24` · `web/lib/rules/time.ts:3` |
| `SEED_SQL_PATH` | Dockerfile | `/app/sql/02-seed.sql` | seed ที่ reset ใช้ | `web/Dockerfile:25` · `web/lib/server/testmode.ts:21-25` |
| `PHOTO_DIR` | Dockerfile | `/app/private/photos` | ที่เก็บรูป before/after (นอก public) | `web/Dockerfile:26` · `web/app/api/photos/[id]/route.ts:9` |
| `WEB_PORT` / `DB_PORT` | compose (host) | 4000 / 5433 | พอร์ตฝั่ง host เท่านั้น | `web/compose.yaml:14` · `db/compose.yaml:15` |
| `POSTGRES_USER/PASSWORD/DB` · `PGTZ` | db compose | `sabai`/`sabai`/`sabai` · `Asia/Bangkok` | | `db/compose.yaml:9-13` |

---

## 2. ชั้นของโค้ด

```
app/<หน้า>/page.tsx (server component)  ──เรียก lib/server/* ตรง ๆ (ไม่ผ่าน API)──┐
components/*.tsx (client) ──fetch──▶ app/api/**/route.ts ──▶ lib/server/*.ts ──▶ lib/rules/*.ts (ฟังก์ชันบริสุทธิ์)
                                                     │            └──▶ lib/db.ts (pg Pool, withTx) ──▶ PostgreSQL
                                                     └──▶ lib/clock.ts ("วันนี้" จุดเดียว)
lib/bot/chat.ts (แชท) ──เรียก buildQuote/createBooking/availableSlots ตัวเดียวกับเว็บ
```

- route ทุกตัวห่อด้วย `handle()` → `ApiError` เป็น JSON `{error,message}` · pg `23P01` (EXCLUDE ชน) → 409 `SLOT_TAKEN` [source `web/lib/server/http.ts:35-46`]
- หน้า server component เรียก lib ตรง เช่น `/account` import `lib/server/customer.ts` [source `web/app/account/page.tsx:8` `:29` `:31`] · `/book` ใช้ `clock()` + `bookableRange()` [source `web/app/book/page.tsx:21` `:51`]
- เงินใน `lib/rules` เป็นสตางค์ (integer) · JSON เป็นบาท [source `web/lib/db.ts:43-57` `web/lib/money.ts`]

### ตาราง route (25 ไฟล์ · 26 handler: GET 15 · POST 11)

นับด้วย `find web/app/api -name route.ts | wc -l` = 25 และ `grep -rhoE "export (async )?function (GET|POST|...)" web/app/api` = GET 15 · POST 11

| # | method | path | ไฟล์:บรรทัด | ฟังก์ชันที่เรียก | component ที่เรียก |
|---|---|---|---|---|---|
| 1 | GET | `/api/health` | `web/app/api/health/route.ts:6` | `getPool().query("SELECT 1")` | ไม่มี component · healthcheck `web/compose.yaml:25` |
| 2 | POST | `/api/test/reset` | `web/app/api/test/reset/route.ts:8` | `resetTestData()` `web/lib/server/testmode.ts:37` | `web/components/AdminQueue.tsx:138` |
| 3 | GET | `/api/test/today` | `web/app/api/test/today/route.ts:9` | `clock()` | ไม่มี (grep ใน web/ e2e-legacy/ scripts/ ไม่พบผู้เรียก) |
| 4 | POST | `/api/auth/login` | `web/app/api/auth/login/route.ts:10` | bcrypt.compare + `encodeSession()` | `web/components/LoginForm.tsx:19` |
| 5 | POST | `/api/auth/logout` | `web/app/api/auth/logout/route.ts:6` | ตั้ง cookie ว่าง maxAge 0 | `web/components/LogoutButton.tsx:15` |
| 6 | GET | `/api/services` | `web/app/api/services/route.ts:6` | `listServices()` `web/lib/server/catalog.ts:45` | ไม่มี (หน้า `/services` `/` เรียก `listServices` ตรง) |
| 7 | GET | `/api/therapists` | `web/app/api/therapists/route.ts:7` | `listTherapists()` `catalog.ts:76` | ไม่มี (หน้า `/therapists` เรียก lib ตรง) |
| 8 | GET | `/api/hotels` | `web/app/api/hotels/route.ts:6` | `listHotels()` `catalog.ts:99` | ไม่มี (หน้า `/transport` เรียก lib ตรง) |
| 9 | GET | `/api/slots` | `web/app/api/slots/route.ts:9` | `availableSlots()` `web/lib/server/booking.ts:308` | `web/components/BookingWizard.tsx:144` (template literal) |
| 10 | POST | `/api/price` | `web/app/api/price/route.ts:10` | `parseBookingInput()` `booking.ts:46` → `buildQuote()` `:105` → `quoteJson()` `:233` | `BookingWizard.tsx:177` |
| 11 | POST | `/api/bookings` | `web/app/api/bookings/route.ts:8` | `createBooking()` `booking.ts:342` | `BookingWizard.tsx:215` · แชทเรียก `createBooking` ตรง `web/lib/bot/chat.ts:238` |
| 12 | POST | `/api/bookings/:id/cancel` | `web/app/api/bookings/[id]/cancel/route.ts:8` | `cancelBooking()` `booking.ts:458` | `web/components/MyBookings.tsx:32` (template literal) |
| 13 | GET | `/api/me` | `web/app/api/me/route.ts:10` | `accountSummary()` `web/lib/server/customer.ts:62` | ไม่มี (หน้า `/account` เรียก lib ตรง) |
| 14 | GET | `/api/me/bookings` | `web/app/api/me/bookings/route.ts:10` | `myBookings()` `customer.ts:82` | ไม่มี (หน้า `/account` เรียก lib ตรง) |
| 15 | GET | `/api/wallet` | `web/app/api/wallet/route.ts:10` | `wallet()` `customer.ts:122` | ไม่มี (หน้า `/wallet` เรียก lib ตรง) |
| 16 | POST | `/api/courses` | `web/app/api/courses/route.ts:8` | `buyCourse()` `web/lib/server/store.ts:76` | `web/components/BuyCourseButton.tsx:22` |
| 17 | GET | `/api/photos/:id` | `web/app/api/photos/[id]/route.ts:12` | `photoForViewer()` `store.ts:105` | `<img src>` `web/app/wallet/page.tsx:92` (url สร้างที่ `customer.ts:151`) |
| 18 | POST | `/api/giftcards` | `web/app/api/giftcards/route.ts:8` | `buyGiftCard()` `store.ts:18` | `web/components/GiftCardShop.tsx:42` |
| 19 | GET | `/api/giftcards/:code` | `web/app/api/giftcards/[code]/route.ts:7` | `giftCardInfo()` `store.ts:54` | `GiftCardShop.tsx:55` |
| 20 | GET | `/api/transport` | `web/app/api/transport/route.ts:10` | `transportQuote()` `web/lib/rules/transport.ts:17` + `getHotel()` | `web/components/TransportCalc.tsx:22` |
| 21 | POST | `/api/chat` | `web/app/api/chat/route.ts:8` | `chat()` `web/lib/bot/chat.ts` | `web/components/ChatBox.tsx:32` |
| 22 | GET | `/api/mood` | `web/app/api/mood/route.ts:8` | `recommendForMood()` + `listServices()` | `web/components/MoodPicker.tsx:29` |
| 23 | GET | `/api/quiz` | `web/app/api/quiz/route.ts:8` | `QUIZ` `web/lib/bot/quiz.ts:12` | ไม่มี (หน้า `/quiz` import `lib/bot/quiz.ts` ตรง) |
| 24 | POST | `/api/quiz` | `web/app/api/quiz/route.ts:18` | `validateAnswers()` `web/lib/bot/quiz.ts:104` → `quizResult()` `quiz.ts:110` + `listServices()` | `web/components/Quiz.tsx:29` |
| 25 | GET | `/api/admin/bookings` | `web/app/api/admin/bookings/route.ts:10` | `queueForDate()` `web/lib/server/admin.ts:8` (owner เท่านั้น `:13-14`) | `web/components/AdminQueue.tsx:33` |
| 26 | POST | `/api/admin/bookings/:id/complete` | `web/app/api/admin/bookings/[id]/complete/route.ts:8` | `completeBooking()` `booking.ts:493` | `AdminQueue.tsx:42` |

สรุป: มีผู้เรียกจาก component 16 handler · `<img>` 1 · healthcheck 1 · **ไม่มีผู้เรียกในเว็บ 8 handler** (#3 #6 #7 #8 #13 #14 #15 #23) — ไม่ได้แปลว่าลบได้ (ดู SPEC-GAPS G10)

---

## 3. กฎร้าน (`web/lib/rules/*` 14 ไฟล์ + `index.ts`)

| BR | กฎ (ภาษาคน) | ค่าคงที่ | ฟังก์ชัน | ถูกเรียกจาก | ข้อความที่พูดกฎเดียวกันซ้ำ |
|---|---|---|---|---|---|
| BR-01 | เปิด 10:00–22:00 รอบเริ่มทุก 30 นาที บริการต้องจบ ≤ 22:00 | `OPEN_MIN` `CLOSE_MIN` `SLOT_STEP_MIN` `slots.ts:4-6` | `buildSlots()` `slots.ts:13` · `isValidStartTime()` `:21` · `endTimeOf()` `:25` | `booking.ts:113` (buildQuote) · `booking.ts:323` (availableSlots) | `web/lib/i18n.ts:37` footer.hours · `i18n.ts:53` home.subtitle · `web/lib/bot/chat.ts:64-66` |
| BR-02 | นักบำบัด 1 คน 1 คิวต่อช่วง `[start,end)` ต่อกันพอดีได้ · "ใครก็ได้" = คนว่าง id น้อยสุด | — | `overlaps()` `overlap.ts:3` · `freeTherapists()` `overlap.ts:14` | `booking.ts:326` · `booking.ts:360-371` | DB `booking_slot_no_overlap` |
| BR-03 | จองได้พรุ่งนี้ (+1) ถึง +30 วัน | `MIN_DAYS_AHEAD` `MAX_DAYS_AHEAD` `dates.ts:4-5` | `isBookableDate()` `dates.ts:7` · `bookableRange()` `:12` | `booking.ts:112` `:316` · `chat.ts:212` · `web/app/book/page.tsx:51` | `i18n.ts:296` err.DATE_OUT_OF_RANGE |
| BR-04 | คู่ = 2 คนพอดี · Couple Suite 1 คู่ต่อช่วง | `COUPLE_SIZE` `party.ts:8` | `checkParty()` `party.ts:12` · `roomBusy()` `booking.ts:287` | `booking.ts:109` `:313` `:373-377` · `BookingWizard.tsx:125` (ฝั่งเบราว์เซอร์) | `i18n.ts:299` · DB `booking_check2` `booking_room_no_overlap` |
| BR-05 | กลุ่ม 3–6 คน · 7+ โทรร้าน · นักบำบัดต้องว่างพอ | `GROUP_MIN` `GROUP_MAX` `party.ts:6-7` | `checkParty()` `party.ts:20-24` | `booking.ts:109` `:313` `:369` · `BookingWizard.tsx:125` | `i18n.ts:83` `:289` `:300` · `PackageCalc.tsx:17` (1–6) · `transport/route.ts:15` (`> 6`) · DB `booking_check3` `booking_party_size_check` |
| BR-06 | กลุ่ม ≥ 4 คน ลด 10% (ไม่ใช้กับแพ็กเกจ/คอร์ส) | `GROUP_DISCOUNT_MIN_PEOPLE` `GROUP_PCT` `pricing.ts:9-10` | `bestPercent()` `pricing.ts:47-57` | `calcPrice()` `pricing.ts:65` | — |
| BR-07 | ยกเลิกเองได้เมื่อเหลือ ≥ 24 ชม. (24 ชม. พอดียกเลิกได้) | `CANCEL_MIN_MS` `cancel.ts:3` | `canCancel()` `cancel.ts:5` | `booking.ts:467` · `customer.ts:98` (ปุ่มในหน้าบัญชี) | `i18n.ts:179` `:305` |
| BR-08 | คะแนนเฉลี่ยทศนิยม 1 ปัดครึ่งขึ้น · ตัวกรอง ≥ 4.5 ใช้ค่าที่ปัดแล้ว | `FILTER_MIN_TENTHS` `rating.ts:3` | `ratingTenths()` `rating.ts:7` · `roundAverage()` `:12` · `formatRating()` `:16` · `passesRatingFilter()` `:20` | `catalog.ts:84` `:92` · `therapists/route.ts:12` (รับเฉพาะ `min=4.5` ตรงตัว) | — |
| BR-09 | แต้ม = floor(ฐาน ÷ ฿100) · ฐาน = ยอดหลังส่วนลดและแต้ม ไม่รวมค่ารถ − ส่วนที่จ่ายด้วย Gift Card · ให้ตอนร้านกดเสร็จ | — | `pointsFor()` `points.ts:6` · `earnBase()` `points.ts:29` | `booking.ts:504-521` (completeBooking) · `pricing.ts:90` (pointsToEarn ในใบสรุป) | — |
| BR-10 | 100 แต้ม = ลด ฿50 เป็นก้อน · ไม่ทำยอดติดลบ · ไม่ใช้ก้อนเกินจำเป็น | `POINT_BLOCK` `BLOCK_VALUE` `points.ts:3-4` | `maxRedeemBlocks()` `points.ts:10` · `redeemPoints()` `:15` | `pricing.ts:69` · `booking.ts:153-156` `:204` | `i18n.ts:103` `:106` · DB `booking_points_redeemed_check` |
| BR-11 | Silver < ฿10,000 ≤ Gold < ฿30,000 ≤ Platinum · ส่วนลด 0/5/10% | `GOLD_MIN` `PLATINUM_MIN` `TIER_PCT` `tier.ts:5-8` | `tierOf()` `tier.ts:10` | `booking.ts:141` · `customer.ts:49` | — |
| BR-12 | ข้อความ "อีก ฿X ถึงระดับถัดไป" / "อยู่ระดับสูงสุดแล้ว" | — | `nextTier()` `tier.ts:16` · `tierInfo()` `customer.ts:48-60` | `accountSummary()` `customer.ts:78` | `i18n.ts:168-169` |
| BR-13 | เดือนเกิด 20% · 1 ครั้งต่อเดือนเกิด · นับตามวันนัด · เฉพาะเดี่ยว/คู่/กลุ่ม | `BIRTHDAY_PCT` `birthday.ts:4` | `isBirthdayMonth()` `birthday.ts:6` · `birthdayEligible()` `:10` | `booking.ts:142-150` `:433-434` · คืนสิทธิ์ `booking.ts:486-487` · `customer.ts:65` | `i18n.ts:107` `:172` · DB PK `birthday_use_pkey (customer_id, year_month)` |
| BR-14 | คอร์ส ฿15,000 = 10+1 = 11 ครั้ง ใช้ได้ 180 วัน (วันหมดอายุยังใช้ได้ ตรวจจากวันนัด) · กันครั้งตอนจอง ตัดจริงตอนเสร็จ | `COURSE_PRICE` `COURSE_SESSIONS` `COURSE_DAYS` `course.ts:4-6` | `courseExpiry()` `:8` · `courseRemaining()` `:12` · `canUseCourse()` `:16` · `isCourseExpired()` `:20` · `courseDaysLeft()` `:24` | `booking.ts:118-139` `:436-438` `:523-527` · `store.ts:76-90` · `customer.ts:125-139` | `i18n.ts:71` `:194` · `chat.ts:144` · DB `course_purchase_check` `course_purchase_check1` |
| BR-15 | Gift Card ฿500–฿10,000 จำนวนเต็ม | `GC_MIN` `GC_MAX` `giftcard.ts:4-5` | `isValidFaceValue()` `giftcard.ts:10` | `store.ts:20` | `i18n.ts:206` `:294` · DB `gift_card_face_value_check` |
| BR-16 | Gift Card ใช้ได้ 365 วัน (วันที่ 365 ยังใช้ได้ ตรวจจากวันจ่าย) ใช้หลายครั้งจนหมด | `GC_DAYS` `giftcard.ts:6` | `giftCardExpiry()` `:14` · `giftCardStatus()` `:21` · `applyGiftCard()` `:27` | `store.ts:29` `:60` · `booking.ts:172` · `pricing.ts:88` | DB `gift_card_check1` (`expires_on = purchased_on + 365`) |
| BR-17 | ≤ 5 กม. ฟรี · > 5 ถึง ≤ 15 กม. ฿300/คัน · > 15 กม. ไม่รับ (ปัดระยะเป็นทศนิยม 1 ก่อนเทียบ) | `FREE_KM_TENTHS` `MAX_KM_TENTHS` `FEE_PER_VEHICLE` `transport.ts:3-5` | `transportQuote()` `transport.ts:17-24` | `pricing.ts:79` · `transport/route.ts:23` | `i18n.ts:146` `:229` · DB `booking_distance_km_check` (≤ 15.0) |
| BR-18 | รถคันละไม่เกิน 4 คน | `SEATS_PER_VEHICLE` `transport.ts:6` | `vehiclesFor()` `transport.ts:8` | `transportQuote()` `transport.ts:21` | `i18n.ts:229` |
| BR-19 | แพ็กเกจ Bangkok Relax ฿2,900 × คน รถรวมแล้ว · ไม่มีส่วนลด % | ราคาอยู่ใน DB `service` P01 `db/init/02-seed.sql:26` | `calcPrice()` `pricing.ts:64` · `transportQuote(…, true)` `pricing.ts:79` · `bestPercent()` `pricing.ts:48` | `booking.ts:178-188` | `web/components/PackageCalc.tsx:24` (คิดราคาซ้ำในเบราว์เซอร์) · `i18n.ts:146` · `chat.ts:141` |
| BR-20 | ลำดับราคา ① เต็ม → ② % สูงสุด 1 อัน → ③ แต้ม → ④ ค่ารถ → ⑤ Gift Card/อื่น · ยอดสรุป = ยอดเก็บจริง | — | `calcPrice()` `pricing.ts:63-111` | `buildQuote()` `booking.ts:178` · ตรวจ `quotedTotal` `booking.ts:352-355` (409 PRICE_CHANGED) | คอมเมนต์ `pricing.ts:2` |

ครบ BR-01–BR-20 (20 แถว) · `index.ts` re-export 14 ไฟล์ [source `web/lib/rules/index.ts:2-15`] · `time.ts` เป็นตัวช่วยวันที่/เวลา +7 ไม่มีกฎร้าน [source `web/lib/rules/time.ts:1-58`]

---

## 4. ฐานข้อมูล

คำสั่งที่รัน (PowerShell): `docker exec sabai06-db psql -U sabai -d sabai -c "\dt"` · `-c "\d booking"` · `-c "\d booking_slot"` + นับ constraint จาก `pg_constraint` (ผลเก็บไว้นอก repo)

[DB] **19 ตาราง** · constraint ทั้งหมด: **CHECK 51 · FK 25 · PK 19 · UNIQUE 10 · EXCLUDE 2** (นับจาก `pg_constraint` ของ schema `public`) · schema มาจาก `db/init/01-schema.sql` (224 บรรทัด) · หัวไฟล์เขียน "ERD 17 ตาราง + hotel + therapist_service" [source `db/init/01-schema.sql:1`]

| ตาราง | กฎที่ DB บังคับ (CHECK / EXCLUDE / UNIQUE / PK) | กฎเดียวกันในโค้ดอยู่ไหน |
|---|---|---|
| `booking` | CHECK 23 ตัว: `booking_booking_type_check` (5 แบบ) · `booking_party_size_check` (1–6) · `booking_check2` (couple → 2 คน + room_id) · `booking_check3` (group 3–6) · `booking_check4` (single 1) · `booking_check5` (course 1 คน + course_purchase_id) · `booking_check6` (giftcard_paid + other_paid = total_amount) · `booking_check` (end > start) · `booking_check1` (สมาชิกหรือชื่อแขก) · `booking_distance_km_check` (0–15.0) · `booking_points_redeemed_check` (หาร 100 ลงตัว) · `booking_status_check` · `booking_discount_kind_check` · เงิน ≥ 0 อีก 9 ตัว · **EXCLUDE `booking_room_no_overlap`** (room_id, period &&) WHERE room_id ไม่ว่าง และไม่ cancelled · UNIQUE `booking_code_key` · FK 4 | `party.ts:12-25` · `transport.ts:20` · `points.ts:15-19` · `pricing.ts:87-89` · `booking.ts:372-377` (room) |
| `booking_slot` | **EXCLUDE `booking_slot_no_overlap`** (therapist_id =, period &&) WHERE (active) · UNIQUE `booking_slot_booking_id_therapist_id_key` · FK `booking_slot_booking_id_fkey` ON DELETE CASCADE · FK therapist | `overlap.ts:3-18` · `booking.ts:357-371` · ยกเลิก = `active = FALSE` `booking.ts:470` · `http.ts:42` (23P01 → 409) |
| `customer` | `customer_points_balance_check` (≥ 0) · `customer_lifetime_spend_check` · `customer_role_check` · `customer_lang_check` · UNIQUE `customer_email_key` | `points.ts:10-19` · `tier.ts:10` · `session.ts:37` |
| `course_purchase` | `course_purchase_check` (used + reserved ≤ total) · `course_purchase_check1` (expires ≥ purchased) · sessions/price ≥ 0 · UNIQUE code | `course.ts:12-18` · `booking.ts:472` (`reserved_sessions > 0`) `:525` (`GREATEST`) |
| `gift_card` | `gift_card_face_value_check` (500–10000 จำนวนเต็ม) · `gift_card_check1` (expires = purchased + 365) · `gift_card_check` (balance ≤ face) · `gift_card_balance_check` · design/channel CHECK · UNIQUE code | `giftcard.ts:4-29` · `store.ts:18-30` |
| `gift_card_txn` | `gift_card_txn_amount_check` (≠ 0) · FK gift_card, booking | `booking.ts:429-432` `:474-481` |
| `point_txn` | `point_txn_points_check` (≠ 0) · `point_txn_reason_check` (earn/redeem/refund/opening) | `booking.ts:427` `:484` `:520` |
| `birthday_use` | **PK `birthday_use_pkey` (customer_id, year_month)** · `birthday_use_year_month_check` · FK `birthday_use_customer_id_fkey` `birthday_use_booking_id_fkey` | `birthday.ts:10-13` · `customer.ts:42-45` |
| `service` | `service_kind_check` (single/package/course) · duration > 0 · price ≥ 0 · UNIQUE code | `booking.ts:82-86` (kindMatches) · `catalog.ts:31` |
| `room` | `room_capacity_check` (> 0) · seed มี 1 ห้อง `(1, 'Couple Suite', 2)` | **`room_id = 1` ตายตัว** `booking.ts:290` `:376` |
| `hotel` | `hotel_distance_km_check` (≥ 0) · UNIQUE code | `catalog.ts:99-107` |
| `review` | `review_stars_check` (1–5) · FK 3 | `rating.ts:7` · `catalog.ts:76-95` |
| `waist_measurement` | `waist_measurement_waist_cm_check` (> 0) · UNIQUE `waist_measurement_booking_id_key` | `complete/route.ts:17` (0–300) · `booking.ts:528-535` |
| `body_photo` | `body_photo_phase_check` (before/after) | `store.ts:105-115` · `customer.ts:148-151` |
| `therapist` | UNIQUE code | `catalog.ts:76` · `booking.ts:297-305` (`t.active`) |
| `therapist_service` | PK (therapist_id, service_id) | `booking.ts:297-305` (capableTherapists) |
| `service_herb` | PK (service_id, herb_id) | `catalog.ts:36-43` |
| `herb` | UNIQUE `herb_name_th_key` | `catalog.ts:36` |
| `app_setting` | PK key · seed `test_today = 2026-10-10T10:00:00+07:00` `db/init/02-seed.sql:217` | `clock.ts:20` · `testmode.ts:47` |

กฎที่ **DB ไม่บังคับ** (อยู่ในโค้ดอย่างเดียว): เวลาเปิด–ปิด BR-01 · ช่วงวันจอง BR-03 · ยกเลิก 24 ชม. BR-07 · ส่วนลด/ลำดับราคา BR-06/11/20 · ค่ารถ ≤ 5 กม. ฟรี BR-17 · ช่างทำบริการได้ (therapist_service) ตอน insert slot

---

## 5. Test hooks และ "วันนี้" ของระบบ

| เรื่อง | ทำอะไร | อ้าง |
|---|---|---|
| นาฬิกา | `now()`: ถ้า `ALLOW_TEST_RESET=1` อ่าน `app_setting.test_today` → ไม่มี/ผิดรูป → env `TODAY` → เวลาจริง · `clock()` คืน `{now, today}` (today = วันที่ไทย) | `web/lib/clock.ts:17-37` · `web/lib/rules/time.ts:30-32` |
| ค่า "ตอนนี้" หลัง reset | `DEFAULT_TEST_NOW = "2026-10-10T10:00:00+07:00"` | `web/lib/server/testmode.ts:9` |
| `POST /api/test/reset {now?}` | ใน transaction เดียว: `LOCK TABLE booking` → `TRUNCATE <TABLES 19 ตาราง> RESTART IDENTITY CASCADE` → รัน seed SQL ทั้งไฟล์ → `UPDATE app_setting test_today` | `testmode.ts:37-50` · `TABLES` `testmode.ts:11-15` |
| seed มาจากไหน | `SEED_SQL_PATH` (`/app/sql/02-seed.sql` ใน image ซึ่ง COPY จาก `db/init/02-seed.sql` ตอน build) → `cwd/sql/02-seed.sql` → `../db/init/02-seed.sql` · cache ในหน่วยความจำ | `testmode.ts:19-30` · `web/Dockerfile:25` `:31` · `db/init/02-seed.sql:2` |
| `GET /api/test/today` | คืน `{now, today}` | `web/app/api/test/today/route.ts:9-13` |
| ปิด hook | `ALLOW_TEST_RESET≠1` → `/api/test/*` ตอบ 404 · ไม่แสดงบัญชีทดสอบ · ไม่มีปุ่มรีเซ็ต | `reset/route.ts:9` · `today/route.ts:10` · `web/app/login/page.tsx:32` · `web/app/admin/page.tsx:36` |
| ตรวจ runtime (รอบนี้) | `GET http://localhost:4100/api/test/today` → `{"now":"2026-10-10T10:00:00+07:00","today":"2026-10-10"}` · `/api/health` → `{"ok":true,"db":true}` | (รอบรันนี้ตั้ง `WEB_PORT=4100` · ค่าเริ่มต้นของผู้เรียก = 4000) |

---

## 6. กับดักถ้าจะแก้

| # | กับดัก | ทำไมอันตราย | อ้าง |
|---|---|---|---|
| T1 | **`room_id = 1` เขียนตายตัว 2 ที่** | ห้องคู่มีห้องเดียวในโค้ด · เพิ่มห้องใน DB แล้วระบบไม่ใช้ | `web/lib/server/booking.ts:290` · `booking.ts:376` · seed `db/init/02-seed.sql:95` |
| T2 | **`TABLES` ใน `lib/server/testmode.ts`** ระบุตารางที่ reset ล้าง | เพิ่มตารางใหม่ (migration) แล้วไม่เติมรายการ → reset ไม่ล้างตารางนั้น / seed ชน | `web/lib/server/testmode.ts:11-15` `:45` |
| T3 | **`db/init` รันเฉพาะตอน volume `sabai06-pgdata` ว่าง** | แก้ `01-schema.sql` ไม่มีผลกับฐานที่มีข้อมูลแล้ว → ต้องทำ migration แยก | `db/compose.yaml:17-18` |
| T4 | seed ถูก COPY เข้า image ตอน build | แก้ `02-seed.sql` แล้วไม่ build เว็บใหม่ → reset ยังใช้ seed เก่า (และ cache ในหน่วยความจำ) | `web/Dockerfile:31` · `testmode.ts:17-30` |
| T5 | **ราคาแพ็กเกจคิดซ้ำในเบราว์เซอร์** | `PackageCalc` คูณ `unitSatang × people` เอง ไม่ผ่าน `calcPrice` · เปลี่ยนกฎแพ็กเกจต้องแก้ 2 ที่ | `web/components/PackageCalc.tsx:24` vs `web/lib/rules/pricing.ts:64` |
| T6 | กฎจำนวนคนคิดทั้งเซิร์ฟเวอร์และเบราว์เซอร์ / ค่าซ้ำ | `checkParty` ถูก import ไปใช้ใน client · ตัวเลข 6 อยู่ใน select ของ PackageCalc และ route transport · input คนจองรับ max 20 | `BookingWizard.tsx:6` `:125` `:331` · `PackageCalc.tsx:17` · `web/app/api/transport/route.ts:15` |
| T7 | **ข้อความกฎซ้ำใน i18n/แชท** (ไม่ได้อ่านจากค่าคงที่) | เปลี่ยนเวลาเปิด/ค่ารถ/24 ชม. ในโค้ดแล้วข้อความยังบอกค่าเก่า | เวลาเปิด `i18n.ts:37` `:53` `chat.ts:64-66` · 24 ชม. `i18n.ts:179` `:305` · 30 วัน `i18n.ts:296` · 3–6 คน `i18n.ts:83` `:300` · 15 กม. `i18n.ts:146` `:229` · 180 วัน `i18n.ts:71` `chat.ts:144` |
| T8 | ค่ากฎซ้ำใน DB CHECK | เปลี่ยนกฎ (เช่น ระยะรถ, ขนาดกลุ่ม, มูลค่าบัตร, 365 วัน) ต้องแก้ทั้งโค้ดและ constraint (migration) | `booking_distance_km_check` · `booking_check3` · `gift_card_face_value_check` · `gift_card_check1` |
| T9 | **นาฬิกาถูกล็อกเมื่อ `ALLOW_TEST_RESET=1`** (ค่าเริ่มต้นใน compose และโค้ด) และ seed มีแถว `test_today` | ถ้าส่งขึ้นจริงด้วยค่าเริ่มต้น "วันนี้" จะค้างที่ 10 ต.ค. 2026 · โค้ดใหม่ต้องใช้ `clock()` ห้าม `new Date()` ตรง | `web/compose.yaml:19` · `web/lib/config.ts:5` · `clock.ts:18-22` · `02-seed.sql:217` |
| T10 | หน้า server component ไม่เรียก API | แก้ route API อย่างเดียว หน้าเว็บไม่เปลี่ยน (ต้องแก้ lib) · และกลับกัน | `web/app/account/page.tsx:29` `:31` · `web/app/wallet/page.tsx:29` · `web/app/services/page.tsx:14` · `web/app/therapists/page.tsx:14` · `web/app/transport/page.tsx:17` · `web/app/quiz/page.tsx:17` (route คู่กัน = §2 #6–8 #13–15 #23) |
| T11 | error `23P01` ทุกตัว → `SLOT_TAKEN` | ถ้าเพิ่ม EXCLUDE ใหม่ ข้อความจะเป็น "เวลานี้ถูกจองแล้ว" เสมอ | `web/lib/server/http.ts:42` |
| T12 | network `sabai06-net` เป็น external | `docker compose up` ล้มถ้ายังไม่สร้าง network | `web/compose.yaml:31-33` · `db/compose.yaml:31-33` |
| T13 | URL ที่ต่อ string ใน component | REA/เครื่องมือ static หา endpoint ไม่เจอ (`/api/slots?${q}`, `/api/bookings/${id}/cancel`) · ค้นด้วย grep `"/api/` ไม่พอ ต้อง grep `` `/api/ `` ด้วย | `BookingWizard.tsx:144` · `MyBookings.tsx:32` · `AdminQueue.tsx:33` `:42` |

---

## 7. Triangulation (REA × source × DB × SPEC)

| endpoint / กฎ | REA เห็น | source บอก | DB บอก | SPEC บอก | ตรงไหม | ถ้า REA ไม่เห็น เพราะอะไร |
|---|---|---|---|---|---|---|
| `POST /api/price` | [E ev_11d475e1] fetch @ book · [E ev_6fbeaec6] 200 ×2 | [source `price/route.ts:10-18` → `booking.ts:105`] ไม่บันทึกอะไร | [DB —] อ่านอย่างเดียว | [SPEC §6] ใบสรุป ไม่บันทึก | ✅ | — |
| `POST /api/bookings` | [E ev_6fbeaec6] 201 ได้ B14 | [source `booking.ts:342-455`] transaction + ตรวจ `quotedTotal` `:352-355` | [DB `booking_slot_no_overlap` `booking_room_no_overlap` `booking_check6`] | [SPEC §6] 201/409/422 | ✅ | — |
| `GET /api/slots` | [E ev_6fbeaec6] [E ev_8dc23d9f] runtime เท่านั้น | [source `BookingWizard.tsx:144` template literal · `booking.ts:308-339`] | [DB `booking_slot` WHERE active] | [SPEC §6] | ✅ | static ไม่เห็นเพราะ URL ต่อ string (`/api/slots?${q}`) — ยืนยัน inference ใน REA-INVENTORY §4 |
| `POST /api/bookings/:id/cancel` | [E ev_6fbeaec6] 200 B05 | [source `MyBookings.tsx:32` template literal · `booking.ts:458-490`] | [DB `booking_status_check` · slot `active=false`] | [SPEC §6, BR-07] | ✅ | static ไม่เห็นเพราะ template literal |
| `GET /api/admin/bookings` | [E ev_6fbeaec6] 200 ×2 | [source `AdminQueue.tsx:33` · owner check `admin/bookings/route.ts:13-14`] | [DB —] | [SPEC §6] 401/403 | ✅ | static ไม่เห็นเพราะ template literal |
| `POST /api/admin/bookings/:id/complete` | [E ev_11d475e1] ชื่อไฟล์เท่านั้น | [source `AdminQueue.tsx:42` · `booking.ts:493-540`] | [DB `booking_status_check`] | [SPEC §6] | ✅ | template literal + HAR ไม่ได้กดปุ่มเสร็จ |
| `/api/me` `/api/me/bookings` `/api/services` `/api/wallet` `/api/therapists` `/api/hotels` `GET /api/quiz` | [E ev_11d475e1] ชื่อไฟล์เท่านั้น | [source ไม่มี component เรียก · หน้าเรียก lib ตรง เช่น `app/account/page.tsx` → `customer.ts`] | [DB —] | [SPEC §6] เขียนเป็น API ปกติ | ⚠️ มี route แต่ UI ไม่ใช้ | หน้า render ฝั่งเซิร์ฟเวอร์ → ไม่มีคำขอในเบราว์เซอร์ (ยืนยัน inference REA §4) · ส่งต่อ SPEC-GAPS G10 |
| `POST /api/test/reset` | [E ev_11d475e1] fetch @ admin | [source `reset/route.ts:9` ปิดเมื่อ `ALLOW_TEST_RESET≠1` · ค่าเริ่มต้น 1 `web/compose.yaml:19`] | [DB TRUNCATE 19 ตาราง `testmode.ts:11-15`] | [SPEC §2] ค่าเริ่มต้น `1` | ⚠️ ระบบที่ส่งมอบเปิด hook ไว้ | — · ส่งต่อ SPEC-GAPS G7 |
| `GET /api/test/today` | [E ev_11d475e1] ชื่อไฟล์ | [source `today/route.ts:9-13` · ไม่มีผู้เรียกในเว็บ] | [DB `app_setting`] | [SPEC §6] | ✅ | ไม่มีผู้เรียกจริง |
| `GET /api/photos/:id` | [E ev_11d475e1] ชื่อไฟล์ | [source `wallet/page.tsx:92` `<img src>` · เจ้าของเท่านั้น `store.ts:105-115`] | [DB `body_photo` → `course_purchase.customer_id`] | [SPEC §6] 401/403 | ✅ | เรียกผ่าน `<img>` ไม่ใช่ fetch · HAR ไม่ได้เปิด /wallet |
| logout / session | [E ev_6fbeaec6] cookie `sabai_session` 7 วัน | [source `session.ts:6` 7 วัน · logout แค่ลบ cookie `logout/route.ts:7-8` · token stateless `session.ts:26-41`] | [DB ไม่มีตาราง session] | [SPEC §6] logout `{ok:true}` | ⚠️ token เดิมยังใช้ได้จนหมดอายุ | ตอบคำถาม REA §5 ข้อ 8 · ส่งต่อ SPEC-GAPS G8 |
| ราคา S01 เดี่ยว ฿1,000 (BR-20) | [E ev_8dc23d9f] ยอดสุทธิ ฿1,000 · [E ev_6fbeaec6] ฿1,000 | [source `pricing.ts:63-90` แขกไม่ล็อกอิน tier 0] | [DB `service` S01 price] | [SPEC BR-20] | ✅ | — |
| BR-03 ช่วงวัน | [E ev_6fbeaec6] slots มีคีย์ `min` `max` | [source `dates.ts:4-14` · `booking.ts:338`] | [DB ไม่บังคับ] | [SPEC BR-03] +1..+30 | ✅ | — |
| BR-07 ยกเลิก 24 ชม. | [E ev_6fbeaec6] B05 ยกเลิกได้ · ปุ่ม B06 ปิด (REA §5 ข้อ 5) | [source `cancel.ts:5-7` (≥) · ตรวจซ้ำฝั่งเซิร์ฟเวอร์ `booking.ts:467` · ปุ่มใช้ค่าเดียวกัน `customer.ts:98`] | [DB ไม่บังคับ] | [SPEC BR-07, §7 U01] | ✅ | — |
| BR-02 ช่างชน | REA ไม่เห็น | [source `overlap.ts:3-18` · `booking.ts:357-371`] | [DB `booking_slot_no_overlap`] | [SPEC BR-02] | ✅ | กฎฝั่งเซิร์ฟเวอร์ (REA static ดูเฉพาะ bundle เบราว์เซอร์) |
| BR-04 ห้องคู่ | REA ไม่เห็น | [source `party.ts:18-19` · `booking.ts:287-295` `:373-377` room_id = 1] | [DB `booking_check2` `booking_room_no_overlap`] | [SPEC BR-04] | ✅ (มีกับดัก T1) | ฝั่งเซิร์ฟเวอร์ + HAR ไม่ได้จองคู่ |
| BR-05 กลุ่ม 3–6 | REA ไม่เห็น | [source `party.ts:20-22` + client `BookingWizard.tsx:125`] | [DB `booking_check3` `booking_party_size_check`] | [SPEC BR-05] | ✅ | ไม่ได้อยู่ในเส้นทางที่ HAR เดิน |
| BR-17 ค่ารถ > 15 กม. ไม่รับ | REA ไม่เห็น | [source `transport.ts:19-22` ปัดเป็นทศนิยม 1 ก่อนเทียบ · runtime: `distance=15.04` → ฿300 รับ · `15.05` → OUT_OF_AREA · `5.04` → ฟรี] | [DB `booking_distance_km_check` ≤ 15.0] | [SPEC BR-17] "> 15 ไม่รับ" | ⚠️ | ไม่มีใน HAR · ส่งต่อ SPEC-GAPS G4 |
| BR-09 ฐานแต้ม | REA ไม่เห็น | [source `points.ts:29-31` ลบ `giftcardPaid` ทั้งก้อน (รวมส่วนที่จ่ายค่ารถ) · runtime: S01 + H04 + GC ฿500 → pointsToEarn 4] | [DB `booking_points_earned_check` ≥ 0] | [SPEC BR-09] "หลังส่วนลด ไม่รวมรถ − Gift Card" | ⚠️ | ฝั่งเซิร์ฟเวอร์ · ส่งต่อ SPEC-GAPS G5 |
| BR-06/11 ส่วนลดกับแพ็กเกจ | REA ไม่เห็น | [source `pricing.ts:48` แพ็กเกจ/คอร์สไม่มีส่วนลด % ทุกชนิด (รวมระดับสมาชิก)] | [DB `booking_discount_kind_check`] | [SPEC BR-06] บอกแค่ "กลุ่ม…ไม่ใช้กับแพ็กเกจ" · BR-11 ไม่พูดถึง | ⚠️ | ฝั่งเซิร์ฟเวอร์ · ส่งต่อ SPEC-GAPS G6 |
| BR-13 เดือนเกิด 1 ครั้ง | REA ไม่เห็น | [source `birthday.ts:10-13` · `booking.ts:433-434`] | [DB PK `birthday_use_pkey`] | [SPEC BR-13] | ✅ | ฝั่งเซิร์ฟเวอร์ |
| BR-15/16 Gift Card | REA ไม่เห็น (ชื่อไฟล์ `giftcards` เท่านั้น) | [source `giftcard.ts:4-29`] | [DB `gift_card_face_value_check` `gift_card_check1`] | [SPEC BR-15, BR-16] | ✅ | HAR ไม่ได้เปิด /giftcard |
| BR-14 คอร์ส | REA ไม่เห็น | [source `course.ts:4-26` · `booking.ts:118-139`] | [DB `course_purchase_check`] | [SPEC BR-14] | ✅ | ฝั่งเซิร์ฟเวอร์ |

รวม 23 แถว: ✅ 17 · ⚠️ 6 · ❌ 0 · ทุกแถวที่ ⚠️ ส่งต่อเป็นคำถามใน `docs/SPEC-GAPS.md` (ไม่ได้ตัดสินเอง)

---

## 8. เอกสารเก่า

`web/SPEC.md` ไม่ตรงโค้ดหลายจุด (ชื่อ container/network/พอร์ตเก่า · อ้างไฟล์ที่ไม่มีใน repo · กฎบางข้อ) → รายละเอียดและคำถามถึงร้านอยู่ใน `docs/SPEC-GAPS.md`

---

## ยังไม่รู้

| # | เรื่อง | ทำไมยังไม่รู้ / ต้องถามใคร |
|---|---|---|
| U1 | เอกสาร `REQUIREMENTS.md` `DESIGN.md` `TEST-DATA.md` ที่ SPEC อ้าง (FR/BR/NFR, D1–D15, E01–E90) | ไม่มีใน repo · ต้องขอจากร้าน/ผู้รับเหมาเดิม |
| U2 | ระบบจริงของร้านตั้ง `ALLOW_TEST_RESET` เท่าไร และมีแถว `test_today` ในฐานจริงไหม | เห็นแค่ค่าเริ่มต้นใน compose/seed · ไม่มีข้อมูลเครื่องจริง |
| U3 | route ที่ UI ไม่ใช้ 8 ตัว มีระบบภายนอกเรียกอยู่ไหม (แอปมือถือ, LINE, สคริปต์ร้าน) | REA/HAR เห็นแค่เบราว์เซอร์ · ไม่มี log ฝั่งเซิร์ฟเวอร์ |
| U4 | ร้านมีห้องคู่กี่ห้องจริง | seed มี 1 ห้อง · โค้ดล็อก `room_id = 1` |
| U5 | ไฟล์ `web/scripts/check-rules.mjs` ผ่านกี่ข้อบนระบบนี้ | ยังไม่ได้รัน (งานนี้อ่านอย่างเดียว) (SPEC อ้าง 90/90 · สคริปต์มีรหัส E 90 ตัว) |
| U6 | ข้อมูลในฐานตอนนี้ไม่ใช่ seed ล้วน (การเก็บ HAR ใน LAB ก่อนจอง B14 และยกเลิก B05) | schema ไม่กระทบ · ถ้าต้องดูข้อมูล seed ให้ reset ก่อน |

---

ทำแผนที่เมื่อ 2026-10-12 · commit `3526f06` (`git rev-parse --short HEAD`) + ไฟล์ที่ยังไม่ commit จาก LAB ก่อน (`docs/REA-INVENTORY.md`, `HANDOVER-CHECK.md`)

---

## ตรวจทานโดยคน

สุ่ม 5 แถว (สุ่มด้วย `Math.random` : กฎร้านแถว 6 และ 10 · route #24 · ฐานข้อมูลแถว 8 · กับดัก T10) แล้วเปิดไฟล์/รัน psql ดูบรรทัดจริง · วันที่ 2026-10-12

| แถวที่สุ่ม | ที่อ้าง | บรรทัดจริง | ตรงไหม | แก้อะไร |
|---|---|---|---|---|
| กฎ BR-06 | `pricing.ts:9-10` · `bestPercent()` `:47-57` · เรียกจาก `:65` | `:9` `GROUP_DISCOUNT_MIN_PEOPLE = 4` · `:10` `GROUP_PCT = 10` · `:48` package/course → none · `:50` group && people ≥ 4 · `:65` `const best = bestPercent(input)` | ✅ | — |
| กฎ BR-10 | `points.ts:3-4` `:10` `:15` · `pricing.ts:69` · `booking.ts:153-156` `:204` · `i18n.ts:103` `:106` | `:3` `POINT_BLOCK = 100` · `:4` `BLOCK_VALUE = 50_00` · `:10` `maxRedeemBlocks` · `:15` `redeemPoints` · `pricing.ts:69` เรียก redeemPoints · `booking.ts:155` POINTS_NOT_ENOUGH · i18n "100 แต้ม = ลด ฿50" | ✅ | — |
| route #24 `POST /api/quiz` | `quiz/route.ts:18` · `quizResult()` · `Quiz.tsx:29` | `:18` `export async function POST` · `:22` `validateAnswers` · `:23` `quizResult` · `Quiz.tsx:29` `fetch("/api/quiz", { method: "POST" …` | ⚠️ ไม่ครบ | เดิมไม่มีไฟล์:บรรทัดของฟังก์ชัน → เติม `validateAnswers()` `quiz.ts:104` · `quizResult()` `quiz.ts:110` (และ #23 `QUIZ` `quiz.ts:12`) |
| DB `birthday_use` | PK `birthday_use_pkey` · `birthday_use_year_month_check` · โค้ด `birthday.ts:10-13` `customer.ts:42-45` | psql `\d birthday_use`: `"birthday_use_pkey" PRIMARY KEY, btree (customer_id, year_month)` · `CHECK (year_month >= 200001 AND year_month <= 299912)` · FK 2 ตัว · `customer.ts:43` `SELECT 1 FROM birthday_use WHERE customer_id = $1 AND year_month = $2` | ✅ (FK ขาด) | เติม FK `birthday_use_customer_id_fkey` `birthday_use_booking_id_fkey` |
| กับดัก T10 | "ตาราง §2 (#6–8, #13–15)" | `app/account/page.tsx:29` `accountSummary(getPool(), …)` · `:31` `myBookings(…)` · `app/wallet/page.tsx:29` `wallet(…)` · `app/services/page.tsx:14` `listServices` · `app/therapists/page.tsx:14` `listTherapists` · `app/transport/page.tsx:17` `listHotels` | ❌ อ้างไม่ครบ | เดิมอ้างแค่ตารางในไฟล์นี้ ไม่มีไฟล์:บรรทัด → เติมบรรทัดจริง 7 จุด + #23 (`app/quiz/page.tsx:17`) · แก้ข้อ §2 ให้อ้าง `account/page.tsx:8` `:29` `:31` ด้วย |

ผล: ตรง 3/5 · ไม่ครบ 2/5 (ไม่มีแถวที่อ้างผิดบรรทัด) · แก้แล้วทั้ง 2 แถว + แถว DB ที่ขาด FK
