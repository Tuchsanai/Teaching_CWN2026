# EXAM-KEY · เฉลยและแผนตรวจข้อสอบบท 06 (ชุด A + ชุด B)

> 🔒 **ผู้สอนเท่านั้น** · ไฟล์คู่กัน: `../EXAM.md` (ผู้เรียน · ชุด A) · `EXAM-B.md` (ใบโจทย์ชุด B แจกวันสอบ)
> ที่มา: `_design/EXAM-DRAFT.md` ภาค 3 · `EXAM-BLUEPRINT.md` (EB) · `CODEBASE-NOTES.md` (CN) · `CR-DESIGN.md` · `REVIEW-PLAN-V1.md` (M9 M10 M11 m9)
> เขียน 12 ต.ค. 2026 (งาน S6) · **เครื่องตรวจ (grader) สร้างและรันจริงแล้ว 12 ต.ค. 2026 ที่ `grader/` (งาน GRADER · วิธีใช้ `grader/README.md`)** · เฉลยอ้างอิง (reference) รันจริงแล้วโดยงาน EXREF 12 ต.ค. 2026 → diff ที่ `exam-ref/<ชุด>-<ข้อ>.diff` · mutant `exam-ref/mutants/M*.diff` · ฐาน "ใช้งานจริง" `exam-ref/prod-data-A.sql` `prod-data-B.sql` · สรุปผลและสิ่งที่แก้ใน key อยู่ที่ **§16**

**ข้อที่แก้ repo เดิม = 6/8 ข้อ (2, 4, 5, 6, 7, 8) = 84/100 คะแนน** · แก้โค้ด/schema ตรง 4 ข้อ (4–7 = 58 คะแนน) · เพิ่ม/แก้เทสต์ใน repo 2 ข้อ (2, 8 = 26 คะแนน) · ไม่แก้ repo 2 ข้อ (1, 3 = 16 คะแนน)

### ป้ายความน่าเชื่อถือของค่า

| ป้าย | ความหมาย |
|---|---|
| ✅ โค้ด | ตรวจกับโค้ด/seed ใน `web/` `db/` แล้ว (อ่าน 12 ต.ค. 2026 · ไม่ได้รัน) |
| 🧪 รันจริง | มาจากการรันจริงที่บันทึกไว้ (CN §7 · `LEGACY-SUITES-RESULT.md`) |
| **[คาด]** | คำนวณจากกฎ + seed · **ต้องยืนยันกับเฉลยอ้างอิงก่อนใช้สอบ** (รวมไว้ที่ §13) |
| **[รันจริง:EXREF 2026-10-12]** | ยืนยันกับเฉลยอ้างอิงที่รันจริง (image ของ `exam-ref/*.diff` บน postgres 16 · ใน network ของ docker ไม่ใช้พอร์ต host) · ค่าที่ไม่ตรงถูกแก้แล้วและบันทึกใน §16 |

---

## 1. VARIANT (`exam/VARIANT.json`)

`s` = ผลรวมเลขทุกหลักของรหัสนักศึกษา

| ชุด | สูตร | v | ค่า |
|---|---|---|---|
| A | `v = s % 2` | 0 | `{"set":"A","v":0,"freeKm":7,"feePerVehicle":350}` (ค่าเดียวกับที่ `EXAM.md` ให้ใช้ฝึกเองได้) |
| | | 1 | `{"set":"A","v":1,"freeKm":8,"feePerVehicle":400}` |
| B | `v = s % 3` | 0 | `{"set":"B","v":0,"pointValue":60,"leaveTherapist":"T03","leaveName":"พี่บุญมี","reviewBooking":"B13","reviewUser":"U01","reviewStars":5,"completeAfterMin":0}` |
| | | 1 | `{"set":"B","v":1,"pointValue":70,"leaveTherapist":"T02","leaveName":"พี่มาลี","reviewBooking":"B07","reviewUser":"U05","reviewStars":1,"completeAfterMin":30}` |
| | | 2 | `{"set":"B","v":2,"pointValue":75,"leaveTherapist":"T06","leaveName":"พี่ดวงใจ","reviewBooking":"B13","reviewUser":"U01","reviewStars":4,"completeAfterMin":60}` |

✅ โค้ด: ชื่อเล่น T02 = พี่มาลี · T06 = พี่ดวงใจ (seed `therapist`) · T02 T03 T06 ทำ S01 ได้ทุกคน · ไม่มีนัด seed วันที่ 15 ต.ค. · B13 = U01 · T03 · completed · B07 = U05 · T05 · completed

---

## 2. ข้อ 1 · อ่านและอธิบาย repo (8 · ข้อละ 0.8 · auto ตรวจ path + regex ของ answer/symbol)

### ชุด A ✅ โค้ด

| # | คำตอบที่ต้องมี | ไฟล์ · symbol |
|---|---|---|
| A1 | `completeBooking` INSERT `point_txn` reason `'earn'` + UPDATE แต้มลูกค้า | `web/lib/server/booking.ts` `completeBooking` |
| A2 | EXCLUDE gist `booking_slot_no_overlap` (therapist_id =, period &&) WHERE active | `db/init/01-schema.sql` |
| A3 | `calcPrice` (② ส่วนลด % → ③ แต้ม → รถ → บัตร) | `web/lib/rules/pricing.ts` |
| A4 | `roomBusy` (`WHERE room_id = 1`) **และ** `createBooking` (`roomId = 1`) | `web/lib/server/booking.ts` (ตอบแค่จุดเดียว = 0.4) |
| A5 | จองได้เฉพาะบริการเดี่ยว 1 คน (`type: "single"`, `people: 1`) | `web/lib/bot/chat.ts` |
| A6 | `app_setting` key `test_today` (อ่านเมื่อ `config.allowTestReset`) → ถัดไป env `TODAY` → เวลาจริง | `web/lib/clock.ts` `clock` |
| A7 | `PackageCalc` | `web/components/PackageCalc.tsx` |
| A8 | slot ปิด (inactive) · คอร์ส `reserved_sessions − 1` · บัตรของขวัญคืนยอด + `gift_card_txn` · แต้มที่แลกคืน (`point_txn` `'refund'`) · สิทธิ์เดือนเกิดคืน (ถ้า `yearMonth(today) <= เดือนของนัด`) | `web/lib/server/booking.ts` `cancelBooking` (ครบ ≥ 4 ใน 5 = เต็ม) |
| A9 | 409 `PRICE_CHANGED` พร้อมยอดใหม่และใบสรุปใหม่ | `createBooking` |
| A10 | **3 จุด**: `web/lib/i18n.ts` `footer.hours` · `home.subtitle` · `web/lib/bot/chat.ts` (คำตอบเวลาเปิด) | ไม่นับคอมเมนต์ใน `rules/slots.ts` และ `OPEN_MIN/CLOSE_MIN` |

### ชุด B ✅ โค้ด

| # | คำตอบที่ต้องมี | ไฟล์ · symbol |
|---|---|---|
| B1 | INSERT `point_txn` reason `'refund'` จำนวน = `points_redeemed` ของนัด | `web/lib/server/booking.ts` `cancelBooking` |
| B2 | `db/init/02-seed.sql` · compose `additional_contexts: dbinit: ../db/init` → Dockerfile `COPY --from=dbinit 02-seed.sql ./sql/` · env `SEED_SQL_PATH=/app/sql/02-seed.sql` · อ่านใน `testmode.ts` | `web/compose.yaml` `web/Dockerfile` `web/lib/server/testmode.ts` |
| B3 | กันไว้ = `createBooking` `reserved_sessions + 1` · ตัดจริง = `completeBooking` `used_sessions + 1` (และ reserved − 1) | `web/lib/server/booking.ts` |
| B4 | ลบ `birthday_use` ของนัด เมื่อ `yearMonth(today) <= เดือนของวันนัด` | `cancelBooking` |
| B5 | HMAC-SHA256 ด้วย `SESSION_SECRET` · อายุ 7 วัน (`MAX_AGE_S`) | `web/lib/session.ts` |
| B6 | เลือกจากนักบำบัดที่ทำบริการนั้นได้และว่างช่วงนั้น แล้วเอา id น้อยสุดตามจำนวนคน (`freeTherapists` เรียง id → `free.slice(0, people)`) | `web/lib/rules/overlap.ts` `freeTherapists` · `web/lib/server/booking.ts` `createBooking` |
| B7 | T01 พี่สมศรี · T05 พี่ทองใบ | `db/init/02-seed.sql` `therapist_service` |
| B8 | ปัดครึ่งขึ้นที่ทศนิยม 1 ตำแหน่ง `floor((20·sum + n) / (2n))` | `web/lib/rules/rating.ts` `ratingTenths` |
| B9 | `/api/test/reset` `/api/test/today` → 404 · นาฬิกาไม่อ่าน `app_setting` · บัญชีทดสอบหน้า login หาย · ปุ่มรีเซ็ตใน /admin หาย | `web/lib/config.ts` `allowTestReset` (ครบ ≥ 3 ใน 4 = เต็ม) |
| B10 | สตางค์ (integer) · `toSatang` / `fromSatang` | `web/lib/db.ts` |

ผู้สอนอ่านเฉพาะข้อที่ auto ได้ 0 แต่ path ถูก → ให้ครึ่ง (0.4)

**ผิดบ่อย:** ตอบจาก `web/SPEC.md` เก่าแทนโค้ด · A4 ตอบจุดเดียว · A10 ตอบ 9 (นับ 3 ภาษา) หรือ 4 (นับคอมเมนต์ใน slots.ts) · B6 ตอบแค่ 'คนที่ว่าง' ไม่บอกเรื่อง id น้อยสุด · B9 ตอบ `flags.ts` (ถอดแล้ว)

---

## 3. ข้อ 2 · ตาข่ายกันพลาด (14 = mutant 4 × 3 + README 2)

**บังคับ:** `tests/exam2/run.mjs` จาก commit `EX2:` รันกับ `sabai-exam-base` แล้ว exit 0 · ไม่ผ่าน = ข้อนี้ 0

### Mutant (diff 1 บรรทัดบน base · เก็บที่ `_solution/exam-ref/mutants/M*.diff` · สร้างและรันแล้วโดย EXREF)

golden อ้างอิง (`exam-ref/A-2.diff` 29 เคส `/api/price` · `exam-ref/B-2.diff` 47 เคส slots 8 บริการ × 5 วัน + คู่ · ยกเลิก B05 3 เวลา · บัตร 5 ใบ × 3 วัน) ผ่านบน base (exit 0) และ**จับ mutant ของชุดตัวเองได้ครบ 4/4 ทั้งสองชุด** (exit 1)

| id | ไฟล์ (✅ โค้ด) | เดิม → mutant | ชุด | เคสที่ฆ่าได้ [รันจริง:EXREF 2026-10-12] |
|---|---|---|---|---|
| M1 | `web/lib/rules/slots.ts:9` | `<= CLOSE_MIN` → `<= CLOSE_MIN - 1` | B | รอบสุดท้ายของ**ทุกบริการ**หาย (S01 รอบสุดท้าย 21:00 → 20:30) · golden B ต่าง 25/47 เคส |
| M2 | `web/lib/rules/pricing.ts:68` `calcPrice` | `percentOf(gross, …)` → `percentOf(gross - redeemPoints(…, gross).discount, best.pct)` (**1 บรรทัดได้จริง**) | A | U06 S05 แลก 1: ส่วนลด ฿80 → ฿75 · ยอด ฿670 → ฿675 · golden A ต่าง 4/29 |
| M3 | `web/lib/rules/points.ts:30` | `earnBase` ไม่หัก `discountAmount` | A | U01 S04 (Gold) `pointsToEarn` 19 → 20 · golden A ต่าง 13/29 |
| M4 | `web/lib/rules/transport.ts:22` | `tenths <= FREE_KM_TENTHS` → `<` | A | H02 5.0 กม. ฟรี → ฿300 · golden A ต่าง 1/29 (เคสขอบเดียว) |
| M5 (สำรอง) | `web/lib/rules/rating.ts:8` | ปัดลงแทนปัดครึ่งขึ้น | — | ไม่ใช้ (ไม่ได้สร้าง) |
| M6 | `web/lib/rules/giftcard.ts:22` | `today > expiresOn` → `>=` | B | GC03 `SABAI-GC-LAST` ที่ now seed: `status` ok → expired · (golden A ที่มีเคสบัตร GC03 ก็จับได้) |
| M7 | `web/lib/rules/pricing.ts:9` | `GROUP_DISCOUNT_MIN_PEOPLE = 4` → `3` | A | กลุ่ม 3 คน ฿3,000 → ฿2,700 · golden A ต่าง 1/29 |
| M8 | `web/lib/rules/cancel.ts:6` | `>= CANCEL_MIN_MS` → `>` | B | ยกเลิก B05 ตอน now 10 ต.ค. 10:00 (24 ชม. พอดี): 200 → 422 `CANCEL_TOO_LATE` · `canCancel` true → false |
| M9 | `web/lib/rules/dates.ts:5` | `MAX_DAYS_AHEAD = 30` → `31` | B | slots 2026-11-10: 422 `DATE_OUT_OF_RANGE` → 200 · **และ** ฟิลด์ `max` ของทุกคำตอบ `/api/slots` (รวม 422) 2026-11-09 → 2026-11-10 → golden ที่เก็บ `max` จับได้แม้ไม่ทดสอบวันที่ +31 |

ไม่ซ้ำ X1–X3 ที่ผู้เรียนใช้ใน LAB 5 · ชุด A ข้อ 2 ใกล้ LAB 5 (golden `/api/price`) **โดยตั้งใจ** (ชุดฝึก)
⚠️ `EXAM-B.md` ข้อ 2 เพิ่มคำว่า "ขอบเวลาเปิด–ปิดร้าน และขอบช่วงวันที่จองได้" (ไม่มีใน EXAM-DRAFT) ให้ระดับคำใบ้เท่าชุด A ที่บอกครบทุกเรื่องที่ mutant แตะ

**README (ผู้สอน 2):** วิธีรัน 1 บรรทัด · บอกว่าค่ามาจากการรันระบบตั้งต้น (วัน/คำสั่ง) · ฟิลด์ที่ตัด (id, เวลาสร้าง, cookie) พร้อมเหตุผล

**ผิดบ่อย:** เก็บ `bookingId`/`createdAt` ใน golden → base ไม่ผ่าน · ไม่ reset ก่อนรัน → ผลขึ้นกับลำดับ · ใช้ `process.cwd()` หา golden (เครื่องตรวจรันจากโฟลเดอร์อื่น · ใช้ `import.meta.url`) · เขียนค่าคาดจาก SPEC (ไม่ใช่ characterization) · ชุด B ไม่ทดสอบวันที่ขอบ 30/31 วัน หรือรอบ 22:00

---

## 4. ข้อ 3 · วิเคราะห์ผลกระทบ (8 = recall × 6 + ผู้สอน 2)

คะแนน auto = 6 × (จุดที่พบ ÷ จุดในรายการ) ปัดลงครึ่งคะแนน · ผู้สอน 2 = ทุกความเสี่ยงมีวิธีพิสูจน์ที่รันได้ (คำสั่ง/เทสต์ ไม่ใช่ "ควรทดสอบ")

| ชุด A · Lotus Suite (10 จุด) ✅ โค้ด | ชุด B · ศุกร์–เสาร์ถึง 23:00 (10 จุด) ✅ โค้ด |
|---|---|
| 1 `roomBusy` `WHERE room_id = 1` | 1 `fitsDay` / `buildSlots(durationMin)` ไม่มีพารามิเตอร์วัน → เปลี่ยน signature |
| 2 `createBooking` `roomId = 1` (ต้องเลือกห้องว่าง) | 2 `isValidStartTime` ผู้เรียก `buildQuote` (`SLOT_INVALID`) |
| 3 `availableSlots` ใช้ `roomBusy` นับห้อง | 3 `availableSlots` ใช้ `buildSlots` |
| 4 seed `room` + `setval` (ห้องใหม่บนระบบจริง = migration แถวใหม่ ไม่ใช่แก้ init อย่างเดียว) | 4 `CLOSE_MIN` ค่าเดียวทั้งระบบ → ต้องแยกตามวัน |
| 5 `booking_room_no_overlap` ใช้ต่อห้องได้อยู่แล้ว (**ไม่ต้องแก้** · ตอบว่าต้องแก้ = ไม่ได้จุดนี้) | 5 ข้อความเวลาเปิดใน `bot/chat.ts` |
| 6 E20 คู่ที่ 2 รอบ 19:00 จาก 409 → 201 (ถ้าวันนัด ≥ 1 พ.ย.) | 6 i18n `footer.hours` · `home.subtitle` (3 ภาษา) |
| 7 TC-BOOK-07 (e2e-legacy) | 7 2026-10-17 = วันเสาร์ → E20 / TC-BOOK-07 อาจมีรอบเพิ่ม · E01–E09 ใช้ 11 ต.ค. (อาทิตย์) ไม่กระทบ |
| 8 ทัวร์ 360° `Tour360` / ข้อความหน้าเว็บเป็นห้องเดียว | 8 สมมติฐานเวลาทำงานนักบำบัด 10–22 (ต้องถามร้าน) |
| 9 วันมีผล 1 พ.ย. ต้องผูกกับ **วันนัด** ไม่ใช่วันจอง | 9 `availableSlots` ช่วงเวลาค้นถึง 23:59 พอแล้ว (ไม่ต้องแก้) |
| 10 รายชื่อตาราง/seed ที่ reset ใช้ (ห้องใหม่ต้องอยู่ใน seed) | 10 วันในสัปดาห์ต้องคิดตามเวลาไทย (`Asia/Bangkok`) |

**ผิดบ่อย:** แก้โค้ดจริงในข้อ 3 (ข้อนี้ห้ามแก้ · commit `EX3:` มี diff นอก `exam/` = ผู้สอนหัก 1) · ความเสี่ยงไม่มีวิธีพิสูจน์ · ชุด A ลืมว่าวันมีผลผูกกับวันนัด

---

## 5. ข้อ 4 · เปลี่ยนกฎเดิม (12 = hidden 7 · check-rules 1 · diff+ORACLE 2 · ผู้สอน 2)

### ชุด A · ค่ารถ · now = seed (2026-10-10 10:00) · [รันจริง:EXREF 2026-10-12] ทั้งตาราง (v0 และ v1 ตรงทุกค่า)

ขอบทศนิยม (รันจริง): ระยะปัดเป็น 0.1 กม. ด้วย `Math.round` ก่อนเทียบ → v0: 7.04 ฟรี · **7.05 = 7.1 → ฿350** · v1: 8.04 ฟรี · 8.05 → ฿400 · ทั้งคู่: 15.04 คิดเงิน · **15.05 → 422 `OUT_OF_AREA`** (hidden test ใช้ค่าทศนิยม 1 ตำแหน่งเท่านั้น จะไม่กำกวม)

| เคส | v0 (7 กม. · ฿350) | v1 (8 กม. · ฿400) |
|---|---|---|
| `/api/transport` H03 5.1 กม. 1 คน | ฿0 | ฿0 |
| distance 7.0 | ฿0 | ฿0 |
| distance 7.1 | ฿350 | ฿0 |
| distance 8.0 | ฿350 | ฿0 |
| distance 8.1 | ฿350 | ฿400 |
| H04 12 กม. 1 คน | ฿350 | ฿400 |
| H05 15.0 | ฿350 | ฿400 |
| H06 15.1 | 422 `OUT_OF_AREA` | 422 `OUT_OF_AREA` |
| H04 5 คน (2 คัน) | ฿700 | ฿800 |
| P01 2 คน H04 | ยอด ฿5,800 · ค่ารถ 0 | เหมือนกัน |
| U04 กลุ่ม 4 + แลก 200 แต้ม + H04 | ฿4,000 − 10% = ฿3,600 − ฿100 = ฿3,500 + ฿350 = **฿3,850** | ฿3,500 + ฿400 = **฿3,900** |
| + GC01 `SABAI-GC-2000` | บัตร ฿2,000 · จ่ายเพิ่ม ฿1,850 · แต้มที่จะได้ floor((4,000 − 400 − 100 − 2,000) ÷ 100) = **15** | จ่ายเพิ่ม ฿1,900 · แต้ม **15** |
| i18n `transport.rule` th/en/zh | มี "7" และ "350" | มี "8" และ "400" |

**เคสเดิมที่ค่าต้องเปลี่ยน** (✅ โค้ด อ่าน check-rules จริง · ค่าใหม่ [รันจริง:EXREF 2026-10-12] · reference แก้ตามตารางนี้แล้ว check-rules 90/90 ทั้ง v0 v1 · e2e TC-TRN-01/02 TC-PRICE-04/05 ผ่าน):

| เคส | เดิม | v0 | v1 |
|---|---|---|---|
| E74 H03 5.1 กม. | ฿300 | ฿0 | ฿0 |
| E75 H04 12 กม. | ฿300 | ฿350 | ฿400 |
| E76 H05 / พิมพ์ 15.0 | ฿300 ×2 | ฿350 ×2 | ฿400 ×2 |
| E78 3/4/5 คน + ใบสรุปกลุ่ม 5 | [1,300] [1,300] [2,600] · [2,600] | [1,350] [1,350] [2,700] · [2,700] | [1,400] [1,400] [2,800] · [2,800] |
| E79 6 คน 12 กม. | ค่ารถ ฿600 · ยอด ฿6,000 | ฿700 · ฿6,100 | ฿800 · ฿6,200 |
| E87 | ยอด ฿3,800 (แต้มเหลือ 50 ไม่เปลี่ยน) | ฿3,850 | ฿3,900 |
| E88 | ยอด ฿3,800 · จ่ายเพิ่ม ฿1,800 (บัตร ฿2,000 · แต้ม 15 ไม่เปลี่ยน) | ฿3,850 · ฿1,850 | ฿3,900 · ฿1,900 |
| e2e-legacy TC-TRN-01 (5.1 / 15.0) | ฿300 / ฿300 | ฿0 / ฿350 | ฿0 / ฿400 |
| e2e-legacy TC-TRN-02 (4 คน / 5 คน H04) | ฿300 / ฿600 | ฿350 / ฿700 | ฿400 / ฿800 |
| e2e-legacy TC-PRICE-04 | ฿3,800 | ฿3,850 | ฿3,900 |
| **e2e-legacy TC-PRICE-05** (U01 Gold S04 + H04 · 3 จุด + ข้อความขั้น) | ฿2,200 | **฿2,250** | **฿2,300** |

⚠️ EXREF: **TC-PRICE-05 ต้องเปลี่ยนด้วย** (key เดิมไม่มี) · รันจริงบน reference ที่ไม่แก้ TC-PRICE-05 → ล้มทั้ง v0 v1 (ได้ ฿2,250/฿2,300 คาด ฿2,200)

**ห้ามเปลี่ยน:** E73 (5.0 ฟรี) · E77 (15.1 นอกพื้นที่) · E80 (5 คน 5.0 = ฿0) · E81–E83 (แพ็กเกจ) · แก้เคสเหล่านี้ = นอกรายการ → ข้อนี้ −50% ถ้าเปลี่ยน "ค่าคาดหวัง"
รายการที่อนุญาตตาม EB: E73–E80, E87, E88 (+ TC-TRN-01/02, TC-PRICE-04, **TC-PRICE-05**) · auto ตรวจ "เปลี่ยนเฉพาะในรายการนี้ + มีแถวใน ORACLE"

**ผู้สอน 2:** ค่าคงที่อยู่ที่ `rules/transport.ts` จุดเดียว (ข้อความดึงจากค่าคงที่หรือแก้ครบ 3 ภาษา) · ✅ โค้ด: ข้อความค่ารถมีแค่ i18n `transport.rule` (+ `package.item3` เรื่อง 15 กม. ไม่เปลี่ยน) · **แชทไม่มีข้อความค่ารถ** (EXAM-DRAFT เขียน "ไม่ลืมแชท" — ไม่ใช่จุดตรวจ)

**ผิดบ่อย:** เปลี่ยน `FREE_KM_TENTHS` เป็น 7 (ลืมหน่วย 0.1 กม. → ต้องเป็น 70/80) · `FEE_PER_VEHICLE` ลืมหน่วยสตางค์ (35000) · แก้ E73/E80 · ไม่แก้ e2e-legacy แล้ว REGRESSION ข้อ 8 แดง

### ชุด B · ค่าแต้ม · now = seed · [รันจริง:EXREF 2026-10-12] ทั้งตาราง (v0 v1 v2 ตรงทุกค่า · unit ฿80 แลก 2 ก้อน → ลด ฿80 ยอด ฿0 ทุก variant · i18n 3 ภาษาตรง)

| เคส | v0 (฿60) | v1 (฿70) | v2 (฿75) |
|---|---|---|---|
| U05 (Gold 5% · 100 แต้ม) S01 แลก 1 | ฿1,000 − ฿50 = ฿950 − ฿60 = **฿890** | ฿880 | ฿875 |
| U06 (Platinum 10% · 199 แต้ม) S05 แลก 1 | ฿800 − ฿80 = ฿720 − ฿60 = **฿660** | ฿650 | ฿645 |
| U04 กลุ่ม 4 + แลก 2 + H04 | ฿3,600 − ฿120 + ฿300 = **฿3,780** | ฿3,760 | ฿3,750 |
| + GC01 ฿2,000 | จ่ายเพิ่ม ฿1,780 | ฿1,760 | ฿1,750 |
| แต้มที่จะได้ (กรณีบน) | floor(1,480 ÷ 100) = **14** | floor(1,460 ÷ 100) = 14 | floor(1,450 ÷ 100) = 14 |
| unit: ยอด ฿80 แลก 2 ก้อน | ลด ฿80 (ไม่ติดลบ) | ฿80 | ฿80 |
| i18n `book.points` 3 ภาษา | "100 แต้ม = ลด ฿60" | ฿70 | ฿75 |

**เคสเดิมที่ค่าต้องเปลี่ยน** (✅ โค้ด · ค่าใหม่ [รันจริง:EXREF 2026-10-12] · reference แก้ตามนี้แล้ว check-rules 90/90 ทั้ง 3 variant): E42 ลด ฿50 → ฿pointValue · E43 เหมือน E42 · E44 ลด ฿100 → 2×pointValue (฿120/140/150) · E87 ฿3,800 → ฿3,780/3,760/3,750 · **E88 ยอด ฿3,800 → เหมือน E87 · จ่ายเพิ่ม ฿1,800 → ฿1,780/1,760/1,750 · แต้มที่จะได้ 15 → 14 และแต้มที่ได้จริงหลังเสร็จ 15 → 14** · E89 ฿670 → ฿660/650/645 · e2e TC-MEM-03 (U05 แลก 1: ฿900 → ฿890/880/875) · TC-PRICE-04 (฿3,800 → ฿3,780/3,760/3,750) · **TC-CXL-03** (U04 S01 แลก 2 + GC01: ยอด/จ่ายด้วยบัตร ฿900 → ฿880/860/850 · บัตรเหลือ ฿1,100 → ฿1,120/1,140/1,150 · แต้ม 50 → 250 ไม่เปลี่ยน)
⚠️ EXREF: **TC-CXL-03 ต้องเปลี่ยนด้วย** (key เดิมไม่มี) · รันจริงบน v2 ที่ไม่แก้ TC-CXL-03 → ล้ม (ได้ ฿850 / ฿1,150)
**ไม่เปลี่ยน:** E41 (99 แต้มแลกไม่ได้) · จำนวนแต้มคงเหลือใน E42–E44 (0 / 99 / 50) · E45 (cap ที่ ฿80 อยู่แล้ว) · อนุญาตตาม EB: E42–E45, E87–E89 (+ TC-MEM-03, TC-PRICE-04, **TC-CXL-03**)

**ผิดบ่อย:** แก้ `BLOCK_VALUE` แต่ลืมหน่วยสตางค์ (6000) · ลืม E88 แต้ม 15 → 14 · แก้จำนวนแต้มคงเหลือ · ลืมข้อความ `book.points` en/zh

---

## 6. ข้อ 5 · แก้บั๊กจากเรื่องร้องเรียน (12 = hidden 7 · check-rules 1 · เทสต์เดิม 1 · commit แดง 1 · ผู้สอน 2)

### ชุด A · ติ๊กรถแต่ไม่มีระยะ (L4 ใน CN §7)

สภาพก่อนแก้ 🧪 รันจริง: e2e-legacy TC-TRN-03 ติด `test.fail` KNOWN-ISSUE (ล้มตั้งแต่ส่งมอบ) · ต้นเหตุ ✅ โค้ด: `components/BookingWizard.tsx` `body()` ส่ง `hotelCode/distanceKm = null` เมื่อว่าง + `next3()` ไม่ตรวจ · API ไม่ตรวจ `wantTransport`

| เคส [รันจริง:EXREF 2026-10-12] | ผล |
|---|---|
| UI: U08 แพ็กเกจ 2 คน ติ๊กรถ ไม่เลือก → ถัดไปขั้น 3 | ยังอยู่ขั้น 3 (`data-step="3"`) · `book-transport-error` = "กรุณาเลือกโรงแรมหรือใส่ระยะทาง" · กด `lang-en` / `lang-zh` แล้วยังขั้น 3 และข้อความเปลี่ยนเป็น en/zh ตาม EXAM.md |
| UI: เลือก H04 → ถัดไป | ขั้น 4 · `summary-amount-transport` `data-amount="0"` ("ค่ารถรับส่ง 1 คัน (12.0 กม.) · รวมในแพ็กเกจแล้ว") · หัวสรุป "… · แพ็กเกจ · 2 คน" · ยอด ฿5,800 |
| UI: กลุ่ม S01 4 คน ใส่ระยะ 12 | ขั้น 4 ค่ารถ = ค่าต่อคันจาก `/api/transport` ของระบบผู้สอบ (รันจริงบนระบบที่ไม่ได้ทำข้อ 4 = ฿300 · ข้อ 4 รันจริง H04 1 คัน = ฿350 v0 / ฿400 v1) |
| API `wantTransport: true` ไม่มี hotel/ระยะ | 422 `TRANSPORT_DISTANCE_REQUIRED` (ทั้ง `/api/price` และ `/api/bookings` · แพ็กเกจด้วย) · ข้อความตาม `Accept-Language`/cookie th/en/zh ตรง EXAM.md · base เดิม: `/api/price` 200 · `/api/bookings` 201 (= เทสต์ API แดงบนโค้ดเดิมจริง) |
| ไม่ติ๊กรถ | 201 (API และ UI จองสำเร็จ) |
| e2e-legacy TC-TRN-03 | **ต้องเอา `test.fail` ออก** (ไม่งั้นขึ้น "expected to fail but passed" = failed) + แถว ORACLE อ้างข้อ 5 → ได้คะแนน "เทสต์เดิม 1" · reference: passed |

⚠️ EXREF (กับดักของ TC-TRN-03 ที่ key เดิมไม่ได้บอก): เทสต์เดิม (1) **คลิก `book-next-3`** → ถ้าผู้สอบ disable ปุ่มเมื่อยังไม่มีราคา (เดิมปุ่ม `disabled={!quote}` และเมื่อ API ตอบ 422 ราคาจะเป็น null) Playwright จะรอจน timeout = failed · (2) นับ `book-error-message` + `book-quote-error-message` ที่มีคำ "ระยะ|โรงแรม" ต้อง **= 1 พอดี** (ไม่ได้ดู `book-transport-error`) · reference ผ่านเพราะ: ส่ง `wantTransport` ใน `body()` → `/api/price` ตอบ 422 → ข้อความอยู่ใน `book-quote-error-message` 1 จุด · ปุ่มถัดไปยังกดได้เมื่อขาดระยะ · ข้อความของ UI อยู่ใน `book-transport-error` (คนละ testid) → hidden UI test ควรตรวจ `book-transport-error` + `data-step` ส่วน TC-TRN-03 เป็นตัวตรวจ "เทสต์เดิม"

`BUGFIX.md` (ผู้สอน 2): ต้นเหตุ 2 ชั้น (UI ไม่บังคับ + API ไม่ตรวจ) · ทำไมไม่มีใครจับ = เทสต์เดิมรู้แต่ติด KNOWN-ISSUE ไว้ / check-rules ไม่มีเคส `wantTransport` ที่ไม่มีระยะ

### ชุด B · กดเสร็จนัดอนาคต (L2 ใน CN §7) · ฉบับปรับตาม D12

ให้คะแนน (12 = auto 10 · ผู้สอน 2 เท่าชุด A): hidden 6 · EVIDENCE 1 · check-rules 1 · เทสต์เดิมเปลี่ยนแค่ setup 1 · commit แดง 1 · ผู้สอน `BUGFIX.md` 2
`X` = `completeAfterMin` ใน VARIANT: v0 = 0 · v1 = 30 · v2 = 60 (= เวลาจบของบริการ 60 นาที)

สภาพก่อนแก้ 🧪 รันจริง (CN §7 L2): กดเสร็จ B02 (17 ต.ค.) วันที่ 10 → 200 · U02 แต้ม 0 → 25 · ยอดสะสม ฿30,000 → ฿32,520 · ต้นเหตุ ✅ โค้ด: `web/lib/server/booking.ts` `completeBooking` ดึง `const { now } = await clock()` (บรรทัด ~496) **แต่ไม่ใช้** · ตรวจแค่ `status !== "confirmed"`

**EX5-EVIDENCE.json** · เครื่องตรวจทำซ้ำบน `sabai-exam-base` (reset ค่าเริ่ม) ด้วยนัดที่ผู้สอบเลือก แล้วเทียบ before/after (ต้องตรงทุกฟิลด์) · ค่าอ้างอิง [รันจริง:EXREF 2026-10-12] (base · reset ค่าเริ่ม → `/api/me` → owner `POST /api/admin/bookings/<id>/complete {}` → `/api/me` · ทุกนัดตอบ 200):

| นัด | ลูกค้า | before → after (points · lifetimeSpend · tier) |
|---|---|---|
| B01 (12 ต.ค. S01 ฿1,000) | U04 | 250 → 260 · ฿9,999 → ฿10,999 · **silver → gold** (เลื่อนระดับก่อนมาใช้บริการ = ได้ส่วนลด 5% ทันที) |
| B02 (17 ต.ค. คู่ ฿2,520) | U02 | 0 → 25 · ฿30,000 → ฿32,520 · platinum → platinum |
| B04 (14 ต.ค. กลุ่ม 5 ฿4,500) | U08 | 0 → 45 · ฿0 → ฿4,500 · silver → silver |
| B05 (11 ต.ค. S05 ฿760) | U01 | 99 → 106 · ฿12,400 → ฿13,160 · gold → gold |
| B06 (10 ต.ค. 15:00 ฿950) | U01 | 99 → 108 · ฿12,400 → ฿13,350 · gold → gold |
| B03 (guest) | — | ไม่มีบัญชี = ไม่นับ (ต้องเลือกนัดสมาชิก) |

**BUGFIX.md · ผลข้างเคียงที่ต้องพบ** (✅ โค้ด · ผู้สอนให้เต็มเมื่อพบ ≥ 4 ใน 6 + ต้นเหตุ + กฎที่ขัด):
1 แต้ม `points_balance` + แถว `point_txn` `'earn'` · 2 `lifetime_spend` → **ระดับสมาชิก/ส่วนลด % เปลี่ยนก่อนใช้บริการ** (BR-11/BR-12) · 3 สถานะ `completed` → ลูกค้า**ยกเลิกไม่ได้ / ไม่ได้คืนแต้ม-บัตร-สิทธิ์** · 4 คอร์ส: `used_sessions + 1` `reserved − 1` (ครั้งถูกตัดก่อนใช้) · 5 รอบเอว `waist_measurement` วันที่ผิด (ถ้าส่ง `waistCm`) · 6 ยอดเข้าก่อนวันจริง (รายงาน/ข้อความ "อีก ฿X ถึง…" เพี้ยน)
กฎที่ขัด: SPEC BR-09 (แต้มจากยอดที่ใช้บริการ) + หมายเหตุสมมติฐาน "ยอดสะสมเพิ่มตอนร้านกดเสร็จ" (SPEC ~บรรทัด 138) · ข้อเสนอข้อมูลเดิม: query หานัด `completed_at < start_at` แล้วให้ร้านตัดสินทีละรายการ (ไม่แก้ข้อมูลเอง)

**hidden test (6 · [รันจริง:EXREF 2026-10-12] ทั้ง X = 0 / 30 / 60)** · `T = 2026-10-10T15:00 + X นาที` (นัด B06)

| เคส | ผล | คะแนน |
|---|---|---|
| reset now = T − 1 นาที → กดเสร็จ B06 | 422 `NOT_STARTED` + ข้อความตามภาษา (th/en/zh ตรง EXAM-B) · U01 ยัง 99 · ฿12,400 | 1.5 |
| reset now = T → กดเสร็จ B06 | 200 · `pointsEarned` 9 · U01 แต้ม 99 → 108 · ฿13,350 | 1.5 |
| reset now ค่าเริ่ม → กดเสร็จ B02 | 422 `NOT_STARTED` · U02 แต้ม 0 · ยอดสะสม ฿30,000 · tier platinum | 1 |
| B08 (completed แล้ว) | 422 `NOT_CONFIRMED` (ลำดับตรวจ: สถานะก่อนเวลา) | 0.5 |
| UI ตารางคิว 10 ต.ค. | ปุ่ม `admin-complete-B06` disabled ที่ T − 1 นาที · enabled ที่ T (รันจริงทั้ง 3 ค่า) | 1.5 |

ขอบ v0 (X = 0) = เวลาเริ่มพอดี · v1/v2 ทำให้ "ตั้งนาฬิกาให้ถึงเวลานัด" แบบใน LAB **ไม่พอ** ต้องอ่านค่า VARIANT และทดสอบขอบ `X − 1 / X` เอง

**เทสต์เดิมที่ต้องเปลี่ยน "เฉพาะการเตรียมสถานการณ์"** (✅ โค้ด · เดิมกดเสร็จนัดที่ยังไม่ถึงเวลา ณ now ของ seed):

| เทสต์ | กดเสร็จ | ทางแก้ที่ถูก | ค่าที่ต้องคงเดิม |
|---|---|---|---|
| E39 | B05 (11 ต.ค. 10:00) | `reset {now ≥ 2026-10-11T10:00 + X}` | แต้มที่ได้ 7 · รวม 106 |
| E40 | B05 | เหมือน E39 | 99 → 106 |
| E88 | นัดกลุ่มที่เพิ่งจอง 16 ต.ค. 10:00 | **reset ไม่ได้** (ลบนัดที่เพิ่งจอง) → seam ตั้งเวลาโดยไม่ล้างข้อมูล (เช่น `POST /api/test/today {now}` เปิดเฉพาะ `config.allowTestReset` · ปัจจุบัน route มีแค่ GET) ไปที่ ≥ 16 ต.ค. 10:00 + X | แต้มที่ได้จริง = ค่าหลังข้อ 4 (**14** ทุก variant) |
| e2e-legacy **TC-MEM-04** | B06 ผ่านปุ่ม `admin-complete-B06` | reset now ≥ T ก่อนเปิดหน้า | ผลเดิม |

ตรวจ auto: `git diff <EX4>..<EX5> -- web/scripts/check-rules.mjs e2e-legacy` ต้องไม่มีบรรทัดที่เปลี่ยน "ตัวเลขคาดหวัง" ของ E39/E40/E88/TC-MEM-04 (ค่า E88 ที่ข้อ 4 แก้อยู่ก่อน EX4 แล้ว)
⚠️ EXAM-DRAFT ไม่ได้ระบุ TC-MEM-04 และไม่ได้บอกว่า E88 ต้องใช้ seam — เพิ่มจากการอ่านโค้ด (S6)
[รันจริง:EXREF 2026-10-12] รายการนี้**ครบแล้ว ไม่มีมากกว่านี้**: reference X = 60 + ชุดทดสอบเดิมที่ยังไม่แก้ → check-rules ล้มเฉพาะ E39 E40 E88 (87/90) · e2e api + chromium ล้มเพิ่มเฉพาะ TC-MEM-04 (ที่เหลือคือ TC-SEC-05 เดิม) · firefox/webkit รันไฟล์ spec เดียวกัน → TC-MEM-04 ทุกเบราว์เซอร์ · หลังแก้เฉพาะ setup (E39/E40 `{ now: 2026-10-11T10:00 + X }` · E88 `POST /api/test/today {now: 2026-10-16T10:00 + X}` ก่อนกดเสร็จ · TC-MEM-04 `api.reset(T)`) → check-rules 90/90 ทั้ง 3 ค่า X · api + chromium 41 passed (expected-fail 3) · 1 failed (TC-SEC-05) · ตัวเลขคาดหวังเดิมทุกตัวคงที่ (E88 แต้มจริง 15 บนระบบที่ไม่มีข้อ 4)

**ผิดบ่อย (ทั้ง 2 ชุด):** commit แดงที่ไม่แดงจริง (เทสต์ผ่านบนโค้ดเดิม) · แก้แค่ UI ไม่แก้ API (ชุด A) หรือแก้แค่ API ไม่ disable ปุ่ม (ชุด B) · ชุด B แก้ E39/E88 โดยเปลี่ยนตัวเลข หรือ skip · ใช้เวลาเครื่องจริง (`Date.now()`) แทนนาฬิกาของระบบ (`clock()`) → hidden test ที่ตั้ง now ไม่ผ่าน

---

## 7. ข้อ 6 · migrate ฐานข้อมูล (16 = ① 4 · ②–⑤ ข้อละ 2 · ⑥ 2 · ผู้สอน rollback 2)

ฐาน "ใช้งานจริง" = `exam-ref/prod-data-A.sql` / `prod-data-B.sql` (**สร้างแล้วโดย EXREF** · คัดไป `runner/` ตอนทำ grader · ใช้เป็น `db/init/03-prod-data.sql` ต่อจาก init ของ EX0): seed + ลูกค้าใหม่ 1 คน (id 10) + นัดใหม่ 5 นัด B14–B18 → ลูกค้า 10 · นัด 18 (A: B14 = S03 วันที่ 20 ต.ค. · B: นัดวันที่ 12 ต.ค. ของ**ทุก** `leaveTherapist`: T03 = B01 ใน seed · T02 = B15 · T06 = B16)

⚠️ **ลำดับสำคัญ:** hidden check ทุกตัว `POST /api/test/reset` ก่อนเคส ซึ่ง TRUNCATE ทุกตารางแล้วโหลด seed ใหม่ → ข้อมูล prod หาย · **ตรวจ ① และ smoke ข้อ 8 ก่อน reset ครั้งแรกเสมอ**

| # | ชุด A (S03 ปิด) [รันจริง:EXREF 2026-10-12] | ชุด B (`leaveTherapist` ลา 15 ต.ค.) [รันจริง:EXREF 2026-10-12 · v0 T03 · v1 T02 · v2 T06] |
|---|---|---|
| ① | migration 2 ครั้ง exit 0 (ครั้งที่ 2: NOTICE skip) · ลูกค้า 10 นัด 18 ครบ · `/api/admin/bookings?date=2026-10-20` มี `B14` S03 confirmed | migration 2 ครั้ง exit 0 · ลูกค้า 10 นัด 18 · คิว 12 ต.ค. ยังมี B15 (T02) B16 (T06) B01 (T03) |
| ② | `/api/services` ไม่มี S03 (เหลือ 8) · `/api/slots` `/api/price` `/api/bookings` S03 → 422 `SERVICE_INVALID` | slots S01 15 ต.ค. 10:00 ไม่มีคนที่ลา · เหลือ 5 คน (16 ต.ค. 6 คนรวมคนที่ลา) |
| ③ | mood: tired → [S01] · aches → [S02, S05] · quiz 72 ชุดคำตอบไม่มี S03 (pain + soft → S02) · `/skin` ไม่มีชื่อ S03 · แชท "ประคบ…ราคา" / "จองประคบ" / "herbal compress price" → ตอบว่าปิดชั่วคราว ไม่เข้าขั้นจอง | ระบุคนที่ลา 15 ต.ค. → 409 `SLOT_TAKEN` · 16 ต.ค. → 201 |
| ④ | owner เปิด S03 กลับ → slots S03 200 · ปิดอีกครั้ง → 422 · ลูกค้าเรียก → 403 | กลุ่ม S01 6 คน 15 ต.ค. 10:00 → 409 · 5 คน → 201 (ไม่มีคนที่ลา) · จองเดี่ยวอัตโนมัติ 15 ต.ค. ได้ 5 คนแรก คนที่ 6 → 409 |
| ⑤ | reset 2 ครั้ง → 200 · S03 ยังปิด | reset 2 ครั้ง → 200 · วันลายังอยู่ |
| ⑥ | check-rules ผ่าน 90/90 (บนฐาน prod-data) | check-rules ผ่าน 90/90 ทั้ง 3 variant (E14 จอง T04 วันที่ 15 ต.ค. ไม่ชน) |
| ถอยกลับ | `down` 2 ครั้ง exit 0 · คอลัมน์หาย · image เดิม (base) บนฐานนั้น check-rules 90/90 | `down` 2 ครั้ง exit 0 · ตารางหาย · image เดิมบนฐานนั้น check-rules 90/90 |

⚠️ EXREF: คำว่า "ประคบสมุนไพร" ยังอยู่ในคำอธิบายแพ็กเกจ P01 (แชทราคารวม "(นวดไทย + ประคบสมุนไพร + รถรับส่งโรงแรม)" และเหตุผล quiz ของ P01) ซึ่ง**ถูกต้อง** (แพ็กเกจยังขาย) → hidden check ③ ต้องตรวจ**รหัส S03 / ชื่อบริการ S03 แบบเต็มบรรทัด** ไม่ใช่ค้นคำ "ประคบสมุนไพร" ในข้อความ (ไม่งั้น reference ตก)

✅ โค้ด จุดที่ S03 ถูกอ้างตายตัว: `lib/bot/chat.ts:47` (คำค้น) · `lib/bot/mood.ts:19, 27` · `lib/bot/quiz.ts:84–85, 115` → ต้องกรองด้วย active (หรือดึงจากฐาน) · **`SkinAnalyzer.tsx` ไม่มี S03** (EXAM-DRAFT เขียนว่ามี — ผิด · ยังตรวจ skin เพื่อกัน regression)

**กับดักที่คาดว่าผู้สอบตก:**
- A: `02-seed.sql` INSERT `service` ระบุคอลัมน์ไม่มี `active` → หลัง reset S03 กลับมา active ถ้าไม่แก้ seed (⑤ ตก) · ใช้ `ALTER TABLE ADD COLUMN` ไม่มี `IF NOT EXISTS` → รันครั้งที่ 2 error (① ตก)
- B: ตาราง `therapist_leave` **ไม่มี FK ไป `therapist`** และไม่เพิ่มในรายชื่อ TRUNCATE ของ `testmode.ts` (แต่ใส่วันลาใน `02-seed.sql`) → **reset ครั้งแรกก็ 500 แล้ว** (`duplicate key` · แถววันลาจาก init/migration ไม่ถูกล้าง แล้ว seed INSERT ซ้ำ) และ 500 ทุกครั้งต่อจากนั้น · ถ้ามี FK `REFERENCES therapist` แม้ไม่เพิ่มในรายชื่อ ตัว `TRUNCATE … CASCADE` ล้างให้เอง → reset 200 ทุกครั้ง [รันจริง:EXREF 2026-10-12 · ทดลองทั้ง 2 แบบ] · `INSERT` วันลาใน migration ไม่มี `ON CONFLICT DO NOTHING` → ครั้งที่ 2 error · วันลาอยู่แค่ใน migration ไม่อยู่ใน `02-seed.sql`
- ทั้งคู่: เขียน migration ไว้ใน `db/init` อย่างเดียว (ไม่รันบนฐานที่มีข้อมูล) · rollback ใช้ `down -v` (= ข้อนี้ 0)

**ผู้สอน 2:** รันไฟล์ถอยกลับจริงบนฐานหลัง migration → ระบบกลับเป็นแบบเดิม · `MIGRATION.md` บอกข้อมูลที่จะหาย (A: สถานะ active · B: วันลาทั้งหมด)

---

## 8. ข้อ 7 · ฟีเจอร์ใหม่ (18 = hidden API 10 · Playwright 3 · check-rules 1 · เทสต์ของผู้สอบ 1 · ผู้สอน 3)

### ชุด A · ประวัติแต้ม (✅ โค้ด: seed `point_txn` · ผลลัพธ์ API [รันจริง:EXREF 2026-10-12])

| เคส | ผล |
|---|---|
| U01 | `balance` 99 · 2 รายการ: [0] earn +19 · B13 · 2026-09-30 · balanceAfter 99 · [1] opening +80 · `bookingCode: null` · 2026-01-15 · balanceAfter 80 |
| U04 จองแบบ E87 (แลก 200) | 201 (นัดใหม่ = B14) · [0] redeem −200 · B14 · balanceAfter 50 |
| ยกเลิกนัดนั้น (16 ต.ค. · ยกเลิกได้ ที่ now seed → 200) | [0] refund +200 · B14 · balanceAfter 250 · [1] redeem −200 · 50 · [2] opening +250 · 250 |
| U01–U08 ทุกคน | Σ points = balance (U01 99 · U04 250 · U05 86+14 = 100 · U06 199 · คนอื่น 0) · owner `items: []` |
| U03 | `items: []` · balance 0 |
| ไม่ล็อกอิน | 401 |
| UI | U01 เห็น 2 แถว `points-row-0` (earn · B13 · +19 · คงเหลือ 99) `points-row-1` (ยอดยกมา +80) · ภาษา en มี "Opening balance" |

⚠️ EXREF (`date` ของรายการใหม่): `point_txn.created_at` มี `DEFAULT now()` = **เวลาเครื่องจริง** ไม่ใช่นาฬิการะบบ → reference ที่อ่าน `created_at` ได้ `date` ของ redeem/refund = วันที่รันจริง (12 ต.ค. 2026 ในการรันนี้) ขณะที่ "วันนี้" ของระบบ = 2026-10-10 · hidden test **ห้ามเทียบ `date` ของรายการที่เพิ่งสร้างกับวันของ seed** (ตรวจแค่รูปแบบ `YYYY-MM-DD` + ลำดับ + points/reason/bookingCode/balanceAfter) · วันที่ของรายการใน seed ตรวจตรงได้

### ชุด B · รีวิว (✅ โค้ด: seed review · `ratingTenths` · ผลลัพธ์ [รันจริง:EXREF 2026-10-12] ทั้ง 3 variant · ก่อนรีวิวตรงทุกค่า)

ก่อนรีวิว: T01 5.0 (15/3) · T02 4.5 (9/2) · T03 4.4 (22/5) · T04 ไม่มี · T05 4.6 (23/5) · T06 4.0 (8/2) · `/api/therapists?min=4.5` = **3 คน** (T01 T02 T05)

| เคส | v0 (U01 · B13 · 5 ดาว) | v1 (U05 · B07 · 1 ดาว) | v2 (U01 · B13 · 4 ดาว) |
|---|---|---|---|
| POST รีวิว | 201 | 201 | 201 |
| คะแนนนักบำบัด | T03 4.4 → **4.5** (27/6 · floor(546/12) = 45) | T05 4.6 → **4.0** (24/6) | T03 4.4 → **4.3** (26/6 · floor(526/12) = 43) |
| `?min=4.5` | 3 → **4 คน** | 3 → **2 คน** | **3 คน** (ไม่เปลี่ยน) |
| ร่วมทุก variant | รีวิวซ้ำ → 409 `ALREADY_REVIEWED` · stars 0 / 6 / 4.5 / "5" → 422 · U01 รีวิว B05 (confirmed) → 422 `NOT_COMPLETED` · U02 รีวิว B13 → 403 · ไม่ล็อกอิน → 401 · นัดกลุ่ม/คู่ (หลายนักบำบัด) → 422 | | |
| UI | U01/U05 เห็นปุ่ม `review-B13` / `review-B07` ในหน้า /account · กดแล้วรีวิวสำเร็จ · หน้านักบำบัดแสดงคะแนนใหม่ (รันจริง v0: `therapist-rating-T03` = 4.5 · ปุ่ม `review-B13` หายหลังรีวิว) | | |

⚠️ EXREF (สิ่งที่ hidden test ต้องกำหนดให้ชัด):
- **นัดกลุ่ม/คู่ไม่มีใน seed ที่ completed** → hidden test ต้องสร้างเอง: `reset {now: "2026-10-17T21:00:00+07:00"}` → owner กดเสร็จ B02 (คู่ U02) / B04 (กลุ่ม U08) → รีวิว → 422 (reference ตอบ `REVIEW_ONE_THERAPIST`) · ใช้ now หลังเวลานัดเพื่อให้ผ่านแม้ระบบมีข้อ 5 (กดเสร็จก่อนเวลาไม่ได้)
- `bookingId` ใน EXAM-B ไม่ได้บอกรูปแบบ → reference รับทั้ง `"B13"` และ `13` · hidden test ควรใช้แบบเดียวกับ `/api/me/bookings` (`id` ตัวเลข) หรือยอมรับทั้งสอง
- stars `"5"` (สตริง) · 0 · 6 · 4.5 · null → 422 ทั้งหมดใน reference
- EXAM-B กำหนดแค่ testid ปุ่ม `review-{รหัสนัด}` ไม่ได้กำหนดช่องเลือกดาว/ปุ่มส่ง → hidden UI test ตรวจได้แค่ "ปุ่มแสดงเฉพาะนัดที่รีวิวได้" ถ้าจะให้กดรีวิวผ่าน UI ต้องเพิ่ม testid ในใบโจทย์ (reference ใช้ `review-stars-{รหัส}` `review-submit-{รหัส}` `review-result-{รหัส}`)
- U01 มีนัดคอร์ส completed นักบำบัด 1 คน (B08 B09 B10 B12) → รีวิวได้ด้วย (201) และเห็นปุ่มด้วย · ไม่ขัดข้อตกลง แต่ hidden UI test อย่าเช็ก "ปุ่มรีวิวมีแค่ 1 ปุ่ม"

**ผู้สอน 3:** แตกงานเป็นขั้น (API → เทสต์ → UI) และ commit message/EX7-STEPS อธิบายได้ · ไม่แก้กฎเดิม (check-rules ไม่มี diff ใน EX6..EX7) · ไม่มี SQL ต่อสตริงจาก input
**ผิดบ่อย:** A: ใช้ `customer.points_balance` คำนวณย้อนหลัง ไม่ใช้ `point_txn` · balanceAfter คิดผิดทิศ (เรียงใหม่ → เก่า ต้องสะสมจากเก่าก่อน) · ลืม redeem ที่เป็นค่าลบ · B: ไม่อัปเดต `review.booking_id` → กันซ้ำไม่ได้ · คิดเฉลี่ยด้วยทศนิยมแล้วปัดเอง (ไม่ใช้ `ratingTenths`)

---

## 9. ข้อ 8 · regression + ส่งมอบ (12 = auto 9 · ผู้สอน 3)

| ตรวจ | คะแนน | วิธี |
|---|---|---|
| ① ตัวเลขใน `REGRESSION.md` ตรงกับที่เครื่องตรวจรันได้ (±0 · e2e-legacy แยก passed / expected-fail / failed) | 3 | เทียบกับผลขั้น 5–6 ของ §11 |
| ② ทุกเคสที่ `git diff EX0..HEAD` เปลี่ยนใน check-rules / golden / e2e-legacy มีใน ORACLE และอ้างข้อ 4–7 | 2 | parse ชื่อเคสจาก diff |
| ③ golden ข้อ 2 (ฉบับ HEAD) ผ่านบนโค้ดสุดท้าย | 2 | รันกับ image HEAD หลัง reset |
| ④ `tests/smoke.mjs`: exit 0 บนระบบผู้สอบ (หลัง migration · ก่อน reset) · exit ≠ 0 บน `sabai-exam-base` · จำนวนแถว `booking` `customer` ก่อน/หลังรันเท่ากัน | 2 | psql `SELECT count(*)` ก่อน/หลัง |
| ผู้สอน: release notes ภาษาคน · ปัญหาที่ยังเหลือ (เช่น cookie หลังออกจากระบบยังใช้ได้ · owner ยกเลิกแทนลูกค้าได้ · test hooks เปิดในโหมดจริง) · ขั้นตอน backup → migration → smoke → ถอยกลับ ไม่มี `down -v` | 3 | อ่าน |

ภาพ e2e-legacy [รันจริง:EXREF 2026-10-12 · reference สะสมข้อ 2+4+5+6+7 (A = v1 · B = v2) · 4 project api + chromium + firefox + webkit]:

| ระบบ | ผลรวม (list reporter) | expected-fail (`test.fail` นับใน passed) | failed |
|---|---|---|---|
| ฐานตั้งต้น (หลัง PREP) | 113 passed · 1 failed (12.6 นาที) | 7 = TC-SEC-04 (api) · TC-GC-04 ×3 · TC-TRN-03 ×3 | TC-SEC-05 |
| ชุด A หลังงานทุกข้อ | 113 passed · 1 failed (11.5 นาที) | **4** = TC-SEC-04 · TC-GC-04 ×3 (TC-TRN-03 ผ่านจริงทั้ง 3 เบราว์เซอร์) | TC-SEC-05 |
| ชุด B หลังงานทุกข้อ | 113 passed · 1 failed (12.5 นาที) | 7 เท่าเดิม | TC-SEC-05 |

เฉพาะ api + chromium (ตัวเลขเดิมใน key): A → expected-fail 2 (TC-GC-04 · TC-SEC-04) · B → expected-fail 3 · ทั้งคู่ 41 passed · 1 failed TC-SEC-05 (ไม่อยู่ในงานข้อสอบ · **ห้าม skip**) · ผู้สอบรายงานตามจริงได้คะแนน ① · ค่าเดียวกันนี้ได้บน check-rules 90/90 และ golden ข้อ 2 (A อัดใหม่หลังข้อ 4 แล้วผ่าน 29/29 · B ไม่ต้องอัดใหม่ 47/47)

**ผิดบ่อย:** smoke เรียก reset/จองจริง (④ ตก) · smoke ตรวจแค่ `/api/health` (base ก็ผ่าน → ④ ตก) · รายงานตัวเลขจากความจำ AI ไม่ได้รันจริง · ORACLE ขาดเคส e2e-legacy

---

## 10. สรุปคะแนน

| ข้อ | อัตโนมัติ | ผู้สอน | รวม | repo |
|---|---|---|---|---|
| 1 | 8 | (ปรับเฉพาะกรณี) | 8 | 🔍 |
| 2 | 12 | 2 | 14 | ✏️ เทสต์ |
| 3 | 6 | 2 | 8 | 🔍 |
| 4 | 10 | 2 | 12 | ✏️ โค้ด + check-rules |
| 5 | 10 | 2 | 12 | ✏️ โค้ด + เทสต์ |
| 6 | 14 | 2 | 16 | ✏️ schema + โค้ด |
| 7 | 15 | 3 | 18 | ✏️ โค้ด + เทสต์ |
| 8 | 9 | 3 | 12 | ✏️ เทสต์ + เอกสาร |
| **รวม** | **84** | **16** | **100** | **✏️ 6/8 = 84 คะแนน** |

เกณฑ์ผ่าน ≥ 60 และข้อ 4–7 ≥ 30/58 · กติกาหักทุกข้อ: เปลี่ยนค่าคาดหวังไม่มีแถว ORACLE → ข้อนั้น −50% · ลบ/skip เทสต์เดิม → 0 · `down -v` ในขั้นตอนที่ส่ง → 0

---

## 11. แผนเครื่องตรวจอัตโนมัติ (**สร้างแล้วที่ `grader/`** [รันจริง:GRADER 2026-10-12] · ตัวที่ใช้จริงต่างจากแผนนี้เล็กน้อย: ไฟล์ hidden อยู่ `grader/hidden/<ชุด>/` · ชื่อ container `exref-g-<id>-*` · e2e-legacy แยก 3 ระบบขนาน · ดู README · ชิ้นส่วนที่ EXREF สร้างและรันแล้ว: mutant · prod-data · diff เฉลยอ้างอิง ที่ `exam-ref/` · ขั้น `Start-Sut`/`Run-Node` ทดลองแบบเดียวกันใน network ของ docker แล้วใช้ได้)

```text
_solution/exam/
├─ grade.ps1                 # วนทุกคน → results.csv + รายงานรายคน (Markdown)
├─ variant.mjs               # รหัสนักศึกษา → VARIANT.json (สูตร §1)
├─ runner/prod-data-A.sql · prod-data-B.sql      # ← คัดจาก exam-ref/ (EXREF สร้างแล้ว)
├─ mutants/M1.diff … M9.diff                      # ← คัดจาก exam-ref/mutants/ (ไม่มี M5)
├─ reference/A/v0 v1 · reference/B/v0 v1 v2    # เฉลยอ้างอิง (repo ที่มี EX0–EX8 ครบ)
└─ checks/
   ├─ package.json           # @playwright/test 1.63.0 (npm ci ครั้งเดียว)
   ├─ A/ ex1.key.json · ex3.key.json · ex4.mjs · ex5.mjs · ex5.ui.spec.ts · ex6.mjs · ex7.mjs · ex7.ui.spec.ts · ex8.mjs
   └─ B/ (ชุดเดียวกัน ค่าตาม §2–§9)
```

ข้อกำหนด check ทุกตัว: reset ก่อนทุกเคส (`POST /api/test/reset {now}`) ยกเว้นขั้น "ก่อน reset" · อ่าน VARIANT ของผู้สอบ · พิมพ์ JSON `{item, set, variant, passed, total, details[]}` · ไม่ขึ้นกับลำดับเคส · **ไม่ใช้พอร์ต host** (Windows จองช่วง 2970–3069 · รันหลายคนพร้อมกันได้) → ทุก container อยู่ใน network `exam-<id>-net`

### 11.1 เตรียมครั้งเดียว: image ฐาน + mutant (PowerShell)

```powershell
$K    = "<repo คอร์ส>\00_tester\06_sabai-spa-legacy-change-request\_solution\exam"
$BASE = "C:\t\exam\base"            # แตกจาก sabai-legacy.zip (ชื่อ sabai06x-*)
docker build --build-context dbinit=$BASE\db\init -t sabai-exam-base $BASE\web
foreach ($m in 1..9) {
  $d = "C:\t\exam\mut\M$m"
  robocopy $BASE $d /E /XD node_modules .next | Out-Null
  Push-Location $d; git apply "$K\mutants\M$m.diff"; Pop-Location
  docker build --build-context dbinit=$d\db\init -t "sabai-exam-m$m" $d\web
}
```

### 11.2 ฟังก์ชันเปิดระบบที่ทดสอบ (ใช้ซ้ำทุกขั้น)

```powershell
function Start-Sut($ID, $img, $initDir) {
  $NET = "exam-$ID-net"; docker network create $NET 2>$null
  docker rm -f "exam-$ID-web" "exam-$ID-db" 2>$null
  docker run -d --name "exam-$ID-db" --network $NET -e POSTGRES_USER=sabai -e POSTGRES_PASSWORD=sabai -e POSTGRES_DB=sabai `
    -e TZ=Asia/Bangkok -e PGTZ=Asia/Bangkok -v "${initDir}:/docker-entrypoint-initdb.d:ro" postgres:16-alpine
  do { Start-Sleep 2; docker exec "exam-$ID-db" pg_isready -U sabai -d sabai | Out-Null } until ($LASTEXITCODE -eq 0)
  docker run -d --name "exam-$ID-web" --network $NET -e DATABASE_URL="postgres://sabai:sabai@exam-$ID-db:5432/sabai" `
    -e HOSTNAME=0.0.0.0 -e TZ=Asia/Bangkok -e ALLOW_TEST_RESET=1 -e SESSION_SECRET=exam-grader $img
  # รอ /api/health {db:true} ด้วย node container ใน network เดียวกัน
}
function Run-Node($ID, $mount, $script, $workdir = "/w") {
  docker run --rm --network "exam-$ID-net" -v "${mount}:/w" -w $workdir -e BASE_URL="http://exam-$ID-web:3000" `
    -e VARIANT=/w/exam/VARIANT.json node:22-alpine node $script; return $LASTEXITCODE
}
```

`node:22-alpine` ต้องเป็น ≥ 22.18 (check-rules import ไฟล์ `.ts` ของ `web/lib/rules`) · ตรวจ `docker run --rm node:22-alpine node -v` · [รันจริง:EXREF 2026-10-12] image ในเครื่อง = v22.23.3 · check-rules รันใน container นี้ผ่าน 90/90 (~21 วินาที)

### 11.3 ขั้นตอนต่อผู้สอบ 1 คน (**วัดจริงด้วย grader: 4 นาที 35 วินาที – 5 นาที 47 วินาที/คน** แบบ e2e ครบ 4 project · ดู K15 ใน §13/§16)

| ขั้น | ทำ | คำสั่งหลัก |
|---|---|---|
| 1 | แตก bundle · หา commit ของแต่ละข้อ | `git clone <id>.bundle C:\t\exam\<id>` · `git -C $W log --format="%H %s" \| Select-String " EX"` · ไม่มี commit ของข้อใด = ตรวจจาก HEAD เท่าที่ทำได้ |
| 2 | ข้อ 1, 3: เทียบ `exam/Q1.json` `exam/IMPACT.md` กับ `checks/<set>/ex1.key.json` `ex3.key.json` | ไม่ต้องรันระบบ · ข้อ 3 ตรวจ `git diff <EX2>..<EX3> --stat` ต้องมีแต่ `exam/` |
| 3 | ข้อ 2: `git archive <EX2> tests/exam2 \| tar -x -C C:\t\exam\<id>-ex2` → `Start-Sut` ด้วย `sabai-exam-base` และ mutant ของชุด (A: m2 m3 m4 m7 · B: m1 m6 m8 m9) โดย `initDir = $BASE\db\init` | `Run-Node $ID C:\t\exam\<id>-ex2 tests/exam2/run.mjs` · base ต้อง 0 · mutant ต้อง ≠ 0 |
| 4 | build image ของผู้สอบจาก HEAD · initDir = `db/init` **ของ commit EX0** + `03-prod-data.sql` | `git -C $W archive <EX0> db/init \| tar -x -C C:\t\exam\<id>-init` · คัด `runner\prod-data-<set>.sql` → `<id>-init\db\init\03-prod-data.sql` · `docker build --build-context dbinit=$W\db\init -t exam-<id>-web $W\web` · `Start-Sut $ID exam-<id>-web C:\t\exam\<id>-init\db\init` |
| 5 | รัน migration ของผู้สอบ **2 ครั้ง** (ไฟล์ขาขึ้นเรียงชื่อ · ไม่รวมไฟล์ที่ชื่อมี `down`/`rollback`) | `docker cp <file> exam-<id>-db:/tmp/` · `docker exec exam-<id>-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/<file>` · ถ้าชื่อไฟล์กำกวม อ่าน `exam/MIGRATION.md` |
| 6 | **ก่อน reset:** ข้อ 6 ① · ข้อ 8 ④ (นับแถว → `Run-Node $ID $W tests/smoke.mjs` → นับแถว) | `docker exec exam-<id>-db psql -U sabai -d sabai -tAc "select count(*) from booking"` |
| 7 | hidden check ข้อ 4–7 (API) | `docker run --rm --network exam-<id>-net -v "$K\checks:/c" -v "$W\exam:/x" -e BASE_URL=http://exam-<id>-web:3000 -e VARIANT=/x/VARIANT.json node:22-alpine node /c/<set>/ex4.mjs` (ex5 ex6 ex7 เหมือนกัน) |
| 8 | hidden check UI (Playwright) | `docker run --rm --network exam-<id>-net -v "$K\checks:/c" -w /c -e BASE_URL=http://exam-<id>-web:3000 mcr.microsoft.com/playwright:v1.63.0-noble npx playwright test <set>/ex5.ui.spec.ts <set>/ex7.ui.spec.ts --reporter=json` |
| 9 | ชุดของผู้สอบเอง: check-rules · golden HEAD · e2e-legacy 4 project | `Run-Node $ID $W web/scripts/check-rules.mjs` · `Run-Node $ID $W tests/exam2/run.mjs` · `docker run --rm --network … -v "$W\e2e-legacy:/e" -w /e -e BASE_URL=… mcr.microsoft.com/playwright:v1.63.0-noble sh -c "npm ci && npx playwright test --project=api --project=chromium --project=firefox --project=webkit --reporter=json"` |
| 10 | diff เคสที่แก้ | `git -C $W diff <EX3>..<EX4> -- web/scripts/check-rules.mjs e2e-legacy` (ข้อ 4) · `<EX4>..<EX5>` (ข้อ 5) · `<EX0>..HEAD` (ข้อ 8 ②) · เทียบกับรายการอนุญาต §5–§6 และแถวใน `exam/ORACLE-CHANGES.md` |
| 10b | ข้อ 5 ชุด B: ทำซ้ำ `exam/EX5-EVIDENCE.json` บน `sabai-exam-base` (reset ค่าเริ่ม → อ่าน `/api/me` ของลูกค้า → owner กดเสร็จนัดที่ระบุ → อ่านอีกครั้ง) เทียบทุกฟิลด์ | `checks/B/ex5.evidence.mjs` (ต้องสร้าง) |
| 11 | ข้อ 5 "แดงก่อนแก้": build image จาก commit `EX5-red` (โค้ดก่อนแก้ + เทสต์) → เทสต์ใหม่ต้อง**แดง** · image จาก `EX5` → ต้อง**เขียว** | หาไฟล์เทสต์จาก `git diff --name-only <EX4>..<EX5-red>` · คำสั่งรันตามที่ผู้สอบเขียนใน `BUGFIX.md` |
| 12 | ข้อ 6 ⑤: reset 2 ครั้ง · ข้อ 8 ④ ส่วน base: `Start-Sut` ด้วย `sabai-exam-base` → smoke ต้อง ≠ 0 | |
| 13 | ปิด/ลบของเครื่องตรวจเอง | `docker rm -f exam-<id>-web exam-<id>-db` · `docker network rm exam-<id>-net` (ไม่มี named volume = ไม่ต้อง `-v`) |

ตรวจ grep กติกาหักคะแนน: `git -C $W grep -n "down -v" HEAD -- exam RELEASE-NOTES.md db/migrations` · `git -C $W diff <EX0>..HEAD -- web/scripts/check-rules.mjs e2e-legacy \| Select-String "^-T\(|test\.skip|\.skip\("`

---

## 12. เช็กลิสต์ก่อนใช้สอบ (ต้องผ่านทุกข้อ)

| ☐ | ตรวจ |
|---|---|
| ☐ | ฐานข้อสอบ = โฟลเดอร์บทหลัง PREP (ถอด BUG_MODE แล้ว) · เปลี่ยนชื่อใน compose ของ zip เป็น `sabai06x-web` `sabai06x-db` `sabai06x-net` volume `sabai06x-pgdata` + `DATABASE_URL` host `sabai06x-db` (พอร์ตยัง 4000/5433) · check-rules ผ่านทั้งหมด |
| ☐ | zip **ไม่มี** `_solution/` `EXAM.md` `CHANGE-REQUESTS/` `tools/` `img/` `.git` (มีแค่ `web/` `db/` `e2e-legacy/` ตาม 🧰 ของ EXAM.md) |
| ☐ | ทดสอบแตก zip บนเครื่องที่ยังมีระบบ LAB (`sabai06-*` + volume มีข้อมูล LAB) ทำตาม ① – ⑤ ของ `EXAM.md` แล้วได้ฐานตั้งต้นจริง · ระบบ LAB กลับมาเปิดได้พร้อมข้อมูลเดิม (M11) |
| ☐ | ทดสอบขั้น ② (ล้าง `sabai06x-pgdata` หลังฝึกชุด A) แล้ว check-rules ผ่านทั้งหมดบนฐานใหม่ |
| ☑ | เฉลยอ้างอิงได้เต็มทุก check อัตโนมัติ [รันจริง:GRADER 2026-10-12]: ชุด A v0 (ประกอบจาก `exam-ref/*.diff` + `grader/selftest/A/`) = **84/84** · โฟลเดอร์ตั้งต้นที่ยังไม่ทำ = **0/84** · ทำข้อ 7 พังโดยตั้งใจ = **73/84** (เสียเฉพาะข้อ 7: 15 → 4) · ชุด B v0 (เฉพาะโค้ดข้อ 2 4–7 ไม่มีเอกสาร) = ข้อ 2 4 5 6 เต็ม · hidden ข้อ 7 เต็ม · ชุด B v1 v2 และ A v1 ยังไม่ได้รันผ่าน grader |
| ☑ | mutant ทุกตัวทำให้ golden อ้างอิงของผู้สอนแดง · base ผ่าน (EXREF 12 ต.ค. 2026: A 4/4 · B 4/4 · base exit 0) |
| ☑ | `tests/smoke.mjs` ของ reference (`grader/selftest/A/tests/smoke.mjs`) ผ่านบน reference และ exit 1 บน base · แถว customer/booking/point_txn ก่อน/หลังเท่ากัน [รันจริง:GRADER 2026-10-12] |
| ☑ | ค่าทุกตัวที่มี [คาด] ใน §13 ตรงกับผลของ reference (ไม่ตรง → แก้ key พร้อมเหตุผล ไม่ใช่แก้ reference ให้ตรง) · EXREF 12 ต.ค. 2026: K1–K14 ยืนยันแล้ว (แก้/เติม key 9 รายการ §16) · K15 ยืนยันแล้วโดย GRADER 12 ต.ค. 2026 (~5–6 นาที/คน) |
| ☐ | grep `EXAM.md` (P8 ใน PREP): `grep -nE "\bM[1-9]\b\|TABLES\|room_id\|EX-B[0-9]\|NOT_STARTED\|therapist_leave\|sabai06-net" EXAM.md` → ไม่มีผล · เพิ่ม `pointValue\|leaveTherapist\|reviewBooking\|ALREADY_REVIEWED\|NOT_COMPLETED` → ไม่มีผล (S6 รันแล้ว 12 ต.ค. 2026: ไม่มีผล · `sabai06x-` 7 บรรทัด) |
| ☐ | **`_solution/EXAM-B.md` และ `EXAM-KEY.md` อยู่ใน repo คอร์ส** → ถ้าผู้เรียน clone repo คอร์สได้ ต้องย้ายออก/ลบจาก branch ที่แจกก่อนวันสอบ (`.git/info/exclude` ของผู้เรียนกันแค่การ commit ไม่กันการอ่าน) |
| ☐ | ชุด B ข้อ 1 ไม่มีคำถามที่ชี้กับดักของข้อ 2–8 ชุดเดียวกัน (M9: B1 เปลี่ยนแล้ว · ไม่ถามรายชื่อตาราง reset) |
| ☐ | README/ภาพของบท 06 ไม่มีแถว L2 (กดเสร็จนัดอนาคต) = เฉลยชุด B ข้อ 5 (M10) |

---

## 13. รายการค่าที่เคยเป็น [คาด] — ต้องยืนยันกับเฉลยอ้างอิงก่อนใช้สอบ (สถานะล่าสุดในคอลัมน์ขวา · รายละเอียด §16)

| # | ข้อ · ชุด | ค่า/พฤติกรรมที่ยังไม่ได้รัน | เสี่ยงเพราะ | สถานะ EXREF 12 ต.ค. 2026 |
|---|---|---|---|---|
| K1 | 2 · A/B | mutant แต่ละตัว "ฆ่าได้" ด้วย golden ที่สมเหตุสมผล · M2 เป็น diff 1 บรรทัดได้จริงไหม | ยังไม่ได้สร้าง diff/image | ✅ [รันจริง:EXREF 2026-10-12] 8/8 · M2 1 บรรทัด |
| K2 | 2 · B | M9 ฆ่าได้ด้วย `/api/slots` วันที่ 2026-11-10 (422 → 200) · M8 ด้วยยกเลิก B05 ที่ now seed | endpoint อาจตอบ error code ต่างที่คาด | ✅ [รันจริง:EXREF 2026-10-12] + รายละเอียดเพิ่ม (§16) |
| K3 | 4 · A | ทุกค่าใน §5 ชุด A โดยเฉพาะ **v1 (8 กม./฿400)** ที่ EB ไม่ได้คำนวณ · ค่าใหม่ของ E74–E79 E87 E88 | คำนวณมือ | ✅ ค่าตรง · ✏️ เพิ่ม TC-PRICE-05 |
| K4 | 4 · A | `/api/transport?distance=7.0/7.1/8.0/8.1` ตอบ fee ตามตาราง (ปัด 0.1 กม. ด้วย `Math.round`) | ขอบทศนิยม | ✅ [รันจริง:EXREF 2026-10-12] |
| K5 | 4 · B | ทุกค่าใน §5 ชุด B (3 variant) · E88 แต้ม 15 → 14 | คำนวณมือ | ✅ ค่าตรง · ✏️ เพิ่ม TC-CXL-03 |
| K6 | 5 · A | ข้อความ/สถานะ UI ของ 3 เคส UI · ค่ารถเคสกลุ่ม 4 คน 12 กม. ตามระบบผู้สอบ | ขึ้นกับการทำข้อ 4 | ✅ [รันจริง:EXREF 2026-10-12] + ✏️ กับดัก TC-TRN-03 |
| K7 | 5 · B | ขอบ T − 1 → 422 · T → 200 ทั้ง 3 ค่า `completeAfterMin` (0/30/60) · แต้ม 99 → 108 · ปุ่ม B06 disabled/enabled · EVIDENCE ของ B01 (U04 silver → gold) B04 B05 B06 | ขอบเวลา + timezone · after ส่วนใหญ่คำนวณมือ | ✅ [รันจริง:EXREF 2026-10-12] · ✏️ เติมค่า B04 |
| K8 | 5 · B | รายการเทสต์เดิมที่ต้องเปลี่ยน setup (เวลา + X) = E39 E40 E88 + **TC-MEM-04** (อาจมีมากกว่านี้ในชุด e2e 3 เบราว์เซอร์) · E88 ต้องมี seam ตั้งเวลา | อ่านโค้ดเท่านั้น | ✅ [รันจริง:EXREF 2026-10-12] ครบ ไม่มีเพิ่ม |
| K9 | 6 · A | ③ ครอบคลุมทุกคำตอบ quiz/mood/แชท · ⑥ check-rules ผ่านทั้งหมดหลังปิด S03 | ต้องรัน reference | ✅ [รันจริง:EXREF 2026-10-12] · ✏️ วิธีตรวจ ③ |
| K10 | 6 · B | slots เหลือ 5 คน · กลุ่ม 6 → 409 / 5 → 201 ทั้ง 3 variant · check-rules ผ่านทั้งหมดหลังมีวันลา · กับดัก reset 500 เกิดเฉพาะเมื่อไม่มี FK | ต้องรัน reference | ✅ ค่าตรง · ✏️ กับดัก 500 ตั้งแต่ reset ครั้งแรก |
| K11 | 6 · A/B | `prod-data-A/B.sql` ยังไม่มี · เกณฑ์ ① ขึ้นกับไฟล์นี้ | ยังไม่สร้าง | ✅ สร้างแล้ว `exam-ref/` · ① ผ่านทั้ง A และ B |
| K12 | 7 · A | รูปแบบ `date` (วันที่ไทย `YYYY-MM-DD`) · ยกเลิกนัด E87-type ได้ที่ now seed | ต้องรัน reference | ✅ ค่า seed ตรง · ✏️ `date` รายการใหม่ = เวลาเครื่อง |
| K13 | 7 · B | T03 4.5 / T05 4.0 / T03 4.3 · `?min=4.5` 4 / 2 / 3 คน (โดยเฉพาะ **v2**) · นัดกลุ่ม → 422 | คำนวณจาก seed | ✅ [รันจริง:EXREF 2026-10-12] · ✏️ setup นัดกลุ่ม/คู่ |
| K14 | 8 | ตัวเลข e2e-legacy หลังงานทุกข้อ (expected-fail 2 ชุด A / 3 ชุด B · TC-SEC-05 failed) · ผล 🧪 เดิมวัดก่อนถอด BUG_MODE | ต้องรันใหม่หลัง PREP | ✅ [รันจริง:EXREF 2026-10-12] (ตาราง §9) |
| K15 | ทั้งหมด | เวลาตรวจ ~6–8 นาที/คน · คำสั่งใน §11 | ยังไม่มี grader | ✅ [รันจริง:GRADER 2026-10-12] **4 นาที 35 วินาที – 5 นาที 47 วินาที/คน** (e2e ครบ 4 project · 4 ครั้ง) · ไม่รัน e2e 2 นาที 26 วินาที · รายละเอียด §16 |

---

## 14. สิ่งที่ต่างจาก `_design/EXAM-DRAFT.md` (S6 ตรวจกับโค้ดแล้ว)

| เรื่อง | DRAFT | ไฟล์นี้ | เหตุผล |
|---|---|---|---|
| ข้อ 5 B เทสต์เดิมที่ต้องเปลี่ยน | E39 E40 E88 | + **TC-MEM-04** · E88 ต้องมี seam ตั้งเวลา (reset จะลบนัดที่เพิ่งจอง · `/api/test/today` มีแค่ GET) | อ่าน `e2e-legacy/tests/member.spec.ts:87` · `check-rules.mjs:603–620` |
| ข้อ 5 B ค่า E88 | "15 เหมือนเดิม" | 14 (ค่าหลังข้อ 4 ทุก variant) ต้องคงที่ช่วง EX4..EX5 | earnBase หักแต้มที่แลก |
| ข้อ 6 A กับดัก | S03 อยู่ใน `SkinAnalyzer.tsx` | ไม่มี · S03 อยู่ใน `lib/bot/*` 5 จุด | grep โค้ด |
| ข้อ 6 B กับดัก reset | ไม่เพิ่มตาราง → 500 | เกิดเฉพาะเมื่อ `therapist_leave` ไม่มี FK (มี FK → `TRUNCATE … CASCADE` ล้างให้) | `testmode.ts:45` |
| ข้อ 4 A ผู้สอน | "ไม่ลืมแชท" | แชทไม่มีข้อความค่ารถ · มีแค่ i18n `transport.rule` | grep โค้ด |
| ข้อ 4 รายการเคส | อนุญาต E73–E80 | แยก "ต้องเปลี่ยน" กับ "ห้ามเปลี่ยน" ราย variant | อ่าน check-rules |
| ลำดับตรวจ | ไม่ได้ระบุ | ข้อ 6 ① และ smoke ต้องตรวจก่อน reset ครั้งแรก | reset TRUNCATE ข้อมูล prod |
| ข้อ 2 B คำใบ้ | ไม่บอกขอบเวลาปิด/ช่วงวัน | บอก (ให้เท่าชุด A) | M1 M9 อยู่ใน slots |
| ขั้นเปิดระบบ | ไม่มีขั้นล้าง `sabai06x-pgdata` หลังฝึก | ขั้น ② ใน EXAM.md | ฐานข้อสอบจะเป็นฐานของรอบฝึก (ปัญหาเดียวกับ M11) |
| ชื่อไฟล์ชุด B | `exam/LETTERS-B.md` | `_solution/EXAM-B.md` (ตามคำสั่งผู้สอน) | — |

---

## 15. บันทึกการปรับ (D12 · ชุด B ข้อ 5)

LAB 10 ส่วน 2 ข้อ 4 (ตั้งเวลาให้ถึงนัดก่อนกดเสร็จ) คงไว้ในบทเรียน → ชุด B ข้อ 5 ปรับให้ความรู้จาก LAB นั้น "จำเป็นแต่ไม่พอ":
- **VARIANT ใหม่ `completeAfterMin`** 0 / 30 / 60 → ขอบกฎต่างกันรายคน ต้องทดสอบขอบ `X − 1 / X` เอง (ตั้งเวลาแค่ "ถึงนัด" แบบ LAB ไม่ผ่าน v1/v2)
- **ขั้นพิสูจน์ก่อนแก้:** หนังสือไม่บอกแล้วว่าลูกค้าได้อะไรไป → ผู้สอบต้องทำซ้ำบนระบบตั้งต้นเอง ส่ง `exam/EX5-EVIDENCE.json` (auto ตรวจกับ base) และ `BUGFIX.md` ต้องอ้างกฎใน SPEC ที่ขัด + ผลข้างเคียงครบ (เช่น B01 ทำให้ U04 เลื่อน silver → gold · completed แล้วยกเลิกไม่ได้)
- คะแนนข้อ 5 ยัง 12 (auto 10 · ผู้สอน 2 = โครงเดียวกับชุด A) · hidden 7 → 6 + EVIDENCE 1 · สัดส่วนข้อที่แก้ repo เดิมยัง 6/8 = 84 คะแนน (ข้อ 5 ยังแก้โค้ด + เทสต์)
- ไฟล์ที่แก้: `EXAM-B.md` (ข้อ 5) · ไฟล์นี้ (§1 VARIANT · §6 ชุด B · §11 ขั้น 10b · §13 K7 K8 · §15) · `EXAM.md` ไม่แตะ · leak grep บน `EXAM.md` รันซ้ำแล้ว: ไม่มีผล (รวมคำ `completeAfterMin` `EVIDENCE`)

---

## 16. EXREF results (รันเฉลยอ้างอิงจริง 12 ต.ค. 2026)

**วิธีรัน:** คัดโฟลเดอร์บท (ไม่รวม `_solution` `node_modules` `.next`) → แก้เฉพาะสำเนา: compose ชื่อ `exref-*` พอร์ต 4200/5633 · ทำเฉลยอ้างอิงแยกโฟลเดอร์ต่อข้อ/variant → build image (`docker build --build-context dbinit=…`) → เปิดคู่ web + postgres:16 ใน network `exref-net` (ไม่ใช้พอร์ต host) → ยิง API ด้วย `node:22-alpine` · UI ด้วย `mcr.microsoft.com/playwright:v1.63.0-noble` · ชุดสะสม A (ข้อ 2+4+5+6+7 · v1) และ B (v2) รัน check-rules + golden + e2e-legacy 4 project · ลบ container/volume/network/image `exref-*` ทั้งหมดหลังจบ
**ไฟล์:** `exam-ref/A-2 A-4 A-5 A-6 A-7 B-2 B-4 B-5 B-6 B-7.diff` (A-4 = v1 · B-4/B-5/B-6 = v2) + `A-4-v0` `B-4-v0` `B-4-v1` `B-5-v0` `B-5-v1` `B-6-v0` `B-6-v1` · `exam-ref/mutants/M1–M4 M6–M9.diff` · `exam-ref/prod-data-A.sql` `prod-data-B.sql` · diff ทุกไฟล์ `git apply` บนโฟลเดอร์บทตั้งต้นได้ (ตรวจแล้ว)
**variant ที่รัน:** A v0 + v1 (ข้อ 4) · B v0 + v1 + v2 (ข้อ 4 ข้อ 5 ข้อ 6 ข้อ 7) · ข้อที่ไม่มีค่ารายคน (A5 A6 A7) รันครั้งเดียว

| K | คาด (key เดิม) | ผลจริง | การแก้ใน key |
|---|---|---|---|
| K1 | mutant ฆ่าได้ · M2 อาจ > 1 บรรทัด | golden อ้างอิง base exit 0 · A จับ M2 M3 M4 M7 · B จับ M1 M6 M8 M9 (exit 1 ทุกตัว) · M2 เป็น 1 บรรทัดได้ (`percentOf(gross - redeemPoints(…, gross).discount, …)`) ฿670 → ฿675 | ยืนยัน · ตาราง §3 เติมค่าจริงและจำนวนเคสที่ต่าง |
| K2 | M9: slots 11-10 422 → 200 · M8: ยกเลิก B05 ที่ now seed | M9 ตรง และ `max` ของทุกคำตอบ slots เปลี่ยน 11-09 → 11-10 · M8: 200 → 422 `CANCEL_TOO_LATE` + `canCancel` true → false · M1: รอบสุดท้ายหายทุกบริการ · M6: GC03 ok → expired | ยืนยัน · เติมรายละเอียดใน §3 |
| K3 | ค่า §5 A ทั้ง v0 v1 · เคสเดิมที่เปลี่ยน = E74–E79 E87 E88 + TC-TRN-01/02 TC-PRICE-04 | ค่าตรงทุกตัว (เช่น E87 ฿3,850/฿3,900 · E88 จ่ายเพิ่ม ฿1,850/฿1,900 แต้ม 15 · E79 ฿6,100/฿6,200) · **TC-PRICE-05 ล้ม** ถ้าไม่แก้ (U01 S04 + H04 ได้ ฿2,250/฿2,300 คาด ฿2,200) | **แก้**: เพิ่ม TC-PRICE-05 ในตาราง "เคสเดิมที่ค่าต้องเปลี่ยน" และรายการที่อนุญาต (§5) |
| K4 | fee ที่ 7.0/7.1/8.0/8.1 ตามตาราง | ตรง · `Math.round` ทำให้ 7.05 → ฿350 (v0) · 8.05 → ฿400 (v1) · 15.05 → 422 | ยืนยัน · เพิ่มหมายเหตุขอบทศนิยม |
| K5 | ค่า §5 B 3 variant · E88 แต้ม 15 → 14 | ค่าตรงทุกตัว (E88 แต้ม 14 ทุก variant ทั้ง quote และหลังกดเสร็จ) · **TC-CXL-03 ล้ม** ถ้าไม่แก้ (v2 ได้ ฿850 / บัตรเหลือ ฿1,150 คาด ฿900 / ฿1,100) | **แก้**: เพิ่ม TC-CXL-03 ในเคสที่ต้องเปลี่ยน + รายการที่อนุญาต (§5 ชุด B) |
| K6 | UI 3 เคส + API 422 | ตรง (ขั้น 3 ค้าง · ข้อความ th/en/zh · H04 → ขั้น 4 ค่ารถ ฿0 "2 คน" · ระยะ 12 → ฿300 บนระบบที่ไม่มีข้อ 4) · TC-TRN-03 ผ่านเมื่อเอา `test.fail` ออก | **เพิ่ม** คำเตือน §6: TC-TRN-03 คลิกปุ่มถัดไป (ห้าม disable) และนับข้อความใน `book-error-message`/`book-quote-error-message` = 1 |
| K7 | ขอบ T−1/T ทั้ง 3 X · EVIDENCE B01 B04 B05 B06 | ตรงทั้ง X = 0/30/60 (API + ปุ่ม UI) · EVIDENCE ตรง · B04 จริง = 0 → 45 · ฿0 → ฿4,500 · silver | ยืนยัน · เติมค่า B04 (เดิม "grader คำนวณ") |
| K8 | E39 E40 E88 + TC-MEM-04 (อาจมีมากกว่า) | ระบบ X = 60 + เทสต์เดิม: check-rules ล้มแค่ E39 E40 E88 · e2e ล้มเพิ่มแค่ TC-MEM-04 → **ไม่มีเพิ่ม** · seam `POST /api/test/today` ใช้ได้ · หลังแก้ setup ผ่านหมดโดยตัวเลขเดิม | ยืนยัน · บันทึกผลใน §6 |
| K9 | ③ ครอบคลุม · ⑥ ผ่าน | ③ ผ่าน (mood 4 · quiz 72 ชุด · skin · แชท 4 ข้อความ) · ⑥ 90/90 · ①–⑤ ผ่านบน prod-data · rollback 2 ครั้ง + image เดิม 90/90 | **เพิ่ม** คำเตือน: hidden check ต้องดูรหัส/ชื่อ S03 ไม่ใช่คำ "ประคบสมุนไพร" (อยู่ในคำอธิบาย P01) |
| K10 | slots 5 คน · กลุ่ม 6/5 · check-rules · กับดัก reset 500 "ครั้งที่ 2" เฉพาะไม่มี FK | ค่าตรงทั้ง 3 variant · check-rules 90/90 · กับดัก: ไม่มี FK + ไม่อยู่ใน TRUNCATE → **500 ตั้งแต่ reset ครั้งแรก** (duplicate key) · มี FK แต่ไม่อยู่ใน TRUNCATE → 200 | **แก้** ข้อความกับดัก B ใน §7 (ครั้งที่ 2 → ครั้งแรก) |
| K11 | prod-data ยังไม่มี | สร้าง `exam-ref/prod-data-A.sql` `-B.sql` · migration 2 ครั้ง + ① ผ่านทั้งสองชุด (ลูกค้า 10 นัด 18) · B มีนัด 12 ต.ค. ของ T02 T03 T06 ครบทุก variant | ยืนยัน · §7 ชี้ไฟล์ใหม่ |
| K12 | `date` YYYY-MM-DD · ยกเลิกนัด E87 ได้ | seed ตรง (2026-09-30 · 2026-01-15) · ยกเลิก 200 · redeem/refund ถูกต้อง · แต่ `date` ของรายการใหม่ = **วันที่เครื่องจริง** (`created_at DEFAULT now()`) ไม่ใช่นาฬิการะบบ | **เพิ่ม** คำเตือน §8: hidden test ห้ามเทียบ `date` ของรายการใหม่กับวันของ seed |
| K13 | T03 4.5 / T05 4.0 / T03 4.3 · min=4.5 4/2/3 · นัดกลุ่ม 422 | ตรงทุก variant · 409/422/403/401 ตรง · นัดกลุ่ม/คู่ → 422 ได้เมื่อสร้างนัด completed เอง (seed ไม่มี) | **เพิ่ม** วิธีเตรียมเคสกลุ่ม/คู่ · รูปแบบ `bookingId` · testid ฟอร์มรีวิวที่ใบโจทย์ไม่ได้กำหนด (§8) |
| K14 | A expected-fail 2 · B 3 · TC-SEC-05 failed (api + chromium) | ตรง · 4 project: ฐาน/B 113 passed (expected-fail 7) 1 failed · A 113 passed (expected-fail 4) 1 failed | ยืนยัน · ตารางใหม่ใน §9 |
| K15 | ~6–8 นาที/คน · คำสั่ง §11 | **[รันจริง:GRADER 2026-10-12]** `grader/grade.mjs` ผ่าน `grade.ps1` (wall-clock ต่อคน · เครื่อง 32 core / RAM 64 GB · Docker Desktop · image ฐาน/mutant/node_modules เตรียมไว้แล้ว): เฉลย A v0 **5:47** (build 3 image มี cache) · เฉลย A v0 build ใหม่ทั้งหมด (3 image ขนาน 39 วินาที) **5:07** · ข้อ 7 พัง **4:41** · ไม่รัน e2e (`-E2E skip`) **2:26** · โฟลเดอร์ตั้งต้น (ไม่มี commit) **5 วินาที** · ชุด B v0 (ไม่รัน e2e) **1:34** · เส้นทางวิกฤต = e2e-legacy แยก 3 ระบบขนาน (api+chromium ~4.3 นาที · firefox / webkit ~4 นาที) · ที่เหลือ (build · mutant 4 ตัวขนาน · hidden API/UI · check-rules 4 ครั้ง) ซ้อนอยู่ในช่วงเดียวกัน · เตรียมครั้งเดียว (image ฐาน + 4 mutant + `npm ci` Playwright) วัดได้ 5 วินาทีเพราะ build cache ของ EXREF ยังอยู่ (เครื่องใหม่คาด ~3–5 นาที: build ~35 วินาที/image ขนาน + npm ci) | **แก้** ~6–8 นาที → **~5–6 นาที/คน** ถ้ารันทีละคน (เร็วกว่าที่ EXREF ประมาณ ≥ 15 นาที เพราะ grader รัน e2e 3 เบราว์เซอร์บน 3 ระบบพร้อมกัน และงานอื่นขนานกับ e2e) · นักศึกษา 40 คน ≈ 3.5–4 ชั่วโมง (หรือ ~1.6 ชั่วโมงถ้า `-E2E skip` แล้วผู้สอนเทียบ REGRESSION.md เอง) |

**สรุป:** ยืนยัน 15 / 15 รายการ (K1–K14 โดย EXREF · K15 โดย GRADER 12 ต.ค. 2026) · แก้/เติม key จากผลจริง 9 รายการ (K3 K5 K6 K7 K9 K10 K12 K13 K15 · ค่าตัวเลขเดิมผิด 0 ค่า ส่วนที่แก้คือรายการเทสต์เดิมที่ต้องเปลี่ยนตกหล่น 2 ตัว + กับดัก/วิธีตรวจ)
