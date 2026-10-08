# yolo1-verify — QA ตรวจรับเว็บ สบายใจ สปา

> สถานะโค้ดตอนตรวจ (2026-10-08 02:10 UTC): มีแค่ API (`spa/app/api/**`), `spa/lib/**`, `spa/components/*` (Header/Footer/ChatBot/MusicToggle/…) และ `spa/app/layout.tsx`
> **ยังไม่มีหน้าเว็บ (page.tsx) เลย, ไม่มี `globals.css`, `BUGS.md`, `SPEC.md`** → ข้อที่ต้องตรวจผ่าน UI ทำได้หลัง build เสร็จ

## 0. เตรียมก่อนตรวจ (ทุกข้อใช้ค่านี้)

```bash
B=http://localhost:3000
# ล็อกวันนี้ = พฤ. 2026-10-08 10:00 (BKK) → D1=2026-10-09, D2=2026-10-10, D30=2026-11-07, D31=2026-11-08
curl -s -X POST $B/api/test/reset -H 'Content-Type: application/json' -d '{"now":"2026-10-08T10:00:00+07:00"}'
# login (เก็บ cookie)  ใช้ nida / ton / new  รหัส Sabai1234!
curl -s -c nida.txt -X POST $B/api/auth/login -H 'Content-Type: application/json' -d '{"email":"nida@sabai.test","password":"Sabai1234!"}'
# ตั้งยอด/แต้ม/เดือนเกิดของสมาชิกเพื่อทดสอบค่าขอบ
curl -s -X POST $B/api/test/user -H 'Content-Type: application/json' -d '{"email":"new@sabai.test","totalSpent":9999,"points":99}'
```
- โรงแรม seed (`spa/lib/server/seed.ts:74-82`): id1=3.0 · id2=5.0 · id3=5.1 · id4=12.0 · id5=15.0 · id6=15.1 · id7=20.0 กม.
- seed สำคัญ: นิดา นัด D1 15:00 นักบำบัด 1 (`seed.ts:188`) · แขก A นัด D2 14:00–15:00 นักบำบัด 1 (`seed.ts:191`) · คู่ D2 18:00–19:30 Couple Suite นักบำบัด 2,3 (`seed.ts:192`) · Gift `GIFT-DAY365`/`GIFT-DAY366`/`GIFT-2000-ORCHID` (`seed.ts:203-205`)
- error message ภาษาตาม cookie `lang` (ค่าเริ่ม th) `spa/lib/server/http.ts:5-8`

---

## 1. เช็กลิสต์ตรวจรับ

### 1.1 BR (ทุกข้อที่มีตัวเลข)

| รหัส | วิธีตรวจที่เร็วที่สุด | ผลที่ต้องได้ |
|---|---|---|
| BR-01 | `GET $B/api/availability?service=thai-massage&date=2026-10-11` (อาทิตย์) และ `date=2026-10-13` (วันหยุด) | slots เริ่ม `10:00` ไม่มี `09:30` · ทั้ง 2 วัน ok:true |
| BR-02 | ผลเดียวกับข้างบน · `POST /api/bookings` time `"10:15"` | มี 10:00, 10:30 ไม่มี 10:15 · 10:15 → 400 `TIME_INVALID` |
| BR-03 | availability `thai-massage` / `aroma-oil` / `bangkok-relax` date=2026-10-12 | 60น.: 21:00=free 21:30=closed · 90น.: 20:30=free 21:00=closed · 120น.: 20:00=free 20:30=closed |
| BR-04 | `POST /api/bookings` `{"service":"thai-massage","date":"2026-10-10","time":"14:30","therapistId":1,"guestName":"QA","guestPhone":"0812345678"}` แล้วลอง time `13:00`, `15:00` | 14:30 → **409** `SLOT_TAKEN` message `"เวลานี้ถูกจองแล้ว"` · 13:00, 15:00 → 201 |
| BR-05 | availability date = `2026-10-08`/`10-09`/`11-07`/`11-08` · ข้ามเดือน: reset now `2026-10-31T10:00:00+07:00` แล้วลอง `2026-11-30`/`2026-12-01` · UI ปฏิทิน: วันที่นอกช่วงต้อง disabled | +0 → 400 `DATE_OUT_OF_RANGE` · +1 ok · +30 ok · +31 400 · 30 พ.ย. ok · 1 ธ.ค. 400 |
| BR-06 | `POST /api/quote` `{"service":"aroma-oil","people":1,"kind":"couple"}` (และ people 3) · booking couple `{"service":"aroma-oil","date":"2026-10-10","time":"18:00","people":2,"kind":"couple",...guest}` | 1/3 คน → 400 `COUPLE_NEEDS_TWO` · คู่ที่ 2 รอบ 18:00 D2 → 409 `"เวลานี้ถูกจองแล้ว"` |
| BR-07 | quote `{"service":"thai-massage","people":2,"kind":"group"}` / people 3 / 6 / 7 | 2 → 400 `GROUP_NEEDS_THREE` · 3,6 ok `kind:"group"` · 7 → 400 `"กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567"` |
| BR-08 | quote thai-massage people 3 / 4 / 6 | 3: groupDiscount 0 · 4: subtotal 3200 groupDiscount 320 → 2880 · 6: 4800→4320 (หมายเหตุ: ไม่มีบริการราคา ฿1,000 ใน seed จึงทดสอบตัวอย่าง ฿4,000→฿3,600 ตรง ๆ ไม่ได้) |
| BR-09 | reset now `2026-10-08T15:00:00+07:00` → login nida → `GET /api/bookings` เอา id นัด D1 15:00 → `POST /api/bookings/{id}/cancel` · ทำซ้ำด้วย now `14:59:00` และ `15:01:00` | 15:00 และ 14:59 → ok status cancelled และรอบนั้นกลับมา free ใน availability · 15:01 → 409 `CANCEL_TOO_LATE` · UI: `canCancel:false` → ปุ่มยกเลิก disabled + ข้อความให้ติดต่อร้าน |
| BR-10 | `GET /api/therapists?minRating=4.5` | ได้ id 1,2,4,5 (4.9/4.5/4.7/5.0) · ไม่มี id 3 (4.4) และ id 6 (0 รีวิว) |
| BR-11 | quote ของ nida thai-massage 1 คน (`-b nida.txt`) ดู `pointsEarned` · unit test `pointsFor(99/100/199/200/2950)` | 800−5%=760 → 7 แต้ม · 0/1/1/2/29 |
| BR-12 | test/user new `points:99` → quote `redeemSets:1` · ton (250) quote `redeemSets:3` | 99 → issue `POINTS_NOT_ENOUGH` · ton → redeemSets 2, pointsUsed 200, pointsDiscount 100 · จองแล้ว `/api/auth/me` points = 50 + แต้มที่ได้ |
| BR-13 | test/user new totalSpent 9999 / 10000 / 29999 / 30000 → `GET /api/auth/me` · login nida → me | silver / gold / gold / platinum · nida: tier gold, nextTierNeed **17600** |
| BR-14 | reset now `2026-10-08…` login ton (เกิด ต.ค., Platinum) quote thai-massage `useBirthday:true` · test/user ton `birthMonth:10` แล้ว reset now `2026-09-30`, `2026-10-31`, `2026-11-01` · จองด้วย useBirthday 2 ครั้ง | birthdayDiscount 160 → 640 (ไม่ใช่ 720 / 560) · 30 ก.ย./1 พ.ย. → `BIRTHDAY_NOT_ELIGIBLE` · 31 ต.ค. ได้ · ครั้งที่ 2 → `BIRTHDAY_NOT_ELIGIBLE` (ตัวอย่าง ฿1,000→฿800 ทำตรงไม่ได้ ไม่มีบริการ ฿1,000) |
| BR-15 | login new → `POST /api/courses` | 201 `total:11, left:11, price:15000, expiresOn = today+180` (2027-04-06) · วันที่ 180/181 **ทดสอบ E2E ไม่ได้** (ดูข้อ 2.1-G1) |
| BR-16 | login nida → `GET /api/wallet` · จอง `{"service":"body-contouring","payWith":"course",...}` | `left:7` · จองแล้ว left 6 · เหลือ 0 → `COURSE_EMPTY` และ UI ตัวเลือก "จองด้วยคอร์ส" disabled |
| BR-17 | `POST /api/giftcards` `{"amount":499,"design":"orchid","channel":"line","recipient":"line-qa"}` แล้ว 500 / 10000 / 10001, design `"rose"`, channel `"sms"` | 499,10001 → 400 `GIFT_AMOUNT` · 500,10000 → 201 `delivery.simulated:true` · design ผิด → `GIFT_DESIGN` · channel ผิด → `GIFT_CHANNEL` |
| BR-18 | `GET /api/giftcards/GIFT-DAY365` และ `/GIFT-DAY366` | 365 → `usable:true` · 366 → `status:"expired"` message `"Gift Card หมดอายุแล้ว"` |
| BR-19 | quote `{"service":"bangkok-relax","people":1}` / people 4 | subtotal 2900 / 11600 (แล้วลดกลุ่ม 10% → 10440) |
| BR-20 | `GET /api/transport?hotelId=2&people=1` … hotelId 3,4,5,6 | 5.0→fee 0 · 5.1→300 · 12→300 · 15.0→300 · 15.1→ ok:false `"ไม่มีบริการรับส่งสำหรับระยะนี้"` |
| BR-21 | `GET /api/transport?hotelId=4&people=4` / 5 / 6 | cars 1 / 2 / 2 · fee 300 / 600 / 600 |
| BR-22 | UI ปุ่ม `lang-th` `lang-en` `lang-zh` (`components/Header.tsx:115`) | มี 3 ปุ่มพอดี · เปลี่ยนหน้าแล้วภาษายังอยู่ (cookie `lang`) |
| BR-23 | UI หน้าเลือกอารมณ์ (ยังไม่มีหน้า) / unit `lib/recommend.ts` | ≥4 อารมณ์ ทุกอารมณ์แนะนำ 1–3 รายการ |
| BR-24 | UI แบบทดสอบ (ยังไม่มีหน้า) | ตอบ 3 ข้อยังไม่มีผล · ครบ 4 ข้อ = 1 แพ็กเกจ |
| BR-25 | DevTools Network ระหว่างวิเคราะห์ผิว/ภาพจำลอง | ไม่มี request ที่ส่งรูป (0 POST/PUT ที่มี image body) |

### 1.2 FR หลัก

| รหัส | วิธีตรวจ | ผลที่ต้องได้ |
|---|---|---|
| FR-01/03 | UI หน้า /book (ยังไม่มี): บริการ → วัน → รอบ → `booking-submit` | ≤4 ขั้น (NFR-03) · ปฏิทินเลือกได้เฉพาะ D1–D30 |
| FR-02/NFR-06 | ยิง booking BR-04 ที่รอบว่าง 2 ครั้งพร้อมกัน (`curl … & curl … & wait`) | 201 หนึ่งครั้งพอดี อีกครั้ง 409 `SLOT_TAKEN` |
| FR-05 | UI เลือก 7 คน | เห็น `"กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567"` ไม่มีปุ่มจอง |
| FR-06 | `POST /api/quote` + UI `price-total` | มีบรรทัด subtotal, groupDiscount, tier/birthdayDiscount, pointsDiscount, transportFee, total, pointsEarned |
| FR-07 | ดู BR-09 | ยกเลิกแล้วรอบกลับว่าง |
| FR-09 | `GET /api/account` (-b nida.txt) | tier gold, totalSpent 12400, points 124, nextTierNeed 17600, waist 4 จุด |
| FR-13 | `GET /api/wallet` | `courses[0].left:7`, `canBookWithCourse:true` |
| FR-16/17 | ดู BR-17/18 + จองด้วย `giftCode` | gift balance ลดตาม `giftUsed` |
| FR-19 | ดู BR-20/21 | แสดงระยะ ค่ารถ จำนวนรถ ก่อนจ่าย |
| FR-24/NFR-09 | เปิดหน้าแรก ไม่กดอะไร | ไม่มีเสียง · `music-toggle` เล่นเมื่อกดเท่านั้น |
| FR-27/28 | `chat-toggle` → `chat-input` "营业时间" → `chat-send` | ตอบเป็นจีน 10:00–22:00 · ถามซ้ำ 10 ครั้งได้คำตอบเดิม |
| FR-31 | `footer-privacy` | หน้า privacy มีข้อความ "ร้านไม่เก็บรูปใบหน้าลูกค้า" · ไม่มี `<input type=file>` ที่อัปโหลดขึ้น server |

### 1.3 NFR (ที่ทดสอบได้)

| รหัส | วิธีตรวจ | ผลที่ต้องได้ |
|---|---|---|
| NFR-01 | Playwright viewport 375×812 ทุกหน้า `scrollWidth <= 375` | ไม่มี scroll แนวนอน · ปุ่ม ≥44×44 |
| NFR-08 | login nida แล้ว `GET /api/account`, `/api/wallet` ด้วย cookie ton | เห็นแต่ข้อมูลของตัวเอง (query กรอง user_id ที่ `app/api/account/route.ts:15-19`, `wallet/route.ts:17-22`) |
| NFR-13 | `time curl -X POST $B/api/test/reset` 2 ครั้ง | ≤2 วินาที · ผลเหมือนกัน (nida 12400 / คอร์สเหลือ 7) |
| NFR-14 | reset `{"now":"2027-01-15T10:00:00+07:00"}` → `GET /api/config` | `today:"2027-01-15"`, `bookable.from:"2027-01-16"`, `to:"2027-02-14"` |
| NFR-15 | `<html data-ready="true" data-bug-mode="0">` | `data-bug-mode` = env, `data-ready` เป็น true หลังหน้าโหลดเสร็จ |
| health | `GET $B/api/health` | `{"ok":true,"db":true}` |

---

## 2. รีวิวโค้ด static

### 2.1 ตัวเลขกฎเทียบกับพรอมต์

| กฎ | ที่โค้ด | ผล |
|---|---|---|
| ระดับ ≥10,000 / ≥30,000 | `spa/lib/rules.ts:5-6`, `spa/lib/server/auth.ts:45-49` | ✅ ถูก (BUG_MODE=0) |
| เดือนเกิด 20% ใช้อันมากกว่า | `spa/lib/rules.ts:164-174`, `auth.ts:52-57` | ✅ Platinum 10% vs 20% → ใช้ 20% · ⚠️ ใช้ได้เฉพาะเมื่อ client ส่ง `useBirthday:true` ไม่ได้เลือกอันมากกว่าให้อัตโนมัติ (`booking.ts:242`) — UI ต้องมีตัวเลือก/ติ๊กให้เอง |
| แต้ม floor/100 | `spa/lib/rules.ts:43-45` | ✅ · คิดจาก `servicesNet` หลังส่วนลดและแต้ม (`rules.ts:198`) ไม่รวมค่ารถ — สมเหตุสมผล แต่ควรระบุใน SPEC |
| 100 แต้ม = ฿50 | `spa/lib/rules.ts:48-50, 177-179` | ✅ ขอเกินจะถูกตัดเหลือสูงสุดแบบเงียบ ๆ (ไม่มี error) |
| กลุ่ม ≥4 ลด 10% | `spa/lib/rules.ts:158` | ✅ |
| กลุ่ม 3–6 / 7 โทร | `spa/lib/rules.ts:34-40`, `booking.ts:265-274` | ✅ |
| ยกเลิก ≥24 ชม. | `spa/lib/time.ts:97-99` (`>=`) | ✅ 24 ชม.พอดียกเลิกได้ |
| ค่ารถ 5/15 กม., 4 คน/คัน | `spa/lib/rules.ts:63-68` | ✅ `<=5` ฟรี, `>15` ไม่รับ |
| gift 500–10,000 | `spa/app/api/giftcards/route.ts:23` | ✅ (ต้องเป็นจำนวนเต็ม) |
| gift 365 วัน | `giftcards/route.ts:30`, `booking.ts:155` (`today > expires_on`) | ✅ วันที่ 365 ใช้ได้ |
| คอร์ส 11 ครั้ง / 180 วัน | `spa/lib/rules.ts:16-18`, `app/api/courses/route.ts:17-20` | ✅ |
| เปิด 10–22, รอบ 30 น., จบ ≤22:00 | `spa/lib/time.ts:6-8, 73-82` | ✅ |
| จอง +1…+30 | `spa/lib/time.ts:84-94` | ✅ ใช้สตริงวันที่ BKK ข้ามเดือนถูก |
| นักบำบัด/Couple Suite ทับกัน | `spa/lib/server/booking.ts:93-118, 268` + advisory lock `:268` | ✅ ขอบชนพอดีไม่นับทับ (`:95`) |
| ตัวกรองรีวิว ≥4.5, 0 รีวิวไม่แสดง | `spa/app/api/therapists/route.ts:17-25` · seed `seed.ts:42-47` | ✅ |

**จุดเสี่ยง / gap ที่พบ**
- **G1** `spa/lib/server/booking.ts:167-173` คอร์สและ `giftProblem` ตรวจด้วย `today` (วันกดจอง) ไม่ใช่วันนัด → คอร์สเหลืออายุ 2 วันยังจองนัด +30 วันได้ (ตีความ BR-15 "วันที่ 181 จองด้วยคอร์สไม่ได้" ได้ 2 แบบ ⚠️ ต้องถามร้าน)
- **G2** ไม่มีวิธีทดสอบ BR-15 วันที่ 180/181 และ BR-16 "เหลือ 1 → 0": seed คอร์สนิดาซื้อ −60 วัน (`seed.ts:172-176`) · `/api/test/reset` ล้างข้อมูลทุกครั้งที่เปลี่ยน now (`app/api/test/reset/route.ts:27`) · `/api/test/user` แก้ used_sessions ไม่ได้ (`app/api/test/user/route.ts:11-21`) → ควรเพิ่ม seed คอร์ส day180/day181/เหลือ 1 แบบ GIFT-DAY365/366
- **G3** ตัวอย่างใน BR-08 (฿4,000→฿3,600) และ BR-14 (฿1,000→฿800) ไม่มีบริการราคา ฿1,000 ใน seed (`seed.ts:10-38`) → ทดสอบได้แค่ตัวเลขเทียบเท่า
- **G4** `spa/lib/server/booking.ts:245` `transport && transport.ok ? transport : transport` เป็น no-op (ไม่ผิดผล แต่อ่านสับสน)
- **G5** แพ็กเกจ Bangkok Relax "รวมรถรับส่ง" แต่ยังคิดค่ารถ >5 กม. (`rules.ts:117-181` ไม่มีกรณีพิเศษ) — ตรงกับเคส Li Wei 12 กม. ฿300 แต่ควรเขียนใน SPEC

### 2.2 data-testid

- มีแล้ว: `site-header`, `nav-*`, `lang-th|en|zh`, `nav-login|logout|account|wallet|book`, `site-footer`, `footer-privacy`, `footer-hours`, `music-toggle`, `chat-*` (`components/Header.tsx:52-133`, `Footer.tsx:10-41`, `MusicToggle.tsx:126`, `ChatBot.tsx:310-372`)
- **ขาดทั้งหมดในขั้นตอนจอง** (ยังไม่มีหน้า): `booking-submit`, `booking-error`, `price-total` และ input บริการ/วัน/รอบ/จำนวนคน/โรงแรม/แต้ม/วันเกิด/gift, ปุ่มยกเลิก, ตัวกรองรีวิว, gift form, wallet, login form
- `chat-msg-${i}` / `chat-option-${i}` (`ChatBot.tsx:323,332`) เป็น index → ไม่ unique ระหว่างรอบสนทนา ต้อง assert ด้วยข้อความหรือ `.last()`

### 2.3 BUG_MODE

| บั๊ก | ที่โค้ด | ปิดจริงเมื่อ 0? |
|---|---|---|
| 1. ฿10,000 ยังเป็น Silver | `spa/lib/server/auth.ts:47` `mode() ? spent > GOLD_MIN : …` | ✅ |
| 2. นักบำบัดทับกันได้ | `spa/lib/server/booking.ts:101` `taken = !mode() && …` (Couple Suite ยังกันอยู่ `:114`) | ✅ |
| 3. คอร์สไม่ลด | `spa/lib/server/booking.ts:286` `courseStep = mode() ? 0 : 1` | ✅ |
- `mode()` = `process.env.BUG_MODE === "1"` (`spa/lib/server/env.ts:1-3`) → ค่าอื่นทุกค่า = ปิด ✅ · compose ส่ง `${BUG_MODE:-0}` (`docker-compose.yml:32`) ✅ · `data-bug-mode` (`app/layout.tsx:33,38`) ✅
- ครบ 3 ตัว ✅ · **ยังไม่มี `spa/BUGS.md`** ❌ · ชื่อ `mode()` ไม่มีคำใบ้ แต่ ternary สองฝั่งใน `auth.ts:47` อ่านออกง่ายถ้าเปิดโค้ด (ไม่ผิดกติกาพรอมต์)

### 2.4 /api/test/reset

- รับ `now` ✅ (`app/api/test/reset/route.ts:14-21`) เก็บใน `settings.fixed_now` (`:28`) และ `getNow()` อ่านทุกกฎวันที่ (`lib/server/clock.ts:5-13`) ✅
- 404 เมื่อ `ALLOW_TEST_RESET≠1` ✅ (`:13`, `env.ts:5-7`) · now ผิดรูปแบบ → 400 `BAD_NOW` ✅
- ส่ง reset **ไม่มี now** → ล้าง fixed_now กลับนาฬิกาจริง (seed อิงเวลาจริง) — ผลไม่คงที่ข้ามวัน

---

## 3. ความเสี่ยง flaky เมื่อรัน 3 เบราว์เซอร์ (chromium / firefox / webkit)

1. **reset เป็น global** — TRUNCATE ทุกตารางรวม `sessions` และ `settings` (`spa/lib/server/schema.ts:162-177`, `app/api/test/reset/route.ts:27`) → ถ้า 3 project รันขนาน project หนึ่ง reset กลางเทสอีกตัว: หลุด login, นัดที่เพิ่งจองหาย, `now` เปลี่ยน → ต้อง `workers: 1` หรือ `fullyParallel:false` + รันทีละ project
2. **ทรัพยากรชนกัน** — ทุกเบราว์เซอร์จองนักบำบัด/Couple Suite/รอบเดียวกัน (มีห้องคู่ 1 ห้อง, นักบำบัด 6 คน) → เบราว์เซอร์ที่สองได้ `SLOT_TAKEN` · กลุ่ม 6 คนต้องว่างครบ 6 คน (`booking.ts:107-111`) ชนง่ายมาก → แยกวัน/เวลาต่อ project หรือ reset ก่อนทุกเทส
3. **ไม่ส่ง now** → seed และ +1/+30 อิงนาฬิกาจริง ข้ามเที่ยงคืน BKK แล้ววันเปลี่ยน · ton เกิด "เดือนนี้" (`seed.ts:167`) → ทุกเทสต้อง reset พร้อม now คงที่
4. **`data-ready` ค้าง true ระหว่างเปลี่ยนหน้า** — layout เริ่ม `"false"` (`app/layout.tsx:37`) แล้ว `useReady` ตั้ง/คืนค่าใน effect (`components/AppProvider.tsx:120-126`) → หลังคลิกลิงก์ client-side ค่ายังเป็น true จากหน้าเก่าจน unmount → `waitFor data-ready=true` ผ่านเร็วเกิน · และถ้าหน้าไหนลืมเรียก `useReady(true)` จะ timeout ทั้งชุด (ตอนนี้ยังไม่มีหน้าไหนเรียก)
5. **animation** — `Reveal` ใส่ class `is-in` เมื่อ IntersectionObserver เห็น (`components/Reveal.tsx:153-168`) + `transitionDelay` → element ใต้จอโปร่งใส/กำลังเลื่อน, screenshot ต่างกันระหว่างเบราว์เซอร์ · ยังไม่มี `globals.css` ให้ยืนยันว่าเคารพ `prefers-reduced-motion` → ตั้ง `reducedMotion:'reduce'` ใน config
6. **ปุ่มแชตลอย** `chatbot__fab` (`components/ChatBot.tsx:368`) อาจบังปุ่ม `booking-submit` ที่จอ 375px → click intercepted (โดยเฉพาะ webkit mobile)
7. **ภาษา error** อ่านจาก cookie `lang` (`lib/server/http.ts:5-8`) — ถ้าเทสก่อนหน้าใน context เดียวกันเปลี่ยนภาษา ข้อความ "เวลานี้ถูกจองแล้ว" จะเป็นอังกฤษ/จีน → ใช้ context ใหม่ต่อเทส
8. **ค่าที่ไม่คงที่** — code การจอง `SB000xx` ตาม sequence (`booking.ts:298`) และ gift code สุ่ม (`app/api/giftcards/route.ts:13-16`) → ห้าม assert ค่าตายตัว
9. **เขตเวลาเบราว์เซอร์** — server ใช้ BKK คงที่ (`lib/time.ts`) แต่ UI ปฏิทินที่ยังไม่เขียนอาจใช้ `new Date()` ของ browser → ตั้ง `timezoneId:'Asia/Bangkok'` ทุก project
10. **ความเร็ว** — login ใช้ `scryptSync` (`lib/server/password.ts:16`) บล็อก event loop + reset hash 3 user ใหม่ทุกครั้ง (`seed.ts:161`) → ถ้ารันขนาน reset/login ช้า อาจเกิน NFR-13 2 วินาที / timeout
11. **ฟอนต์** `next/font/google` `display:"swap"` (`app/layout.tsx:13-16`) → layout shift ก่อนฟอนต์โหลด กระทบ screenshot/ตำแหน่งคลิก และ build ต้องต่ออินเทอร์เน็ต
12. **Web Audio บน webkit/firefox headless** (`components/MusicToggle.tsx`) อาจ resume ไม่ได้โดยไม่มี user gesture จริง → assert แค่สถานะปุ่ม (`aria-pressed`) ไม่ใช่เสียง
