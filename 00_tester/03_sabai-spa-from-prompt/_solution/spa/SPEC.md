# SPEC — สบายใจ สปา · Sabai Jai Wellness Spa

เอกสารสเปกสำหรับนักพัฒนาและผู้ทดสอบ อ้างอิง `USER-STORIES.md` (US) และ `REQUIREMENTS.md` (FR / BR / NFR)

- เทคโนโลยี: Next.js 15 (App Router, TypeScript, `output: "standalone"`) + PostgreSQL 16 ผ่านไลบรารี `pg` (SQL ตรง ๆ ไม่มี ORM)
- รัน: `cd spa` → `docker compose up -d --build` → http://localhost:3000
- เวลาของร้าน = Asia/Bangkok (UTC+7) ทุกกฎคิดจาก "วันนี้" ของเว็บ (ล็อกได้ด้วย `POST /api/test/reset`)
- ทุกหน้า: `<html data-ready="true|false" data-bug-mode="0|1">` — `data-ready` เป็น `"true"` เมื่อหน้าโหลดข้อมูลเสร็จ

---

## 1. หน้าเว็บ

| path | ทำอะไร | FR |
|---|---|---|
| `/` | หน้าแรก: hero เต็มจอ (`brand/hero.jpg`) ลายไทย บริการซิกเนเจอร์ เลือกอารมณ์ แพ็กเกจ Couple Suite สมุนไพร 6 ชนิด นักบำบัด Gift Card ระดับสมาชิก | FR-21, FR-22, FR-25 |
| `/services` | รายการบริการทั้งหมด ราคา เวลา สมุนไพร + คำเตือนการแพ้ + ตัวกรองหมวด | FR-22 |
| `/services/[slug]` | รายละเอียดบริการ สมุนไพรพร้อมรูป คำเตือนการแพ้ ปุ่มจอง | FR-22 |
| `/book` | จอง 4 ขั้น: บริการ(+จำนวนคน/นักบำบัด) → วัน → รอบ → ยืนยัน (รถรับส่ง แต้ม วันเกิด คอร์ส Gift Card) + สรุปราคาแยกบรรทัด | FR-01–06, FR-10, FR-11, FR-13, FR-17, FR-19 |
| `/packages/bangkok-relax` | แพ็กเกจ Bangkok Relax: รายการที่รวม ราคาต่อคน คำนวณราคาตามจำนวนคน คำนวณค่ารถ | FR-18, FR-19 |
| `/therapists` | นักบำบัด 6 คน: คะแนนเฉลี่ย (ทศนิยม 1) จำนวนรีวิว ข้อความรีวิว ตัวกรอง "4.5 ดาวขึ้นไป" | FR-08 |
| `/rooms/couple-suite` (`/rooms` redirect มาที่นี่) | ทัวร์ 360° ลากหมุนได้ (pointer/touch/ลูกศร) + ปุ่ม "จองห้องนี้" + ห้องอื่น ๆ | FR-23 |
| `/gift-cards` | ซื้อ Gift Card (มูลค่า ลาย ช่องทาง) แสดงข้อความ "ส่ง" แบบจำลอง + ตรวจสอบบัตร (ยอดคงเหลือ/วันหมดอายุ) | FR-16, FR-17 |
| `/mood` | เลือกอารมณ์ 4 แบบ → แนะนำ 1–3 บริการ + ปุ่ม "จองเลย" | FR-25 |
| `/quiz` | แบบทดสอบ 4 ข้อ มีแถบ "ข้อ 1/4" → แนะนำ 1 แพ็กเกจ + เหตุผล + ปุ่มจอง | FR-26 |
| `/skin` | วิเคราะห์ผิวจากรูปในเบราว์เซอร์ (canvas) + ปุ่ม "ลองด้วยรูปตัวอย่าง" + ภาพจำลองก่อน/หลัง (CSS filter) | FR-29, FR-30 |
| `/privacy` | นโยบายความเป็นส่วนตัว "ร้านไม่เก็บรูปใบหน้าลูกค้า" (3 ภาษา) | FR-31 |
| `/login`, `/register` | เข้าสู่ระบบ (email + รหัสผ่าน) / สมัครสมาชิก | FR-09 |
| `/account` | ระดับ แต้ม ยอดสะสม ยอดถึงระดับถัดไป สถานะวันเกิด นัดที่จะถึง (ยกเลิก) ประวัติทรีตเมนต์ กราฟรอบเอว รูปก่อน/หลัง | FR-07, FR-09, FR-11, FR-14, FR-15 |
| `/wallet` | คอร์สกระชับสัดส่วน (เหลือ X จาก 11 ครั้ง, วันหมดอายุ) ปุ่ม "จองด้วยคอร์ส" ซื้อคอร์ส Gift Card ที่ซื้อ | FR-12, FR-13 |
| ทุกหน้า | ปุ่มภาษา ไทย/English/中文 (จำใน cookie `lang` + localStorage) · ปุ่มเพลงสปา · chatbot มุมขวาล่าง | FR-20, FR-24, FR-27, FR-28 |

---

## 2. ราคาและกฎ

### 2.1 บริการ (seed)

| slug | ชื่อ | นาที | ราคา | สมุนไพร |
|---|---|---|---|---|
| `thai-massage` | นวดไทย | 60 | ฿800 | ไพล |
| `herbal-compress` | ประคบสมุนไพร | 60 | ฿900 | ไพล ขมิ้น ตะไคร้ มะกรูด |
| `foot-reflexology` | นวดเท้า | 60 | ฿600 | ตะไคร้ |
| `aroma-oil` | นวดน้ำมันอโรมา | 90 | ฿1,500 | ตะไคร้ มะกรูด |
| `coconut-rice-scrub` | ขัดผิวข้าวมะพร้าว | 90 | ฿1,400 | ทานาคา ขมิ้น |
| `turmeric-facial` | ทรีตเมนต์หน้าขมิ้น | 60 | ฿1,200 | ขมิ้น ทานาคา |
| `aloe-hydrating-facial` | ทรีตเมนต์หน้าว่านหางจระเข้ | 60 | ฿1,100 | ว่านหางจระเข้ |
| `body-contouring` | กระชับสัดส่วน | 90 | ฿1,500 | ไพล ขมิ้น |
| `bangkok-relax` | แพ็กเกจ Bangkok Relax (นวดไทย + ประคบ + รถรับส่ง) | 120 | ฿2,900/คน | ไพล ขมิ้น ตะไคร้ |

นักบำบัด: 1 มาลี 4.9 (10 รีวิว) · 2 ปิยะดา 4.5 (2) · 3 กานดา 4.4 (5) · 4 สมชาย 4.7 (10) · 5 ประภา 5.0 (3) · 6 อรุณ ยังไม่มีรีวิว
ห้อง: `couple-suite` (1 ห้อง, 2 คน) · `thai-massage-room` · `herbal-steam`

โรงแรม (ระยะทางตายตัว): 1 Sukhumvit Garden 3.0 · 2 Lumphini Park View 5.0 · 3 Siam Square Boutique 5.1 · 4 Chatuchak Park 12.0 · 5 Chao Phraya Riverside 15.0 · 6 Bang Na Lakeside 15.1 · 7 Suvarnabhumi Airport 20.0 กม.

### 2.2 กฎ

| รหัส | กฎในระบบ | FR | ที่ตรวจ |
|---|---|---|---|
| BR-01 | รอบแรก 10:00 ปิด 22:00 ทุกวัน (ไม่มีวันหยุด) — ไม่มีรอบ 09:30 | FR-01 | server + UI |
| BR-02 | รอบทุก 30 นาที: 10:00, 10:30 … 21:30 (ไม่มี 10:15) | FR-01 | server + UI |
| BR-03 | เวลาเริ่ม + ระยะบริการ ≤ 22:00 — 60 นาที: 21:00 ได้ 21:30 ไม่ได้ · 90 นาที: 20:30 ได้ 21:00 ไม่ได้ · 120 นาที: 20:00 ได้ — รอบที่เกินแสดงแต่ `disabled` (`data-status="closed"`) | FR-01 | server + UI |
| BR-04 | นักบำบัด 1 คน 1 คิว ช่วงเวลา `[เริ่ม, จบ)` ทับกัน → "เวลานี้ถูกจองแล้ว" · จบชนเริ่มพอดีไม่ถือว่าทับ (14:00–15:00 กับ 15:00 ได้) | FR-02 | server (transaction + advisory lock) |
| BR-05 | จองได้ พรุ่งนี้ (+1) ถึง +30 วัน (รวมทั้งสองวัน) · วันนี้และ +31 กดไม่ได้ | FR-03 | server + ปฏิทิน |
| BR-06 | 2 คน = คู่ (Couple Suite 1 ห้อง, เริ่มพร้อมกัน, ใช้นักบำบัด 2 คน) · ปุ่ม "คู่" กดได้เมื่อจำนวนคน = 2 เท่านั้น · Couple Suite ทับเวลา → "เวลานี้ถูกจองแล้ว" | FR-04 | server + UI |
| BR-07 | 3–6 คน = กลุ่ม (ใช้นักบำบัดเท่าจำนวนคน) · ≥7 คน → "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567" และจองไม่ได้ | FR-05 | server + UI |
| BR-08 | ≥4 คน ลด 10% ของค่าบริการรวม (฿4,000 → ฿3,600) · 3 คนไม่ลด | FR-06 | server |
| BR-09 | ยกเลิกเองได้เมื่อ `เวลานัด − ตอนนี้ ≥ 24 ชม.` (24 ชม. พอดีได้) · ไม่ได้ → ปุ่ม disabled + ข้อความให้ติดต่อร้าน · ยกเลิกแล้วเวลานั้นว่าง แต้ม/คอร์ส/Gift Card/วันเกิด คืนให้ | FR-07 | server + UI |
| BR-10 | ตัวกรอง "4.5 ดาวขึ้นไป" = `rating >= 4.5` และต้องมีรีวิว ≥1 (นักบำบัด 6 ไม่แสดง) | FR-08 | server (`?minRating=4.5`) |
| BR-11 | แต้มที่ได้ = `floor(ยอดค่าบริการสุทธิ / 100)` (หลังส่วนลดและแต้ม ไม่รวมค่ารถ) ได้ทันทีเมื่อจองสำเร็จ · ฿99→0 ฿100→1 ฿199→1 ฿2,950→29 | FR-09 | server |
| BR-12 | แลก 100 แต้ม = ลด ฿50 ต่อชุด แลกได้สูงสุด `floor(แต้ม/100)` ชุด (และไม่เกินยอด) · <100 แต้ม ช่องแลก disabled · หักแต้มทันทีเมื่อจองสำเร็จ | FR-10 | server + UI |
| BR-13 | Silver < ฿10,000 (0%) · Gold ≥ ฿10,000 (5%) · Platinum ≥ ฿30,000 (10%) · "อีก ฿X ถึงระดับ Y" / "คุณอยู่ระดับสูงสุดแล้ว" · ยอดสะสม = ผลรวมค่าบริการสุทธิที่จอง (ไม่รวมค่ารถ คอร์ส Gift Card) | FR-09 | server |
| BR-14 | เดือนเกิด (เดือนของ "วันนี้") ลด 20% ได้ 1 ครั้งต่อปีปฏิทิน · ไม่รวมกับส่วนลดระดับ ใช้อันที่มากกว่า (Platinum ฿1,000 → ฿800) · ใช้แล้วตัวเลือกหายไป | FR-11 | server + UI |
| BR-15 | คอร์ส ฿15,000 = 11 ครั้ง หมดอายุ = วันซื้อ + 180 วัน (ซื้อ 1 ม.ค. → 30 มิ.ย.) · ใช้ได้ถ้า "วันนี้" ≤ วันหมดอายุ (วันที่ 180 ได้ 181 ไม่ได้) | FR-12 | server |
| BR-16 | คอร์สเหลือ 0 → "จองด้วยคอร์ส" disabled และ server ตอบ `COURSE_EMPTY` · ใช้ได้กับ `body-contouring` 1 คนเท่านั้น · จองสำเร็จหัก 1 ครั้ง | FR-13 | server + UI |
| BR-17 | Gift Card ฿500–฿10,000 (จำนวนเต็ม) · ลาย `orchid` / `lotus` / `gold` · ช่องทาง `line` / `email` · ส่งแบบจำลอง (ไม่ส่งจริง) | FR-16 | server + UI |
| BR-18 | Gift Card ใช้ได้ถึง วันซื้อ + 365 วัน (วันที่ 365 ได้ 366 → "Gift Card หมดอายุแล้ว") · ใช้จ่ายได้หลายครั้งจนยอดหมด | FR-17 | server |
| BR-19 | Bangkok Relax ฿2,900/คน 120 นาที (1 คน ฿2,900 · 4 คน ฿11,600 ก่อนส่วนลดอื่น) | FR-18 | server |
| BR-20 | ค่ารถ: ≤5.0 กม. ฟรี · >5.0–15.0 กม. ฿300 ต่อคัน · >15.0 กม. "ไม่มีบริการรับส่งสำหรับระยะนี้" (จองไม่ได้ถ้าเลือกรถ) · ใช้กับแพ็กเกจด้วย | FR-19 | server + UI |
| BR-21 | รถ 1 คัน ≤4 คน: คัน = `ceil(คน/4)` (4→1, 5→2, 6→2) | FR-19 | server + UI |
| BR-22 | 3 ภาษาเท่านั้น th / en / zh | FR-20 | UI |
| BR-23 | อารมณ์ 4 แบบ แนะนำ 1–3 บริการ | FR-25 | UI |
| BR-24 | แบบทดสอบ 4 ข้อพอดี ตอบครบจึงแสดงผล 1 รายการ | FR-26 | UI |
| BR-25 | ไม่มีการอัปโหลด/เก็บรูปใบหน้า · วิเคราะห์ผิว/ภาพจำลองทำใน browser (blob URL + canvas) ไม่มี request ส่งรูป | FR-29–31 | UI |

### 2.3 ลำดับคำนวณราคา (FR-06, `lib/rules.ts → computeQuote`)

1. `ค่าบริการ` = ราคาต่อคน × จำนวนคน
2. `ส่วนลดกลุ่ม` = 10% เมื่อ ≥4 คน (ปัดเป็นบาท)
3. `ส่วนลดสมาชิก` = max(ระดับ %, วันเกิด 20% ถ้าเลือกใช้และมีสิทธิ์) คิดจากยอดหลังข้อ 2 — แสดงบรรทัด `price-tier-discount` หรือ `price-birthday-discount`
4. `แลกแต้ม` = ชุด × ฿50
5. `ค่าบริการสุทธิ` = 1 − 2 − 3 − 4 → ใช้คิดแต้มที่จะได้ (BR-11) และเพิ่มยอดสะสม
6. `ค่ารถ` บวกเพิ่ม (ไม่มีส่วนลด) → `ยอดสุทธิ` (`price-total`)
7. `Gift Card` หักจากยอดสุทธิไม่เกินยอดคงเหลือ → `ยอดที่ต้องชำระที่ร้าน` (`price-due`)
8. จองด้วยคอร์ส: ค่าบริการถูกคอร์สจ่ายทั้งหมด (`price-course`) ไม่ได้แต้ม ยอดสุทธิ = ค่ารถ

ตัวอย่าง: นิดา (Gold) นวดไทย 1 คน = ฿800 − ฿40 = ฿760 ได้ 7 แต้ม · ต้น (Platinum, เดือนเกิด) ฿1,500 → ลดวันเกิด ฿300 = ฿1,200 · กลุ่ม 4 คน Bangkok Relax ฿11,600 − ฿1,160 = ฿10,440 (+ ค่ารถ 12 กม. ฿300 = ฿10,740 สำหรับลูกค้าทั่วไป)

---

## 3. `data-testid`

ชื่อที่มี `{…}` คือค่าที่เปลี่ยนตามข้อมูล (slug / id / เวลา / วันที่)

### ทุกหน้า (Header / Footer / Chatbot)
| testid | ใช้ทำอะไร |
|---|---|
| `site-header`, `site-footer` | ส่วนหัว / ท้ายเว็บ |
| `nav-home`, `nav-services`, `nav-package`, `nav-therapists`, `nav-rooms`, `nav-gift`, `nav-mood`, `nav-quiz`, `nav-skin`, `nav-book` | ลิงก์เมนู |
| `nav-login` / `nav-account`, `nav-wallet`, `nav-logout` | เมนูสมาชิก (ตามสถานะ login) |
| `nav-toggle` | ปุ่มเมนูบนมือถือ (กว้าง ≤1180px) |
| `lang-th`, `lang-en`, `lang-zh` | เปลี่ยนภาษา (`aria-pressed="true"` = ภาษาปัจจุบัน) |
| `music-toggle` | เปิด/ปิดเพลงสปา (`data-playing="true|false"`, `aria-pressed`) |
| `footer-hours`, `footer-privacy` | เวลาเปิด / ลิงก์นโยบาย |
| `chat-toggle`, `chat-panel`, `chat-close` | เปิด/ปิด chatbot |
| `chat-input`, `chat-send` | ช่องพิมพ์ / ปุ่มส่ง |
| `chat-messages`, `chat-msg-{i}` | ข้อความ (i เริ่ม 0, `data-from="bot|user"`) |
| `chat-options`, `chat-option-{i}` | ปุ่มตัวเลือกด่วนของขั้นปัจจุบัน (`data-value`) |
| `chat-quick-hours`, `chat-quick-price`, `chat-quick-book` | ปุ่มลัดตอนเปิดแชท |

### `/` หน้าแรก
`hero`, `hero-book`, `hero-explore`, `home-all-services`, `service-card-{slug}` (+ `service-price-{slug}`, `service-duration-{slug}`, `service-herbs-{slug}`, `service-book-{slug}`, `service-detail-{slug}`), `home-mood-{relax|stressed|tired|sore}`, `home-mood-result`, `home-mood-book-{slug}`, `home-package`, `home-tour`, `home-therapists`, `home-tool-quiz`, `home-tool-skin`, `home-tool-mood`, `home-gift`, `home-member`

### `/services`, `/services/{slug}`
| testid | ใช้ทำอะไร |
|---|---|
| `cat-{all|massage|body|facial|package}` | ตัวกรองหมวด |
| `service-list` | รายการบริการ |
| `service-card-{slug}`, `service-price-{slug}`, `service-duration-{slug}`, `service-herbs-{slug}` | การ์ด ราคา เวลา สมุนไพร (`li[data-herb]`) |
| `allergy-warning` | "ถ้าแพ้สมุนไพรชนิดใด กรุณาแจ้งร้านก่อนรับบริการ" |
| `service-detail-duration`, `service-detail-price`, `service-detail-herbs`, `service-detail-book` | หน้ารายละเอียด |

### `/book`
| testid | ใช้ทำอะไร |
|---|---|
| `service-option-{slug}` | เลือกบริการ (`aria-checked`) |
| `booking-herbs`, `booking-allergy` | สมุนไพร + คำเตือนการแพ้ของบริการที่เลือก |
| `booking-people`, `booking-people-minus`, `booking-people-plus` | จำนวนคน |
| `booking-kind-single`, `booking-kind-couple`, `booking-kind-group` | แบบการจอง (disabled ถ้าจำนวนคนไม่ตรง) |
| `booking-group-error` | ≥7 คน: "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567" |
| `booking-therapist` | select นักบำบัด (ว่าง = ร้านจัดให้) |
| `booking-date-range` | ข้อความช่วงวันที่จองได้ |
| `calendar`, `cal-prev`, `cal-next`, `cal-month`, `cal-day-{YYYY-MM-DD}` | ปฏิทิน (วันนอกช่วง = `disabled`) |
| `slot-list`, `slot-{HH-MM}` | รอบเวลา เช่น `slot-20-30` (`data-status="free|booked|closed"`, closed = disabled) |
| `slot-error` | เลือกรอบที่เต็ม → "เวลานี้ถูกจองแล้ว" |
| `booking-end-time` | เวลาจบของรอบที่เลือก |
| `booking-transport`, `booking-hotel` | ต้องการรถ / เลือกโรงแรม |
| `transport-info`, `transport-distance`, `transport-cars`, `transport-fee`, `transport-error` | ระยะ / จำนวนรถ / ค่ารถ / "ไม่มีบริการรับส่งสำหรับระยะนี้" |
| `booking-login-hint`, `booking-guest-name`, `booking-guest-phone` | ผู้ไม่ได้ login ต้องกรอกชื่อ+เบอร์ |
| `booking-member`, `booking-member-tier`, `booking-points-balance` | ข้อมูลสมาชิก |
| `booking-redeem`, `booking-redeem-max`, `booking-redeem-hint` | แลกแต้ม (disabled เมื่อ <100 แต้ม) |
| `booking-birthday` | checkbox ส่วนลดวันเกิด (แสดงเฉพาะเมื่อมีสิทธิ์) |
| `booking-pay-cash`, `booking-pay-course`, `booking-course-hint` | วิธีชำระ / จองด้วยคอร์ส (เฉพาะ body-contouring) |
| `booking-gift-code`, `booking-gift-apply`, `booking-gift-remove`, `booking-gift-status`, `booking-gift-error` | Gift Card |
| `booking-issue-{CODE}` | ปัญหาจาก server ก่อนกดจอง (เช่น `booking-issue-COURSE_EMPTY`) |
| `booking-error` | error หลังกดยืนยัน (เช่น "เวลานี้ถูกจองแล้ว") |
| `booking-submit` | ปุ่มยืนยันการจอง |
| `booking-summary`, `summary-service`, `summary-people`, `summary-date`, `summary-time` | กล่องสรุป |
| `price-summary`, `price-subtotal`, `price-group-discount`, `price-tier-discount`, `price-birthday-discount`, `price-points-discount`, `price-course`, `price-transport`, `price-total`, `price-gift`, `price-due`, `price-points-earn` | สรุปราคาทุกบรรทัด |
| `booking-success`, `booking-code`, `booking-success-when`, `booking-success-therapists`, `booking-success-total`, `booking-another`, `booking-view-mine` | หน้าจองสำเร็จ |

### `/packages/bangkok-relax`
`package-price`, `package-includes`, `package-inc-thai-massage`, `package-inc-herbal-compress`, `package-inc-transfer`, `package-herbs`, `allergy-warning`, `package-people`, `package-people-minus`, `package-people-plus`, `package-total`, `package-hotel`, `package-transport`, `package-cars`, `package-transport-fee`, `package-transport-error`, `package-book`

### `/therapists`
`filter-all`, `filter-45`, `therapist-count`, `therapist-list`, `therapist-card-{id}` (`data-rating`), `therapist-rating-{id}`, `therapist-review-count-{id}`, `therapist-toggle-reviews-{id}`, `therapist-reviews-{id}`, `therapist-book-{id}`

### `/rooms/couple-suite`
`tour-360` (`data-angle` 0–359, `data-loaded`), `tour-angle`, `tour-left`, `tour-right`, `tour-auto`, `tour-book`, `room-card-{slug}`

### `/gift-cards`
`gift-form`, `gift-amount`, `gift-quick-{500|1000|2000|5000|10000}`, `gift-design-{orchid|lotus|gold}`, `gift-channel-line`, `gift-channel-email`, `gift-recipient`, `gift-recipient-name`, `gift-sender`, `gift-message`, `gift-error`, `gift-submit`, `gift-preview`, `gift-success`, `gift-code`, `gift-amount-result`, `gift-expiry` (`data-date`), `gift-card-expiry`, `gift-sent-message`, `gift-simulated-note`, `gift-again`, `gift-check-form`, `gift-check-code`, `gift-check-submit`, `gift-check-result` (`data-status="valid|expired|empty"`), `gift-check-balance`, `gift-check-expiry`, `gift-check-valid`, `gift-check-error`

### `/mood`, `/quiz`, `/skin`
| หน้า | testid |
|---|---|
| `/mood` | `mood-relax`, `mood-stressed`, `mood-tired`, `mood-sore`, `mood-result` (`data-mood`), `mood-reason`, `mood-rec-{slug}`, `mood-book-{slug}` |
| `/quiz` | `quiz-card`, `quiz-progress` ("ข้อ 1/4"), `quiz-question` (`data-question`), `quiz-option-{value}`, `quiz-back`, `quiz-answered`, `quiz-result` (`data-service`), `quiz-result-service`, `quiz-reason`, `quiz-book`, `quiz-restart` |
| `/skin` | `skin-private`, `skin-stage`, `skin-file`, `skin-sample`, `skin-preview`, `skin-result-card`, `skin-result` (`data-type`), `skin-avg` (`data-r/g/b`), `skin-brightness`, `skin-redness`, `skin-rec-{slug}`, `skin-book-{slug}`, `skin-disclaimer`, `skin-rules`, `sim-treatment`, `sim-slider`, `sim-label`, `sim-compare`, `sim-before`, `sim-after` (`data-filter`) |

### `/privacy`, `/login`, `/register`, `/account`, `/wallet`
| หน้า | testid |
|---|---|
| `/privacy` | `privacy-no-face`, `privacy-skin` |
| `/login` | `login-form`, `login-email`, `login-password`, `login-submit`, `login-error`, `login-register-link`, `login-demo-{nida|ton|new}` (กรอกอีเมลให้) |
| `/register` | `register-form`, `register-name`, `register-email`, `register-password`, `register-birth-month`, `register-error`, `register-submit` |
| `/account` | `account-need-login`, `member-tier` (`data-tier`), `member-points`, `member-spent`, `member-next-tier`, `member-birthday` (`data-status`), `upcoming-list`, `no-upcoming`, `booking-item-{code}`, `cancel-btn-{code}`, `cancel-blocked-{code}`, `cancel-success`, `cancel-error`, `waist-chart`, `waist-point-{i}` (`data-cm`), `waist-drop`, `body-photos`, `photo-before`, `photo-after`, `history-list`, `history-row-{i}` (เรียงล่าสุดก่อน), `account-wallet` |
| `/wallet` | `wallet-need-login`, `course-card`, `course-remaining` ("เหลือ 7 จาก 11 ครั้ง", `data-left`), `course-expires` (`data-date`), `course-expired`, `course-none`, `course-book` (disabled เมื่อใช้ไม่ได้), `course-problem`, `course-buy`, `course-buy-result`, `wallet-gifts`, `wallet-gift-{code}` |

---

## 4. ข้อความ error (คำต่อคำ)

| code | ไทย | English | 中文 |
|---|---|---|---|
| `SLOT_TAKEN` | เวลานี้ถูกจองแล้ว | This time is already booked | 该时间已被预订 |
| `GROUP_TOO_LARGE` | กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567 | Groups of 7 or more: please call the spa at 02-123-4567 | 7 人及以上团体，请致电本店 02-123-4567 |
| `COUPLE_NEEDS_TWO` | จองคู่ต้องมีผู้รับบริการ 2 คนพอดี | A couple booking must be exactly 2 guests | 双人预约必须恰好 2 人 |
| `GROUP_NEEDS_THREE` | จองกลุ่มต้องมี 3–6 คน | A group booking needs 3–6 guests | 团体预约需要 3–6 人 |
| `PEOPLE_INVALID` | กรุณาระบุจำนวนคนให้ถูกต้อง | Please enter a valid number of guests | 请输入有效人数 |
| `DATE_OUT_OF_RANGE` | จองได้ตั้งแต่พรุ่งนี้ถึง 30 วันข้างหน้าเท่านั้น | You can book from tomorrow up to 30 days ahead only | 仅可预约明天至 30 天内的日期 |
| `TIME_INVALID` | รอบเวลานี้ไม่เปิดให้จอง (เปิด 10:00–22:00 ทุก 30 นาที และต้องเสร็จไม่เกิน 22:00) | This time is not bookable (10:00–22:00 every 30 min, must finish by 22:00) | 该时间不可预约（10:00–22:00 每 30 分钟一场，须在 22:00 前结束） |
| `SERVICE_REQUIRED` | กรุณาเลือกบริการ | Please choose a treatment | 请选择护理项目 |
| `DATE_REQUIRED` | กรุณาเลือกวัน | Please choose a date | 请选择日期 |
| `TIME_REQUIRED` | กรุณาเลือกรอบเวลา | Please choose a time | 请选择时间 |
| `GUEST_INFO` | กรุณากรอกชื่อและเบอร์โทร | Please enter your name and phone number | 请填写姓名和电话 |
| `THERAPIST_NOT_FOUND` | ไม่พบนักบำบัดนี้ | Therapist not found | 未找到该理疗师 |
| `CANCEL_TOO_LATE` | เหลือน้อยกว่า 24 ชั่วโมง ยกเลิกเองไม่ได้ กรุณาติดต่อร้าน 02-123-4567 | Less than 24 hours left — please contact the spa at 02-123-4567 to cancel | 距离预约不足 24 小时，无法自行取消，请致电本店 02-123-4567 |
| `ALREADY_CANCELLED` | นัดนี้ถูกยกเลิกไปแล้ว | This booking is already cancelled | 该预约已取消 |
| `LOGIN_REQUIRED` | กรุณาเข้าสู่ระบบ | Please log in | 请先登录 |
| `LOGIN_FAILED` | อีเมลหรือรหัสผ่านไม่ถูกต้อง | Incorrect email or password | 电子邮件或密码错误 |
| `EMAIL_TAKEN` | อีเมลนี้เป็นสมาชิกอยู่แล้ว | This email is already registered | 该电子邮件已注册 |
| `REGISTER_INVALID` | กรุณากรอกชื่อ อีเมล รหัสผ่าน (อย่างน้อย 8 ตัว) และเดือนเกิดให้ครบ | Please enter name, email, password (8+ characters) and birth month | 请填写姓名、电子邮件、密码（至少 8 位）和出生月份 |
| `POINTS_NOT_ENOUGH` | แต้มไม่พอสำหรับแลกส่วนลด | Not enough points to redeem | 积分不足，无法兑换 |
| `BIRTHDAY_NOT_ELIGIBLE` | ใช้ส่วนลดเดือนเกิดไม่ได้ (ไม่ใช่เดือนเกิด หรือใช้ไปแล้วปีนี้) | Birthday discount not available (not your birth month or already used) | 无法使用生日折扣（非生日月或今年已使用） |
| `COURSE_NONE` | คุณยังไม่มีคอร์ส | You don't have a course | 您还没有课程 |
| `COURSE_EMPTY` | คอร์สเหลือ 0 ครั้ง จองด้วยคอร์สไม่ได้ | No sessions left on your course | 课程剩余 0 次，无法使用课程预约 |
| `COURSE_EXPIRED` | คอร์สหมดอายุแล้ว จองด้วยคอร์สไม่ได้ | Your course has expired | 课程已过期，无法使用课程预约 |
| `COURSE_NOT_APPLICABLE` | คอร์สใช้ได้กับบริการกระชับสัดส่วน 1 คนเท่านั้น | The course is for 1-guest body contouring only | 课程仅限单人塑身护理 |
| `GIFT_NOT_FOUND` | ไม่พบ Gift Card นี้ | Gift card not found | 未找到该礼品卡 |
| `GIFT_EXPIRED` | Gift Card หมดอายุแล้ว | This gift card has expired | 礼品卡已过期 |
| `GIFT_EMPTY` | Gift Card นี้ใช้ยอดหมดแล้ว | This gift card has no balance left | 该礼品卡余额为零 |
| `GIFT_AMOUNT` | มูลค่า Gift Card ต้องอยู่ระหว่าง ฿500–฿10,000 | Gift card amount must be ฿500–฿10,000 | 礼品卡面额须在 ฿500–฿10,000 之间 |
| `GIFT_DESIGN` | กรุณาเลือกลาย Gift Card | Please choose a gift card design | 请选择礼品卡设计 |
| `GIFT_CHANNEL` | กรุณาเลือกช่องทางส่ง (LINE หรืออีเมล) | Please choose LINE or email | 请选择发送方式（LINE 或电子邮件） |
| `GIFT_RECIPIENT` | กรุณากรอก LINE ID หรืออีเมลผู้รับให้ถูกต้อง | Please enter a valid LINE ID or email for the recipient | 请正确填写收件人的 LINE ID 或电子邮件 |
| `TRANSPORT_TOO_FAR` | ไม่มีบริการรับส่งสำหรับระยะนี้ | Transfer is not available for this distance | 该距离不提供接送服务 |
| `HOTEL_REQUIRED` | กรุณาเลือกโรงแรม | Please choose your hotel | 请选择酒店 |
| `NOT_FOUND` | ไม่พบข้อมูล | Not found | 未找到 |
| `SERVER` | ระบบขัดข้อง กรุณาลองใหม่ | Something went wrong, please try again | 系统出错，请重试 |

ข้อความอื่นที่ทดสอบได้: "ถ้าแพ้สมุนไพรชนิดใด กรุณาแจ้งร้านก่อนรับบริการ" · "ผลนี้เป็นคำแนะนำเบื้องต้น ไม่ใช่การวินิจฉัยของแพทย์" · "ภาพจำลองเท่านั้น ผลจริงแต่ละคนต่างกัน" · "ร้านไม่เก็บรูปใบหน้าลูกค้า" · "อีก ฿17,600 ถึงระดับ Platinum" · "คุณอยู่ระดับสูงสุดแล้ว" · "เหลือ 7 จาก 11 ครั้ง" · "ลดลง 4 ซม. จากครั้งแรก" (ทุกข้อความมี 3 ภาษาใน `lib/i18n.ts`)

---

## 5. API

ทุกเส้นตอบ JSON · error = `{ "ok": false, "error": "<CODE>", "message": "<ข้อความภาษาตาม cookie lang>" }` · session = cookie `sabai_session` (httpOnly)

| method | path | body / query | ตัวอย่างคำตอบ |
|---|---|---|---|
| GET | `/api/health` | – | `{"ok":true,"db":true}` · DB ล่ม → 503 `{"ok":false,"db":false}` |
| POST | `/api/test/reset` | `{"now":"2027-01-15T10:00:00+07:00"}` (ไม่ใส่ = ใช้นาฬิกาจริง) · ใช้ได้เมื่อ `ALLOW_TEST_RESET=1` ไม่งั้น 404 | `{"ok":true,"now":"2027-01-15T03:00:00.000Z","locked":true,"today":"2027-01-15","bookable":{"from":"2027-01-16","to":"2027-02-14"}}` |
| POST | `/api/test/user` | ตัวช่วยทดสอบ (ต้อง `ALLOW_TEST_RESET=1`) ทุกช่องไม่บังคับยกเว้น email: `{"email":"nida@sabai.test","totalSpent":10000,"points":99,"birthMonth":1,"birthdayUsedYear":null,"coursePurchasedOn":"2026-07-18","courseUsed":11}` — `coursePurchasedOn` ย้ายวันซื้อคอร์สล่าสุด (หมดอายุ = +180 วัน) ใช้ทดสอบวันที่ 180/181 · `courseUsed` ตั้งจำนวนครั้งที่ใช้ไป | `{"ok":true,"user":{"email":"…","total_spent":10000,"points":99,…},"course":{"total_sessions":11,"used_sessions":11,"purchased_on":"2026-07-18","expires_on":"2027-01-14"}}` |
| GET | `/api/config` | – | `{"ok":true,"now":"…","today":"2027-01-15","bookable":{"from":"2027-01-16","to":"2027-02-14"},"open":"10:00","close":"22:00","slotMinutes":30,"phone":"02-123-4567","hotels":[{"id":1,"name":"Sukhumvit Garden Hotel","nameZh":"…","distanceKm":3}, …]}` |
| GET | `/api/services` | – | `{"ok":true,"services":[{"slug":"thai-massage","duration":60,"price":800,"herbs":["plai"],"name_th":"นวดไทย",…}, …]}` |
| GET | `/api/services/{slug}` | – | `{"ok":true,"service":{…}}` / 404 |
| GET | `/api/therapists` | `?minRating=4.5` | `{"ok":true,"minRating":4.5,"therapists":[{"id":1,"rating":4.9,"review_count":10,"reviews":[…]}, …]}` |
| GET | `/api/rooms` | – | `{"ok":true,"rooms":[{"slug":"couple-suite","capacity":2,…}, …]}` |
| GET | `/api/availability` | `?service=thai-massage&date=2027-01-16&people=1&therapistId=1` | `{"ok":true,"duration":60,"kind":"single","slots":[{"time":"10:00","status":"free"}, … {"time":"21:30","status":"closed"}]}` |
| GET | `/api/transport` | `?hotelId=4&people=5` | `{"ok":true,"available":true,"distanceKm":12,"cars":2,"feePerCar":300,"fee":600}` · 15.1 กม. → `"available":false,"error":"TRANSPORT_TOO_FAR"` |
| POST | `/api/quote` | `{"service":"thai-massage","people":4,"transport":true,"hotelId":4,"redeemSets":1,"useBirthday":false,"payWith":"cash","giftCode":null}` | `{"ok":true,"quote":{"subtotal":3200,"groupDiscount":320,"tierDiscount":0,"birthdayDiscount":0,"pointsDiscount":0,"transportFee":300,"cars":1,"total":3180,"giftUsed":0,"due":3180,"pointsEarned":0,…},"issues":[]}` |
| POST | `/api/bookings` | `{"service":"thai-massage","date":"2027-01-16","time":"14:00","people":1,"therapistId":1,"transport":false,"hotelId":null,"redeemSets":0,"useBirthday":false,"payWith":"cash","giftCode":null,"guestName":"Mei","guestPhone":"0812345678","source":"web"}` | 201 `{"ok":true,"booking":{"id":9,"code":"SB00009","date":"2027-01-16","time":"14:00","endTime":"15:00","therapists":[1],"room":null,"quote":{…}}}` · ทับ → 409 `{"ok":false,"error":"SLOT_TAKEN","message":"เวลานี้ถูกจองแล้ว"}` |
| GET | `/api/bookings` | (login) | `{"ok":true,"bookings":[{"code":"SB00006","date":"…","time":"15:00","status":"confirmed","canCancel":true,…}]}` |
| POST | `/api/bookings/{id}/cancel` | (login, เจ้าของเท่านั้น) | `{"ok":true,"booking":{"id":6,"code":"SB00006","status":"cancelled"}}` · <24 ชม. → 409 `CANCEL_TOO_LATE` |
| POST | `/api/auth/login` | `{"email":"nida@sabai.test","password":"Sabai1234!"}` | `{"ok":true,"user":{"name":"นิดา","tier":"gold","points":124,"totalSpent":12400,"nextTier":"platinum","nextTierNeed":17600,"birthday":"not-month"}}` · ผิด → 401 `LOGIN_FAILED` |
| POST | `/api/auth/logout` | – | `{"ok":true}` |
| POST | `/api/auth/register` | `{"name":"Mei","email":"mei@example.com","password":"12345678","birthMonth":5}` | 201 `{"ok":true,"user":{…"tier":"silver"}}` |
| GET | `/api/auth/me` | – | `{"ok":true,"user":{…}|null}` |
| GET | `/api/account` | (login) | `{"ok":true,"member":{…},"upcoming":[…],"history":[…],"waist":[{"date":"…","cm":82},…],"waistDrop":4,"photos":[…]}` |
| GET | `/api/wallet` | (login) | `{"ok":true,"courses":[{"total":11,"used":4,"left":7,"purchasedOn":"…","expiresOn":"…","expired":false}],"canBookWithCourse":true,"courseProblem":null,"giftCards":[…]}` |
| POST | `/api/courses` | (login) | 201 `{"ok":true,"course":{"total":11,"left":11,"price":15000,"purchasedOn":"2027-01-15","expiresOn":"2027-07-14"}}` |
| POST | `/api/giftcards` | `{"amount":2000,"design":"orchid","channel":"line","recipient":"mom-line","recipientName":"Mom","senderName":"Fon","message":"…"}` | 201 `{"ok":true,"giftCard":{"code":"GC-…","amount":2000,"expiresOn":"2028-01-15"},"delivery":{"simulated":true,"sent":false}}` |
| GET | `/api/giftcards/{code}` | – | `{"ok":true,"giftCard":{…},"usable":false,"status":"expired","error":"GIFT_EXPIRED","message":"Gift Card หมดอายุแล้ว"}` |

ภาษา: API อ่าน cookie `lang` (`th`/`en`/`zh`) เพื่อเลือกภาษาใน `message`

---

## 6. ผู้ใช้ seed และกฎ "AI"

### 6.1 ผู้ใช้ seed (รหัสผ่าน `Sabai1234!` ทุกคน) — สร้างใหม่ทุกครั้งที่ reset โดยอิง "วันนี้"

| email | ข้อมูล |
|---|---|
| `nida@sabai.test` | คุณนิดา · Gold · ยอดสะสม ฿12,400 ("อีก ฿17,600 ถึงระดับ Platinum") · 124 แต้ม · คอร์สกระชับสัดส่วน ซื้อเมื่อ วันนี้−60 วัน ใช้ไป 4 เหลือ 7 · นัด **พรุ่งนี้ 15:00** นวดไทย กับมาลี (`SB00006`) · รอบเอว 82.0 → 80.5 → 79.0 → 78.0 ซม. (ลดลง 4 ซม.) · ประวัติ 5 ครั้ง · รูปก่อน/หลัง (ลำตัว) · เดือนเกิด ≠ เดือนนี้ |
| `ton@sabai.test` | คุณต้น · Platinum ฿30,000 · 250 แต้ม · เกิดเดือนเดียวกับ "วันนี้" (ยังไม่ได้ใช้ส่วนลดวันเกิด) |
| `new@sabai.test` | สมาชิกใหม่ · Silver · ฿0 · 0 แต้ม |

ข้อมูล seed อื่น: วันที่ +2 มีคิว **มาลี (นักบำบัด 1) 14:00–15:00** และ **Couple Suite 18:00–19:30** (ไว้ทดสอบ BR-04 / BR-06) · Gift Card `GIFT-2000-ORCHID` (฿2,000 ใช้ได้) · `GIFT-DAY365` (ซื้อเมื่อ 365 วันก่อน → วันนี้ยังใช้ได้) · `GIFT-DAY366` (366 วันก่อน → หมดอายุ)

### 6.2 กฎ "AI" ทั้งหมด (NFR-12: ไม่เรียก API ภายนอก ไม่มีการสุ่ม)

**แนะนำตามอารมณ์** (`lib/recommend.ts → MOOD_RULES`)

| อารมณ์ | บริการที่แนะนำ (ตามลำดับ) |
|---|---|
| ผ่อนคลาย `relax` | aroma-oil, foot-reflexology |
| เครียด `stressed` | aroma-oil, herbal-compress, coconut-rice-scrub |
| เหนื่อย `tired` | foot-reflexology, thai-massage, bangkok-relax |
| ปวดเมื่อย `sore` | thai-massage, herbal-compress |

**แบบทดสอบ 4 ข้อ** — Q1 goal (relax / pain / skin / shape) · Q2 time (60 / 90 / 120) · Q3 pressure (soft / medium / strong) · Q4 transfer (yes / no) · กฎแรกที่ตรงชนะ:

| # | เงื่อนไข | ผล | เหตุผล (key) |
|---|---|---|---|
| 1 | transfer = yes | bangkok-relax | transfer |
| 2 | goal = skin และ pressure = soft | aloe-hydrating-facial | skinSoft |
| 3 | goal = skin | turmeric-facial | skinBright |
| 4 | goal = shape | body-contouring | shape |
| 5 | goal = pain และ pressure = strong | thai-massage | painStrong |
| 6 | goal = pain | herbal-compress | painHerbal |
| 7 | goal = relax และ time = 60 | foot-reflexology | relaxShort |
| 8 | goal = relax (90/120) | aroma-oil | relaxLong |

**วิเคราะห์ผิว** — วาดพื้นที่กลางภาพ 60% ลง canvas 96×96 ในเบราว์เซอร์ หาค่าเฉลี่ย R,G,B → `ความสว่าง = round(0.299R + 0.587G + 0.114B)` · `ความแดง = round(R − G)` · กฎแรกที่ตรงชนะ:

| เงื่อนไข | ผล | แนะนำ |
|---|---|---|
| ความแดง ≥ 45 | ผิวแดง ระคายเคืองง่าย (`sensitive`) | aloe-hydrating-facial |
| ความสว่าง < 120 | ผิวหมองคล้ำ (`dull`) | turmeric-facial, coconut-rice-scrub |
| ความสว่าง ≥ 170 | ผิวขาดความชุ่มชื้น (`dry`) | aloe-hydrating-facial, turmeric-facial |
| อื่น ๆ (120–169) | ผิวสมดุล (`balanced`) | turmeric-facial, aroma-oil |

รูปจากเครื่องใช้ `URL.createObjectURL` (blob:) ไม่มี request ส่งรูปออก · ปุ่ม "ลองด้วยรูปตัวอย่าง" ใช้ `/assets/skin/sample-face.jpg`

**ภาพจำลองก่อน/หลัง** — รูปเดียวกัน ฝั่ง "หลัง" ใส่ CSS filter: turmeric-facial `brightness(1.10) saturate(1.06) contrast(1.03)` · aloe-hydrating-facial `brightness(1.06) saturate(0.90) contrast(0.97) blur(0.4px)` · coconut-rice-scrub `brightness(1.12) contrast(1.05) saturate(1.02)` + ป้าย "ภาพจำลองเท่านั้น ผลจริงแต่ละคนต่างกัน"

**Chatbot** (`lib/chatbot.ts`) — ภาษาที่ตอบ = ภาษาของข้อความล่าสุดที่มีตัวอักษร (มีอักษรจีน → 中文 · อักษรไทย → ไทย · a–z → English) · คำสำคัญ (แถวแรกที่ตรงชนะ):

| intent | คำสำคัญ |
|---|---|
| จอง | 预约 预订 订位 · จอง · book reserve appointment |
| ยกเลิก | 取消 · ยกเลิก · cancel |
| ราคา | 多少钱 价格 价钱 费用 收费 价目 · ราคา เท่าไร เท่าไหร่ กี่บาท ค่าบริการ · price cost how much rate fee |
| เวลาเปิด | 营业时间 几点 开门 关门 营业 · เวลาเปิด เปิดกี่โมง ปิดกี่โมง เวลาทำการ เปิด ปิด · hour open close opening what time |
| รถรับส่ง | 接送 酒店 · รถรับส่ง รับส่ง โรงแรม · transfer pickup hotel shuttle |
| สมุนไพร/แพ้ | 过敏 草药 · แพ้ สมุนไพร · allerg herb |
| ติดต่อ | 地址 在哪 电话 · ที่อยู่ เบอร์ โทร · address where location phone call |
| ทักทาย | 你好 您好 · สวัสดี · hello hi hey |

ตัวอย่าง: "营业时间?" → "我们每天营业 10:00–22:00，全年无休。…" · "多少钱?" → รายการราคาภาษาจีน รวม "曼谷放松套餐 Bangkok Relax (120 分钟) ฿2,900/人"

ขั้นตอนจองผ่านแชท: บริการ → วัน (YYYY-MM-DD / พรุ่งนี้ / 明天 / tomorrow) → จำนวนคน (≥7 → ข้อความโทรร้าน) → เวลา (จาก `/api/availability`; รอบเต็ม → "เวลานี้ถูกจองแล้ว") → ต้องการรถไหม → โรงแรม (เกิน 15 กม. → "ไม่มีบริการรับส่งสำหรับระยะนี้") → ชื่อ+เบอร์ (ถ้าไม่ได้ login) → สรุปราคารวมค่ารถจาก `/api/quote` → ยืนยัน → `POST /api/bookings` (`source:"chatbot"`) ใช้กฎเดียวกับหน้าจองทุกข้อ · พิมพ์ "ยกเลิก / cancel / 取消" เพื่อหยุด

**เพลงสปา** — Web Audio API (drone + เสียงระฆังตามลำดับโน้ตตายตัว) สร้างเมื่อกดปุ่ม `music-toggle` เท่านั้น กดอีกครั้งหยุด

---

## 7. อื่น ๆ

- ตาราง/seed สร้างเองตอน web เริ่มทำงาน (`instrumentation.ts` → `CREATE TABLE IF NOT EXISTS` แล้ว seed ถ้า `users` ว่าง) — ไม่ต่อ DB ตอน `next build`
- กันจองชน (NFR-06): ทุกการจอง/ยกเลิกอยู่ใน transaction เดียวและถือ `pg_advisory_xact_lock` → คำขอพร้อมกันสำเร็จ 1 คนพอดี อีกคนได้ `SLOT_TAKEN`
- รหัสผ่าน: `scrypt` (`node:crypto`) เก็บแบบ `scrypt$salt$hash`
- โหมดบั๊กสำหรับฝึก: `BUG_MODE=1` (ดู `BUGS.md`)
