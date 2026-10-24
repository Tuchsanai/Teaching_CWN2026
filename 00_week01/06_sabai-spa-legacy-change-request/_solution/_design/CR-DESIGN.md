# CR-DESIGN · Change Request ของบท 06 + การตัดสินเรื่องบั๊ก + เส้นทาง LAB

> สำหรับผู้สอน · อ้างอิงโค้ดและผลรันใน `CODEBASE-NOTES.md` (ย่อว่า **CN**)
> "วันนี้" ของระบบในทุกเกณฑ์ = `2026-10-10T10:00:00+07:00` (ค่า reset เริ่มต้น) เว้นแต่ระบุ `now=` · ปี พ.ศ. 2569 = ค.ศ. 2026
> ค่าที่คาดหวังของ CR = **คำนวณจากกฎใหม่ (ยังไม่ได้ implement/รัน)** · ค่าที่บอกพฤติกรรมปัจจุบันมาจากการรันจริง (CN §7)

เนื้อเรื่อง: ระบบจองคิวของร้านใช้งานจริงมาแล้ว ผู้รับเหมาเดิม (บท 04) ส่งมอบโค้ด + SPEC + ชุดตรวจ `check-rules.mjs` (เขียว 90/90) แล้วหมดสัญญา · คุณจันทร์จ้างทีมใหม่ (ผู้เรียน + Claude Code) ส่ง "หนังสือขอเปลี่ยนแปลงระบบ" มาทีละฉบับ · ผู้เรียนต้อง onboard → วิเคราะห์ผลกระทบ → สร้างตาข่ายกันพลาด → ให้ Agent แก้ → พิสูจน์ด้วย regression

---

## 1. Change Request 5 ฉบับ

ภาพรวม

| CR | ประเภท | เรื่อง | BR/FR หลัก | DB | ขนาด | ลำดับใน LAB |
|---|---|---|---|---|---|---|
| CR-02 | (b) เปลี่ยนกฎเดิม | ส่วนลดกลุ่มแบบขั้นบันได มีผล 1 พ.ย. | BR-06, BR-20 | — | S–M | LAB 6 |
| CR-03 | (c) บั๊กจากลูกค้าร้องเรียน | นัดซ้ำ 2 นัดจากการกดซ้ำ/เน็ตหลุด | BR-02, NFR-12, FR-03, FR-26 | — (advisory lock) | M | LAB 7 |
| CR-04 | (d) ต้อง migrate DB | วันหยุดร้าน (ตารางใหม่ + seed) | BR-01, BR-03, A2/Q19 | ตารางใหม่ `shop_holiday` | M (+ ส่วน b = L) | LAB 8 |
| CR-01 | (a) ฟีเจอร์ใหม่ | ลูกค้าเลื่อนนัดเอง | BR-01–04, 07, 13, 14, FR-07 | — | L | LAB 9 |
| CR-05 | (e) รายงาน/หลังร้าน | รายงานยอดรายช่วงวัน + CSV | D3, NFR-17 | — | M | LAB 10 |

ลำดับใน LAB เรียงจากเล็ก → ใหญ่ (กฎ → บั๊ก → schema → ฟีเจอร์ → รายงาน) ไม่ใช่ตามเลข CR (เลข CR = ลำดับที่ร้านส่งมา)

---

### CR-01 · ขอให้ลูกค้าเลื่อนนัดเองได้ (ฟีเจอร์ใหม่)

> **หนังสือขอเปลี่ยนแปลงระบบ ฉบับที่ 1/2569** · วันที่ 12 ต.ค. 2569
> เรียน ทีมพัฒนาระบบ
>
> ทุกวันนี้ลูกค้าที่อยากเปลี่ยนวันต้อง "ยกเลิก" แล้วจองใหม่ บางคนยกเลิกแล้วรอบเดิมโดนคนอื่นจองไป หรือส่วนลดเดือนเกิดหายเพราะจองใหม่ไม่ทัน แล้วโทรมาต่อว่าร้าน ร้านอยากให้มีปุ่ม **"เลื่อนนัด"** ในหน้าบัญชีของลูกค้าค่ะ
>
> 1. เลื่อนได้เฉพาะนัดที่ยังไม่ได้ใช้บริการ และต้องเหลือเวลาก่อนนัด**เดิม** 24 ชม. ขึ้นไป (เหมือนกฎยกเลิก)
> 2. ใช้บริการเดิม แบบเดิม จำนวนคนเดิม **ราคาเดิม** ไม่ต้องคิดใหม่ (แต้ม บัตรของขวัญ ที่ใช้ไปแล้วก็คงเดิม)
> 3. วันใหม่ต้องอยู่ในช่วงที่จองได้ตามปกติ (พรุ่งนี้ถึงอีก 30 วัน) และเป็นรอบที่มีจริง
> 4. ต้องเป็น**นักบำบัดคนเดิม** (ลูกค้าเลือกคนนี้มา) ถ้าคนเดิมไม่ว่างก็ไม่ให้เลื่อนเวลานั้น ห้องคู่ก็ต้องว่าง
> 5. ถ้านัดนั้นใช้ส่วนลดเดือนเกิด ห้ามเลื่อนออกนอกเดือนเกิด · ถ้าจองด้วยคอร์ส ห้ามเลื่อนเลยวันหมดอายุคอร์ส
> 6. เลื่อนแล้วรอบเดิมต้องว่างให้คนอื่นจองได้ทันที
> 7. ลูกค้าเลื่อนได้เฉพาะนัดของตัวเอง ร้านยังใช้วิธีเดิม (ยกเลิกแล้วจองให้ใหม่)
>
> ขอบคุณค่ะ · จันทร์ (เจ้าของร้านสบายใจ สปา) โทร 02-123-4567

**สเปกที่ทีมตกลง (ผู้สอนเป็นคน "ตอบคำถาม" ถ้าผู้เรียนถาม):** `POST /api/bookings/:id/reschedule {date, time}` → 200 `{ok, code, date, time, endTime, therapists[], total}` · `GET /api/bookings/:id/reschedule-slots?date=` → รอบที่**นักบำบัดคนเดิม (และห้องเดิม) ว่าง โดยไม่นับนัดตัวเอง** · หน้า `/account`: ปุ่ม `reschedule-{code}` (กดไม่ได้เมื่อ < 24 ชม.) → `reschedule-dialog` · `reschedule-date` · `reschedule-slot-{HH:MM}` · `reschedule-confirm` · ผล `reschedule-done` "เลื่อนนัด {code} เป็น {วันที่} {เวลา} แล้ว" · error ใหม่ 3 ภาษา: `RESCHEDULE_TOO_LATE` (+phone), `RESCHEDULE_NOT_ALLOWED`, `RESCHEDULE_BIRTHDAY`, `RESCHEDULE_SAME`

**เกณฑ์ยอมรับ (ค่าขอบจาก seed)**

| AC | ทำ | ผลที่ต้องได้ | ทดสอบอะไร |
|---|---|---|---|
| 1 | U01 เลื่อน B05 (S05 11 ต.ค. 10:00 T04) → 12 ต.ค. 10:00 | 200 · `total` 760 (เท่าเดิม) · `/api/slots` S05 11 ต.ค. 10:00 มี T04 · guest จอง S05 12 ต.ค. 10:00 `therapists:["T04"]` → 409 `SLOT_TAKEN` | ย้ายทั้ง `booking` และ `booking_slot` |
| 2 | เหมือนข้อ 1 ที่ `now=2026-10-10T10:00` / `10:01` | 200 / 422 `RESCHEDULE_TOO_LATE` + `phone` · B05 ยังเป็น 11 ต.ค. | ขอบ 24 ชม. พอดี (เหมือน E31/E32) |
| 3 | U01 เลื่อน B06 (วันนี้ 15:00) | 422 `RESCHEDULE_TOO_LATE` | |
| 4 | U02 เลื่อน B02 (คู่ S02 17 ต.ค. 19:00 T01+T02 ห้องคู่) → 17 ต.ค. 19:30 | **200** (ช่วงใหม่ทับช่วงเดิมของตัวเอง ต้องไม่นับเป็นชน) | กับดัก self-overlap ทั้ง `booking_slot` และ `booking_room_no_overlap` |
| 5 | U04 เลื่อน B01 (S01 T03) → 13 ต.ค. 10:00 / 14 ต.ค. 16:00 | 200 / 409 `SLOT_TAKEN` (T03 ติด B04) | นักบำบัดคนเดิม |
| 6 | `reschedule-slots` ของ B01 วันที่ 14 ต.ค. เทียบ `/api/slots?service=S01&date=2026-10-14&type=single` | รายการของ B01 **ไม่มี 16:00** ขณะที่ `/api/slots` มี 16:00 ว่าง (T06 — เหมือน E21) | ห้ามใช้ `/api/slots` เดิมตรง ๆ |
| 7 | U01 เลื่อน B05 → 9 พ.ย. 10:00 / 10 พ.ย. 10:00 | 200 / 422 `DATE_OUT_OF_RANGE` | BR-03 +30/+31 |
| 8 | U01 เลื่อน B05 → 11 ต.ค. 21:00 / 21:30 | 200 / 422 `SLOT_INVALID` | BR-01 จบ 22:00 พอดี |
| 9 | U01 เลื่อน B05 → 11 ต.ค. 10:00 (เวลาเดิม) | 422 `RESCHEDULE_SAME` | |
| 10 | U02 เลื่อน B05 (ของ U01) · ไม่ล็อกอิน · owner เลื่อน B05 | 403 `FORBIDDEN` · 401 · 403 | สิทธิ์ |
| 11 | U05 เลื่อน B07 (completed) | 422 `RESCHEDULE_NOT_ALLOWED` | |
| 12 | U02 จอง S01 31 ต.ค. 10:00 `useBirthday` (฿800) → เลื่อนไป 1 พ.ย. / 30 ต.ค. | 422 `RESCHEDULE_BIRTHDAY` / 200 ยอด ฿800 · `birthday_use` ยังเป็น 202610 แถวเดียว | BR-13 |
| 13 | U07 (C02 เหลือ 1 ครั้ง หมด 20 ต.ค.) จองคอร์ส 19 ต.ค. 10:00 → เลื่อน 20 ต.ค. / 21 ต.ค. | 200 / 422 `COURSE_UNAVAILABLE` · `/api/wallet` C02 `reserved` = 1 (ไม่ใช่ 2) `remaining` 0 | กับดัก "ยกเลิก+จองใหม่" จะเช็กคอร์สแล้วเหลือ 0 |
| 14 | U04 จองแบบ E87 (แต้ม 200 + H04) → เลื่อน | แต้มคงเหลือ 50 เท่าเดิม · `point_txn` ไม่มีแถวใหม่ | ราคา/แต้มไม่คิดใหม่ |
| 15 | UI: U01 `/account` → `reschedule-B05` → เลือก 12 ต.ค. 10:00 → ยืนยัน → รีโหลด | แถว B05 แสดง 12 ต.ค. 10:00–11:00 · ปุ่มของ B06 disabled | Playwright |

| หัวข้อ | รายละเอียด |
|---|---|
| BR/FR ที่กระทบ | BR-01, 02, 03, 04, 07, 13, 14 · FR-07, FR-17 · NFR-12 (กดพร้อมกัน), NFR-17 (ราคาไม่เปลี่ยน) |
| ไฟล์ที่คาด | ใหม่ `app/api/bookings/[id]/reschedule/route.ts`, `.../reschedule-slots/route.ts` · `lib/server/booking.ts` (`rescheduleBooking()`, ปรับ `busySlots`/`roomBusy` ให้รับ `excludeBookingId`) · `lib/rules/cancel.ts` (ใช้ `canCancel` ซ้ำหรือเปลี่ยนชื่อเป็น `canChange`) · `components/MyBookings.tsx` (+ dialog) · `lib/server/customer.ts` (`canReschedule` ใน `myBookings`) · `lib/i18n.ts` · `SPEC.md` |
| ตาราง | `booking` (UPDATE `start_at`,`end_at` → `period` GENERATED ขยับเอง) · `booking_slot` (UPDATE `period` **ต้องทำเอง**) · ไม่มีคอลัมน์ใหม่ |
| ความเสี่ยง regression | E30–E33 (กฎ 24 ชม.), E31 (รอบว่างหลังเปลี่ยน), E53–E56 (เดือนเกิด), E58–E63 (ครั้งคอร์ส), E14/BOOK-06 (กดพร้อมกัน), CXL-01–03 · แชทไม่กระทบ |
| ขนาด | **L** (~250–400 บรรทัดรวม UI + เทสต์) |

---

### CR-02 · ปรับส่วนลดกลุ่มเป็นขั้นบันได (เปลี่ยนกฎเดิม)

> **หนังสือขอเปลี่ยนแปลงระบบ ฉบับที่ 2/2569** · วันที่ 12 ต.ค. 2569
> เรียน ทีมพัฒนาระบบ
>
> ช่วงไฮซีซันร้านอยากดึงกลุ่มเล็กและกลุ่มใหญ่ให้มากขึ้น ขอเปลี่ยนส่วนลดกลุ่มเป็นแบบนี้ค่ะ
>
> | จำนวนคน (จองกลุ่ม) | ส่วนลด |
> |---|---|
> | 3 คน | 5% |
> | 4 คน | 10% (เท่าเดิม) |
> | 5–6 คน | 15% |
>
> - **ใช้กับการจองที่ทำตั้งแต่วันที่ 1 พ.ย. 2569 เป็นต้นไป** นัดที่จองไว้ก่อนหน้านั้นราคาเดิม ไม่ต้องไปแก้
> - กฎอื่นเหมือนเดิม: ส่วนลดหลายอย่างให้เลือกอันที่ลดมากที่สุดอันเดียว แพ็กเกจ Bangkok Relax ไม่มีส่วนลดกลุ่ม 7 คนขึ้นไปโทรหาร้าน
>
> จันทร์

**ประเด็นที่ผู้เรียนต้องถาม/ตีความ:** "วันที่จอง" = วันนี้ของระบบตอนกดจอง (`clock()`) ไม่ใช่วันนัด · ปี 2569 → 2026 · ส่วนลดเท่ากัน (กลุ่ม 5% = Gold 5%, กลุ่ม 4 คน 10% = Platinum 10%) ใช้ลำดับเดิม กลุ่ม → ระดับ → เดือนเกิด

**เกณฑ์ยอมรับ** (กลุ่ม S01 วันที่ 5 พ.ย. 10:00 · `now=2026-11-01T10:00` เว้นแต่ระบุ)

| AC | ทำ | ผลที่ต้องได้ |
|---|---|---|
| 1 | U08 (Silver) กลุ่ม 2 / 3 / 4 / 5 / 6 / 7 คน | 422 `GROUP_TOO_SMALL` / **฿2,850** / ฿3,600 / **฿4,250** / **฿5,100** / 422 `GROUP_CALL_SHOP` + phone |
| 2 | U01 (Gold 5%) กลุ่ม 3 | ฿2,850 `discountKind: "group"` (เท่ากัน → กลุ่มก่อน) |
| 3 | U02 (Platinum 10%) กลุ่ม 3 / 4 / 5 | ฿2,700 `tier` / ฿3,600 `group` / ฿4,250 `group` |
| 4 | U08 กลุ่ม 6 + H04 (12 กม. 2 คัน) | ฿5,100 + ฿600 = **฿5,700** (เดิม ฿6,000 ใน E79) |
| 5 | U08 แพ็กเกจ P01 4 คน | ฿11,600 `discountAmount` 0 (ไม่เปลี่ยน) |
| 6 | U08 กลุ่ม 3 ที่ `now=2026-10-31T23:59` / `2026-11-01T00:00` | ฿3,000 / ฿2,850 (ขอบวันมีผล) |
| 7 | ขอราคาที่ `now=10-31T23:59` (฿3,000) → reset `now=11-01T00:00` → จองด้วย `quotedTotal: 3000` | 409 `PRICE_CHANGED` `total: 2850` |
| 8 | reset `now=2026-11-01` → ตารางคิว 14 ต.ค. | B04 (กลุ่ม 5 คน จอง 8 ต.ค.) ยังเป็น ฿4,500 |
| 9 | `check-rules.mjs` ทั้งชุด (now = 10 ต.ค.) | **90/90 โดยไม่แก้ค่าคาดหวังเดิมสักตัว** (E26 ฿3,000 · E28 ฿4,500 · E79 ฿6,000 = อัตราเดิมก่อนวันมีผล) · เคสใหม่ E91+ สำหรับอัตราใหม่ |

| หัวข้อ | รายละเอียด |
|---|---|
| BR/FR | BR-06 (เปลี่ยน), BR-20 (ลำดับเดิม), BR-19/A15 (แพ็กเกจยกเว้น) · REQUIREMENTS + TEST-DATA ต้องแก้แถว BR-06 |
| ไฟล์ที่คาด | `lib/rules/pricing.ts` (`GROUP_PCT` → `groupPct(people, bookedOn)`, `bestPercent`/`calcPrice` รับ `bookedOn`) · `lib/server/booking.ts` `buildQuote()` ส่ง `today` · `scripts/check-rules.mjs` (เพิ่มเคส) · `SPEC.md` §4 · ตรวจ `i18n.ts` (label ใช้ `{p}%` อยู่แล้ว ไม่ต้องแก้) · แชทได้ผลอัตโนมัติ (ใช้ `buildQuote`) |
| ตาราง | ไม่มี (ไม่ต้องย้อนแก้ `booking.discount_pct` ของนัดเก่า) |
| ความเสี่ยง regression | **unit test E45/E50/E71 เรียก `R.calcPrice({...})` โดยไม่มี `bookedOn`** → ถ้าค่า default ผิด (เช่น `undefined` แล้วไปใช้อัตราใหม่หรือ throw) เคส unit พัง · E84–E88 (กลุ่ม 4 คน) · TC-PRICE-01, BOOK-08, BOOK-09 ของ e2e (ผูกกับวันที่ 10 ต.ค. จึงยังผ่าน) |
| ขนาด | **S–M** (~30–60 บรรทัด + เคสใหม่ ~10) |

---

### CR-03 · ลูกค้าโดนจองซ้ำ 2 นัด (แก้บั๊กจากเรื่องร้องเรียน)

> **หนังสือขอเปลี่ยนแปลงระบบ ฉบับที่ 3/2569 (ด่วน)** · วันที่ 12 ต.ค. 2569
> เรียน ทีมพัฒนาระบบ
>
> เมื่อวานมีลูกค้าร้องเรียนค่ะ คุณสมชายจองนวดผ่านมือถือ เน็ตค้างเลยกดใหม่ ได้ข้อความจองสำเร็จ 2 รหัส ร้านเห็นในตารางคิวเป็น 2 นัด จัดหมอนวดไว้ 2 คน เสียคิวไปหนึ่งคิว อีกรายจองผ่านแชทแล้วมาจองหน้าเว็บซ้ำเวลาเดียวกันก็ได้อีกนัด
>
> ร้านขอว่า **คนเดียวกันต้องไม่มีนัดที่เวลาทับกัน** ถ้าจองซ้ำให้ขึ้นข้อความบอกว่ามีนัดอยู่แล้ว พร้อมรหัสนัดเดิม (ถ้ามาหลายคนให้จองแบบคู่หรือกลุ่มอยู่แล้วค่ะ)
> "คนเดียวกัน" คือบัญชีสมาชิกเดียวกัน หรือถ้าไม่ได้สมัครสมาชิกก็ดูจากเบอร์โทร (บางคนพิมพ์มีขีด บางคนไม่มีขีด)
>
> จันทร์

**ทีมตกลง:** สมาชิก → เทียบ `customer_id` · ไม่ล็อกอิน → เทียบ `guest_phone` ที่ normalize เป็นตัวเลขล้วน · "ทับกัน" = `[start,end)` overlap กับนัดสถานะ ≠ cancelled (ต่อกันพอดีจองได้ เหมือน BR-02) · error `DUPLICATE_BOOKING` 409 `{existing: "B03"}` ข้อความ th "คุณมีนัดในช่วงเวลานี้อยู่แล้ว (รหัส {code})" / en "You already have a booking at this time (code {code})" / zh "您在该时段已有预约（预约号 {code}）" · ตรวจในเซิร์ฟเวอร์ (เว็บ + แชทได้พร้อมกัน) ไม่ใช่แค่ปิดปุ่ม

**สภาพปัจจุบัน [รันจริง CN §7 L1]:** guest ส่งคำขอเดิม 3 ครั้ง → 201 ทั้ง 3 (B14 T01, B15 T02, B16) · UI กดสองครั้งไม่ซ้ำเพราะปุ่ม `disabled={busy}`

**เกณฑ์ยอมรับ**

| AC | ทำ | ผลที่ต้องได้ |
|---|---|---|
| 1 (ทำซ้ำเรื่องร้องเรียน) | guest `contactPhone "0810000003"` (= B03 คุณสมชาย 081-000-0003, S02 13 ต.ค. 10:00–11:30) จอง S02 13 ต.ค. 10:00 | 409 `DUPLICATE_BOOKING` `existing: "B03"` · ตารางคิว 13 ต.ค. ยังมี 1 นัด (ก่อนแก้ = 201 ได้นัดที่ 2 กับนักบำบัดคนอื่น) |
| 2 | เบอร์เดียวกัน S01 13 ต.ค. 11:00 / S02 13 ต.ค. 11:30 | 409 (ทับ 11:00–11:30) / 201 (ต่อกันพอดี) |
| 3 | เบอร์อื่น `0899999999` S02 13 ต.ค. 10:00 | 201 (คนละคน) |
| 4 | U04 (B01 S01 12 ต.ค. 14:00–15:00) จอง S05 12 ต.ค. 14:30 / 15:00 / 13:00 | 409 / 201 / 201 |
| 5 | guest ใช้เบอร์ `081-111-0004` (เบอร์ของ U04) จอง 12 ต.ค. 14:00 | 201 (สมาชิกเทียบด้วยบัญชี guest เทียบกับ guest_phone เท่านั้น — ตามที่ตกลง) |
| 6 | U02 (B02 คู่ 17 ต.ค. 19:00–20:30) จองเดี่ยว S01 17 ต.ค. 20:00 | 409 `existing: "B02"` |
| 7 | `now=2026-10-10T09:59` U01 ยกเลิก B05 แล้วจอง S05 11 ต.ค. 10:00 ใหม่ | 201 (นัดที่ยกเลิกไม่นับ) |
| 8 | U03 ส่งคำขอเดียวกัน 2 ครั้งพร้อมกัน (S01 20 ต.ค. 10:00 ไม่ระบุนักบำบัด) | สถานะ `[201, 409]` · คิว 20 ต.ค. ของ U03 = 1 นัด |
| 9 | guest เบอร์เดียวกัน 2 คำขอพร้อมกัน | `[201, 409]` (guest ไม่มีแถว customer ให้ล็อก → ต้องมี lock อื่น เช่น `pg_advisory_xact_lock(hashtext(phone))`) |
| 10 | แชท: guest จองผ่านแชทซ้ำกับ B03 | คำตอบแชทมีข้อความ DUPLICATE_BOOKING ภาษาเดียวกับที่ถาม |
| 11 | UI: ขั้น 4 ยืนยันนัดที่ซ้ำ | `book-error` `data-error-code="DUPLICATE_BOOKING"` แสดงรหัสนัดเดิม |
| 12 | `check-rules.mjs` | ยังผ่านทุกข้อ (คาดการณ์จากการอ่าน: ไม่มีเคสที่คนเดิมจองทับตัวเองแล้วคาดหวัง 201 — ต้องยืนยันด้วยการรัน) |

| หัวข้อ | รายละเอียด |
|---|---|
| BR/FR | BR-02 (นิยาม overlap เดียวกัน), NFR-12, FR-03, FR-26 (แชท), NFR-17 · บันทึกเป็นกฎใหม่ BR-21 |
| ไฟล์ที่คาด | `lib/server/booking.ts` `createBooking()` (ตรวจหลัง `buildQuote(lock=true)` ซึ่งล็อกแถว customer อยู่แล้วสำหรับสมาชิก + advisory lock สำหรับ guest) · ใหม่ `lib/rules/phone.ts` (`normalizePhone`) · `lib/i18n.ts` · `components/BookingWizard.tsx` (แสดงรหัสเดิม — ErrorBox เดิมใช้ได้) · `SPEC.md` §5–6 |
| ตาราง | ไม่ต้อง migrate · (ทางเลือก) index `booking (guest_phone)` |
| ความเสี่ยง regression | E14/BOOK-06 (กดพร้อมกันคนละคน ต้องยังได้ 201+409 `SLOT_TAKEN` ไม่ใช่ `DUPLICATE_BOOKING`), E19–E25 (คู่/กลุ่ม), E90 · deadlock ถ้าลำดับล็อกไม่คงที่ |
| ขนาด | **M** (~60–100 บรรทัด + เทสต์ที่ "แดงก่อนแก้") |

---

### CR-04 · วันหยุดร้าน (ต้อง migrate ฐานข้อมูล)

> **หนังสือขอเปลี่ยนแปลงระบบ ฉบับที่ 4/2569** · วันที่ 12 ต.ค. 2569
> เรียน ทีมพัฒนาระบบ
>
> ตอนทำระบบครั้งแรก ทีมเดิมถามว่าวันหยุดนักขัตฤกษ์ร้านเปิดไหม ตอนนั้นยังไม่ได้ตอบ ตอนนี้ขอแจ้งว่า **ร้านปิดบางวัน** ค่ะ ปีนี้ปิด
>
> - 23 ต.ค. 2569 วันปิยมหาราช
> - 5 ธ.ค. 2569 วันพ่อแห่งชาติ
> - 31 ธ.ค. 2569 วันสิ้นปี
>
> วันที่ร้านปิดต้องจองไม่ได้ทุกช่องทาง (หน้าเว็บ แชท จองด้วยคอร์ส) และขึ้นข้อความบอกลูกค้าว่าร้านหยุดวันอะไร
> **ข้อมูลลูกค้าและนัดที่มีอยู่ในระบบตอนนี้ห้ามหาย** (ระบบใช้งานจริงอยู่)
> ถ้าเป็นไปได้ ขอให้ร้านเพิ่ม/ลบวันหยุดเองได้ในหน้าหลังร้าน แต่ถ้าวันไหนมีลูกค้าจองไว้แล้ว ระบบต้องไม่ยอมให้ปิดวันนั้น (ร้านจะโทรเลื่อนลูกค้าก่อน)
>
> จันทร์

**ทีมตกลง:** ตารางใหม่ `shop_holiday (holiday_date DATE PK, name_th, name_en, name_zh)` · `GET /api/holidays` · error `SHOP_CLOSED` 422 th "วันนี้ร้านหยุด ({name}) กรุณาเลือกวันอื่น" / en "The shop is closed on this day ({name}). Please choose another date" / zh "本店当天休息（{name}），请选择其他日期" · ลำดับตรวจ: นอกช่วงวัน (`DATE_OUT_OF_RANGE`) ก่อน → วันหยุด → รอบเวลา · ไม่ขยายอายุคอร์ส/บัตร · ส่วน (b) หลังร้าน = `POST /api/admin/holidays {date,name}` / `DELETE /api/admin/holidays/:date`

**สิ่งที่ "ซ่อน" อยู่ (ผู้เรียนต้องหาเองตอนวิเคราะห์ผลกระทบ — CN §5, §7)**

| กับดัก | ถ้าพลาดจะเห็นอะไร |
|---|---|
| `db/init/*` รันเฉพาะ volume ว่าง → ระบบจริงต้องใช้ไฟล์ migration (`db/migrations/001_shop_holiday.sql` แบบ idempotent: `CREATE TABLE IF NOT EXISTS` + `INSERT … ON CONFLICT DO NOTHING`) | `docker compose up` แล้วไม่มีตาราง → 500 · หรือแก้ด้วย `down -v` = ข้อมูลลูกค้าหาย (ผิดข้อห้ามในหนังสือ) |
| `lib/server/testmode.ts` `TABLES` ไม่มีตารางใหม่ | `/api/test/reset` → seed INSERT ชน PK → 500 → check-rules ล้มทั้งชุด |
| seed ต้องอยู่ใน `02-seed.sql` (reset อ่านไฟล์เดียวผ่าน `SEED_SQL_PATH`) | ใส่ไฟล์ `03-holiday.sql` แล้ว reset ไม่มีวันหยุด |
| `01-schema.sql` ต้องมีตารางด้วย (ติดตั้งใหม่) | เครื่องใหม่ไม่มีตาราง |
| แชทจองผ่าน `availableSlots`/`createBooking` | ถ้าตรวจแค่ใน UI แชทยังจองได้ |

**เกณฑ์ยอมรับ**

| AC | ทำ | ผลที่ต้องได้ |
|---|---|---|
| 1 | `GET /api/holidays` | 3 แถว 2026-10-23, 2026-12-05, 2026-12-31 |
| 2 | `/api/slots?service=S01&date=2026-10-23&type=single` | 422 `SHOP_CLOSED` ข้อความมี "วันปิยมหาราช" |
| 3 | `/api/slots` S01 วันที่ 10-22 / 10-24 | 200 · 23 รอบ (ค่าปกติ [รันจริง: S01 23 รอบ สุดท้าย 21:00]) |
| 4 | `/api/price` และ `/api/bookings` วันที่ 10-23 (guest, U01 คอร์ส C01, กลุ่ม U08) | 422 `SHOP_CLOSED` ทุกแบบ · ไม่มีแถวใหม่ใน `booking` |
| 5 | วันที่ 2026-12-05 ที่ `now` ค่าเริ่ม / `now=2026-11-10T10:00` · 12-04, 12-06 ที่ `now=11-10` | 422 `DATE_OUT_OF_RANGE` / 422 `SHOP_CLOSED` · 200, 200 |
| 6 | UI `/book` เลือกวันที่ 23 ต.ค. | `book-error` `data-error-code="SHOP_CLOSED"` (wizard แสดง error จาก `/api/slots` อยู่แล้ว) · ไม่มีปุ่มรอบ |
| 7 | reset 2 ครั้งติด | ทั้ง 2 ครั้ง 200 · ยังมี 3 วันหยุด |
| 8 | รัน migration บน DB ที่มีข้อมูลอยู่ (หลังจองนัดใหม่ B14 ไว้ก่อน) 2 ครั้ง | ไม่ error · B14 ยังอยู่ · มี 3 วันหยุด |
| 9 | `check-rules.mjs` | 90/90 (ไม่มีเคสใช้วันที่ 10-23 / 12-05 / 12-31 — CN §6.1) |
| 10 (b) | owner เพิ่มวันหยุด 2026-10-14 / 2026-10-15 / 2026-10-10 (วันนี้) / 2026-10-09 | 409 `HAS_BOOKINGS` (B04 ยืนยันอยู่) / 201 แล้ว slots 10-15 → 422 / 422 / 422 |
| 11 (b) | owner ลบ 2026-10-15 · U01 เรียก POST/DELETE | 200 แล้ว slots 10-15 → 200 · 403 |

| หัวข้อ | รายละเอียด |
|---|---|
| BR/FR | BR-01 (เพิ่ม "ยกเว้นวันหยุด"), BR-03, BR-14 (คอร์ส), FR-01, FR-26 · ปิดสมมติฐาน A2/Q19 |
| ไฟล์ที่คาด | `db/init/01-schema.sql`, `db/init/02-seed.sql`, ใหม่ `db/migrations/001_shop_holiday.sql` · `lib/server/testmode.ts` · `lib/server/booking.ts` (`availableSlots`, `buildQuote`) · `lib/server/catalog.ts` (`listHolidays`) · ใหม่ `app/api/holidays/route.ts` (+ `app/api/admin/holidays/...`) · `lib/i18n.ts` · (b) `components/AdminQueue.tsx` หรือหน้าใหม่ · `SPEC.md` |
| ตาราง | ใหม่ `shop_holiday` |
| ความเสี่ยง regression | reset ทั้งระบบ (ทุกเทสต์), E15–E18 (BR-03 ลำดับ error), แชท, `/book` |
| ขนาด | **M** (ส่วน a) · **L** (รวมส่วน b หลังร้าน) |

---

### CR-05 · รายงานยอดสำหรับเจ้าของร้าน (หน้าหลังร้าน)

> **หนังสือขอเปลี่ยนแปลงระบบ ฉบับที่ 5/2569** · วันที่ 12 ต.ค. 2569
> เรียน ทีมพัฒนาระบบ
>
> สิ้นเดือนร้านต้องส่งตัวเลขให้นักบัญชี ตอนนี้ต้องนั่งเปิดตารางคิวทีละวันแล้วจดเอง ขอหน้า **รายงาน** ที่เลือกช่วงวันได้ (ไม่เกินครั้งละ 3 เดือน) และกดโหลดเป็นไฟล์ไปเปิดใน Excel ได้ ขอดู
>
> - จำนวนนัดแยกสถานะ (ยืนยัน / ใช้บริการแล้ว / ยกเลิก)
> - ยอดขายจากนัดที่ใช้บริการแล้ว แยกว่าจ่ายด้วยบัตรของขวัญเท่าไร ช่องทางอื่นเท่าไร และส่วนลดแต่ละแบบรวมเท่าไร
> - แต้มที่ให้ลูกค้าไป · จำนวนครั้งคอร์สที่ใช้ · ยอดของนัดที่ยังไม่มา
> - หมอนวดแต่ละคนทำไปกี่คิว
>
> เห็นได้เฉพาะเจ้าของร้านนะคะ
>
> จันทร์

**ทีมตกลง:** นับตาม**วันนัด** (เวลาไทย) ช่วง `from`–`to` รวมปลาย · `GET /api/admin/report?from=&to=` → `{counts:{confirmed,completed,cancelled}, revenue, giftcardPaid, otherPaid, transportFee, discounts:{group,tier,birthday}, pointsEarned, courseSessions, pendingValue, byTherapist:[{code,completed}]}` (ยอดเงิน = นัด completed · `pendingValue` = นัด confirmed) · `&format=csv` → `text/csv; charset=utf-8` มี BOM · แถวละ 1 นัด เรียงตามเวลา หัวคอลัมน์ `date,code,status,type,people,service,total,giftcard_paid,other_paid,discount_kind,discount_amount,points_earned` · ช่วงเกิน 92 วัน หรือ from > to → 422 · หน้า `/admin/report` testid `report-from` `report-to` `report-run` `report-revenue` `report-count-{status}` `report-csv` + ลิงก์ `nav-admin-report`

**เกณฑ์ยอมรับ** (ตัวเลขจาก seed — **[รันจริง: SQL บน seed, CN §2]**)

| AC | ทำ | ผลที่ต้องได้ |
|---|---|---|
| 1 | 2026-09-01 ถึง 2026-09-30 | completed 3 · cancelled 1 · confirmed 0 · `revenue` 1900 · `otherPaid` 1900 · `discounts.tier` 100 · `pointsEarned` 19 · `courseSessions` 2 · `byTherapist` T01 1, T03 1, T05 1 (คนอื่น 0) |
| 2 | 2026-10-01 ถึง 2026-10-31 | completed 1 (B07) · confirmed 6 · `revenue` 1440 · `discounts.birthday` 360 · `pointsEarned` 14 · `pendingValue` 11130 |
| 3 | 2026-10-05 ถึง 2026-10-05 / 10-06 ถึง 10-09 | B07 เท่านั้น / ทุกค่า 0 (200 ไม่ใช่ error) |
| 4 | owner กด "ใช้บริการเสร็จ" B06 แล้วดู 10-10 ถึง 10-10 | completed 1 · `revenue` 950 · `pointsEarned` 9 |
| 5 | 2026-08-01 ถึง 2026-10-31 / ถึง 2026-11-01 / from 10-31 to 10-01 | 200 (92 วัน) / 422 (93 วัน) / 422 |
| 6 | CSV ช่วง 2026-09 | หัวคอลัมน์ตรงตามข้างบน + 4 แถว (B10, B11, B12, B13) · ไฟล์ขึ้นต้น BOM |
| 7 | U01 / ไม่ล็อกอิน | 403 / 401 |
| 8 | NFR-17: `revenue` = Σ `total_amount` ในตารางคิวของนัด completed ทุกวันในช่วง | เท่ากัน |

| หัวข้อ | รายละเอียด |
|---|---|
| BR/FR | D3 (หลังร้าน), NFR-17, BR-09 (แต้ม), BR-14 (คอร์ส) |
| ไฟล์ที่คาด | `lib/server/admin.ts` (`reportFor`) · ใหม่ `app/api/admin/report/route.ts` · ใหม่ `app/admin/report/page.tsx` + component · `components/NavMenu.tsx` · `lib/i18n.ts` · `SPEC.md` |
| ตาราง | ไม่มี (อ่านอย่างเดียว) |
| ความเสี่ยง regression | ต่ำ · ระวังเรื่องโซนเวลา (นัด 00:00–07:00 UTC ตกวันผิด) และ NUMERIC → สตางค์ (`toSatang`) |
| ขนาด | **M** |

---

## 2. ตัดสินเรื่องบั๊กของระบบเดิม

### 2.1 `flags.ts` เปิดเผยคำตอบง่ายเกินไปไหม → **ใช่ สำหรับบท 06**

บท 04 ผู้เรียนเป็น "ผู้ทดสอบที่ห้ามอ่านเฉลย" → flag ซ่อนไว้ได้ แต่บท 06 **ให้ Agent อ่านทั้ง repo เป็นกิจกรรมหลัก** แล้วสิ่งต่อไปนี้จะโผล่ใน 5 นาทีแรกของ onboarding:

| ช่องทางรั่ว | ที่อยู่ | Agent เห็นอะไร |
|---|---|---|
| ชื่อ env + คอมเมนต์ | `lib/flags.ts` | getter 3 ตัวพร้อมคอมเมนต์ "นาทีเผื่อเก็บห้อง", "ลำดับขั้นหักส่วนลด", "ยอดที่ใช้เป็นฐานคิดแต้ม" + ค่าถูก/ผิดคู่กัน |
| สเปก | `SPEC.md` §1, §2 | "`1` = เปิดบั๊กที่ตั้งใจใส่ 3 ตัว (เฉลยใน `BUGS.md`)" |
| HTML | `app/layout.tsx` | `<html data-bug-mode="0">` (REA/HAR ก็เห็น) |
| ชุดตรวจ | `check-rules.mjs` `main()` | อ่าน `data-bug-mode` แล้วสลับโหมด unit test |
| เอกสารบท 04 | `04/_solution/web/BUGS.md`, `BUG-HUNT.md`, `TEST-RUN-1.md` | เฉลยบั๊ก flag 3 ตัว + L1/L3/L4/L5 (อยู่ใน repo คอร์สเดียวกัน) |

และ "ระบบเดิมของหน่วยงานรัฐ" ที่มีสวิตช์เปิดบั๊กไม่สมจริง

### 2.2 ข้อตัดสิน

| เรื่อง | ตัดสิน | เหตุผล |
|---|---|---|
| `BUG_MODE` ในโค้ดบท 06 | **ถอดออกทั้งหมด** ค่าถูกต้องถาวร (diff §2.3) · `flags.ts` → `config.ts` เหลือ `allowTestReset` | กันรั่ว · baseline ชัด: `check-rules` 90/90 = "สิ่งที่ส่งมอบตามสัญญา" |
| บั๊กเทียม 3 ตัวของบท 04 | **ไม่อยู่ใน repo ผู้เรียน** → ย้ายเป็น *mutant patch* ใน `_solution/mutants/` (M1 buffer 1 นาที, M2 แต้มก่อน %, M3 แต้มจากราคาเต็ม) + เพิ่ม mutant ใหม่ที่ไม่เคยเฉลย (M4 `<= 5.0` → `< 5.0` ใน transport, M5 ปัดคะแนนรีวิวลง, M6 Gift Card หมดอายุ `>=`) | ใช้วัด "ตาข่าย" ที่ผู้เรียนสร้าง (LAB 5, ข้อสอบข้อ 2): เทสต์ที่ดีต้องแดงเมื่อ apply mutant |
| บั๊กจริงที่ไม่มี flag (CN §7 L1–L8) | **คงไว้ถาวร ไม่ใส่คอมเมนต์ ไม่ใส่ flag** | เหมือนระบบจริง: ชุดเทสต์เขียวแต่ยังมีบั๊ก · ผู้เรียนเจอผ่าน characterization/สำรวจ หรือผ่านหนังสือร้องเรียน |
| ใช้ L ตัวไหนที่ไหน | L1 → CR-03 · L5 → LAB 5 (บันทึกเป็น known issue ไม่แก้) · L4 → ข้อสอบชุด A ข้อ 5 · **L2 → ข้อสอบชุด B ข้อ 5** (ไม่มีในเอกสารบท 04 — grep แล้วไม่พบ) · L3 → งานเสริม (ต้องมีตาราง session) · L6 → ผูกกับ CR-03 (normalize เบอร์) · L7/L8 → หัวข้อคุยใน release notes | กระจายให้แต่ละ LAB มีของจริงให้เจอ · ข้อสอบชุด B ใช้บั๊กที่ไม่มีเฉลยเผยแพร่ |
| บั๊กเทียมเพิ่มใน repo | **ไม่เพิ่ม** | บั๊กจริงพอ · กับดัก regression (CN §7 ตารางล่าง) ทำหน้าที่ "ระเบิดเวลา" ให้ CR อยู่แล้ว |

### 2.3 Diff ที่เสนอ (ยังไม่ได้แก้ไฟล์จริง)

```diff
--- a/web/lib/flags.ts            (ลบไฟล์)
+++ b/web/lib/config.ts           (ไฟล์ใหม่)
+// ค่าตั้งของระบบที่อ่านจาก env จุดเดียว
+export const config = {
+  /** เปิด /api/test/*, นาฬิกาทดสอบ, บัญชีทดสอบหน้า login, ปุ่มรีเซ็ต /admin */
+  get allowTestReset(): boolean {
+    return (process.env.ALLOW_TEST_RESET ?? "1") === "1";
+  },
+};

--- a/web/lib/rules/slots.ts
+++ b/web/lib/rules/slots.ts
-import { flags } from "../flags.ts";
 import { minutesOf, timeOf } from "./time.ts";
@@
 function fitsDay(startMin: number, durationMin: number): boolean {
-  return startMin + durationMin <= CLOSE_MIN - flags.closingBufferMin;
+  return startMin + durationMin <= CLOSE_MIN;
 }

--- a/web/lib/rules/pricing.ts
+++ b/web/lib/rules/pricing.ts
-import { flags } from "../flags.ts";
@@
-  let running = gross;
-  let discountAmount = 0;
-  let pointsRedeemed = 0;
-  let pointsDiscount = 0;
-  for (const step of flags.priceSteps) {
-    if (step === "percent") {
-      discountAmount = percentOf(running, best.pct);
-      running -= discountAmount;
-    } else {
-      const r = redeemPoints(input.type === "course" ? 0 : input.redeemBlocks, input.points, running);
-      pointsRedeemed = r.blocks * 100;
-      pointsDiscount = r.discount;
-      running -= pointsDiscount;
-    }
-  }
-  const subtotal = running;
+  // ② ส่วนลด % → ③ หักแลกแต้ม
+  const discountAmount = percentOf(gross, best.pct);
+  const r = redeemPoints(input.type === "course" ? 0 : input.redeemBlocks, input.points, gross - discountAmount);
+  const pointsRedeemed = r.blocks * 100;
+  const pointsDiscount = r.discount;
+  const subtotal = gross - discountAmount - pointsDiscount;

--- a/web/lib/rules/points.ts
+++ b/web/lib/rules/points.ts
-import { flags } from "../flags.ts";
@@
 export function earnBase(b: EarnInput): number {
-  const net = flags.loyaltyBasis === "net" ? b.gross - b.discountAmount - b.pointsDiscount : b.gross - b.pointsDiscount;
-  return Math.max(0, net - b.giftcardPaid);
+  return Math.max(0, b.gross - b.discountAmount - b.pointsDiscount - b.giftcardPaid);
 }

--- a/web/app/layout.tsx
+++ b/web/app/layout.tsx
-import { flags } from "@/lib/flags.ts";
@@
-    <html lang={lang} data-ready="false" data-bug-mode={flags.bugMode}>
+    <html lang={lang} data-ready="false">

--- a/web/lib/clock.ts · app/admin/page.tsx · app/login/page.tsx · app/api/test/reset/route.ts · app/api/test/today/route.ts
-import { flags } from "@/lib/flags.ts";          (หรือ "./flags.ts" ใน clock.ts)
+import { config } from "@/lib/config.ts";
-flags.allowTestReset
+config.allowTestReset

--- a/web/compose.yaml
+++ b/web/compose.yaml
-      BUG_MODE: ${BUG_MODE:-0}

--- a/web/scripts/check-rules.mjs
+++ b/web/scripts/check-rules.mjs
-  // ให้ unit test ใช้โหมดเดียวกับเว็บที่กำลังตรวจ
-  const html = await fetch(`${BASE}/`).then((r) => r.text());
-  const mode = html.match(/data-bug-mode="(\d)"/)?.[1] ?? "0";
-  process.env.BUG_MODE = mode;
   R = await import("../lib/rules/index.ts");
-
-  console.log(`ตรวจกฎร้าน ${BASE} (BUG_MODE=${mode}) · ${cases.length} เคส\n`);
+  console.log(`ตรวจกฎร้าน ${BASE} · ${cases.length} เคส\n`);

--- a/web/SPEC.md
-# เปิดโหมดบั๊ก / ปิด
-$env:BUG_MODE = "1"; docker compose -f web/compose.yaml up -d --force-recreate
-$env:BUG_MODE = "0"; docker compose -f web/compose.yaml up -d --force-recreate
-| `BUG_MODE` | web | `0` | `1` = เปิดบั๊กที่ตั้งใจใส่ 3 ตัว (เฉลยใน `BUGS.md`) · อ่านผ่าน `lib/flags.ts` จุดเดียว |
-ทุกหน้ามี header … · `<html data-ready="true|false" data-bug-mode="0|1" lang="th|en|zh">`
+ทุกหน้ามี header … · `<html data-ready="true|false" lang="th|en|zh">`
```

ผลข้างเคียงที่ต้องรู้:
- ผลลัพธ์ตัวเลขเท่ากับ `BUG_MODE=0` เดิมทุกกรณี (refactor ล้วน) → **หลังแก้ต้องรัน check-rules ได้ 90/90** เป็นหลักฐาน
- e2e ของบท 04 ถ้าคัดลอกมาใช้: `global-setup.ts` จะได้ `bugMode '?'` → รายงานขึ้น "ไม่รู้โหมด" (ไม่ทำให้เทสต์ล้ม) → แก้ป้ายใน `build-report.mjs` หรือเอาออก
- ห้ามแก้บท 04 (BRIEF ข้อ 3) · diff นี้ใช้กับ `06/web` เท่านั้น
- `ORIGINAL-BUGS-ch04.md` ยังเก็บไว้ใน `_solution` และกลายเป็นที่มาของ mutant M1–M3

---

## 3. เส้นทาง LAB บท 06 (12 LAB)

สัญลักษณ์: 🔧 = แก้โค้ด/สคีมาของ repo เดิม · 📝 = เพิ่มไฟล์ทดสอบ/เอกสารใน repo เดิม (ไม่แตะโค้ดระบบ) · 👀 = อ่าน/รันอย่างเดียว
ผู้เรียนทำงานบนสำเนาของ `06/web` + `06/db` ในโฟลเดอร์ของตัวเอง แล้ว `git init` + commit baseline (เพื่อให้ทุก CR มี diff ให้รีวิว)

| LAB | ชื่อ | ผู้เรียนทำ (คัดลอกพรอมต์ → Claude Code) | ผลลัพธ์ | เทคนิค | ชนิด | เวลา |
|---|---|---|---|---|---|---|
| 1 | รับมอบระบบ | เปิด 2 compose project · health · `check-rules` · ตั้ง git baseline | `HANDOVER-CHECK.md` (90/90, เวลา, เวอร์ชัน) | smoke test, ตรวจของที่ส่งมอบ | 👀 | 30 นาที |
| 2 | Onboarding ด้วย Agent | ให้ Claude อ่าน repo แล้วอธิบาย: สถาปัตยกรรม, BR → ไฟล์, ตาราง, test hooks · ผู้เรียนสุ่มตรวจ 5 ข้อกับโค้ดจริง (file:line) | `docs/ONBOARDING.md` + ตาราง "AI บอก vs โค้ดจริง" | repo reading, จับ AI มั่ว | 📝 | 45 นาที |
| 3 | มองแบบ black-box ด้วย REA | `next build` → `rea analyze-javascript-application .next/static` · อัด HAR ของ flow จอง → `inspect-web-network-capture` · เทียบ endpoint ที่กู้ได้กับ SPEC §6 | `docs/REA-INVENTORY.md` (endpoint/API ที่ใช้จริงจากหน้าเว็บ) · `docs/SPEC-GAPS.md` (เทียบ CN §8) | REA (บท 05), HAR | 👀 | 45 นาที |
| 4 | CLAUDE.md ของระบบเดิม | เขียนกติกาให้ Agent: ห้ามแก้ค่าคาดหวังโดยไม่อ้าง CR, ต้องรัน regression, ห้าม `down -v`, migration ต้อง idempotent, แม่แบบ impact analysis, จุดกับดัก (CN §7) | `CLAUDE.md` + `docs/IMPACT-TEMPLATE.md` | context engineering | 📝 | 30 นาที |
| 5 | ตาข่ายกันพลาด (characterization) | golden master ของ `/api/price` (เมทริกซ์ผู้ใช้ × แบบจอง × แต้ม/บัตร/รถ), `/api/slots` ทุกบริการ, ตารางคิว · **เพิ่ม test seam** `POST /api/test/clock {now}` (เลื่อนนาฬิกาโดยไม่ล้างข้อมูล) · บันทึกพฤติกรรมแปลก (L5, L6, L7) เป็น known issue ไม่แก้ · ผู้สอนรัน mutant M1–M6 ให้ดูว่าตาข่ายจับได้กี่ตัว | `tests/golden/*.json`, `scripts/golden.mjs`, `KNOWN-ISSUES.md` | golden master, seam (Feathers), mutation | 🔧 📝 | 75 นาที |
| 6 | CR-02 เปลี่ยนกฎ | impact analysis ก่อน (ไฟล์, เทสต์, ข้อความ) → ให้ Agent แก้ → เคสใหม่ E91+ → ตรวจว่า E26/E28/E79 **ไม่ต้องแก้** (วันมีผล) · golden diff ต้องว่าง | `docs/impact/CR-02.md`, diff, เคสใหม่ | impact analysis, effective date, oracle hygiene | 🔧 | 60 นาที |
| 7 | CR-03 แก้บั๊กจากเรื่องร้องเรียน | เขียนเทสต์ทำซ้ำเรื่องร้องเรียน (ต้อง**แดง**ก่อน) → แก้ → เขียว · ทดสอบกดพร้อมกัน (AC 8–9) | เทสต์ `tests/cr03.spec` + diff + หลักฐาน แดง→เขียว | reproduce-first, concurrency | 🔧 | 60 นาที |
| 8 | CR-04 migration | ออกแบบตาราง → migration idempotent → รันบน DB ที่มีข้อมูลจริง (จองนัดไว้ก่อน) → seed/reset/TABLES → API/UI/แชท | `db/migrations/001_*.sql`, diff, `docs/MIGRATION-RUNBOOK.md` (+ rollback) | expand-migrate, data safety | 🔧 | 75 นาที |
| 9 | CR-01 ฟีเจอร์ใหม่ | แตกงานเป็นขั้น (API → slots เฉพาะคนเดิม → UI) ให้ Agent ทำทีละขั้น · เทสต์ AC 1–14 ด้วย API + AC 15 ด้วย Playwright | diff, `tests/cr01.*`, `e2e/reschedule.spec.ts` | incremental change, self-overlap | 🔧 | 90 นาที |
| 10 | CR-05 รายงาน | ค่าคาดหวังต้องมาจาก SQL บน seed (ไม่ใช่จากหน้าจอที่เพิ่งทำ) · CSV เปิดใน Excel ภาษาไทยไม่เพี้ยน | diff, `tests/cr05.*`, ไฟล์ CSV ตัวอย่าง | independent oracle | 🔧 | 60 นาที |
| 11 | Regression เต็มชุด | `check-rules` + golden + เทสต์ CR ทั้งหมด + e2e บท 04 ที่เกี่ยวข้อง · `rea compare-application-versions` bundle ก่อน/หลัง · ตาราง "ค่าคาดหวังที่เปลี่ยน → CR ที่อนุญาต" | `REGRESSION-REPORT.md` | regression, version diff | 📝 | 45 นาที |
| 12 | ส่งมอบ | release notes ภาษาคน (ให้คุณจันทร์อ่าน), UAT checklist ต่อ CR, ขั้นตอน deploy + migration + rollback, known issues ที่ยังเหลือ (L3, L7, L8) | `RELEASE-NOTES.md`, `UAT-CHECKLIST.md` | release management | 📝 | 30 นาที |

นับ: **แก้ repo เดิม 10/12 LAB** (🔧 6 LAB: 5–10 · 📝 อย่างเดียว 4 LAB: 2, 4, 11, 12) · อ่าน/รันอย่างเดียว 2 LAB (1, 3) · แก้**โค้ด**ระบบ 6/12 = ครึ่งหนึ่งพอดี · เวลารวม ~10.75 ชม. (แบ่ง 2 วัน)

สิ่งที่ต้องเตรียมในโฟลเดอร์บท 06 (งานถัดไป):

| ไฟล์ | เนื้อหา |
|---|---|
| `06/web`, `06/db` | ใช้ diff §2.3 (ถอด BUG_MODE) |
| `06/change-requests/CR-01..05.md` | เฉพาะ "หนังสือ" ในกรอบ quote ของ §1 (ไม่ใส่สเปกที่ตกลง/AC — ผู้เรียนต้องถามและเขียนเอง แล้วเทียบกับเฉลย) |
| `06/e2e` (ทางเลือก) | คัดลอกจาก `04/_solution/e2e` เป็น "ชุด regression ที่ผู้รับเหมาเดิมส่งมอบ" (ตัด test-report/ และ triage) |
| `06/_solution/` | เฉลยต่อ LAB + `mutants/M1..M6.diff` + implementation อ้างอิงของ CR ทั้ง 5 (ต้องรัน AC ทั้งหมดให้ผ่านจริงก่อนเผยแพร่) |
