# BRIEF · บท 03 · เว็บ Wellness Spa จากพรอมต์ล้วน → ทดสอบด้วย Playwright

(paths below are as seen from the remote box; on Windows the same folder is
`C:\Users\oishi\Documents\GitHub\CWN\Teaching\00_tester\03_sabai-spa-from-prompt`)

## ผู้เรียน
- นักศึกษา ประสบการณ์น้อย เพิ่งเรียนบท 01 (ติดตั้ง Playwright บน Windows) และ 02 (ทดสอบเว็บร้านอาหารสัตว์ที่มีให้พร้อม)
- เวลาเรียนจำกัด → ต้องง่ายมาก, copy & paste พรอมต์อย่างเดียว, อธิบายด้วย "รูป" เป็นหลัก ข้อความน้อย
- ใช้ Claude Code บน Windows 10/11 + Docker Desktop + Node.js + Playwright (ติดตั้งแล้วจากบท 01)

## ต้นแบบที่ต้องอ่านก่อน (สไตล์ต้องเหมือนกัน)
- /root/workspace/CWN/Teaching/00_tester/01_playwright-local-windows/README.md
- /root/workspace/CWN/Teaching/00_tester/02_petshop-test-from-plan/README.md  ← สำคัญที่สุด (รูปแบบ LAB, ตาราง ✅ ผลจริง, 👀 สังเกต, รูปการ์ตูนน่ารัก)
- /root/workspace/CWN/Teaching/00_tester/02_petshop-test-from-plan/TEST-PLAN.md, CLAUDE.md, e2e/ (reporter ที่ทำ GIF+MP4+TEST-REPORT.md)
- รูปการ์ตูนใน 02/img/concept-*.jpg : เด็กผู้ชายผมน้ำตาล เสื้อฮู้ดสีน้ำเงิน + หุ่นยนต์สีขาวหน้าจอฟ้า, ข้อความภาษาไทยในรูป, 3:2

## หลักการใหญ่ของบทนี้ (ผู้สอนสั่ง)
1. **ทุกระบบสร้างจากพรอมต์ล้วน (from scratch)** ในโฟลเดอร์บทมีแค่ README.md, img/ (รูปประกอบบทเรียน) และ assets/ (รูปที่เว็บจะใช้ ทำด้วย image gen ไว้ให้แล้ว เพราะ Claude Code ของนักศึกษาสร้างรูปไม่ได้) — ไม่มีโค้ด ไม่มี CLAUDE.md ไม่มี TEST-PLAN ให้ก่อน
2. ลำดับความคิดแบบมืออาชีพ: **สัมภาษณ์ (เจ้าของ + ลูกค้า) → User Story → FR / BR / NFR → ให้ Claude "เขียนพรอมต์สร้างเว็บ" (BUILD-PROMPT.md) → นักศึกษา copy พรอมต์นั้นไปวาง → Claude สร้างเว็บ Next.js + PostgreSQL ใน Docker (docker compose, ไม่เกิน 2 container) → เดินดูเว็บ → TEST-PLAN.md → Playwright test 3 เบราว์เซอร์ → GIF + MP4 + TEST-REPORT.md แบบ tester → จับบั๊ก (BUG_MODE)**
3. เว็บต้อง "ว้าว" (นักศึกษาจะได้ตั้งใจเรียน) รูปในเว็บใช้จาก assets/ ทั้งหมด
4. แต่ละ LAB: 🎯 เป้าหมาย 1 บรรทัด · รูปอธิบาย · 💬 พรอมต์ (กรอบ text ให้ copy) · ✅ ผลจริง · 👀 สังเกต 2 ข้อ — แบบเดียวกับบท 02

## โจทย์ธุรกิจ: สปาเพื่อสุขภาพและความงาม (ชื่อแบรนด์: "สบายใจ สปา · Sabai Jai Wellness Spa", กรุงเทพฯ)
AI และ Personalization
- AI Skin Analysis: อัปโหลดเซลฟี่ AI วิเคราะห์ผิวและแนะนำทรีตเมนต์
- Wellness Quiz: ตอบคำถามสั้น ๆ ได้แพ็กเกจสปาเฉพาะตัว
- AI Chatbot: ตอบคำถามและจองคิวได้ รองรับ ไทย / อังกฤษ / จีน
- Before/After Simulator: จำลองผลลัพธ์หลังทำทรีตเมนต์
การจองคิว
- จองแบบ real-time เลือกบริการ นักบำบัด และเวลา
- ดูโปรไฟล์และรีวิวนักบำบัด
- จองคู่ / จองกลุ่ม
- จองตามอารมณ์ (เหนื่อย / เครียด / อยากผ่อนคลาย)
สมาชิกและสิทธิพิเศษ
- Wellness Wallet: ซื้อคอร์ส ดูจำนวนครั้งที่เหลือ
- ระดับสมาชิก สะสมแต้ม สิทธิพิเศษวันเกิด
- Gift Card ออนไลน์ ส่งผ่าน LINE หรือ email
ติดตามสุขภาพ
- Dashboard ประวัติทรีตเมนต์และรูป before/after
- กราฟติดตามผลคอร์สกระชับสัดส่วน
ประสบการณ์และความเป็นไทย
- 360 Virtual Tour ห้องสปา
- ข้อมูลสมุนไพรไทยในแต่ละทรีตเมนต์
- เสียงดนตรีสปาเบา ๆ ขณะเปิดเว็บ
- แพ็กเกจนักท่องเที่ยว รวมรถรับส่งจากโรงแรม

## รูปที่เว็บจะได้ (กำลังสร้างอยู่ ใช้ชื่อไฟล์นี้อ้างอิงได้) ใน assets/
brand/hero.jpg, brand/logo.png, brand/chatbot-avatar.png (มาสคอตดอกบัว)
treatments/ thai-massage, aroma-oil, herbal-compress, foot-reflexology, turmeric-facial, aloe-hydrating-facial, coconut-rice-scrub, body-contouring (.jpg)
therapists/therapist-1..6.jpg (1 หญิง40+ นวดไทย, 2 หญิง20+ อโรมา, 3 หญิง30+ ผิวหน้า, 4 ชาย30+ นวด, 5 หญิง50+ สมุนไพร, 6 ชาย20+ โค้ชกระชับสัดส่วน)
rooms/ room-thai-massage, room-couple-suite, room-herbal-steam (.jpg ภาพกว้าง ใช้ทำ virtual tour แบบลากหมุน)
herbs/ plai, turmeric, lemongrass, kaffir-lime, thanaka, aloe-vera (.png)
gift/ giftcard-orchid, giftcard-lotus, giftcard-gold (.jpg)
packages/ hotel-transfer.jpg, couple-package.jpg
moods/ mood-tired, mood-stressed, mood-relax (.png แมวดินปั้นน่ารัก)
skin/sample-face.jpg (หน้าตัวอย่างสำหรับ before/after simulator)

## ข้อจำกัดทางเทคนิคที่ต้องคิดเผื่อ
- "AI" ทั้งหมดต้องเป็น **กฎตายตัว (rule-based, deterministic)** ไม่เรียก AI จริง เพื่อให้ test ได้ผลเดิมทุกครั้ง และไม่ต้องใช้ API key
- เพลงต้องไม่เล่นเองอัตโนมัติ (เบราว์เซอร์บล็อก) → ปุ่มเปิด/ปิด, สร้างเสียงด้วย Web Audio ได้ ไม่ต้องมีไฟล์เสียง
- รูปเซลฟี่ประมวลผลในเบราว์เซอร์ ไม่อัปโหลดเก็บ (PDPA)
- LINE/email ของ gift card เป็นการจำลอง (แสดงตัวอย่างข้อความที่ "ส่ง")
- ต้องมี data-testid ทุกจุดสำคัญ, /api/health, /api/test/reset (รีเซ็ตข้อมูลทดสอบ), ผู้ใช้ตัวอย่าง (seed), BUG_MODE=1 ฝังบั๊ก 3 จุด
- เว็บ + DB = docker compose 2 service (web: Next.js, db: postgres) port 3000
- เวลา "real-time" ต้องทดสอบได้ → ควรล็อกวันที่/เวลาอ้างอิงได้ (เช่น ให้ test ส่งวันที่เอง หรือใช้วันพรุ่งนี้)
- นักศึกษาใช้ Windows (PowerShell) ทุกคำสั่งในพรอมต์ต้องใช้ได้บน Windows
