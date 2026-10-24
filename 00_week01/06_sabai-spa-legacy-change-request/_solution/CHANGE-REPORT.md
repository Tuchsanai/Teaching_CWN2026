# CHANGE-REPORT · สบายใจ สปา (งานแก้ตาม Change Request)

## สรุปรวม CR-01–05 (ส่งมอบ 2026-10-12 · รอตรวจรับ UAT)

> ไฟล์ที่แก้ = โค้ด/DB ระหว่าง commit แดง → commit แก้ (ไม่รวมเทสต์และเอกสาร · ทุก CR แก้ `web/SPEC.md` ด้วย) · regression = ผลรอบเต็ม `REGRESSION-REPORT.md` (HEAD `ef47d72`) · smoke วันขึ้นระบบ `tests/smoke.mjs` 7/7 · ลำดับขึ้น/ถอยรวม `docs/DEPLOY-RUNBOOK.md`

| CR | commit แดง | commit แก้ | ไฟล์ที่แก้ | เทสต์ใหม่ | regression | ความเสี่ยงคงค้าง | วิธีถอยกลับ |
|---|---|---|---|---|---|---|---|
| CR-01 เลื่อนนัด | `8aba74e` (API) · `e54fdc5` (UI) | `802f853` (A+B API) · `f4edf7b` (C หน้าเลื่อนนัด) | 7: `web/app/api/bookings/[id]/reschedule/route.ts` `…/reschedule-slots/route.ts` (ใหม่) · `web/components/MyBookings.tsx` · `web/lib/i18n.ts` · `web/lib/server/booking.ts` `customer.ts` `http.ts` | `tests/cr01.mjs` R1–R22 **22/22** · `e2e-cr` CR01-UI-1/2 **6/6** (3 เบราว์เซอร์) · smoke 5–6 | check-rules 90/90 · golden 62/62 · e2e-legacy test:all = baseline (ล้ม TC-SEC-05 เดิม) | ไม่มีประวัติการเลื่อน (⏳ Q13) · วันหยุด/แพ็กเกจตัดสินแทนร้าน (⏳ Q9 Q10) · `room_id = 1` (T1) · กล่องเลื่อนนัดมี race ปุ่มรอบค้างเมื่อเปลี่ยนวันก่อนรอบแรกโหลด (เซิร์ฟเวอร์ปฏิเสธ · RELEASE-NOTES ข้อ 16) | `git revert f4edf7b 802f853` → `up -d --build --wait` · ไม่มี migration · นัดที่เลื่อนแล้วคงเวลาใหม่ |
| CR-02 ส่วนลดขั้นบันได | `4dbcb90` | `d982284` | 2: `web/lib/rules/pricing.ts` · `web/lib/server/booking.ts` | `tests/cr02.mjs` C1–C18+C7b **19/19** | check-rules 90/90 (E24–E29 E79 E90 ไม่แก้ค่า) · golden price 62/62 | ⚠️ A1–A4 รอร้านยืนยัน · เครื่องจริงต้อง `ALLOW_TEST_RESET=0` ไม่งั้นอัตราใหม่ไม่เริ่ม · ไม่มีเทสต์หน้าจอหลัง 1 พ.ย. · วันมีผลอยู่ในโค้ด | `git revert d982284` → `up -d --build --wait` · ไม่มี migration · นัดที่จองด้วยอัตราใหม่คงยอดเดิม |
| CR-03 กันจองซ้ำ | `eb0bf69` | `fe187aa` | 4: `web/lib/bot/chat.ts` · `web/lib/i18n.ts` · `web/lib/server/booking.ts` · `web/lib/server/http.ts` | `tests/cr03.mjs` C1–C18 **18/18** · `e2e-cr` CR03-UI-1 **3/3** | check-rules 90/90 · golden 62/62 · e2e-legacy TC-BOOK-05/06/07 ผ่าน | `+66`/`0` คนละเบอร์ (⏳ Q3) · จองแทนคนอื่นด้วยเบอร์ตัวเองถูกบล็อก (⏳ Q10) · เบอร์ไม่มีตัวเลข (KI-02) ไม่ถูกตรวจ | `git revert fe187aa` → `up -d --build --wait` · ไม่มี migration |
| CR-04 วันหยุดร้าน (ส่วน ก) | `d221eda` | `7a2dc24` | 12: `db/migrations/001_shop_holiday.sql` `.down.sql` (ใหม่) · `db/init/01-schema.sql` `02-seed.sql` · `web/app/api/holidays/route.ts` `web/lib/server/holiday.ts` (ใหม่) · `web/lib/bot/chat.ts` `i18n.ts` `server/booking.ts` `http.ts` `testmode.ts` | `tests/cr04.mjs` H1–H14 **14/14** · `e2e-cr` CR04-UI-1/2 **6/6** · migration ×2 · ติดตั้งใหม่ · ซ้อมถอยกลับ (down → up) · smoke 3 | check-rules 90/90 · golden 62/62 · e2e-legacy = baseline | **ลำดับ deploy: migration ก่อนเว็บ** · ส่วน ข (ร้านเพิ่ม/ลบเอง) ยังไม่ทำ · ปี 2570 ยังไม่มีวันหยุด · ข้อความ "วันนี้ร้านหยุด" | เว็บก่อน: tag image เดิม + `up --no-build --force-recreate` → แล้ว `001_shop_holiday.down.sql` · หาย = แถว `shop_holiday` เท่านั้น (ซ้อมแล้ว นัดใหม่ B14 อยู่ครบ) |
| CR-05 รายงาน + CSV | `15fb782` | `ef47d72` | 6: `web/app/admin/report/page.tsx` `web/app/api/admin/report/route.ts` `web/components/AdminReport.tsx` (ใหม่) · `web/app/layout.tsx` · `web/lib/i18n.ts` · `web/lib/server/admin.ts` | `tests/cr05.mjs` R1–R12 **12/12** · `e2e-cr` CR05-UI-1/2 **6/6** · smoke 7 | check-rules 90/90 · golden admin-queue 62/62 · คิวหลังร้านไม่เปลี่ยน | ⏳ Q2 Q4 Q5 Q7 Q9 Q11 ตัดสินแทนร้าน · นักบำบัดแสดงเป็นรหัส · นัดที่ไม่กด "เสร็จ" ไม่เข้ายอดขาย · seed ไม่มีนัดข้ามวัน UTC | `git revert ef47d72` → `up -d --build --wait` · ไม่มี migration · ไม่มีข้อมูลถูกเขียน |

รวม: เทสต์ใหม่ระดับ API **85** เคส (22+19+18+14+12) · UI ใหม่ 7 เคส × 3 เบราว์เซอร์ · ไม่มีแดงใหม่ใน regression · ค่าคาดหวังเดิม (check-rules · e2e-legacy · golden) ไม่ถูกแก้

## CR-02 · ส่วนลดกลุ่มขั้นบันได มีผล 1 พ.ย. 2569

| รายการ | ค่า |
|---|---|
| CR / คำตอบร้าน | `CHANGE-REQUESTS/CR-02.md` · `CHANGE-REQUESTS/answers/CR-02-ANSWERS.md` |
| impact | `docs/impact/CR-02.md` (คำถาม Q1–Q9 · อธิบายของเดิม · ค่าคาดหวังคิดมือ 18 แถว · สมมติฐาน ⚠️ A1–A4) |
| commit | `4dbcb90` CR-02 test: แดงก่อนแก้ → commit "CR-02: ส่วนลดกลุ่มขั้นบันได มีผล 1 พ.ย. 2026" (ถัดไป) |

### ไฟล์ที่แก้ (`git diff --stat 3bcd8c9` ก่อน commit แก้)

```
 docs/impact/CR-02.md      | 166 +++  (ใหม่)
 tests/cr02.mjs            | 214 +++  (ใหม่)
 web/SPEC.md               |   4 +-
 web/lib/rules/pricing.ts  |  21 ++-
 web/lib/server/booking.ts |   1 +
 + docs/TRACEABILITY.md (ใหม่) · CHANGE-REPORT.md (ใหม่) · CHANGE-REQUESTS/REGISTER.md
```

โค้ดที่เปลี่ยนจริง 2 ไฟล์: `pricing.ts` เพิ่ม `GROUP_DISCOUNT_SCHEDULE` (ตารางอัตราจุดเดียว ช่วงแรกใช้ค่าคงที่เดิม `GROUP_DISCOUNT_MIN_PEOPLE`/`GROUP_PCT`) + `groupPercent(people, bookedOn?)` + `PriceInput.bookedOn?` (ไม่ส่ง = อัตราเดิม) · `booking.ts` `buildQuote` ส่ง `bookedOn: today` (วันนี้จาก `clock()`) · ไม่มี migration · ไม่แก้ i18n/แชท/หน้าเว็บ

### แดง → เขียว

| ชุดทดสอบ | ก่อนแก้ | หลังแก้ | หมายเหตุ |
|---|---|---|---|
| `tests/cr02.mjs` | 10/19 (ล้ม C2 C4 C5 C8 C9 C11 C13 C14 C17) | **19/19** | ตัวที่ผ่านตั้งแต่ก่อนแก้ = เคสล็อกของเดิม (ขนาดกลุ่ม · ก่อนวันมีผล · นัดเดิม · แพ็กเกจ) |
| `web/scripts/check-rules.mjs` | 90/90 | **90/90** | `git diff web/scripts/check-rules.mjs` ว่าง |
| `tests/golden/run.mjs` | 62/62 | **62/62** | ไม่ `--update` |
| `e2e-cr` chromium | 4 + expected-fail 2 | **4 + expected-fail 2** | |
| `e2e-legacy` api+chromium | ผ่านจริง 38 · ล้ม 1 · test.fail 3 | **38 · 1 · 3** | ล้ม = TC-SEC-05 (ปัญหาเดิม ไม่เกี่ยว CR-02) · 3 เบราว์เซอร์รอบเต็มทำตอนส่งมอบ |

### พฤติกรรมที่เปลี่ยนโดยตั้งใจ (เฉพาะการจอง/ใบสรุปที่ "วันนี้" ≥ 2026-11-01)

- กลุ่ม 3 คน 0% → 5% · กลุ่ม 5–6 คน 10% → 15% · กลุ่ม 4 คนคง 10% (S01 นัด 5 พ.ย.: 3 คน ฿2,850 · 4 คน ฿3,600 · 5 คน ฿4,250 · 6 คน ฿5,100)
- Gold กลุ่ม 3 คน: ยอดเท่าเดิม ฿2,850 แต่ `discountKind` เปลี่ยน tier → group (ร้านยืนยันให้ขึ้น "ส่วนลดกลุ่ม")
- ใบสรุปที่เปิดก่อน 31 ต.ค. 24:00 แล้วกดยืนยันหลังเที่ยงคืน → 409 `PRICE_CHANGED` พร้อมใบสรุปใหม่ (กลไกเดิม)
- ไม่เปลี่ยน: ขนาดกลุ่ม 3–6 · แพ็กเกจ/คอร์ส · ส่วนลดระดับ/เดือนเกิด · ยอดของนัดที่บันทึกแล้ว (รวม B04 และนัดที่จองก่อน 1 พ.ย. แม้วันนัดหลัง 1 พ.ย.)

### ความเสี่ยงคงค้าง

- ⚠️ สมมติฐานที่ร้านยังไม่ยืนยัน: A1 กลุ่ม 2 คนยังจองไม่ได้ · A2 ยกเลิกแล้วจองใหม่หลัง 1 พ.ย. ได้อัตราใหม่ (เลื่อนนัดให้ตัดสินใน CR-01) · A3 ไม่มีวันสิ้นสุดโปร · A4 แชทยังจองกลุ่มไม่ได้
- ระบบจริงต้องไม่ตั้ง `ALLOW_TEST_RESET=1` (T9) ไม่งั้น "วันนี้" ค้างที่ `test_today` และอัตราใหม่จะไม่เริ่มเอง
- วันมีผลเขียนในโค้ด (`GROUP_DISCOUNT_SCHEDULE`) · เปลี่ยนวัน/เพิ่มช่วงต้อง deploy ใหม่
- e2e-legacy ไม่ได้ทดสอบหลัง 1 พ.ย. (ล็อกวันที่ 10 ต.ค.) → อัตราใหม่ถูกพิสูจน์ด้วย `tests/cr02.mjs` ระดับ API เท่านั้น ยังไม่มีเทสต์หน้าจอแสดง "ส่วนลดกลุ่ม 5%/15%"

### วิธีถอยกลับ

1. `git revert <commit CR-02 แก้>` (ไม่ revert commit เทสต์ ถ้าต้องการเก็บเทสต์ไว้เป็นหลักฐาน — เทสต์จะกลับเป็นแดง 9 เคสชุดเดิม)
2. `docker compose -f web/compose.yaml up -d --build --wait` (~1 นาที)
3. ตรวจ `/api/health` `db: True` · `node web/scripts/check-rules.mjs` 90/90 · `node tests/golden/run.mjs` 62/62
4. ไม่มี migration · นัดที่จองหลัง 1 พ.ย. ด้วยอัตราใหม่คงยอดที่บันทึก (ถอยโค้ดไม่ย้อนแก้ข้อมูล) · ตรวจ: `SELECT code, party_size, discount_pct, total_amount FROM booking WHERE booking_type='group' AND created_at >= '2026-11-01 00:00+07'`

## CR-03 · กันจองซ้ำของคนเดียวกัน (เรื่องร้องเรียน · BR-21)

| รายการ | ค่า |
|---|---|
| CR / คำตอบร้าน | `CHANGE-REQUESTS/CR-03.md` (ด่วน) · `CHANGE-REQUESTS/answers/CR-03-ANSWERS.md` |
| impact | `docs/impact/CR-03.md` (ทำซ้ำเรื่องร้องเรียน · คำถาม Q1–Q10 · ต้นเหตุ · ค่าคาดหวัง 16 เคส + UI-1 · เพิ่ม C17–C18 หลังเจอแดงไม่ตั้งใจ) |
| commit | `eb0bf69` CR-03 test: ทำซ้ำเรื่องร้องเรียน (แดง) → commit "CR-03: กันจองซ้ำของคนเดียวกัน" (ถัดไป) |

### ทำซ้ำเรื่องร้องเรียน (ก่อนแก้ · ไม่ล็อกอิน)
POST /api/bookings S02 13 ต.ค. 10:00 คุณสมชาย `081-000-0003` → **201 B14** · `0810000003` → **201 B15** · ซ้ำอีก → **201 B16** · `Promise.all` 2 คำขอ → **201 B17 + 201 B18** · แชทจองซ้ำ → "จองสำเร็จ! รหัสการจอง B14"

### ต้นเหตุ (ไฟล์:บรรทัด ของโค้ดก่อนแก้ `d982284`)
- `web/app/api/bookings/route.ts:12` และแชท `web/lib/bot/chat.ts:238` เรียก `createBooking` ตรง ไม่มีการดู "ตัวคน"
- `web/lib/server/booking.ts:343-378` (`createBooking`) ตรวจแค่ราคา `:354` นักบำบัดว่าง `:359-372` ห้องคู่ `:374-378` แล้วจัดนักบำบัดว่างคนถัดไปให้ `:371` → คนเดิมได้นัดที่ 2 กับหมอนวดอีกคน (ร้านเสียคิว)
- DB มี EXCLUDE แค่ต่อนักบำบัด `db/init/01-schema.sql:152` และต่อห้อง `:137` · ไม่มีอะไรผูกกับคน · เบอร์เก็บตามที่พิมพ์ `guest_phone VARCHAR(20)` `:101` จึงเทียบ `081-000-0003` กับ `0810000003` ไม่ได้
- หน้าเว็บกดสองครั้งไม่ซ้ำเพราะปุ่ม `book-confirm` `disabled={busy}` `web/components/BookingWizard.tsx:616` (+ `setBusy(true)` `:211`) — กันได้แค่แท็บเดียวกันระหว่างรอคำตอบ · เน็ตค้างแล้วกดใหม่ในหน้าใหม่ / ยิง API ตรง / แชท ไม่ผ่านปุ่มนี้

### ทำไมชุดตรวจที่ส่งมอบไม่จับ
- เทสต์ "กดพร้อมกัน" มีแค่ **คนละคนแย่งนักบำบัดคนเดียว** (`therapists:["T04"]`): `web/scripts/check-rules.mjs:196-204` (E14 U03+U04) และ `e2e-legacy/tests/book.api.spec.ts:7-11` (TC-BOOK-06) → พิสูจน์ EXCLUDE ของนักบำบัดเท่านั้น
- TC-BOOK-05 ทดสอบดับเบิลแตะปุ่มในหน้าเดียว (ปุ่มถูกปิดอยู่แล้ว) · ไม่มีเคส "คนเดียวกันจองทับนัดที่มีอยู่" หรือ "คนเดียวกัน 2 คำขอพร้อมกัน" เลย · SPEC 1.0 ไม่มีกฎนี้

### ไฟล์ที่แก้ (`git diff --stat eb0bf69` ก่อน commit แก้)

| ไฟล์ | บรรทัด | ทำอะไร |
|---|---|---|
| `web/lib/server/booking.ts` | +35 | `phoneDigits()` `:343` · `assertNoOverlapForPerson()` `:353-371` (advisory lock ต่อคน + ค้นนัดทับ → 409 `DUPLICATE_BOOKING {existing}`) · เรียกใน `createBooking` `:411-413` หลังตรวจนักบำบัด/ห้อง ก่อน insert |
| `web/lib/i18n.ts` | +2 | `err.DUPLICATE_BOOKING` 3 ภาษา `:290` (ตามคำตอบร้าน ②) |
| `web/lib/server/http.ts` | 1 | `errorBody()` แทน `{code}` ด้วย `extra.existing` `:29` |
| `web/lib/bot/chat.ts` | 1 | แชทส่ง `e.extra` ให้ข้อความ error `:264` |
| `web/SPEC.md` | +4/−2 | BR-21 · error `DUPLICATE_BOOKING` · API POST /api/bookings · ประวัติ 1.2 |
| `tests/cr03.mjs` | (ใหม่ + C17–C18) | 18 เคส |
| `e2e-cr/tests/cr03.spec.ts` | ใหม่ | UI-1 |

ไม่แก้: `BookingWizard.tsx` (ErrorBox ขั้น 4 แสดง `data-error-code` + message อยู่แล้ว) · ไม่มี migration · `web/scripts/check-rules.mjs` `tests/golden/` `e2e-legacy/` diff ว่าง

### ลำดับล็อก (กัน deadlock)
ทุกคำขอขอล็อกลำดับเดียวกัน: แถวลูกค้า `FOR UPDATE` (เฉพาะสมาชิก · มีอยู่เดิมใน `buildQuote`) → `pg_advisory_xact_lock(hashtext('cr03-person:m:<id>' | 'cr03-person:g:<ตัวเลข>'))` **1 ตัว** → insert `booking` → `booking_slot` · ล็อกปล่อยเองตอน commit/rollback · คนละคนไม่รอกัน (คนละ key) → TC-BOOK-06/E14 ยังได้ `SLOT_TAKEN` จาก EXCLUDE เหมือนเดิม

### แดง → เขียว

| ชุด | ก่อนแก้ | หลังแก้ |
|---|---|---|
| `node tests/cr03.mjs` | 5/16 (ล้ม C1 C2 C3 C6 C9 C10 C11 C13 C14 C15 C16) | **18/18** (รันซ้ำ 5 รอบ 18/18) |
| `e2e-cr/tests/cr03.spec.ts` chromium | ล้ม (ไม่มี `book-error`) | ผ่าน |
| check-rules | 90/90 | **90/90** |
| golden | 62/62 | **62/62** |
| cr02 | 19/19 | **19/19** |
| e2e-cr chromium | 4 + expected-fail 2 | **5 + expected-fail 2** |
| e2e-legacy api+chromium | 38 / 1 / 3 | **38 / 1 (TC-SEC-05 เดิม) / 3** · TC-BOOK-06 พร้อมกันคนละคน = `SLOT_TAKEN` ✅ |

### พฤติกรรมที่เปลี่ยนโดยตั้งใจ
- คนเดียวกัน (บัญชี หรือ เบอร์ตัวเลขล้วนของคนไม่ล็อกอิน) จองเวลาทับนัดที่ยังไม่ยกเลิก → 409 `DUPLICATE_BOOKING` "คุณมีนัดในช่วงเวลานี้อยู่แล้ว (รหัส Bxx)" ทั้งหน้าเว็บ API และแชท
- ลำดับ error: คิว/ห้องเต็มตอบ `SLOT_TAKEN` ก่อน (คงผล e2e-legacy TC-BOOK-07) · BR-21 ตรวจเมื่อเวลานั้นจองได้

### ความเสี่ยงคงค้าง
- `+66 81…` กับ `081…` ถือเป็นคนละเบอร์ (คำตอบร้าน: ตัวเลขล้วน) — Q3 ยังค้าง
- คนจองให้คนอื่นด้วยเบอร์ตัวเองในเวลาเดียวกันจะถูกบล็อก (ต้องจองคู่/กลุ่ม) — Q10 ยังค้าง
- เบอร์ที่ไม่มีตัวเลขเลย (เช่น `abc` · KI-02) ไม่ถูกตรวจ BR-21 (ไม่มีตัวตนให้เทียบ) — known issue เดิม
- นัดซ้ำที่มีอยู่แล้วในฐานไม่ถูกแตะ (ร้านจัดการเอง ④)

### วิธีถอยกลับ
`git revert <commit CR-03>` → `docker compose -f web/compose.yaml up -d --build --wait` → `/api/health` + check-rules 90/90 · ไม่มี migration ไม่มีข้อมูลต้องคืน

## CR-04 · วันหยุดร้าน (ส่วน ก) + migration 001

| รายการ | ค่า |
|---|---|
| CR / คำตอบร้าน | `CHANGE-REQUESTS/CR-04.md` (ต้องเสร็จก่อน 23 ต.ค.) · `CHANGE-REQUESTS/answers/CR-04-ANSWERS.md` |
| impact | `docs/impact/CR-04.md` (คำถาม Q1–Q10 · หลักฐาน db/init/seed/reset · ค่าคาดหวัง 14 เคส + UI 2) |
| runbook | `docs/MIGRATION-RUNBOOK.md` (สำรอง · รัน · ตรวจ · ถอยกลับ · ผลซ้อม) |
| commit | `d221eda` CR-04 test: แดงก่อนแก้ → commit "CR-04: วันหยุดร้าน + migration 001" (ถัดไป) |
| ขอบเขต | ส่วน ก เท่านั้น · ส่วน ข (หลังร้านเพิ่ม/ลบวันหยุดเอง) เลื่อน (ร้านยอม ①) |

### ไฟล์ที่แก้ (`git diff --stat d221eda` ก่อน commit แก้)

| ไฟล์ | เปลี่ยน |
|---|---|
| `db/migrations/001_shop_holiday.sql` · `.down.sql` (ใหม่) | ตาราง `shop_holiday` + 3 แถว (รันซ้ำได้) · ถอย = DROP |
| `db/init/01-schema.sql` · `db/init/02-seed.sql` | เครื่องติดตั้งใหม่ + seed ของ reset (โครง/แถวตรงกับ migration) |
| `web/lib/server/testmode.ts` | `TABLES` + `shop_holiday` (T2) |
| `web/lib/server/holiday.ts` (ใหม่) · `web/app/api/holidays/route.ts` (ใหม่) | อ่าน/ตรวจวันหยุด · `GET /api/holidays` |
| `web/lib/server/booking.ts` | `assertShopOpen()` หลังเช็กช่วงวันใน `buildQuote()` และ `availableSlots()` |
| `web/lib/bot/chat.ts` | ขั้นเลือกวัน: วันหยุด → ข้อความ `SHOP_CLOSED` + ถามวันใหม่ |
| `web/lib/server/http.ts` · `web/lib/i18n.ts` | `{name}` ในข้อความ error · `err.SHOP_CLOSED` 3 ภาษา |
| `web/SPEC.md` (1.3) · `docs/MIGRATION-RUNBOOK.md` · `docs/TRACEABILITY.md` · `REGISTER.md` | เอกสาร |

ไม่แตะ `web/components/*` (ขั้น 2 ของหน้าจองแสดง error จาก `/api/slots` อยู่แล้ว) · `check-rules.mjs` · `tests/golden/` · `e2e-legacy/`

### ซ้อม migration บนฐานที่มีข้อมูล

สำรอง `backups/before-cr04.sql` (52,535 ไบต์ · ไม่ commit) → reset + จองใหม่ B14 (ไม่ล็อกอิน S01 20 ต.ค. 14:00) → migrate ครั้งที่ 1 `INSERT 0 3` exit 0 → ครั้งที่ 2 NOTICE skip + `INSERT 0 0` exit 0 → `count = 3` · `th_ok = t` · B14 อยู่ · booking 14 / customer 9 เท่าเดิม → เว็บรุ่นเดิม reset 200 → `docker tag … before-cr04` → rebuild 41 วิ → reset ×2 = 200 · ติดตั้งใหม่ (`sabai06-fresh`) 20 ตาราง shop_holiday 3 แถว

### แดง → เขียว

| ชุด | ก่อนแก้ | หลังแก้ |
|---|---|---|
| `node tests/cr04.mjs` | 3/14 (ผ่านเฉพาะเคสล็อกของเดิม H4 H9 H14) | **14/14** |
| `e2e-cr/tests/cr04.spec.ts` chromium | UI-1 ล้ม · UI-2 ผ่าน | **2/2** |
| check-rules | 90/90 | **90/90** |
| golden · cr02 · cr03 | 62 · 19 · 18 | **62 · 19 · 18** |
| e2e-cr chromium | 5 + expected-fail 2 | **7 + expected-fail 2** |
| e2e-legacy api+chromium | 38 / 1 / 3 | **38 / 1 (TC-SEC-05 เดิม) / 3** |

### พฤติกรรมที่เปลี่ยนโดยตั้งใจ
- 23 ต.ค. / 5 ธ.ค. / 31 ธ.ค. 2569 (เมื่ออยู่ในช่วงจอง) → 422 `SHOP_CLOSED` "วันนี้ร้านหยุด (<ชื่อวันหยุด>) กรุณาเลือกวันอื่น" ที่ `/api/slots` `/api/price` `/api/bookings` (ทุกแบบ รวมคอร์ส) หน้า /book ขั้น 2 และแชท
- วันหยุดที่เกินช่วง 30 วัน ยังตอบ `DATE_OUT_OF_RANGE` ก่อน
- API ใหม่ `GET /api/holidays`

### ความเสี่ยงคงค้าง
- **ลำดับ deploy:** เว็บรุ่นนี้ขึ้นก่อนรัน migration → จอง/ราคา/รอบ/reset ตอบ 500 (runbook บังคับ migrate ก่อน)
- ข้อความร้าน "วันนี้ร้านหยุด" ใช้คำว่า "วันนี้" ทั้งที่หมายถึงวันที่เลือก (ใช้ตามคำตอบร้าน ② คำต่อคำ · เสนอร้านพิจารณา "วันที่เลือกร้านหยุด")
- ปี 2570 ยังไม่มีวันหยุด · เพิ่ม/ลบต้องทำ SQL จนกว่าจะมีส่วน ข
- ช่องทางที่ไม่ใช่การจองรอบ (ซื้อคอร์ส บัตรของขวัญ) ไม่ปิด ตามคำตอบ ① (วันหยุดไม่ต่ออายุ)

### วิธีถอยกลับ
เว็บก่อน: `docker tag sabai06-web:before-cr04 sabai06-web:latest` → `docker compose -f web/compose.yaml up -d --no-build --force-recreate --wait` (หรือ `git revert`) · แล้ว DB: `001_shop_holiday.down.sql` ด้วย `docker cp` + `psql -f` · ข้อมูลที่หาย = แถว `shop_holiday` เท่านั้น (รายละเอียด `docs/MIGRATION-RUNBOOK.md`)

## CR-01 · ลูกค้าเลื่อนนัดเอง (ฟีเจอร์ใหม่ · BR-22)

| รายการ | ค่า |
|---|---|
| CR / คำตอบร้าน | `CHANGE-REQUESTS/CR-01.md` · `CHANGE-REQUESTS/answers/CR-01-ANSWERS.md` |
| impact | `docs/impact/CR-01.md` (คำถาม Q1–Q14 · ที่เก็บเวลา/กฎห้ามซ้อน/ทำไมไม่ใช้ `/api/slots` และ "ยกเลิกแล้วจองใหม่" · ค่าคาดหวัง R1–R22 + UI 2 · แผน 3 ขั้น) |
| commit | `8aba74e` CR-01 test: แดงก่อนแก้ → `802f853` CR-01 A+B: API เลื่อนนัด → `e54fdc5` CR-01 C test: หน้าเลื่อนนัด แดงก่อนแก้ → "CR-01 C: หน้าเลื่อนนัด" (ถัดไป) |
| ขอบเขต | API เลื่อนนัด + รอบที่เลื่อนได้ + ปุ่ม/กล่องในหน้า `/account` · **ไม่มี migration** · นอกขอบเขต (④): SMS/อีเมล · ร้านเลื่อนให้ · เปลี่ยนบริการ/จำนวนคน |

### ไฟล์ที่แก้ (`git diff --stat 7a2dc24` · ไม่รวมเทสต์/เอกสาร impact)

| ไฟล์ | เปลี่ยน |
|---|---|
| `web/lib/server/booking.ts` | `rescheduleBooking()` `rescheduleSlots()` (+ `loadReschedTarget` `checkReschedDate` `reschedFree`) · `busySlots()` `roomBusy()` `assertNoOverlapForPerson()` รับ `excludeBookingId` (ค่าเริ่ม null = เดิม) |
| `web/app/api/bookings/[id]/reschedule/route.ts` · `reschedule-slots/route.ts` (ใหม่) | `POST` / `GET` ตาม ② |
| `web/lib/server/http.ts` | `RESCHEDULE_TOO_LATE` แนบ `phone` + แทน `{phone}` ในข้อความ |
| `web/lib/i18n.ts` | `err.RESCHEDULE_*` 4 ตัว + `account.reschedule*` 8 ตัว ครบ th/en/zh |
| `web/lib/server/customer.ts` | `myBookings()` + `canReschedule` |
| `web/components/MyBookings.tsx` | ปุ่ม `reschedule-{code}` + `RescheduleDialog` (testid ตาม ②) |
| `web/SPEC.md` (1.4) · `docs/TRACEABILITY.md` · `CHANGE-REQUESTS/REGISTER.md` | เอกสาร |

ไม่แตะ `db/` (ไม่มีตาราง/คอลัมน์ใหม่) · `web/lib/bot/chat.ts` (แชทไม่มีเมนูนัดของฉัน) · `check-rules.mjs` · `tests/golden/` · `e2e-legacy/`

### ออกแบบ: UPDATE แถวเดิม ไม่ "ยกเลิกแล้วจองใหม่"
`booking.start_at/end_at` (คอลัมน์ `period` คำนวณเอง) + `booking_slot.period` ทุกแถวที่ active ใน transaction เดียว · ล็อก: แถวลูกค้า → แถวนัด → advisory lock ของคน (CR-03) · EXCLUDE ของ DB เทียบกับแถวอื่นเท่านั้น จึงเลื่อนทับเวลาเดิมของตัวเองได้ · คอลัมน์เงิน/แต้ม/บัตร/คอร์ส/`birthday_use` ไม่ถูกแตะ

### แดง → เขียว
| ชุด | ก่อนแก้ | หลังแก้ |
|---|---|---|
| `node tests/cr01.mjs` (API R1–R22) | 0/22 (endpoint ยังไม่มี → 404) | **22/22** |
| `e2e-cr/tests/cr01.spec.ts` chromium/firefox/webkit | 0/6 (ไม่มีปุ่ม `reschedule-B05`) | **6/6** |
| check-rules | 90/90 | **90/90** (diff ว่าง) |
| golden · cr02 · cr03 · cr04 | 62 · 19 · 18 · 14 | **62 · 19 · 18 · 14** |
| e2e-cr 3 เบราว์เซอร์ (ต่อเบราว์เซอร์) | — | **9 + expected-fail 2** (KI-01b KI-02b) ×3 · ล้ม 0 |
| e2e-legacy `test:all` (api / chromium / firefox / webkit) | api+chromium 38 / 1 / 3 | api 4 + test.fail 1 + ล้ม 1 (TC-SEC-05 เดิม) · chromium 34 + 2 · firefox 34 + 2 · webkit 33 + 2 + **ล้ม 1 TC-UI-02 (flaky webkit มีอยู่เดิม: รันซ้ำ ×3 บน image `before-cr04` ก็ล้ม 1/3 · `/skin` ไม่ได้แตะ)** |

### พฤติกรรมที่เปลี่ยนโดยตั้งใจ
- API ใหม่ 2 ตัว + error ใหม่ 4 ตัว (`RESCHEDULE_TOO_LATE` `RESCHEDULE_NOT_ALLOWED` `RESCHEDULE_BIRTHDAY` `RESCHEDULE_SAME`)
- หน้า `/account` มีปุ่ม "เลื่อนนัด" ข้างปุ่มยกเลิกในนัดสถานะยืนยัน (กดไม่ได้เมื่อ < 24 ชม.)
- `/api/slots` `/api/bookings` ไม่เปลี่ยน (พารามิเตอร์ใหม่มีค่าเริ่ม = เดิม · golden/e2e-legacy ยืนยัน)

### ความเสี่ยงคงค้าง
- ไม่มีประวัติการเลื่อน (เวลาเดิมหายเมื่อ UPDATE) · คิวร้านเห็นแค่เวลาใหม่ · ร้านไม่ได้ขอ (⏳ Q13)
- วันหยุดร้าน (CR-04) ห้ามเลื่อนไป — ตัดสินแทนร้าน (⏳ Q9) · แพ็กเกจ (รถ/โรงแรม) เลื่อนได้แบบทั่วไปแต่ยังไม่มีเทสต์แยก (⏳ Q10)
- `room_id = 1` ตายตัว (T1) ยังอยู่ใน `roomBusy()` — ถ้าเพิ่มห้องคู่ต้องแก้พร้อมการจอง

### วิธีถอยกลับ
`git revert` 2 commit แก้ (C แล้ว A+B) → `docker compose -f web/compose.yaml up -d --build --wait` · ไม่มี migration · นัดที่ลูกค้าเลื่อนไปแล้วคงเวลาใหม่ (ต้องให้ร้านแก้รายนัดถ้าจำเป็น)

## CR-05 · รายงานยอดสำหรับเจ้าของร้าน + CSV

| รายการ | ค่า |
|---|---|
| CR / คำตอบร้าน | `CHANGE-REQUESTS/CR-05.md` · `CHANGE-REQUESTS/answers/CR-05-ANSWERS.md` |
| impact | `docs/impact/CR-05.md` (คำถาม Q1–Q12 · ของเดิมที่ต่อยอด · SQL ค่าคาดหวังอิสระ 3 ช่วง + ขอบ 92/93 วัน · โซนเวลา/หน่วยเงิน) |
| commit | `15fb782` CR-05 test: แดงก่อนแก้ → "CR-05: รายงานยอด + CSV" (`git log --grep "CR-05"`) |
| ขอบเขต | API `GET /api/admin/report` (JSON + `format=csv`) + หน้า `/admin/report` + เมนู owner · **อ่านอย่างเดียว ไม่มี migration** · นอกขอบเขต (④): กราฟ · ส่งอีเมลอัตโนมัติ · VAT |

### ไฟล์ที่แก้ (`git diff --stat f4edf7b` · ไม่รวมเทสต์/เอกสาร)

| ไฟล์ | เปลี่ยน |
|---|---|
| `web/lib/server/admin.ts` | `checkReportRange()` (≤ 92 วัน · from ≤ to) · `salesReport()` · `salesReportCsv()` · ช่วง `[toInstant(from,"00:00"), toInstant(to+1,"00:00"))` · รวมเงินเป็นสตางค์ (`toSatang`) → บาท (`toBaht`) / CSV (`fromSatang`) · ไม่แก้ `queueForDate()` |
| `web/app/api/admin/report/route.ts` (ใหม่) | 401/403 แบบเดียวกับ `/api/admin/bookings` · CSV `text/csv; charset=utf-8` + BOM + `Content-Disposition: attachment` |
| `web/app/admin/report/page.tsx` · `web/components/AdminReport.tsx` (ใหม่) | หน้า + ตาราง + ลิงก์ CSV (testid ตาม ②) · ช่วงเริ่มต้น = เดือนของ `clock()` |
| `web/app/layout.tsx` | เมนู `nav-admin-report` (owner) |
| `web/lib/i18n.ts` | `nav.adminReport` + `report.*` 22 ตัว + `err.REPORT_RANGE` ครบ th/en/zh |
| `web/SPEC.md` (1.5) · `docs/TRACEABILITY.md` · `CHANGE-REQUESTS/REGISTER.md` | เอกสาร |

ไม่แตะ `db/` · `web/lib/bot/chat.ts` (แชทไม่มีทางเข้ารายงาน · R12 ยืนยันว่าไม่รั่ว) · `check-rules.mjs` · `tests/golden/` · `e2e-legacy/`

### ค่าคาดหวังมาจาก SQL ก่อนเขียนโค้ด (ไม่ลอกจากหน้า)
ก.ย. 0/3/1 · ยอดขาย ฿1,900 (ส่วนลดระดับ ฿100 · แต้ม 19 · คอร์ส 2) · ต.ค. 6/1/0 · ฿1,440 (เดือนเกิด ฿360 · แต้ม 14 · ยอดนัดยืนยัน ฿11,130) · 6–9 ต.ค. 0 ทั้งหมด (= ③1) · 1 ส.ค.–31 ต.ค. 92 วันได้ / 1 ส.ค.–1 พ.ย. 93 วัน 422 (= ③2) · ตรวจไขว้ `point_txn` earn และนัดประเภทคอร์สได้ค่าเดียวกัน · ตรวจเพิ่ม: ยอดขาย/จำนวน/ยอดยืนยันในรายงาน = Σ ตารางคิวหลังร้านทุกวันในช่วง (ก.ย. ต.ค. ส.ค.–ต.ค. ตรงทั้ง 3) และหลังตั้งเวลาเป็น 12 ต.ค. 14:00 แล้วกดเสร็จ B01 → ต.ค. ฿2,440 (R10)

### แดง → เขียว
| ชุด | ก่อนแก้ | หลังแก้ |
|---|---|---|
| `node tests/cr05.mjs` (R1–R12) | 1/12 (endpoint ยังไม่มี → 404 · R12 แชทผ่านอยู่แล้ว) | **12/12** |
| `e2e-cr/tests/cr05.spec.ts` chromium/firefox/webkit | — (เขียนหลังทำหน้า) | **6/6** |
| check-rules | 90/90 | **90/90** |
| golden · cr01 · cr02 · cr03 · cr04 | 62 · 22 · 19 · 18 · 14 | **62 · 22 · 19 · 18 · 14** |
| e2e-cr chromium | 9 + expected-fail 2 | **11 + expected-fail 2** · ล้ม 0 |
| e2e-legacy api+chromium (ผ่านจริง / ล้ม / test.fail) | 38 / 1 / 3 | **38 / 1 (TC-SEC-05 เดิม) / 3** |

### พฤติกรรมที่เปลี่ยนโดยตั้งใจ
- API ใหม่ 1 ตัว + error ใหม่ `REPORT_RANGE` · หน้าใหม่ `/admin/report` · เมนูเจ้าของร้านมี 2 ลิงก์ (หลังร้าน · รายงานยอด)
- ของเดิมไม่เปลี่ยน (คิวหลังร้าน `/api/admin/bookings` · การจอง · ราคา)

### ความเสี่ยงคงค้าง
- seed ไม่มีนัดที่วัน UTC ≠ วันไทย (ร้านเปิด 10:00–22:00) → บั๊กโซนเวลาแบบตัดวันตาม UTC เทสต์ด้วย seed จับได้ไม่หมด (มีเคสขอบ R9 เท่าที่ข้อมูลมี)
- ⏳ ตัดสินแทนร้าน (รอยืนยัน): ยอดขายรวมค่ารถ · แต้ม = `booking.points_earned` · ครั้งคอร์ส = นัดคอร์สที่ใช้บริการแล้ว · หมอนวดแสดงทุกคนรวม 0 · ช่วงเริ่มต้น = เดือนนี้ · CSV เงิน `1900.00` ชื่อบริการภาษาไทย · ยอดนัดยืนยันรวมนัดที่เลยเวลาแต่ร้านยังไม่กดเสร็จ
- นัดที่ร้านลืมกด "ใช้บริการเสร็จ" จะไม่อยู่ในยอดขาย (อยู่ในยอดนัดยืนยันแทน)

### วิธีถอยกลับ
`git revert` commit "CR-05: รายงานยอด + CSV" → `docker compose -f web/compose.yaml up -d --build --wait` · ไม่มี migration · ไม่มีข้อมูลที่ถูกเขียน
