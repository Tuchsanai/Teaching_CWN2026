# TEST PLAN — สบายใจ สปา (Sabai Jai Wellness Spa)

| หัวข้อ | รายละเอียด |
|---|---|
| เวอร์ชันเอกสาร | 1.0 · 2026-10-08 |
| อ้างอิง | `REQUIREMENTS.md` (FR-01–31, BR-01–25, NFR-01–15) · `spa/SPEC.md` |
| ไม่ได้อ้างอิง | `spa/BUGS.md` (ตั้งใจไม่เปิด เพื่อทดสอบแบบไม่รู้คำตอบล่วงหน้า) |
| หลักการ | ผลที่คาดหวังทุกข้อใช้ตัวเลขและข้อความจาก SPEC ถ้า SPEC ไม่ได้ระบุค่าไว้ จะเขียนว่า **"ต้องถาม"** และไม่เดาค่าเอง (รวบรวมไว้ในหัวข้อ 8) |

---

## 1. ระบบที่ทดสอบและขอบเขต

### 1.1 ระบบที่ทดสอบ

| รายการ | ค่า |
|---|---|
| ระบบ | เว็บจองสปา "สบายใจ สปา" (SPA 3 ภาษา: ไทย / English / 中文) |
| URL | http://localhost:3000 |
| เทคโนโลยี | Next.js 15 + PostgreSQL 16 (`pg`) |
| Container | `sabai-web` (port 3000) และ `sabai-db` (postgres:16-alpine) ทั้ง 2 ตัวมี healthcheck |
| เวลาร้าน | Asia/Bangkok (UTC+7) ล็อก "วันนี้" ได้ด้วย `POST /api/test/reset` |
| ผู้ใช้ทดสอบ (seed) | `nida@sabai.test` (Gold) · `ton@sabai.test` (Platinum, เกิดเดือนเดียวกับวันนี้) · `new@sabai.test` (Silver) รหัสผ่าน `Sabai1234!` |
| เบราว์เซอร์ | Chromium desktop 1280×800 และ mobile viewport 375×812 (Playwright) |
| โหมด | บันทึกค่า `<html data-bug-mode>` ลงในรายงานทุกรอบที่ทดสอบ |

### 1.2 ขอบเขต

| ทดสอบ | ไม่ทดสอบ (เหตุผล) |
|---|---|
| FR-01 ถึง FR-31 ทุกข้อ (ดูหัวข้อ 5) | การส่ง Gift Card จริงทาง LINE/email (SPEC: ส่งแบบจำลอง `sent:false`) |
| BR-01 ถึง BR-25 ทุกข้อ รวมค่าขอบ | การชำระเงินจริง (ไม่มี payment gateway ชำระที่ร้าน `price-due`) |
| NFR ที่วัดได้ในเครื่องทดสอบ: 01, 03, 04, 05, 06, 07, 08, 09, 12, 13, 14, 15 | Load / stress test และการวัดความเร็วบนเน็ต 4G จริง (NFR-02) ดูแค่ค่าที่สังเกตได้ |
| API ทุกเส้นใน SPEC §5 ทั้งกรณีปกติและ error | Safari / iPhone จริง (NFR-10) ทดสอบได้เฉพาะ Chromium **ต้องถาม** ว่าจะมีเครื่องจริงให้หรือไม่ |
| การกันจองชนเมื่อกดพร้อมกัน (NFR-06) | Security / penetration test เชิงลึก (ทดสอบแค่การเข้าถึงโดยไม่ login และข้อมูลข้ามบัญชี) |
| หน้า UI ทุกหน้าใน SPEC §1 ทั้ง desktop และ 375 px | การอนุมัติลวดลายและสีโดยเจ้าของร้าน (FR-21) ผู้ทดสอบตรวจได้แค่ว่ามีองค์ประกอบครบ |
| | ฝั่งหลังร้าน / admin dashboard (ไม่มีใน SPEC) |
| | การ build / deploy / ตั้งค่า Docker |

---

## 2. เทคนิคที่ใช้ (พร้อมตัวอย่างจากเว็บนี้)

| เทคนิค | ความหมาย | ตัวอย่างจากเว็บนี้ | TC |
|---|---|---|---|
| Happy path | ทำตามขั้นตอนปกติจนจบ | ลูกค้าทั่วไปจองนวดไทย 1 คน วันพรุ่งนี้ 10:00 จนเห็น `booking-success` และยอด ฿800 | TC-BOOK-01 |
| Negative | ใส่ค่าผิดหรือทำสิ่งที่ไม่อนุญาต ระบบต้องปฏิเสธพร้อมข้อความที่ถูกต้อง | Gift Card ฿499 → "มูลค่า Gift Card ต้องอยู่ระหว่าง ฿500–฿10,000" · 7 คน → "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567" · โรงแรม 15.1 กม. → "ไม่มีบริการรับส่งสำหรับระยะนี้" | TC-GIFT-01, TC-BOOK-06, TC-BOOK-07 |
| Boundary (ค่าขอบ) | ทดสอบค่าที่อยู่ตรงขอบทั้งสองฝั่ง | ยอดสะสม ฿9,999 Silver / ฿10,000 Gold · รอบ 21:00 ได้ / 21:30 ไม่ได้ (60 นาที) · +30 วันได้ / +31 ไม่ได้ · ยกเลิก 24 ชม. พอดีได้ / 23:59 ชม. ไม่ได้ · Gift Card วันที่ 365 / 366 · คอร์สวันที่ 180 / 181 · รีวิว 4.4 / 4.5 | TC-MEM-01, TC-BOOK-02, TC-BOOK-03, TC-DASH-02, TC-GIFT-02, TC-WAL-03, TC-THER-01 |
| Equivalence partitioning | แบ่งข้อมูลเป็นกลุ่มที่ระบบทำแบบเดียวกัน แล้วเลือกตัวแทนกลุ่มละ 1 ค่า | จำนวนคน: 0 (ไม่ถูกต้อง) / 1 (เดี่ยว) / 2 (คู่) / 3 (กลุ่มไม่ลด) / 4–6 (กลุ่มลด 10%) / ≥7 (โทรร้าน) · ระยะทาง: ≤5.0 ฟรี / 5.1–15.0 ฿300 / >15.0 ไม่รับ · ระดับ: Silver / Gold / Platinum | TC-BOOK-06, TC-BOOK-07, TC-MEM-01 |
| State (รีโหลด / ทำซ้ำ) | ดูว่าสถานะถูกต้องหลังรีโหลด ทำซ้ำ หรือย้อนกลับ | เลือก English แล้วรีโหลดยังเป็น English · ใช้ส่วนลดวันเกิดแล้วครั้งที่ 2 ต้องไม่มีตัวเลือก · ยกเลิกนัดแล้วรอบว่าง และยกเลิกซ้ำได้ "นัดนี้ถูกยกเลิกไปแล้ว" · จองด้วยคอร์ส 7 → 6 แล้วยกเลิกกลับเป็น 7 · กดยืนยันซ้ำต้องไม่เกิดการจอง 2 รายการ | TC-EXP-01, TC-MEM-04, TC-DASH-02, TC-WAL-01, TC-BOOK-04 |
| API | เรียก API ตรงด้วย curl / Playwright `request` ตรวจ status code, `error` code และ `message` | ไม่ login เรียก `GET /api/wallet` → 401 `LOGIN_REQUIRED` · ยิง `POST /api/bookings` 2 ครั้งพร้อมกัน → 201 หนึ่งครั้ง และ 409 `SLOT_TAKEN` หนึ่งครั้ง · `POST /api/quote` ตัวอย่างใน SPEC → `total: 3180` | TC-API-01, TC-API-02, TC-BOOK-06 |

---

## 3. ระดับความรุนแรง (Priority)

| ระดับ | นิยาม | ตัวอย่างในเว็บนี้ |
|---|---|---|
| **P1** | เงินผิด / จองไม่ได้ / จองซ้อน | ส่วนลดระดับหรือวันเกิดคิดผิด · ค่ารถผิด · แต้มหรือครั้งคอร์สหักผิด · ปุ่มจองใช้ไม่ได้ · ได้รอบที่ทับกับคิวเดิม |
| **P2** | ฟีเจอร์สำคัญทำงานผิดแต่ยังจองและจ่ายเงินได้ถูกต้อง | ตัวกรองรีวิวผิด · แชทตอบผิดภาษา · แบบทดสอบแนะนำผิด · แปลภาษาไม่ครบ · หน้าจอมือถือเลื่อนซ้าย–ขวาได้ |
| **P3** | เรื่องความสวยงาม หรือปัญหาที่เกิดไม่บ่อย | ลายไทยไม่แสดง · ทัวร์ 360° หมุนสะดุด · ปุ่มเพลงแสดงสถานะผิด |

---

## 4. Test Case

### 4.1 การเตรียมข้อมูล (ใช้ในคอลัมน์ "ข้อมูลที่ใช้")

| ย่อ | ความหมาย |
|---|---|
| **R0** | `POST /api/test/reset {"now":"2026-10-08T10:00:00+07:00"}` → today = 2026-10-08 (พฤ.) · จองได้ 2026-10-09 ถึง 2026-11-07 |
| **R(เวลา)** | reset ด้วยเวลาที่ระบุ เช่น R(2026-10-08T15:00:00+07:00) |
| **U{…}** | `POST /api/test/user {…}` ตั้งค่าสมาชิกก่อนทดสอบ แล้ว login ใหม่ |
| **L(nida)** | login `nida@sabai.test` / `Sabai1234!` (เช่นเดียวกับ ton, new) · **Guest** = ไม่ login กรอก `booking-guest-name`="Mei" `booking-guest-phone`="0812345678" |
| วันที่ | D+1 = 2026-10-09 · D+2 = 2026-10-10 (มีคิว seed: มาลี 14:00–15:00 และ Couple Suite 18:00–19:30) · D+3 = 2026-10-11 (อาทิตย์) · D+5 = 2026-10-13 (วันนวมินทรมหาราช วันหยุดนักขัตฤกษ์) · D+30 = 2026-11-07 · D+31 = 2026-11-08 |

ทุก TC เริ่มจาก R0 ยกเว้นที่ระบุไว้ต่างออกไป

### 4.2 ตาราง Test Case (33 ข้อ)

| ID | โมดูล | สิ่งที่ทดสอบ | FR/BR | ระดับ | ข้อมูลที่ใช้ | ผลที่คาดหวัง (ตัวเลข/ข้อความจริงจาก SPEC) |
|---|---|---|---|---|---|---|
| TC-HOME-01 | HOME | หน้าแรกแสดง hero ลายไทย และพาไปหน้าจองได้ | FR-21 | P3 | เปิด `/` | `hero` แสดงรูป `brand/hero.jpg` (โหลดสำเร็จ naturalWidth > 0) · มีส่วน `home-package`, `home-tour`, `home-therapists`, `home-gift`, `home-member` · กด `hero-book` ไปที่ `/book` · รูปทุกรูปมี `alt` ไม่ว่าง (NFR-11) · ลวดลายและสีตรงกับแบบที่เจ้าของร้านอนุมัติ: **ต้องถาม** (SPEC ไม่มีภาพต้นแบบที่อนุมัติแล้ว) |
| TC-HOME-02 | HOME | ทุกบริการแสดงสมุนไพรและคำเตือนการแพ้ | FR-22 | P2 | `/services`, `/services/herbal-compress`, `/book` เลือก `thai-massage` | `service-list` มี 9 บริการ ราคาและเวลาตรงตาราง SPEC §2.1 เช่น `service-price-thai-massage` ฿800 `service-duration-thai-massage` 60 นาที · `service-herbs-herbal-compress` มี `li[data-herb]` 4 รายการ (ไพล ขมิ้น ตะไคร้ มะกรูด) · `allergy-warning` = "ถ้าแพ้สมุนไพรชนิดใด กรุณาแจ้งร้านก่อนรับบริการ" · `/book` แสดง `booking-herbs` = ไพล และ `booking-allergy` |
| TC-MOOD-01 | MOOD | เลือกอารมณ์ 4 แบบ ได้คำแนะนำ 1–3 บริการตามกฎตายตัว | FR-25, BR-23 | P2 | `/mood` กด `mood-relax`, `mood-stressed`, `mood-tired`, `mood-sore` อย่างละ 10 ครั้ง | relax → `mood-rec-aroma-oil`, `mood-rec-foot-reflexology` (2) · stressed → aroma-oil, herbal-compress, coconut-rice-scrub (3) · tired → foot-reflexology, thai-massage, bangkok-relax (3) · sore → thai-massage, herbal-compress (2) · ลำดับถูกต้อง และได้ผลเดิม 10/10 ครั้ง (NFR-12) · กด `mood-book-aroma-oil` ไป `/book` (บริการถูกเลือกไว้ให้หรือไม่: **ต้องถาม**) |
| TC-BOOK-01 | BOOK | **E2E** จองคิวเดี่ยวจนจบ (Guest) | FR-01, FR-06 | P1 | R0 · Guest · `/` → `hero-book` → `service-option-thai-massage` (1 คน, นักบำบัด = ร้านจัดให้) → `cal-day-2026-10-09` → `slot-10-00` → กรอกชื่อ/เบอร์ → `booking-submit` | ใช้ 4 ขั้นจนถึงปุ่มยืนยัน (NFR-03) · `booking-end-time` = 11:00 · `price-subtotal` ฿800 · `price-total` ฿800 · `price-due` ฿800 · หลังกดยืนยันเห็น `booking-success` · `booking-code` รูปแบบ `SB` + ตัวเลข 5 หลัก (เลขจริง **ต้องถาม**) · `booking-success-total` ฿800 · `GET /api/availability?service=thai-massage&date=2026-10-09&people=1&therapistId=<นักบำบัดใน booking-success-therapists>` → 10:00 = `booked` |
| TC-BOOK-02 | BOOK | รอบเวลา: เปิด 10:00 ทุก 30 นาที และต้องจบไม่เกิน 22:00 (รวมวันอาทิตย์และวันหยุด) | FR-01, BR-01, BR-02, BR-03 | P1 | R0 · `/api/availability` และ `/book` วันที่ 2026-10-11 (อา.) และ 2026-10-13 (วันหยุด) · บริการ thai-massage (60), aroma-oil (90), bangkok-relax (120) | ไม่มีรอบ 09:30 · รอบแรก 10:00 · มี 10:30 ไม่มี 10:15 · รอบสุดท้ายที่แสดงคือ 21:30 · 60 นาที: `slot-21-00` = free, `slot-21-30` = closed (disabled) · 90 นาที: `slot-20-30` free, `slot-21-00` closed · 120 นาที: `slot-20-00` free, `slot-20-30` closed · ทั้งสองวันมีรอบให้จอง · `POST /api/bookings` เวลา 09:30 / 10:15 / thai-massage 21:30 → `TIME_INVALID` "รอบเวลานี้ไม่เปิดให้จอง (เปิด 10:00–22:00 ทุก 30 นาที และต้องเสร็จไม่เกิน 22:00)" |
| TC-BOOK-03 | BOOK | ปฏิทินกดได้เฉพาะ +1 ถึง +30 วัน รวมกรณีข้ามเดือน | FR-03, BR-05 | P1 | R0 แล้ว R(2026-10-31T10:00:00+07:00) | R0: `cal-day-2026-10-08` disabled · `cal-day-2026-10-09` กดได้ · `cal-day-2026-11-07` กดได้ · `cal-day-2026-11-08` disabled · `GET /api/config` → `bookable.from` "2026-10-09" `bookable.to` "2026-11-07" · `POST /api/bookings` date 2026-10-08 และ 2026-11-08 → `DATE_OUT_OF_RANGE` "จองได้ตั้งแต่พรุ่งนี้ถึง 30 วันข้างหน้าเท่านั้น" · R(10-31): `cal-day-2026-11-30` กดได้ · `cal-day-2026-12-01` disabled |
| TC-BOOK-04 | BOOK | **จองซ้อน**: นักบำบัด 1 คนรับ 1 คิว (ขอบชนพอดีจองได้) และกดยืนยันซ้ำ | FR-02, BR-04 | P1 | R0 · thai-massage 1 คน · `booking-therapist` = 1 (มาลี) · วันที่ 2026-10-10 (มีคิว 14:00–15:00) | `slot-13-30`, `slot-14-00`, `slot-14-30` = `booked` · `slot-13-00` และ `slot-15-00` = `free` · กดรอบที่เต็ม → `slot-error` "เวลานี้ถูกจองแล้ว" · API จอง 14:30 → 409 `{"ok":false,"error":"SLOT_TAKEN","message":"เวลานี้ถูกจองแล้ว"}` · จอง 13:00 และ 15:00 → 201 ทั้งคู่ · จอง 15:00 ซ้ำ → 409 `SLOT_TAKEN` · UI กด `booking-submit` 2 ครั้งติดกัน → เกิดการจองแค่ 1 รายการ |
| TC-BOOK-05 | BOOK | จองคู่ 2 คนพอดี และ **Couple Suite ซ้อน** | FR-04, FR-02, BR-06 | P1 | R0 · aroma-oil (90 นาที) · วันที่ 2026-10-10 (Couple Suite มีคิว 18:00–19:30) | จำนวนคน 2 → `booking-kind-couple` กดได้ · 1 และ 3 คน → disabled · `slot-17-00`, `slot-18-00` = `booked` · `slot-16-30` และ `slot-19-30` = `free` · จอง 18:00 → 409 "เวลานี้ถูกจองแล้ว" · จอง 19:30 → 201 `room` = "couple-suite", `therapists` มี 2 คน, เริ่มพร้อมกัน, `endTime` 21:00 · คู่ที่ 2 จอง 19:30 ซ้ำ → 409 `SLOT_TAKEN` |
| TC-BOOK-06 | BOOK | จำนวนคน: คู่ / กลุ่ม 3–6 / ≥7 โทรร้าน และส่วนลดกลุ่ม 10% | FR-05, FR-06, BR-07, BR-08 | P1 | R0 · Guest · thai-massage ฿800 · จำนวนคน 0, 2, 3, 4, 6, 7 · `POST /api/quote` body ตัวอย่างใน SPEC §5 | 2 คน → `booking-kind-group` disabled · 3 คน กลุ่มได้ ไม่ลด `price-total` ฿2,400 · 4 คน `price-group-discount` −฿320 → ฿2,880 · 6 คน −฿480 → ฿4,320 · 7 คน → `booking-group-error` "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567" และจองไม่ได้ (API → `GROUP_TOO_LARGE`) · 0 คน → `PEOPLE_INVALID` "กรุณาระบุจำนวนคนให้ถูกต้อง" · quote ตัวอย่าง → `subtotal` 3200, `groupDiscount` 320, `transportFee` 300, `cars` 1, `total` 3180, `due` 3180 |
| TC-BOOK-07 | BOOK | ค่ารถตามระยะทาง และจำนวนรถ | FR-19, FR-06, BR-20, BR-21 | P1 | R0 · Guest · thai-massage · `booking-transport` เปิด · โรงแรม 2 (5.0), 3 (5.1), 4 (12.0), 5 (15.0), 6 (15.1), 7 (20.0) กม. · จำนวนคน 1, 4, 5, 6 | 1 คน: โรงแรม 2 → `transport-fee` ฿0 · โรงแรม 3 → ฿300, `price-total` ฿1,100 · โรงแรม 5 → ฿300 · โรงแรม 6 และ 7 → `transport-error` "ไม่มีบริการรับส่งสำหรับระยะนี้" และจองไม่ได้ · โรงแรม 4: 4 คน → `transport-cars` 1 ค่ารถ ฿300 · 5 คน → 2 คัน ฿600 (`price-total` ฿4,200) · 6 คน → 2 คัน ฿600 · `GET /api/transport?hotelId=4&people=5` → `{"available":true,"distanceKm":12,"cars":2,"feePerCar":300,"fee":600}` · เปิดรถแต่ไม่เลือกโรงแรม → "กรุณาเลือกโรงแรม" · รูปแบบการแสดงระยะทางบนหน้า (5 หรือ 5.0 กม.): **ต้องถาม** |
| TC-BOOK-08 | BOOK | แพ็กเกจ Bangkok Relax: รายการที่รวม ราคาต่อคน และราคารวม | FR-18, FR-19, BR-19, BR-08 | P1 | R0 · Guest · `/packages/bangkok-relax` 1 คน และ 4 คน · โรงแรม 4 (12 กม.) และ 6 (15.1 กม.) → `package-book` | `package-price` ฿2,900 · มี `package-inc-thai-massage`, `package-inc-herbal-compress`, `package-inc-transfer` · `package-herbs` ไพล ขมิ้น ตะไคร้ · 1 คน `package-total` ฿2,900 · 4 คน `package-total`: ฿11,600 (ก่อนลด) หรือ ฿10,440 (หลังลดกลุ่ม) **ต้องถาม** · โรงแรม 4 → `package-cars` 1, `package-transport-fee` ฿300 · โรงแรม 6 → `package-transport-error` · ที่ `/book` 4 คน + โรงแรม 4: `price-subtotal` ฿11,600, `price-group-discount` −฿1,160, `price-transport` ฿300, `price-total` ฿10,740 |
| TC-THER-01 | THER | คะแนนรีวิว และตัวกรอง "4.5 ดาวขึ้นไป" | FR-08, BR-10 | P2 | R0 · `/therapists` · `GET /api/therapists?minRating=4.5` | `filter-all` → 6 คน · `therapist-rating-1` 4.9 (`therapist-review-count-1` 10) · 2 = 4.5 (2) · 3 = 4.4 (5) · 4 = 4.7 (10) · 5 = 5.0 (3) · `filter-45` → แสดง 4 คน คือ id 1, 2, 4, 5 · ไม่แสดง id 3 (4.4) และ id 6 (ไม่มีรีวิว) · API ได้ 4 คน · `therapist-toggle-reviews-1` เปิดข้อความรีวิว · ข้อความของนักบำบัดที่ยังไม่มีรีวิว: **ต้องถาม** |
| TC-AI-01 | AI | แบบทดสอบ 4 ข้อ ต้องตอบครบก่อนแสดงผล และใช้กฎแรกที่ตรง | FR-26, BR-24 | P2 | `/quiz` ชุดคำตอบ (goal, time, pressure, transfer): A = pain, 60, strong, no · B = skin, 90, soft, no · C = skin, 90, soft, yes · D = relax, 60, medium, no · E = relax, 120, medium, no · ชุด A ทำซ้ำ 10 ครั้ง | `quiz-progress` เริ่มที่ "ข้อ 1/4" · ตอบ 3 ข้อแล้วยังไม่มี `quiz-result` · ตอบครบ 4 ข้อ → `quiz-result` 1 รายการ: A → `data-service` "thai-massage" · B → "aloe-hydrating-facial" · C → "bangkok-relax" (กฎ transfer ชนะ) · D → "foot-reflexology" · E → "aroma-oil" · A ได้ผลเดิม 10/10 ครั้ง · `quiz-book` ไป `/book` · ข้อความเหตุผลใน `quiz-reason`: **ต้องถาม** (SPEC ให้แค่ key) |
| TC-AI-02 | AI | วิเคราะห์ผิว + ภาพจำลอง ทำในเบราว์เซอร์ ร้านไม่เก็บรูปใบหน้า | FR-29, FR-30, FR-31, BR-25 | P2 | `/skin` กด `skin-sample` 10 ครั้ง และอัปโหลดรูปผ่าน `skin-file` · เปิด DevTools Network · `/privacy` | `skin-result` มี `data-type` อย่างใดอย่างหนึ่งใน sensitive / dull / dry / balanced ตามกฎ SPEC §6.2 เมื่อคำนวณจาก `skin-avg` data-r/g/b (ความสว่าง = round(0.299R+0.587G+0.114B) ตรงกับ `skin-brightness` · ความแดง = round(R−G) ตรงกับ `skin-redness`) · ผลของรูปตัวอย่าง: **ต้องถาม** · ได้ผลเดิม 10/10 ครั้ง · `skin-disclaimer` "ผลนี้เป็นคำแนะนำเบื้องต้น ไม่ใช่การวินิจฉัยของแพทย์" · `sim-treatment` turmeric-facial → `sim-after` `data-filter` "brightness(1.10) saturate(1.06) contrast(1.03)" · `sim-label` "ภาพจำลองเท่านั้น ผลจริงแต่ละคนต่างกัน" · รูปที่อัปโหลดมี src ขึ้นต้นด้วย `blob:` · ไม่มี request ส่งรูปออก 0 ครั้ง (NFR-07) · `privacy-no-face` มีข้อความ "ร้านไม่เก็บรูปใบหน้าลูกค้า" |
| TC-CHAT-01 | CHAT | chatbot ตอบเวลาเปิด–ปิดและราคา ในภาษาที่ลูกค้าพิมพ์ | FR-27, BR-22 | P2 | `chat-toggle` → พิมพ์ "营业时间?" · "多少钱?" · "เปิดกี่โมง" · "what time do you open" · แต่ละคำถามถามซ้ำ 10 ครั้ง | "营业时间?" → ข้อความบอทขึ้นต้นด้วย "我们每天营业 10:00–22:00，全年无休。" · "多少钱?" → มี "曼谷放松套餐 Bangkok Relax (120 分钟) ฿2,900/人" · "เปิดกี่โมง" → ตอบเป็นภาษาไทยและมี 10:00–22:00 · "what time do you open" → ตอบเป็นภาษาอังกฤษ · ข้อความเต็มของคำตอบภาษาไทย/อังกฤษ: **ต้องถาม** · ตอบแต่ละข้อ ≤ 2 วินาที (NFR-05) · คำตอบเหมือนเดิม 10/10 ครั้ง (NFR-12) |
| TC-CHAT-02 | CHAT | จองผ่าน chatbot ด้วยกฎเดียวกับหน้าจอง และสรุปราคารวมค่ารถ | FR-28, BR-07, BR-19, BR-20 | P1 | R0 · Guest · `chat-quick-book` → bangkok-relax → "พรุ่งนี้" → 7 คน แล้วแก้เป็น 4 คน → 10:00 → ต้องการรถ → Bang Na Lakeside (15.1) แล้วเปลี่ยนเป็น Chatuchak Park (12.0) → ชื่อ Mei เบอร์ 0812345678 → ยืนยัน | 7 คน → "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567" · 15.1 กม. → "ไม่มีบริการรับส่งสำหรับระยะนี้" · สรุปราคา ฿11,600 − ฿1,160 + ค่ารถ ฿300 = ฿10,740 · ยืนยันแล้วได้รหัสจอง และการจองมี `source` "chatbot" วันที่ 2026-10-09 เวลา 10:00 · `GET /api/availability` รอบนั้นของนักบำบัดที่ได้รับมอบหมายเป็น `booked` · พิมพ์ "ยกเลิก" ระหว่างทางแล้วการจองหยุด |
| TC-MEM-01 | MEM | **ค่าขอบระดับสมาชิก** ฿9,999 / ฿10,000 / ฿29,999 / ฿30,000 และส่วนลดตามระดับ | FR-09, FR-06, BR-13 | P1 | R0 · U{"email":"new@sabai.test","totalSpent":9999} แล้ว 10000, 29999, 30000 · ทุกค่า L(new) → `/account` และ `/book` thai-massage 1 คน | ฿9,999 → `member-tier` data-tier "silver" · `member-next-tier` "อีก ฿1 ถึงระดับ Gold" · `/book` ไม่มีส่วนลดระดับ `price-total` ฿800 · ฿10,000 → "gold" · "อีก ฿20,000 ถึงระดับ Platinum" · `price-tier-discount` −฿40 → ฿760 · ฿29,999 → "gold" · "อีก ฿1 ถึงระดับ Platinum" · ฿760 · ฿30,000 → "platinum" · "คุณอยู่ระดับสูงสุดแล้ว" · −฿80 → ฿720 |
| TC-MEM-02 | MEM | ได้แต้ม floor(ยอดสุทธิ/100) และยอดสะสมเพิ่ม | FR-09, BR-11, BR-13 | P1 | R0 · L(nida) (Gold 124 แต้ม ฿12,400) · thai-massage 1 คน 2026-10-11 11:00 ไม่แลกแต้ม · ไม่ใช้รถ | `price-tier-discount` −฿40 · `price-total` ฿760 · `price-points-earn` 7 (ปัดทิ้ง 7.6 → 7 ไม่ใช่ 8) · หลังจองสำเร็จ `member-points` 131 · `member-spent` ฿13,160 · ค่าขอบ ฿99 → 0, ฿100 → 1, ฿199 → 1 ทำจากราคาบริการใน seed ไม่ได้ (บริการถูกสุด ฿600): **ต้องถาม** วิธีสร้างยอดเหล่านี้ |
| TC-MEM-03 | MEM | แลกแต้ม 100 แต้ม = ฿50 ค่าขอบ 99 / 100 / 250 แต้ม หักแต้มทันที | FR-10, BR-12 | P1 | R0 · (ก) L(nida) 124 แต้ม thai-massage แลก 1 ชุด · (ข) U{"email":"nida@sabai.test","points":99} · (ค) L(ton) 250 แต้ม thai-massage แลก 2 ชุด | (ก) `booking-redeem-max` 1 · `price-points-discount` −฿50 · `price-total` ฿710 · ได้ 7 แต้ม → `member-points` 31 (124−100+7) · `member-spent` ฿13,110 · (ข) `booking-redeem` disabled · `POST /api/quote` `redeemSets:1` → `issues` มี `POINTS_NOT_ENOUGH` "แต้มไม่พอสำหรับแลกส่วนลด" · (ค) `booking-redeem-max` 2 · ส่วนลด −฿100 · `price-total` ฿620 (800 − 80 − 100) · `member-points` 56 (250−200+6) |
| TC-MEM-04 | MEM | ส่วนลดเดือนเกิด 20% ใช้ได้ 1 ครั้ง ไม่รวมกับส่วนลดระดับ และค่าขอบเดือน | FR-11, FR-06, BR-14 | P1 | R0 · L(ton) (Platinum เกิดเดือน ต.ค.) · aroma-oil ฿1,500 1 คน 2026-10-09 12:00 · ค่าขอบเดือน: R(2026-09-30 / 10-01 / 10-31 / 11-01 เวลา 10:00) + U{"email":"ton@sabai.test","birthMonth":10,"birthdayUsedYear":null} | มี `booking-birthday` · ติ๊กแล้ว `price-birthday-discount` −฿300 · ไม่มีส่วนลดระดับซ้อน · `price-total` ฿1,200 (ไม่ใช่ ฿1,050 หรือ ฿1,350) · `price-points-earn` 12 · จองแล้วเปิด `/book` ใหม่ → ไม่มี `booking-birthday` · quote `useBirthday:true` → `BIRTHDAY_NOT_ELIGIBLE` "ใช้ส่วนลดเดือนเกิดไม่ได้ (ไม่ใช่เดือนเกิด หรือใช้ไปแล้วปีนี้)" · 30 ก.ย. ไม่มีตัวเลือก · 1 ต.ค. มี · 31 ต.ค. มี · 1 พ.ย. ไม่มี |
| TC-WAL-01 | WAL | **จองด้วยคอร์สแล้วครั้งลด** และยกเลิกแล้วคืนครั้ง | FR-13, FR-07, BR-16 | P1 | R0 · L(nida) (คอร์สใช้ไป 4) · `/wallet` → `/book` body-contouring 1 คน `booking-pay-course` วันที่ 2026-10-12 10:00 · จากนั้นยกเลิกที่ `/account` | ก่อนจอง `course-remaining` "เหลือ 7 จาก 11 ครั้ง" (`data-left` 7) · `price-course` แสดงว่าคอร์สจ่ายค่าบริการ ฿1,500 · `price-total` ฿0 · `price-points-earn` 0 · จองสำเร็จ → `/wallet` `data-left` 6 · `member-points` ยังเป็น 124 · `member-spent` ยังเป็น ฿12,400 · ยกเลิกนัดนี้ (เหลือมากกว่า 24 ชม.) → `data-left` กลับเป็น 7 |
| TC-WAL-02 | WAL | คอร์สเหลือ 1 → 0 แล้วจองด้วยคอร์สไม่ได้ และใช้ได้เฉพาะ body-contouring 1 คน | FR-13, BR-16 | P1 | R0 · U{"email":"nida@sabai.test","courseUsed":10} → จองด้วยคอร์ส 1 ครั้ง · แล้ว U{…"courseUsed":11} · ลอง thai-massage จ่ายด้วยคอร์ส | เหลือ 1 → จองได้ แล้ว `data-left` 0 · เหลือ 0 → `course-book` disabled · `/book` `booking-pay-course` disabled · `booking-issue-COURSE_EMPTY` "คอร์สเหลือ 0 ครั้ง จองด้วยคอร์สไม่ได้" · API `payWith:"course"` → `error` "COURSE_EMPTY" (HTTP status: **ต้องถาม**) · thai-massage + คอร์ส → `COURSE_NOT_APPLICABLE` "คอร์สใช้ได้กับบริการกระชับสัดส่วน 1 คนเท่านั้น" |
| TC-WAL-03 | WAL | ซื้อคอร์ส ฿15,000 ได้ 11 ครั้ง อายุ 180 วัน (ค่าขอบวันที่ 180 / 181) | FR-12, BR-15 | P1 | R0 · L(new) → `/wallet` `course-buy` · U{"email":"nida@sabai.test","coursePurchasedOn":"2026-04-11"} และ "2026-04-10" | ก่อนซื้อ `course-none` · ซื้อแล้ว `course-remaining` "เหลือ 11 จาก 11 ครั้ง" · `course-expires` data-date "2027-04-06" · `POST /api/courses` → 201 `price` 15000 `left` 11 · ซื้อ 2026-04-11 → หมดอายุ 2026-10-08 (วันที่ 180) → `course-book` กดได้ · ซื้อ 2026-04-10 → หมดอายุ 2026-10-07 (วันที่ 181) → `course-expired` แสดง · `course-book` disabled · `booking-issue-COURSE_EXPIRED` "คอร์สหมดอายุแล้ว จองด้วยคอร์สไม่ได้" |
| TC-GIFT-01 | GIFT | ซื้อ Gift Card: ค่าขอบมูลค่า ลาย และช่องทาง | FR-16, BR-17 | P2 | R0 · `/gift-cards` มูลค่า 499, 500, 10000, 10001, 500.5 · ไม่เลือกลาย · ไม่เลือกช่องทาง · email ผู้รับ "abc" · ชุดที่ถูกต้อง: 2000, orchid, line, "mom-line" | 499 / 10001 / 500.5 → `gift-error` "มูลค่า Gift Card ต้องอยู่ระหว่าง ฿500–฿10,000" · 500 และ 10000 ผ่าน · ไม่เลือกลาย → "กรุณาเลือกลาย Gift Card" · ไม่เลือกช่องทาง → "กรุณาเลือกช่องทางส่ง (LINE หรืออีเมล)" · email ผิด → "กรุณากรอก LINE ID หรืออีเมลผู้รับให้ถูกต้อง" · มีลายให้เลือก 3 แบบคือ orchid / lotus / gold · ชุดที่ถูกต้อง → `gift-success` · `gift-code` ขึ้นต้นด้วย "GC-" · `gift-expiry` data-date "2027-10-08" · `gift-simulated-note` แสดง · API `delivery` = `{"simulated":true,"sent":false}` |
| TC-GIFT-02 | GIFT | ใช้ Gift Card จ่ายค่าบริการ และวันหมดอายุ 365 / 366 | FR-17, BR-18 | P1 | R0 · Guest · `/book` aroma-oil ฿1,500 1 คน 2026-10-09 12:00 ใช้ `GIFT-2000-ORCHID` · จองครั้งที่ 2 thai-massage ฿800 ด้วยบัตรเดิม · `gift-check` ใช้ `GIFT-DAY365` และ `GIFT-DAY366` | ครั้งแรก `price-total` ฿1,500 · `price-gift` −฿1,500 · `price-due` ฿0 · ตรวจบัตรเหลือ `gift-check-balance` ฿500 · ครั้งที่ 2 `price-gift` −฿500 · `price-due` ฿300 · บัตรเหลือ ฿0 → `data-status` "empty" "Gift Card นี้ใช้ยอดหมดแล้ว" · DAY365 → `data-status` "valid" · `gift-check-expiry` 2026-10-08 · DAY366 → `data-status` "expired" "Gift Card หมดอายุแล้ว" · ใช้ DAY366 ที่ `/book` → `booking-gift-error` "Gift Card หมดอายุแล้ว" และ `price-due` ไม่ลด |
| TC-DASH-01 | DASH | หน้าสมาชิก (`/account`): ระดับ แต้ม ประวัติ กราฟรอบเอว รูปก่อน/หลัง และข้อมูลข้ามบัญชี | FR-09, FR-14, FR-15 | P2 | R0 · L(nida) → `/account` · logout · L(ton) → `/account`, `/wallet` · ton เรียก `POST /api/bookings/6/cancel` | `member-tier` "gold" · `member-points` 124 · `member-spent` ฿12,400 · `member-next-tier` "อีก ฿17,600 ถึงระดับ Platinum" · `upcoming-list` มี `booking-item-SB00006` (2026-10-09 15:00 นวดไทย มาลี) · `waist-point-*` data-cm 82, 80.5, 79, 78 · `waist-drop` "ลดลง 4 ซม. จากครั้งแรก" · `history-row-0`–`4` = 5 แถว วันที่เรียงจากล่าสุด · มี `photo-before`, `photo-after` และไม่เห็นใบหน้าในรูป (ตรวจด้วยตา) · logout แล้วเปิด `/account` → `account-need-login` · ton ไม่เห็น SB00006, กราฟรอบเอว หรือรูปของนิดา (NFR-08) · ton ยกเลิกนัดของนิดาต้องไม่สำเร็จ (error code / status: **ต้องถาม**) |
| TC-DASH-02 | DASH | ยกเลิกนัดเองได้เมื่อเหลือ ≥ 24 ชม. (ค่าขอบ 24 ชม. พอดี) | FR-07, BR-09 | P1 | L(nida) นัด SB00006 = 2026-10-09 15:00 · R(2026-10-08T14:59:00+07:00) · R(…T15:00:00+07:00) · R(…T15:01:00+07:00) | 14:59 และ 15:00:00 → `cancel-btn-SB00006` กดได้ · กดแล้ว `cancel-success` · `/api/availability?service=thai-massage&date=2026-10-09&people=1&therapistId=1` → 15:00 = `free` · ยกเลิกซ้ำผ่าน API → `ALREADY_CANCELLED` "นัดนี้ถูกยกเลิกไปแล้ว" · 15:01 → ปุ่ม disabled · `cancel-blocked-SB00006` "เหลือน้อยกว่า 24 ชั่วโมง ยกเลิกเองไม่ได้ กรุณาติดต่อร้าน 02-123-4567" · API cancel → 409 `CANCEL_TOO_LATE` |
| TC-EXP-01 | EXP | เปลี่ยนภาษา 3 ภาษา จำค่าที่เลือกเมื่อเปลี่ยนหน้า และแปลครบ | FR-20, BR-22 | P2 | `/` กด `lang-en` → ไป `/book` → รีโหลด · กด `lang-zh` แล้วเปิดทุกหน้าใน SPEC §1 · API จองรอบเต็มพร้อม cookie `lang=en` และ `lang=zh` | มีปุ่มภาษาแค่ 3 ปุ่ม (`lang-th`, `lang-en`, `lang-zh`) ไม่มีภาษาที่ 4 · `lang-en` มี `aria-pressed="true"` และยังเป็น English หลังเปลี่ยนหน้าและรีโหลด (cookie `lang`=en) · หน้า 中文 และ English มีตัวอักษรไทย 0 จุด ยกเว้นชื่อร้าน (NFR-04) · API `message` = "This time is already booked" / "该时间已被预订" |
| TC-EXP-02 | EXP | ปุ่มเพลงสปา: ไม่เล่นเองเมื่อเปิดเว็บ และเปิด/ปิดได้ | FR-24 | P3 | เปิด `/` ครั้งแรก (ล้าง storage) → กด `music-toggle` 2 ครั้ง | โหลดครั้งแรก `music-toggle` data-playing="false" และไม่มีเสียงเล่นเอง (NFR-09) · กดครั้งที่ 1 → data-playing="true", `aria-pressed="true"` · กดครั้งที่ 2 → "false" |
| TC-EXP-03 | EXP | ทัวร์ 360° ห้อง Couple Suite ลากหมุนได้ และมีปุ่มจอง | FR-23 | P3 | `/rooms` · `tour-right`, `tour-left`, ลากเมาส์, ปุ่มลูกศร · `tour-book` | `/rooms` redirect ไป `/rooms/couple-suite` · `tour-360` data-loaded="true" ภายใน 5 วินาที (NFR-10) · กด `tour-right` / ลาก / ลูกศร แล้ว `data-angle` เปลี่ยน และอยู่ในช่วง 0–359 เสมอ (รวมกรณีหมุนผ่าน 0) · มุมที่เปลี่ยนต่อการกด 1 ครั้ง: **ต้องถาม** · `tour-book` แสดงข้อความ "จองห้องนี้" และพาไปหน้าจอง (เลือกแบบคู่ไว้ให้หรือไม่: **ต้องถาม**) |
| TC-MOB-01 | MOB | ใช้งานบนจอ 375 px: ไม่มีแถบเลื่อนแนวนอน ปุ่ม ≥ 44×44 และจองได้ | FR-01, FR-20 | P2 | viewport 375×812 · หน้า `/`, `/services`, `/book`, `/packages/bangkok-relax`, `/therapists`, `/rooms/couple-suite`, `/gift-cards`, `/mood`, `/quiz`, `/skin`, `/account`, `/wallet` · ทำ TC-BOOK-01 ซ้ำบนมือถือ | ทุกหน้า `document.documentElement.scrollWidth` ≤ 375 (NFR-01) · `nav-toggle` แสดงและเปิดเมนูได้ · `nav-toggle`, `lang-*`, `chat-toggle`, `slot-*`, `booking-submit` มีขนาด ≥ 44×44 px · จองจนเห็น `booking-success` ได้ |
| TC-API-01 | API | เรียก API ที่ต้อง login โดยไม่ login ต้องได้ **401** | FR-07, FR-09, FR-13 | P2 | R0 · ไม่มี cookie `sabai_session`: `GET /api/account`, `GET /api/wallet`, `GET /api/bookings`, `POST /api/courses`, `POST /api/bookings/6/cancel` · ทำซ้ำพร้อม cookie `lang=en` | ทุกเส้นได้ HTTP **401** · body `{"ok":false,"error":"LOGIN_REQUIRED","message":"กรุณาเข้าสู่ระบบ"}` (lang=en → "Please log in") · ไม่มีข้อมูลสมาชิกในคำตอบ · หลังเรียกแล้ว SB00006 ยัง `confirmed` และไม่มีคอร์สใหม่เกิดขึ้น · หมายเหตุ: SPEC ระบุแค่ code `LOGIN_REQUIRED` ไม่ได้ระบุ status 401 → **ต้องถาม** เพื่อยืนยัน (แผนนี้ใช้ 401 เป็นเกณฑ์) |
| TC-API-02 | API | **จองซ้อนพร้อมกัน**: 2 คำขอพร้อมกันต้องสำเร็จ 1 คนพอดี | FR-02, BR-04, BR-06 | P1 | R0 · ยิง `POST /api/bookings` 2 คำขอพร้อมกัน (`Promise.all` / `curl &`) thai-massage 2026-10-09 `therapistId` 2 คนละชื่อ Guest ทำ 10 รอบ เวลา 10:00–14:30 · คู่: aroma-oil 2 คน 2026-10-12 12:00 ยิงพร้อมกัน 2 คำขอ | ทุกรอบได้ 201 หนึ่งครั้ง และ 409 `{"ok":false,"error":"SLOT_TAKEN","message":"เวลานี้ถูกจองแล้ว"}` หนึ่งครั้ง (10/10 รอบ) (NFR-06) · availability ของรอบนั้นเป็น `booked` และมีการจองแค่ 1 รายการต่อรอบ · Couple Suite: 201 หนึ่งครั้ง และ 409 หนึ่งครั้ง |

---

## 5. Traceability (FR/BR → TC)

### 5.1 FR

| FR | TC ที่ครอบคลุม |
|---|---|
| FR-01 | TC-BOOK-01, TC-BOOK-02, TC-MOB-01 |
| FR-02 | TC-BOOK-04, TC-BOOK-05, TC-API-02 |
| FR-03 | TC-BOOK-03 |
| FR-04 | TC-BOOK-05 |
| FR-05 | TC-BOOK-06 |
| FR-06 | TC-BOOK-01, TC-BOOK-06, TC-BOOK-07, TC-MEM-01, TC-MEM-04 |
| FR-07 | TC-DASH-02, TC-WAL-01, TC-API-01 |
| FR-08 | TC-THER-01 |
| FR-09 | TC-MEM-01, TC-MEM-02, TC-DASH-01, TC-API-01 |
| FR-10 | TC-MEM-03 |
| FR-11 | TC-MEM-04 |
| FR-12 | TC-WAL-03 |
| FR-13 | TC-WAL-01, TC-WAL-02, TC-API-01 |
| FR-14 | TC-DASH-01 |
| FR-15 | TC-DASH-01 |
| FR-16 | TC-GIFT-01 |
| FR-17 | TC-GIFT-02 |
| FR-18 | TC-BOOK-08 |
| FR-19 | TC-BOOK-07, TC-BOOK-08 |
| FR-20 | TC-EXP-01, TC-MOB-01 |
| FR-21 | TC-HOME-01 |
| FR-22 | TC-HOME-02 |
| FR-23 | TC-EXP-03 |
| FR-24 | TC-EXP-02 |
| FR-25 | TC-MOOD-01 |
| FR-26 | TC-AI-01 |
| FR-27 | TC-CHAT-01 |
| FR-28 | TC-CHAT-02 |
| FR-29 | TC-AI-02 |
| FR-30 | TC-AI-02 |
| FR-31 | TC-AI-02 |

### 5.2 BR

| BR | TC ที่ครอบคลุม |
|---|---|
| BR-01 | TC-BOOK-02 |
| BR-02 | TC-BOOK-02 |
| BR-03 | TC-BOOK-02 |
| BR-04 | TC-BOOK-04, TC-API-02 |
| BR-05 | TC-BOOK-03 |
| BR-06 | TC-BOOK-05, TC-API-02 |
| BR-07 | TC-BOOK-06, TC-CHAT-02 |
| BR-08 | TC-BOOK-06, TC-BOOK-08 |
| BR-09 | TC-DASH-02 |
| BR-10 | TC-THER-01 |
| BR-11 | TC-MEM-02 |
| BR-12 | TC-MEM-03 |
| BR-13 | TC-MEM-01, TC-MEM-02 |
| BR-14 | TC-MEM-04 |
| BR-15 | TC-WAL-03 |
| BR-16 | TC-WAL-01, TC-WAL-02 |
| BR-17 | TC-GIFT-01 |
| BR-18 | TC-GIFT-02 |
| BR-19 | TC-BOOK-08, TC-CHAT-02 |
| BR-20 | TC-BOOK-07, TC-CHAT-02 |
| BR-21 | TC-BOOK-07 |
| BR-22 | TC-EXP-01, TC-CHAT-01 |
| BR-23 | TC-MOOD-01 |
| BR-24 | TC-AI-01 |
| BR-25 | TC-AI-02 |

ผลตรวจ: FR 31/31 และ BR 25/25 มี TC อย่างน้อย 1 ข้อ

### 5.3 NFR ที่ตรวจร่วมไปด้วย (ข้อมูลเสริม)

| NFR | TC |
|---|---|
| NFR-01 | TC-MOB-01 |
| NFR-03 | TC-BOOK-01 |
| NFR-04 | TC-EXP-01 |
| NFR-05 | TC-CHAT-01 |
| NFR-06 | TC-API-02 |
| NFR-07 | TC-AI-02 |
| NFR-08 | TC-DASH-01 |
| NFR-09 | TC-EXP-02 |
| NFR-10 | TC-EXP-03 |
| NFR-11 | TC-HOME-01 |
| NFR-12 | TC-MOOD-01, TC-AI-01, TC-AI-02, TC-CHAT-01 |
| NFR-13, NFR-14 | ใช้ใน R0 / R(เวลา) ทุก TC (ตรวจตามเงื่อนไขเริ่มทดสอบ หัวข้อ 6) |
| NFR-15 | ทุก TC ใช้ `data-testid` และเทียบข้อความทุกตัวอักษร |

---

## 6. เงื่อนไขเริ่มและเกณฑ์ผ่าน

### 6.1 เริ่มทดสอบได้เมื่อ (Entry criteria)

| # | เงื่อนไข | วิธีตรวจ |
|---|---|---|
| 1 | Container 2 ตัว **healthy** ทั้งคู่: `sabai-db` และ `sabai-web` | ผู้ดูแลระบบตรวจ `docker ps` แล้วคอลัมน์ STATUS ต้องเป็น `(healthy)` ทั้ง 2 ตัว (ผู้ทดสอบไม่ได้รัน docker เอง) |
| 2 | `GET /api/health` → 200 `{"ok":true,"db":true}` | curl |
| 3 | R0 สำเร็จ → `{"ok":true,"locked":true,"today":"2026-10-08","bookable":{"from":"2026-10-09","to":"2026-11-07"}}` ภายใน 2 วินาที | curl |
| 4 | หลัง R0 login nida แล้วได้ `totalSpent` 12400, `points` 124, `nextTierNeed` 17600 และ wallet `left` 7 (ข้อมูลตั้งต้นตรง SPEC §6.1) | curl |
| 5 | บันทึกค่า `data-bug-mode` ของหน้าเว็บลงรายงาน | เปิด `/` |

### 6.2 ผ่านเกณฑ์เมื่อ (Exit criteria)

| # | เกณฑ์ |
|---|---|
| 1 | TC ระดับ **P1 ผ่านทั้งหมด** (19/19) |
| 2 | ผ่านรวม **≥ 95%** → ต้องผ่านอย่างน้อย 32 จาก 33 ข้อ (32/33 = 97.0% · 31/33 = 93.9% ยังไม่ผ่าน) |
| 3 | TC ที่ Blocked หรือไม่มีหลักฐานครบตามหัวข้อ 7 นับเป็น "ไม่ผ่าน" |
| 4 | ข้อที่เขียนว่า "ต้องถาม" ต้องได้คำตอบก่อนปิดรอบ ถ้ายังไม่ได้คำตอบ ให้ตรวจเฉพาะส่วนที่ไม่ขึ้นกับค่านั้น และบันทึกเป็น open question |

---

## 7. หลักฐาน (Evidence)

| กฎ | รายละเอียด |
|---|---|
| ทุก TC ที่เปิดหน้าเว็บ | ต้องมีทั้ง **GIF** และ **MP4** ครบ 2 ไฟล์ ถ้าขาดไฟล์ใดไฟล์หนึ่งให้นับว่าไม่ผ่าน |
| TC ที่ต้องมี GIF + MP4 | 31 ข้อ คือทุกข้อยกเว้น TC-API-01 และ TC-API-02 |
| TC ที่เรียก API อย่างเดียว | TC-API-01, TC-API-02: เก็บไฟล์ `.log` ที่มี request, HTTP status และ response body ทุกครั้ง (ถ้าเปิดหน้าเว็บประกอบ ต้องมี GIF + MP4 ด้วย) |
| ชื่อไฟล์ | `evidence/<TC-ID>/<TC-ID>.gif` และ `evidence/<TC-ID>/<TC-ID>.mp4` เช่น `evidence/TC-BOOK-01/TC-BOOK-01.mp4` |
| วิธีอัด | Playwright `use: { video: 'on' }` ได้ไฟล์ `.webm` แล้วแปลงเป็นไฟล์ที่ต้องส่ง: `ffmpeg -i in.webm -c:v libx264 -pix_fmt yuv420p TC.mp4` และ `ffmpeg -i in.webm -vf "fps=8,scale=960:-1:flags=lanczos" TC.gif` |
| สิ่งที่ต้องเห็นในคลิป | ค่าที่ตรวจตามคอลัมน์ "ผลที่คาดหวัง" ต้องอ่านได้ชัดในคลิป (เช่น `price-total` ฿10,740 หรือข้อความ "เวลานี้ถูกจองแล้ว") |
| เมื่อพบ defect | แนบ GIF/MP4 ของ TC นั้น + ภาพหน้าจอจังหวะที่ผิด + request/response ที่เกี่ยวข้อง ระบุระดับ P1/P2/P3 ตามหัวข้อ 3 |

---

## 8. รายการ "ต้องถาม" (SPEC ไม่ได้ระบุค่าไว้)

| # | คำถาม | TC ที่เกี่ยวข้อง |
|---|---|---|
| 1 | API ที่ต้อง login แต่ไม่ได้ login ตอบ HTTP status อะไร (แผนนี้ใช้ 401 เป็นเกณฑ์ SPEC ระบุแค่ code `LOGIN_REQUIRED`) | TC-API-01 |
| 2 | HTTP status ของ error อื่นนอกจาก `SLOT_TAKEN`, `CANCEL_TOO_LATE`, `LOGIN_FAILED` (เช่น `COURSE_EMPTY`, `DATE_OUT_OF_RANGE`, `GROUP_TOO_LARGE`) | TC-BOOK-03, TC-BOOK-06, TC-WAL-02 |
| 3 | เลข `booking-code` ของการจองใหม่หลัง reset (SPEC บอกแค่รูปแบบ SB00006) | TC-BOOK-01 |
| 4 | `package-total` 4 คนที่หน้าแพ็กเกจแสดง ฿11,600 (ก่อนลด) หรือ ฿10,440 (หลังลดกลุ่ม) | TC-BOOK-08 |
| 5 | ผลวิเคราะห์ผิวของ `sample-face.jpg` เป็นประเภทใด | TC-AI-02 |
| 6 | ข้อความเหตุผลของแบบทดสอบ (SPEC ให้แค่ key) และข้อความเต็มที่ chatbot ตอบเป็นภาษาไทย/อังกฤษ | TC-AI-01, TC-CHAT-01 |
| 7 | ปุ่ม "จองเลย" / `quiz-book` / `tour-book` เลือกบริการหรือแบบคู่ไว้ให้ที่ `/book` หรือไม่ | TC-MOOD-01, TC-AI-01, TC-EXP-03 |
| 8 | ทัวร์ 360° หมุนกี่องศาต่อการกด 1 ครั้ง | TC-EXP-03 |
| 9 | ภาพต้นแบบลายไทยและสีที่เจ้าของร้านอนุมัติ | TC-HOME-01 |
| 10 | ข้อความที่แสดงสำหรับนักบำบัดที่ยังไม่มีรีวิว | TC-THER-01 |
| 11 | วิธีสร้างยอดสุทธิ ฿99 / ฿100 / ฿199 เพื่อทดสอบค่าขอบแต้ม (ราคาบริการต่ำสุด ฿600) | TC-MEM-02 |
| 12 | error code / status เมื่อสมาชิกยกเลิกนัดของคนอื่น | TC-DASH-01 |
| 13 | รูปแบบการแสดงระยะทางบนหน้า (5 หรือ 5.0 กม.) | TC-BOOK-07 |
| 14 | โมดูล DASH หมายถึงหน้า `/account` ของสมาชิก (ตามที่แผนนี้ตีความ) หรือแดชบอร์ดหลังร้าน (ไม่มีใน SPEC) | TC-DASH-01, TC-DASH-02 |
| 15 | จะมี Safari / iPhone จริงสำหรับ NFR-10 หรือไม่ | TC-EXP-03 |

---

## 9. สรุปจำนวน Test Case

| โมดูล | จำนวน TC | P1 | P2 | P3 |
|---|---|---|---|---|
| HOME | 2 | 0 | 1 | 1 |
| MOOD | 1 | 0 | 1 | 0 |
| BOOK | 8 | 8 | 0 | 0 |
| THER | 1 | 0 | 1 | 0 |
| AI | 2 | 0 | 2 | 0 |
| CHAT | 2 | 1 | 1 | 0 |
| MEM | 4 | 4 | 0 | 0 |
| WAL | 3 | 3 | 0 | 0 |
| GIFT | 2 | 1 | 1 | 0 |
| DASH | 2 | 1 | 1 | 0 |
| EXP | 3 | 0 | 1 | 2 |
| MOB | 1 | 0 | 1 | 0 |
| API | 2 | 1 | 1 | 0 |
| **รวม** | **33** | **19** | **11** | **3** |
