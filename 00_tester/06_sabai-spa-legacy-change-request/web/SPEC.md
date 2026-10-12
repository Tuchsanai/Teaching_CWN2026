# SPEC · เว็บ สบายใจ สปา · Sabai Jai Wellness Spa

> เอกสารส่งมอบ ฉบับ 1.0 · ก.ย. 2569 · บริษัท โค้ดไว จำกัด

อ้างอิง: REQUIREMENTS.md (FR-01–35, BR-01–20, NFR-01–18) · DESIGN.md (D1–D15) · TEST-DATA.md (seed, E01–E90, T1–T17)
สแตก: Next.js 15 App Router + TypeScript · PostgreSQL 16 ผ่าน `pg` (SQL ตรง ไม่ใช้ ORM) · Docker compose 2 โปรเจกต์ (`db/`, `web/`) บน network `sabai-net`

---

## 1. วิธีรัน (PowerShell)

```powershell
# 0) อยู่ที่โฟลเดอร์รากของโปรเจกต์ (ที่มี db/ และ web/)
# 1) หยุด container อื่นที่จับพอร์ต 3000 หรือ 5433 (stop อย่างเดียว ไม่ลบ)
docker ps --format "{{.Names}} {{.Ports}}"
docker stop <ชื่อ container ที่จับพอร์ต>        # ถ้ามี เช่น petshop

# 2) network ร่วม
docker network inspect sabai-net *> $null; if (-not $?) { docker network create sabai-net }

# 3) ฐานข้อมูล → รอ healthy
docker compose -f db/compose.yaml up -d
docker inspect -f "{{.State.Health.Status}}" sabai-db

# 4) เว็บ (build ไม่ต่อ db) → รอ healthy
docker compose -f web/compose.yaml up -d --build
docker inspect -f "{{.State.Health.Status}}" sabai-web

# 5) ตรวจ
Invoke-RestMethod http://localhost:3000/api/health          # ok=True db=True
cd web; node scripts/check-rules.mjs; cd ..                  # ผ่าน 90 / 90 ข้อ (ต้องใช้ Node ≥ 22.18 บนเครื่อง)

# รีเซ็ตข้อมูลทดสอบ + ล็อกวันนี้
Invoke-RestMethod -Method Post http://localhost:3000/api/test/reset -ContentType "application/json" -Body '{"now":"2026-10-10T10:00:00+07:00"}'

# ล้างฐานข้อมูลทั้งหมดแล้วเริ่มใหม่ (ลบ volume)
docker compose -f db/compose.yaml down -v
```

สคริปต์ช่วยทุกตัวเป็น `node scripts/*.mjs` (ไม่มีไฟล์ .sh):

| สคริปต์ | ใช้ทำอะไร |
|---|---|
| `node scripts/check-rules.mjs` | ยิง API ตรวจ E01–E90 (reset ก่อนทุกเคส) + unit test เรียก `lib/rules` ตรง · env `BASE_URL` (ค่าเริ่มต้น `http://localhost:3000`) |
| `node scripts/resize.mjs <dir>` | ย่อรูปจาก Codex → webp (`public/assets`, รูป body → `private/photos`) |

## 2. Environment

| ตัวแปร | ที่ | ค่าเริ่มต้น | ความหมาย |
|---|---|---|---|
| `DATABASE_URL` | web | `postgres://sabai:sabai@sabai-db:5432/sabai` | ต่อ db ภายใน `sabai-net` (นอก docker: `postgres://sabai:sabai@localhost:5433/sabai`) |
| `HOSTNAME` | web | `0.0.0.0` | ให้ Next standalone ฟังทุก interface |
| `PORT` | web | `3000` | |
| `TZ` | web, db | `Asia/Bangkok` | |
| `ALLOW_TEST_RESET` | web | `1` | `1` = เปิด `/api/test/*`, ใช้ `app_setting.test_today` เป็นนาฬิกา, แสดงบัญชีทดสอบในหน้า login, ปุ่มรีเซ็ตใน /admin · `0` = ปิดทั้งหมด (`/api/test/reset` ตอบ 404) |
| `SESSION_SECRET` | web | `sabai-jai-local-session-secret-2026` (compose) | กุญแจลงลายเซ็น cookie `sabai_session` (HMAC-SHA256) |
| `TODAY` | web | ว่าง | นาฬิกาสำรอง เช่น `2026-10-10T10:00` (ไม่มีโซน = เวลาไทย) ใช้เมื่อไม่มี `app_setting.test_today` |
| `SEED_SQL_PATH` | web (image) | `/app/sql/02-seed.sql` | seed ที่ reset เรียก (คัดลอกจาก `db/init/02-seed.sql` ตอน build ผ่าน `additional_contexts`) |
| `PHOTO_DIR` | web (image) | `/app/private/photos` | ที่เก็บรูป before/after (นอก public) |
| `POSTGRES_USER/PASSWORD/DB` | db | `sabai` / `sabai` / `sabai` | |

นาฬิกา (`lib/clock.ts`, NFR-13): `app_setting.test_today` (เมื่อ `ALLOW_TEST_RESET=1`) → env `TODAY` → เวลาจริง · seed ตั้ง `test_today = 2026-10-10T10:00:00+07:00` · กฎที่ใช้วันที่ทุกข้อ (BR-03/07/13/14/16) เรียก `clock()` เท่านั้น

---

## 3. หน้าเว็บ

ทุกหน้ามี header (โลโก้ · ปุ่มเพลง · ปุ่มภาษา ไทย/English/中文 · เข้าสู่ระบบ/ออกจากระบบ · เมนู) · footer (เวลาเปิด เบอร์ร้าน 02-123-4567) · ปุ่มแชทลอย · `<html data-ready="true|false" lang="th|en|zh">`

| path | ทำอะไร | FR |
|---|---|---|
| `/` | hero ลายกล้วยไม้/บัว · อารมณ์วันนี้ 4 แบบ → บริการแนะนำ + ปุ่มจอง · บริการยอดนิยม · ลิงก์แบบทดสอบ/วิเคราะห์ผิว/แชท | FR-27, FR-32 |
| `/services` | บริการทั้งหมด (ชื่อ เวลา ราคา สมุนไพร) + ปุ่มจอง | FR-31 |
| `/book` | จอง 4 ขั้น: ① บริการ+แบบ (เดี่ยว/คู่/กลุ่ม/แพ็กเกจ/จองด้วยคอร์ส)+จำนวนคน ② วัน (พรุ่งนี้–+30) + รอบว่าง + นักบำบัด (เดี่ยว) · ปุ่ม "ดูห้อง 360°" เมื่อจองคู่ ③ ข้อมูลติดต่อ + แลกแต้ม/เดือนเกิด/Gift Card/รถรับส่ง/คอร์ส (ราคาจาก `/api/price`) ④ สรุป: สมุนไพร + ราคาแยกบรรทัด + ค่ารถ (จำนวนคัน) ก่อนปุ่มยืนยัน → ข้อความยืนยัน · query: `service`, `type`, `people` | FR-01–06, 10, 12, 14, 20–23, 31–33 |
| `/package` | Bangkok Relax: ราคาต่อคน · สิ่งที่ได้ 3 อย่าง · คำนวณราคารวมตามจำนวนคน · ปุ่มจอง | FR-21 |
| `/therapists` | นักบำบัด คะแนนเฉลี่ย 1 ตำแหน่ง จำนวนรีวิว · ตัวกรอง "4.5 ดาวขึ้นไป" (`?min=4.5` เปิดตัวกรองไว้) | FR-08 |
| `/transport` | คำนวณค่ารถรับส่ง: เลือกโรงแรม H01–H06 หรือพิมพ์ระยะ + จำนวนคน → ค่ารถ จำนวนคัน | FR-22 |
| `/giftcard` | ซื้อ Gift Card (มูลค่า ลาย 3 แบบ ส่ง LINE/email แบบจำลอง แสดงข้อความที่ "ส่ง") · ตรวจยอด/วันหมดอายุ | FR-19, FR-20 |
| `/chat` | ผู้ช่วยแชท: ถามเวลาเปิด ราคา 3 ภาษา · จองผ่านแชท (บริการเดี่ยว) ด้วย API เดียวกับเว็บ | FR-25, FR-26 |
| `/quiz` | แบบทดสอบ 4 ข้อ แถบ 1/4…4/4 → แพ็กเกจแนะนำ 1 รายการ + เหตุผล + ปุ่มจอง | FR-28 |
| `/skin` | ข้อความแจ้งก่อนเลือกรูป → เลือกเซลฟี่ (หรือภาพตัวอย่างของร้าน) → วิเคราะห์ด้วย Canvas ในเครื่อง → ทรีตเมนต์แนะนำ 1–3 · ภาพจำลองก่อน/หลัง + ป้าย "ภาพจำลอง ผลจริงแต่ละคนต่างกัน" | FR-29, FR-30 |
| `/login` | ล็อกอินอีเมล+รหัสผ่าน (โหมดทดสอบแสดงบัญชี seed) · `?next=` | — |
| `/account` | ระดับ ส่วนลด ยอดสะสม ข้อความ "อีก ฿X ถึง …"/"อยู่ระดับสูงสุดแล้ว" · แต้มคงเหลือ · สถานะเดือนเกิด · นัดและประวัติ (ล่าสุด→เก่าสุด, "ยกเลิก") + ปุ่มยกเลิก (กดไม่ได้เมื่อ < 24 ชม. + เบอร์ร้าน) · ไม่มีช่องอัปโหลดรูป | FR-07, 09, 11, 12, 17, 35 |
| `/wallet` | คอร์ส "เหลือ X จาก 11 ครั้ง" วันหมดอายุ อีก N วัน/หมดอายุแล้ว · ปุ่มจองด้วยคอร์ส · กราฟรอบเอว + "ลดไปแล้ว X ซม." · รูป before/after (เฉพาะเจ้าของ) · ปุ่มซื้อคอร์ส | FR-13–16, 18 |
| `/admin` | (owner) ตารางคิวรายวัน · "ใช้บริการเสร็จ" (ให้แต้ม, ตัดครั้งคอร์ส, บันทึกรอบเอว) · ปุ่ม "รีเซ็ตข้อมูลทดสอบ" (โหมดทดสอบ) | D3, D5, D11, FR-09, FR-14, FR-16 |

---

## 4. กฎร้าน → ไฟล์/ฟังก์ชัน

ฟังก์ชันบริสุทธิ์ทั้งหมดอยู่ใน `lib/rules/*` (ไม่แตะ db · เงินเป็นสตางค์ integer) · ราคาที่เก็บจริงคิดที่เซิร์ฟเวอร์ (`lib/server/booking.ts`)

| รหัส | กฎ | ไฟล์ / ฟังก์ชัน |
|---|---|---|
| BR-01 | เปิด 10:00–22:00 รอบทุก 30 นาที จบ ≤ 22:00 | `lib/rules/slots.ts` `buildSlots()`, `isValidStartTime()` |
| BR-02 | นักบำบัด 1 คิว/เวลา `[start,end)` | `lib/rules/overlap.ts` `overlaps()`, `freeTherapists()` + db `EXCLUDE booking_slot_no_overlap` |
| BR-03 | จองได้ +1 ถึง +30 วัน | `lib/rules/dates.ts` `isBookableDate()`, `bookableRange()` |
| BR-04 | คู่ 2 คนพอดี · Couple Suite 1 คู่/ช่วง | `lib/rules/party.ts` `checkParty()` + `lib/server/booking.ts` `roomBusy()` + db `EXCLUDE booking_room_no_overlap` |
| BR-05 | กลุ่ม 3–6 · 7+ โทรร้าน · นักบำบัดต้องพอ | `lib/rules/party.ts` `checkParty()` · `createBooking()` |
| BR-06 | กลุ่ม ≥ 4 ลด 10% (ไม่ใช้กับแพ็กเกจ) | `lib/rules/pricing.ts` `bestPercent()` |
| BR-07 | ยกเลิกได้เมื่อเหลือ ≥ 24 ชม. | `lib/rules/cancel.ts` `canCancel()` · `cancelBooking()` |
| BR-08 | คะแนนเฉลี่ยทศนิยม 1 (ปัดครึ่งขึ้น) · กรอง ≥ 4.5 | `lib/rules/rating.ts` `ratingTenths()`, `roundAverage()`, `passesRatingFilter()` |
| BR-09 | แต้ม = floor(ยอดจ่าย ÷ 100) หลังส่วนลด ไม่รวมรถ − Gift Card | `lib/rules/points.ts` `pointsFor()`, `earnBase()` · ให้ตอนร้านกดเสร็จ `completeBooking()` |
| BR-10 | 100 แต้ม = ฿50 เป็นก้อน ไม่ติดลบ | `lib/rules/points.ts` `maxRedeemBlocks()`, `redeemPoints()` |
| BR-11 | Silver/Gold/Platinum | `lib/rules/tier.ts` `tierOf()`, `TIER_PCT` |
| BR-12 | "อีก ฿X ถึง …" / "อยู่ระดับสูงสุดแล้ว" | `lib/rules/tier.ts` `nextTier()` · `lib/server/customer.ts` `tierInfo()` |
| BR-13 | เดือนเกิด 20% 1 ครั้ง/เดือน ตามวันนัด เดี่ยว/คู่/กลุ่ม | `lib/rules/birthday.ts` `birthdayEligible()` + db PK `birthday_use` |
| BR-14 | คอร์ส 11 ครั้ง 180 วัน (วันหมดอายุยังใช้ได้) | `lib/rules/course.ts` `courseExpiry()`, `canUseCourse()`, `courseRemaining()` · กันครั้งตอนจอง (`reserved_sessions`) ตัดจริงตอนเสร็จ (D5) |
| BR-15 | Gift Card ฿500–฿10,000 จำนวนเต็ม | `lib/rules/giftcard.ts` `isValidFaceValue()` + db CHECK |
| BR-16 | Gift Card 365 วัน (ตรวจจากวันจ่าย T14) ใช้หลายครั้ง | `lib/rules/giftcard.ts` `giftCardExpiry()`, `giftCardStatus()`, `applyGiftCard()` |
| BR-17 | ≤ 5 กม. ฟรี · ≤ 15 กม. ฿300/คัน · > 15 ไม่รับ | `lib/rules/transport.ts` `transportQuote()` |
| BR-18 | คันละ 4 คน | `lib/rules/transport.ts` `vehiclesFor()` |
| BR-19 | Bangkok Relax ฿2,900 × คน รถรวมแล้ว | `lib/rules/pricing.ts` `calcPrice()` (type `package`) + `transportQuote(…, true)` |
| BR-20 | ① เต็ม → ② % สูงสุด 1 อัน → ③ แต้ม → ④ รถ → ⑤ Gift Card/อื่น · สรุป = เก็บจริง | `lib/rules/pricing.ts` `calcPrice()` · `createBooking()` ตรวจ `quotedTotal` (409 ถ้าไม่เท่า) |

| FR | ไฟล์หลัก |
|---|---|
| FR-01–06, 10, 12, 14, 20–23, 31 | `components/BookingWizard.tsx`, `app/book/page.tsx`, `lib/server/booking.ts` (`availableSlots`, `buildQuote`, `createBooking`), `app/api/slots`, `app/api/price`, `app/api/bookings` |
| FR-07, FR-17 | `components/MyBookings.tsx`, `lib/server/customer.ts` `myBookings()`, `cancelBooking()` |
| FR-08 | `components/TherapistList.tsx`, `lib/server/catalog.ts` `listTherapists()` |
| FR-09, FR-11, FR-12 | `app/account/page.tsx`, `lib/server/customer.ts` `accountSummary()` |
| FR-13, FR-15, FR-16, FR-18 | `app/wallet/page.tsx`, `components/WaistChart.tsx`, `lib/server/customer.ts` `wallet()`, `lib/server/store.ts` `buyCourse()`, `photoForViewer()`, `app/api/photos/[id]` |
| FR-19, FR-20 | `components/GiftCardShop.tsx`, `lib/server/store.ts` `buyGiftCard()`, `giftCardInfo()` |
| FR-21 | `app/package/page.tsx`, `components/PackageCalc.tsx` |
| FR-22 | `components/TransportCalc.tsx`, `app/api/transport` |
| FR-24 | `components/LangSwitcher.tsx`, `lib/i18n.ts` (cookie `lang`) |
| FR-25, FR-26 | `components/ChatBox.tsx`, `lib/bot/chat.ts` (เรียก `buildQuote`/`createBooking` ตัวเดียวกับเว็บ) |
| FR-27 | `components/MoodPicker.tsx`, `lib/bot/mood.ts` |
| FR-28 | `components/Quiz.tsx`, `lib/bot/quiz.ts` |
| FR-29, FR-30 | `components/SkinAnalyzer.tsx` (Canvas ในเบราว์เซอร์ ไม่อัปโหลด ไม่เก็บ storage) |
| FR-32 | `components/ThaiOrnament.tsx`, `app/globals.css` |
| FR-33 | `components/Tour360.tsx` (pointer events = เมาส์ + นิ้ว, ลูกศรคีย์บอร์ด) |
| FR-34 | `components/MusicToggle.tsx` (Web Audio API เริ่มเมื่อกดปุ่มเท่านั้น) |
| FR-35 | ไม่มี `<input type="file">` ยกเว้นหน้า `/skin` (เซลฟี่ไม่ถูกเก็บ) · db ไม่มีคอลัมน์รูปโปรไฟล์ |

ข้อเสนอจาก DESIGN ที่ใช้: D1 ยกเลิก ≥ 24 ชม. คืนครั้ง · D2 คืนแต่ใช้ไม่ได้หลังหมดอายุ · D3 มี /admin · D4 คืนสิทธิ์เดือนเกิดถ้ายังไม่เลยเดือนนั้น · D5 กันครั้งตอนจอง ตัดตอนเสร็จ · D6 คอร์ส 60 นาที · D7 "ใครก็ได้" = คนว่าง id น้อยสุด · D8 ยกเลิกทั้งนัด · D9/T3 ไม่ล็อกอินจองด้วยชื่อ+เบอร์ ไม่ได้แต้ม · D10 ไม่ต่อระบบจ่ายจริง (`other_paid` = จ่ายที่ร้าน) · D11 แต้มให้ตอนร้านกดเสร็จ · D12 ทุกคนทำงาน 10:00–22:00 · D13 ราคาต่าง → 409 กลับไปดูสรุป · D14 แชทขอชื่อ+เบอร์ (ถ้าล็อกอินใช้บัญชี) · D15 รูปเก็บนอก web root เสิร์ฟผ่าน API ตรวจเจ้าของ

สมมติฐานเพิ่มที่โค้ดใช้ (เอกสารไม่ระบุ): ยอดสะสมเพิ่มตอนร้านกดเสร็จด้วยยอดจ่ายไม่รวมค่ารถ (A10) · การซื้อคอร์สนับยอดสะสมทันที (E61) และไม่ได้แต้ม (A8) · Gift Card ที่หมดอายุ/ยอด ฿0 ใบสรุปแสดง error แต่ไม่หักบัตร และจองต่อได้โดยจ่ายช่องทางอื่นเต็มจำนวน · แลกแต้มใช้ก้อนเท่าที่จำเป็น (ยอด ฿80 แลก 2 ก้อนลดได้ ฿80) · แพ็กเกจแลกแต้มได้ · แชทจองได้เฉพาะบริการเดี่ยว 1 คน · เบอร์ร้าน 02-123-4567 (สมมติ)

---

## 5. ข้อความ error (คำต่อคำ 3 ภาษา)

API ตอบ `{"error": "<CODE>", "message": "<ข้อความ>", ...}` ภาษาตาม cookie `lang` (ไม่มี = ไทย) · CODE ที่มี `phone` จะแนบ `"phone":"02-123-4567"`

| CODE | HTTP | ไทย | English | 中文 |
|---|---|---|---|---|
| `SLOT_TAKEN` | 409 | เวลานี้ถูกจองแล้ว | This time is already booked | 该时段已被预订 |
| `GROUP_CALL_SHOP` (+phone) | 422 | กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน | Groups of 7 or more, please call the shop | 7人及以上团体请致电本店 |
| `OUT_OF_AREA` | 422 | อยู่นอกพื้นที่รับส่ง | Outside the pickup area | 超出接送范围 |
| `GC_EXPIRED` | (ใน `giftCardError` ของใบสรุป / สถานะบัตร) | บัตรหมดอายุแล้ว | This card has expired | 此卡已过期 |
| `GC_EMPTY` | (ใน `giftCardError`) | บัตรนี้ไม่มียอดคงเหลือ | This card has no balance left | 此卡余额为零 |
| `GC_NOT_FOUND` | 422 / 404 | ไม่พบ Gift Card นี้ | Gift card not found | 未找到该礼品卡 |
| `GC_VALUE` | 422 | มูลค่าต้องเป็นจำนวนเต็ม ฿500–฿10,000 | Value must be a whole number from ฿500 to ฿10,000 | 面值须为 500–10,000 泰铢的整数 |
| `GC_FIELDS` | 422 | กรุณาเลือกลาย ช่องทาง และกรอกผู้รับ | Please choose a design, channel and recipient | 请选择卡面、发送方式并填写收件人 |
| `DATE_OUT_OF_RANGE` | 422 | เลือกวันได้ตั้งแต่พรุ่งนี้ถึงอีก 30 วัน | Choose a date from tomorrow up to 30 days ahead | 只能选择明天起30天内的日期 |
| `SLOT_INVALID` | 422 | ไม่มีรอบเวลานี้ | This time slot does not exist | 没有这个时段 |
| `SINGLE_ONE` | 422 | จองเดี่ยวได้ 1 คน | Single booking is for 1 person | 单人预约限1人 |
| `COUPLE_NEEDS_2` | 422 | จองคู่ต้องมี 2 คนพอดี (3 คนขึ้นไปให้จองกลุ่ม) | Couple booking needs exactly 2 people (3+ please book a group) | 双人预约须为2人（3人以上请团体预约） |
| `GROUP_TOO_SMALL` | 422 | จองกลุ่มต้องมี 3–6 คน (1–2 คนให้จองเดี่ยวหรือคู่) | Group booking needs 3–6 people (1–2 please book single or couple) | 团体预约需3–6人（1–2人请单人或双人预约） |
| `BAD_PEOPLE` | 422 | จำนวนคนไม่ถูกต้อง | Invalid number of people | 人数无效 |
| `THERAPIST_INVALID` | 422 | นักบำบัดที่เลือกทำบริการนี้ไม่ได้ | The selected therapist does not offer this service | 所选理疗师不提供此服务 |
| `SERVICE_INVALID` | 422 | ไม่พบบริการนี้ หรือแบบการจองไม่ตรงกับบริการ | Service not found or does not match the booking type | 未找到服务或与预约类型不符 |
| `PRICE_CHANGED` | 409 | ราคาเปลี่ยน กรุณาตรวจสอบสรุปอีกครั้ง | The price has changed, please review the summary again | 价格已变更，请重新确认汇总 |
| `CANCEL_TOO_LATE` (+phone) | 422 | เหลือเวลาน้อยกว่า 24 ชม. ยกเลิกเองไม่ได้ กรุณาโทรหาร้าน | Less than 24 hours left — please call the shop to cancel | 距离预约不足24小时，无法自行取消，请致电本店 |
| `CANCEL_NOT_ALLOWED` | 422 | นัดนี้ยกเลิกไม่ได้ | This appointment cannot be cancelled | 此预约无法取消 |
| `COURSE_UNAVAILABLE` | 422 | ใช้คอร์สนี้ไม่ได้ (เหลือ 0 ครั้งหรือหมดอายุ) | This course cannot be used (0 sessions left or expired) | 此疗程无法使用（剩余0次或已过期） |
| `POINTS_NOT_ENOUGH` | 422 | แต้มไม่พอแลก | Not enough points | 积分不足 |
| `BIRTHDAY_UNAVAILABLE` | 422 | ใช้ส่วนลดเดือนเกิดไม่ได้ | Birthday discount is not available | 无法使用生日折扣 |
| `CONTACT_REQUIRED` | 422 | กรุณากรอกชื่อและเบอร์โทร | Please enter your name and phone | 请填写姓名和电话 |
| `QUOTE_REQUIRED` | 422 | ต้องส่งยอดที่แสดงในหน้าสรุป (quotedTotal) | quotedTotal from the summary is required | 需要提供汇总金额 quotedTotal |
| `BAD_DISTANCE` | 422 | ระยะทางไม่ถูกต้อง | Invalid distance | 距离无效 |
| `BAD_REQUEST` | 422 | ข้อมูลไม่ถูกต้อง | Invalid request | 请求无效 |
| `NOT_CONFIRMED` | 422 | นัดนี้ไม่ได้อยู่ในสถานะยืนยัน | This appointment is not confirmed | 此预约不是已确认状态 |
| `LOGIN_REQUIRED` | 401 | กรุณาเข้าสู่ระบบ | Please log in | 请登录 |
| `LOGIN_FAILED` | 401 | อีเมลหรือรหัสผ่านไม่ถูกต้อง | Incorrect email or password | 邮箱或密码错误 |
| `FORBIDDEN` | 403 | ไม่มีสิทธิ์เข้าถึง | Access denied | 无权访问 |
| `NOT_FOUND` | 404 | ไม่พบข้อมูล | Not found | 未找到 |
| `SERVER` | 500 | ระบบขัดข้อง กรุณาลองใหม่ | Something went wrong, please try again | 系统错误，请重试 |

ข้อความบนหน้าจอที่ไม่ใช่ error แต่ใช้ตรวจบ่อย:

| key | ไทย | English | 中文 |
|---|---|---|---|
| ยืนยันการจอง | จองสำเร็จ! รหัสการจอง {code} | Booking confirmed! Code {code} | 预约成功！预约号 {code} |
| ระดับถัดไป | อีก ฿{X} ถึง {Gold/Platinum} | ฿{X} more to {tier} | 还差 ฿{X} 升级到 {tier} |
| ระดับสูงสุด | อยู่ระดับสูงสุดแล้ว | You are at the top tier | 已是最高等级 |
| Wallet | เหลือ {r} จาก {t} ครั้ง | {r} of {t} sessions left | 剩余 {r} / {t} 次 |
| รอบเอว | ลดไปแล้ว {x} ซม. | Reduced {x} cm | 已减少 {x} 厘米 |
| ยกเลิกไม่ได้ (บัญชี) | เหลือน้อยกว่า 24 ชม. ยกเลิกเองไม่ได้ กรุณาโทรหาร้าน | Less than 24 hours left. Please call the shop | 不足24小时，无法自行取消，请致电本店 |
| สถานะนัด | ยืนยัน / ยกเลิก / ใช้บริการแล้ว | Confirmed / Cancelled / Completed | 已确认 / 已取消 / 已完成 |
| ภาพจำลอง | ภาพจำลอง ผลจริงแต่ละคนต่างกัน | Simulation only — actual results vary by person | 仅为模拟效果，实际效果因人而异 |
| ส่ง Gift Card (จำลอง) | ส่งบัตรทาง {LINE/อีเมล} ถึง {ผู้รับ} แล้ว (จำลอง — ไม่ได้ส่งจริง) | Card sent via {channel} to {to} (simulated — not actually sent) | 已通过 {channel} 发送给 {to}（模拟，未实际发送） |
| ไม่มีรีวิว | ยังไม่มีรีวิว | No reviews yet | 暂无评价 |

---

## 6. API

ทุกเส้นตอบ JSON · เงินในฟิลด์ตัวเลขเป็น **บาท** (เช่น `1187.5`) · ฟิลด์ `*Label` เป็นข้อความแสดงผล (`฿1,187.50`) · auth = cookie `sabai_session` (httpOnly) จาก `/api/auth/login`

| method | path | body / query | ตอบกลับ | สถานะ |
|---|---|---|---|---|
| GET | `/api/health` | — | `{"ok":true,"db":true}` (ต่อ db ไม่ได้ → `db:false` ไม่ throw) | 200 |
| POST | `/api/test/reset` | `{"now"?: ISO}` (ไม่ส่ง = `2026-10-10T10:00:00+07:00`) | `{"ok":true,"now":"2026-10-10T10:00:00+07:00"}` · TRUNCATE ทุกตาราง + รัน seed ใน transaction เดียว | 200 · 422 now ผิด · 404 เมื่อ `ALLOW_TEST_RESET≠1` |
| GET | `/api/test/today` | — | `{"now","today"}` | 200 · 404 |
| POST | `/api/auth/login` | `{"email","password"}` | `{"ok":true,"user":{id,name,email,role}}` + Set-Cookie | 200 · 401 `LOGIN_FAILED` |
| POST | `/api/auth/logout` | — | `{"ok":true}` | 200 |
| GET | `/api/services` | `?lang=` | `{"services":[{code,name,kind,durationMin,price,herbs[],image}]}` | 200 |
| GET | `/api/therapists` | `?min=4.5` `?service=S01` | `{"therapists":[{code,name,rating:"5.0"\|null,ratingTenths,reviewCount,passes45,services[]}]}` | 200 |
| GET | `/api/hotels` | — | `{"hotels":[{code,name,distanceKm}]}` | 200 |
| GET | `/api/slots` | `service, date, type=single\|couple\|group\|package\|course, people` | `{"date","min","max","durationMin","slots":[{time,endTime,available,therapists:[{code,name}]}]}` (รอบที่จบเกิน 22:00 ไม่อยู่ในรายการ) | 200 · 422 (`DATE_OUT_OF_RANGE`, `SERVICE_INVALID`, party codes) |
| POST | `/api/price` | BookingInput (ด้านล่าง ไม่ต้องมี quotedTotal) | ใบสรุป: `gross, discountKind, discountPct, discountAmount, pointsRedeemed, pointsDiscount, subtotal, distanceKm, vehicles, transportFee, total, totalLabel, giftcardPaid, otherPaid, pointsToEarn, lines[{key,label,amount,display}], birthdayAvailable, maxRedeemBlocks, pointsBalance, course, giftCard{status,balance,balanceAfter}, giftCardError{code,message}\|null, service{herbs}` | 200 · 401 (คอร์ส/แลกแต้มต้องล็อกอิน) · 422 |
| POST | `/api/bookings` | BookingInput + `quotedTotal` | `{"bookingId","code":"B14","status":"confirmed","total","totalLabel","therapists":["T06"],"therapistNames","message":"จองสำเร็จ! รหัสการจอง B14","detail","quote"}` | 201 · 409 `SLOT_TAKEN` / `PRICE_CHANGED` (แนบ `total`, `quote`) · 422 · 401 |
| POST | `/api/bookings/:id/cancel` | `:id` = เลข id หรือ `B05` | `{"ok":true,"bookingId","code","status":"cancelled"}` | 200 · 401 · 403 (นัดคนอื่น) · 404 · 422 `CANCEL_TOO_LATE` (+phone) / `CANCEL_NOT_ALLOWED` |
| GET | `/api/me` | — | `{id,name,email,role,points,maxRedeemBlocks,tier,tierLabel,tierPct,lifetimeSpend,nextTier,remainingToNext,tierMessage,birthMonth,birthdayThisMonth:"none"\|"available"\|"used"}` | 200 · 401 |
| GET | `/api/me/bookings` | — | `{"bookings":[{id,code,serviceName,date,time,endTime,therapists[],status,statusLabel,total,totalLabel,viaCourse,canCancel,cancelBlockedReason}]}` เรียงล่าสุด→เก่าสุด | 200 · 401 |
| GET | `/api/wallet` | — | `{"courses":[{id,code,total,used,reserved,remaining,remainingLabel,purchasedOn,expiresOn,daysLeft,expired,usable}],"waist":[{date,cm}],"waistReducedCm","photos":[{id,phase,url}]}` | 200 · 401 |
| POST | `/api/courses` | — | `{id,code,price:15000,total:11,remaining:11,purchasedOn,expiresOn,message}` · ยอดสะสม +฿15,000 | 201 · 401 |
| GET | `/api/photos/:id` | — | ไฟล์รูป (image/webp, no-store) | 200 · 401 ไม่ล็อกอิน · 403 ไม่ใช่เจ้าของ · 404 |
| POST | `/api/giftcards` | `{"value":int,"design":"orchid\|lotus\|gold","channel":"line\|email","recipient","message"?}` | `{code,value,design,channel,recipient,purchasedOn,expiresOn,expiresLabel,simulated:true,sentMessage,preview}` | 201 · 422 `GC_VALUE`/`GC_FIELDS` |
| GET | `/api/giftcards/:code` | — | `{code,faceValue,balance,balanceLabel,design,purchasedOn,expiresOn,status:"ok"\|"expired"\|"empty",message}` | 200 · 404 `GC_NOT_FOUND` |
| GET | `/api/transport` | `distance` หรือ `hotel=H04`, `people` (1–6), `package=1` | `{distanceKm,people,vehicles,perVehicle,fee,feeLabel,free}` | 200 · 422 `OUT_OF_AREA` / `BAD_DISTANCE` / `BAD_PEOPLE` |
| POST | `/api/chat` | `{"message","state"?}` (ส่ง `state` จากคำตอบก่อนกลับมาทุกครั้ง) | `{"reply","lang","state",booking?:{bookingId,code,total}}` | 200 · 422 |
| GET | `/api/mood` | `mood=stressed\|tired\|aches\|insomnia` | `{mood,reason,services:[…]}` (1–3 รายการ) | 200 · 422 |
| GET | `/api/quiz` | — | `{"questions":[{id,text,options[{value,label}]}]}` (4 ข้อ) | 200 |
| POST | `/api/quiz` | `{"answers":{"goal","time","pressure","stay"}}` | `{code,name,price,image,reason}` | 200 · 422 |
| GET | `/api/admin/bookings` | `date=YYYY-MM-DD` | `{date,today,bookings:[{id,code,time,customer,member,service,type,people,therapists[],status,total,totalLabel,viaCourse,pointsEarned}]}` | 200 · 401 · 403 (ไม่ใช่ owner) |
| POST | `/api/admin/bookings/:id/complete` | `{"waistCm"?: number}` | `{ok,bookingId,code,status:"completed",pointsEarned}` (แต้ม BR-09 + ยอดสะสม · คอร์ส reserved−1 used+1 · บันทึกรอบเอว) | 200 · 401 · 403 · 404 · 422 `NOT_CONFIRMED` |

**BookingInput**

```json
{
  "type": "single | couple | group | package | course",
  "serviceCode": "S01",            // package → P01, course → K01 (ละได้)
  "people": 1,                     // couple = 2, group = 3–6, package = 1–6
  "date": "2026-10-20", "time": "10:00",
  "therapists": ["T04"],           // ไม่ส่ง = ระบบจัดคนว่าง id น้อยสุด (D7) · ถ้าส่งต้องเท่าจำนวนคน
  "contactName": "…", "contactPhone": "…",   // จำเป็นเมื่อไม่ล็อกอิน
  "redeemBlocks": 0,               // จำนวนก้อน 100 แต้ม
  "useBirthday": false,
  "giftCardCode": "SABAI-GC-2000",
  "hotelCode": "H04",              // หรือ "distanceKm": 12.0
  "coursePurchaseId": 1,           // type course (ไม่ส่ง = คอร์สที่ใช้ได้และหมดอายุก่อน)
  "quotedTotal": 3800              // POST /api/bookings เท่านั้น: ต้องเท่ายอดที่คิดใหม่ ไม่งั้น 409
}
```

---

## 7. ผู้ใช้ seed

| รหัส | อีเมล | รหัสผ่าน | ใช้ทดสอบ |
|---|---|---|---|
| U01 | nida@sabai.test | Nida@2026 | Gold ฿12,400 · 99 แต้ม (แลกไม่ได้) · คอร์ส C01 เหลือ 7/11 · กราฟรอบเอว 4 จุด · รูป before/after · ประวัติ 8 แถว · ยกเลิก B05 (24 ชม.) / B06 (วันนี้) |
| U02 | ton@sabai.test | Ton@2026 | Platinum ฿30,000 · เกิด ต.ค. ยังไม่ใช้สิทธิ์ · จองคู่ B02 · GC03 |
| U03 | may@sabai.test | May@2026 | สมาชิกใหม่ Silver ฿0 ไม่มีนัด · ซื้อคอร์สใหม่ (E61) |
| U04 | fon@sabai.test | Fon@2026 | Silver ฿9,999 · 250 แต้ม · เจ้าของ GC01 (฿2,000) GC05 (฿0) · B01 |
| U05 | prae@sabai.test | Prae@2026 | Gold ฿29,999 · 100 แต้ม · ใช้สิทธิ์เดือนเกิด ต.ค. แล้ว · C04 หมดอายุ · GC04 หมดอายุ |
| U06 | vipa@sabai.test | Vipa@2026 | Platinum ฿45,000 · 199 แต้ม · C03 เหลือ 0 · GC02 |
| U07 | kan@sabai.test | Kan@2026 | Gold ฿10,000 · C02 เหลือ 1 หมดอายุ 20 ต.ค. |
| U08 | liwei@sabai.test | LiWei@2026 | นักท่องเที่ยว ภาษา zh · กลุ่ม B04 · แพ็กเกจ รถรับส่ง |
| owner | owner@sabai.test | Owner@2026 | role owner → `/admin` ตารางคิว + กดใช้บริการเสร็จ + รีเซ็ต |
| (ไม่ล็อกอิน) | — | — | จองด้วยชื่อ+เบอร์ (ไม่ได้แต้ม) · B03 คุณสมชาย 081-000-0003 |

Gift Card: `SABAI-GC-2000` (GC01) · `SABAI-GC-PART` (GC02) · `SABAI-GC-LAST` (GC03 วันนี้วันสุดท้าย) · `SABAI-GC-EXP` (GC04 หมดอายุ) · `SABAI-GC-ZERO` (GC05 ยอด ฿0)
โรงแรม: H01 2.0 · H02 5.0 · H03 5.1 · H04 12.0 · H05 15.0 · H06 15.1 กม.

---

## 8. data-testid

ทุกปุ่ม/ช่องกรอกมีชื่อที่ `getByRole` หาได้ (ข้อความ, `<label>` หรือ `aria-label`) · `{code}` = รหัสบริการ/นัด/คอร์ส เช่น `S01`, `B05`, `C01` · `{HH:MM}` เช่น `20:30`

### ทุกหน้า (layout)

| testid | คืออะไร |
|---|---|
| `brand-link` | โลโก้ → หน้าแรก |
| `music-toggle` | ปุ่มเปิด/ปิดเพลง (`aria-pressed`, `data-playing="true|false"`) |
| `lang-switcher` · `lang-th` `lang-en` `lang-zh` | กลุ่มปุ่มภาษา / ปุ่มแต่ละภาษา (`aria-pressed`) |
| `nav-login` · `logout-button` | เข้าสู่ระบบ / ออกจากระบบ |
| `nav-toggle` | ปุ่มเมนู (มือถือ, `aria-expanded`) |
| `nav-home` `nav-services` `nav-book` `nav-package` `nav-therapists` `nav-giftcard` `nav-transport` `nav-chat` `nav-quiz` `nav-skin` `nav-account` `nav-wallet` `nav-admin` | ลิงก์เมนู (account/wallet เมื่อล็อกอิน · admin เมื่อเป็น owner) |
| `footer-phone` | เบอร์ร้านท้ายหน้า |
| `chat-fab` | ปุ่มแชทลอย |

### `/` หน้าแรก

| testid | คืออะไร |
|---|---|
| `home-hero` · `home-title` | hero / หัวข้อ |
| `home-book` · `home-package` | ปุ่มจองคิว / ดูแพ็กเกจ |
| `mood-section` | กล่องอารมณ์วันนี้ |
| `mood-stressed` `mood-tired` `mood-aches` `mood-insomnia` | ปุ่มอารมณ์ (`role=radio`, `aria-checked`) |
| `mood-result` · `mood-reason` | ผลแนะนำ / เหตุผล |
| `mood-rec-{code}` · `mood-book-{code}` | บริการที่แนะนำ / ปุ่มจองต่อ |
| `home-svc-{code}` · `home-book-{code}` | การ์ดบริการยอดนิยม / ปุ่มจอง |
| `home-quiz` `home-skin` `home-chat` | ลิงก์ไปแบบทดสอบ/วิเคราะห์ผิว/แชท |

### `/services`

| testid | คืออะไร |
|---|---|
| `service-card-{code}` | การ์ดบริการ |
| `service-name-{code}` · `service-price-{code}` · `service-herbs-{code}` | ชื่อ / ราคา / รายการสมุนไพร |
| `service-book-{code}` | ปุ่มจอง |

### `/book` จอง 4 ขั้น

| testid | คืออะไร |
|---|---|
| `book-step-indicator` | "ขั้นที่ n จาก 4" (`data-step`) |
| `book-type-single` `book-type-couple` `book-type-group` `book-type-package` `book-type-course` | radio แบบการจอง (`book-type-label-*` = label) |
| `book-service` | select บริการ |
| `book-people` | จำนวนคน (คู่/กลุ่ม/แพ็กเกจ) |
| `book-service-herbs` | สมุนไพรของบริการที่เลือก (ขั้น 1) |
| `book-tour-open` · `book-tour-open-2` | ปุ่ม "ดูห้อง 360°" (ขั้น 1 / ขั้น 2 เมื่อจองคู่) |
| `book-next-1` `book-next-2` `book-next-3` | ปุ่มถัดไป |
| `book-back-2` `book-back-3` `book-back-4` | ปุ่มย้อนกลับ |
| `book-error` · `book-error-message` | กล่อง error (`data-error-code`) / ข้อความ |
| `shop-phone` | เบอร์ร้านใน error (กลุ่ม 7+) |
| `book-date` | วันที่ (`min`/`max` = พรุ่งนี้ถึง +30) |
| `book-slots` · `book-slot-{HH:MM}` | กลุ่มรอบว่าง / ปุ่มรอบ (`aria-pressed`) |
| `book-no-slots` | ข้อความไม่มีรอบว่าง |
| `book-therapist` | select นักบำบัด (จองเดี่ยว) |
| `book-contact-name` · `book-contact-phone` | ชื่อ / เบอร์ |
| `book-course` · `book-course-none` | select คอร์ส / ข้อความไม่มีคอร์สที่ใช้ได้ |
| `book-points` · `book-points-info` · `book-points-none` | select จำนวนครั้งแลกแต้ม (disabled เมื่อแต้ม < 100) / แต้มที่มี / ข้อความแต้มไม่พอ |
| `book-birthday` · `book-birthday-label` | checkbox ส่วนลดเดือนเกิด (แสดงเมื่อเข้าเงื่อนไข) |
| `book-giftcard` · `book-giftcard-apply` | รหัส Gift Card / ปุ่มใช้บัตร |
| `book-giftcard-info` · `book-giftcard-after` · `book-giftcard-error` | ยอดในบัตร / ยอดคงเหลือหลังใช้ / error บัตร (`data-error-code`) |
| `book-transport` · `book-hotel` · `book-distance` | checkbox รถรับส่ง / select โรงแรม / ระยะทาง |
| `book-quote-error` · `book-quote-error-message` | error จากใบเสนอราคา (เช่น อยู่นอกพื้นที่รับส่ง) |
| `book-quote-total` | ยอดสุทธิล่าสุด (ขั้น 3) |
| `book-summary` | กล่องสรุปขั้น 4 |
| `summary-service` · `summary-when` | บริการ / วันเวลา |
| `book-herbs` | สมุนไพรในหน้ายืนยัน (FR-31) |
| `summary-lines` | ตารางราคา |
| `summary-line-{key}` · `summary-amount-{key}` | แถว / จำนวนเงิน (`data-amount` บาท) · key: `gross` `discount` `points` `transport` `total` `giftcard` `other` `course` |
| `summary-total` | ยอดสุทธิ (`data-amount`) |
| `book-earn-points` | แต้มที่จะได้หลังใช้บริการ |
| `book-course-after` | "เหลือ X จาก 11 ครั้ง" หลังจองด้วยคอร์ส |
| `book-confirm` | ปุ่มยืนยันการจอง |
| `booking-done` · `booking-confirmation` | กล่อง/ข้อความยืนยัน "จองสำเร็จ! รหัสการจอง B14" |
| `booking-detail` · `booking-therapists` · `booking-code` | รายละเอียด / นักบำบัด / รหัส (hidden) |
| `book-again` | จองอีกครั้ง |
| `tour-dialog` · `tour-view` · `tour-angle` · `tour-close` | ทัวร์ 360° (`tour-view` เป็น `role=slider`, `data-angle` 0–359) |

### `/package`

| testid | คืออะไร |
|---|---|
| `package-card` · `package-title` · `package-price` | การ์ด / ชื่อ / ราคาต่อคน (`data-amount`) |
| `package-includes` · `package-item-1..3` | สิ่งที่ได้ 3 อย่าง |
| `package-people` · `package-total` · `package-book` | จำนวนคน / ราคารวม (`data-amount`) / ปุ่มจอง |

### `/therapists`

| testid | คืออะไร |
|---|---|
| `filter-45` | checkbox "4.5 ดาวขึ้นไป" |
| `therapist-count` | "แสดง n คน" |
| `therapist-{T01}` · `therapist-name-{T01}` | การ์ด / ชื่อ |
| `therapist-rating-{T01}` | คะแนน "5.0" หรือ "ยังไม่มีรีวิว" |
| `therapist-reviews-{T01}` · `therapist-book-{T01}` | จำนวนรีวิว / ปุ่มจอง |

### `/transport`

| testid | คืออะไร |
|---|---|
| `transport-rule` | ข้อความกติกา |
| `transport-hotel` · `transport-distance` · `transport-people` · `transport-calc` | โรงแรม / ระยะ / จำนวนคน / ปุ่มคำนวณ |
| `transport-result` · `transport-fee` · `transport-vehicles` | ผล / ค่ารถ (`data-amount`) / จำนวนคัน |
| `transport-error` | "อยู่นอกพื้นที่รับส่ง" |

### `/giftcard`

| testid | คืออะไร |
|---|---|
| `gc-value` | มูลค่า |
| `gc-design-orchid` `gc-design-lotus` `gc-design-gold` | radio ลาย (`gc-design-label-*` = label) |
| `gc-preview` | ตัวอย่างบัตร |
| `gc-channel-line` `gc-channel-email` | radio ช่องทาง (`gc-channel-label-*` = label) |
| `gc-recipient` · `gc-message` · `gc-submit` | ผู้รับ / ข้อความ / ปุ่มซื้อและส่ง |
| `gc-error` | error (มูลค่า/ข้อมูลไม่ครบ) |
| `gc-result` · `gc-sent` · `gc-code` · `gc-expires` · `gc-preview-text` | ผล / ข้อความ "ส่ง" (จำลอง) / รหัส / วันหมดอายุ / ข้อความที่ส่ง |
| `gc-check-code` · `gc-check-submit` | ช่องรหัส / ปุ่มตรวจยอด |
| `gc-check-result` · `gc-check-status` · `gc-check-balance` · `gc-check-expires` · `gc-check-error` | ผล (`data-status`) / "ใช้ได้" หรือ "บัตรหมดอายุแล้ว" / ยอด / วันหมดอายุ / ไม่พบบัตร |

### `/chat` `/quiz` `/skin`

| testid | คืออะไร |
|---|---|
| `chat-log` · `chat-bot-msg` · `chat-user-msg` | กล่องข้อความ / ข้อความผู้ช่วย / ข้อความผู้ใช้ |
| `chat-input` · `chat-send` | ช่องพิมพ์ / ปุ่มส่ง |
| `quiz` · `quiz-progress` · `quiz-question` | แบบทดสอบ / "ข้อ n/4" (`data-current`) / คำถาม |
| `quiz-option-{value}` · `quiz-back` | ตัวเลือก / ย้อนกลับ |
| `quiz-result` · `quiz-package` · `quiz-reason` · `quiz-book` · `quiz-restart` | ผล / แพ็กเกจ (`data-code`) / เหตุผล / ปุ่มจอง / ทำใหม่ |
| `skin-notice` · `skin-accept` | ข้อความแจ้งก่อนเลือกรูป / ปุ่มรับทราบ |
| `skin-file` · `skin-sample` | input รูปเซลฟี่ / ใช้ภาพตัวอย่าง |
| `skin-type` · `skin-metrics` | ผลวิเคราะห์ (`data-type`) / ค่าที่วัด |
| `skin-recs` · `skin-rec-{code}` · `skin-book-{code}` | ทรีตเมนต์แนะนำ / ปุ่มจอง |
| `skin-sim` · `sim-label` | ภาพจำลองก่อน/หลัง / ป้าย "ภาพจำลอง ผลจริงแต่ละคนต่างกัน" |

### `/login` `/account` `/wallet`

| testid | คืออะไร |
|---|---|
| `login-email` · `login-password` · `login-submit` · `login-error` · `test-accounts` | ฟอร์มล็อกอิน / รายชื่อบัญชีทดสอบ |
| `account-login` · `wallet-login` | ปุ่มไปล็อกอิน (เมื่อยังไม่ล็อกอิน) |
| `account-hello` | "สวัสดี {ชื่อ}" |
| `account-tier-card` · `account-tier` · `account-tier-pct` · `account-spend` · `account-tier-message` | ระดับ (`data-tier`) / ส่วนลด / ยอดสะสม (`data-amount`) / "อีก ฿X ถึง …" |
| `account-points` | แต้มคงเหลือ (`data-points`) |
| `account-birthday` | สถานะเดือนเกิด (`data-state="available|used"`) |
| `account-wallet-link` | ไป Wallet |
| `history-list` · `booking-{B05}` | รายการนัด/ประวัติ / แถว (`data-status`) |
| `booking-service-{B05}` `booking-date-{B05}` `booking-therapist-{B05}` `booking-paid-{B05}` `booking-status-{B05}` | บริการ / วันเวลา / นักบำบัด / ราคาที่จ่าย / สถานะ ("ยกเลิก") |
| `cancel-{B05}` · `cancel-confirm-{B05}` · `cancel-abort-{B05}` | ปุ่มยกเลิก (disabled เมื่อ < 24 ชม.) / ยืนยัน / ย้อนกลับ |
| `cancel-blocked-{B05}` · `cancel-phone-{B05}` · `cancel-result-{B05}` | ข้อความให้โทรหาร้าน / เบอร์ / ผลยกเลิก |
| `course-{C01}` · `course-remaining-{C01}` · `course-expires-{C01}` | การ์ดคอร์ส (`data-remaining`, `data-expired`) / "เหลือ 7 จาก 11 ครั้ง" / วันหมดอายุ |
| `course-days-{C01}` · `course-expired-{C01}` · `course-book-{C01}` | "อีก N วัน" (`data-days`) / "หมดอายุแล้ว" / ปุ่มจองด้วยคอร์ส (disabled เมื่อใช้ไม่ได้) |
| `wallet-empty` | ยังไม่มีคอร์ส |
| `waist-chart` · `waist-point-{0..}` · `waist-reduced` · `waist-empty` | กราฟ / จุด (`data-date`, `data-cm`) / "ลดไปแล้ว X ซม." (`data-cm`) / ไม่มีข้อมูล |
| `body-photos` · `body-photo-before` · `body-photo-after` | รูป before/after |
| `buy-course` · `buy-course-result` | ปุ่มซื้อคอร์ส / ผล |

### `/admin`

| testid | คืออะไร |
|---|---|
| `admin-forbidden` · `admin-login` | ไม่มีสิทธิ์ / ปุ่มล็อกอิน |
| `admin-today` · `admin-date` | วันนี้ของระบบ / เลือกวันที่ |
| `admin-table` · `admin-empty` | ตารางคิว / ไม่มีคิว |
| `admin-row-{B05}` · `admin-status-{B05}` | แถว (`data-status`) / สถานะ |
| `admin-waist-{B08}` | รอบเอว (นัดคอร์ส) |
| `admin-complete-{B05}` · `admin-result-{B05}` | ปุ่ม "ใช้บริการเสร็จ" / ผล "+N แต้ม" |
| `admin-reset` · `admin-reset-result` | ปุ่มรีเซ็ตข้อมูลทดสอบ / ผล |
