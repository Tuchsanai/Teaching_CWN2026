---
name: baankafe-known-policies
description: รายการนโยบายร้าน BaanKafe ที่ไม่เขียนในโจทย์แต่เทสต์ตรวจ (ค่าส่ง รับเองที่ร้าน, ส่งด่วนจำกัดน้ำหนัก, เงินคืน silver ไม่ได้ x2 เดือนเกิด ฯลฯ) พร้อมสูตรอ้างอิงของ cafe_bill, split_bill, shipping_fee, cashback
---

# นโยบายร้าน BaanKafe (รู้ไว้ก่อนเขียน solve.py)

โจทย์บอกกติกาหลักเท่านั้น แต่เทสต์ตรวจ "นโยบายแฝง" ด้วย อ่านรายการด้านล่างแล้วใช้เมื่อโจทย์ตรงหรือคล้าย
ทุกฟังก์ชัน: input เป็นสตางค์จำนวนเต็ม, ตรวจ input เข้มตามสกิล `baankafe-money-function` (int จริง ไม่รับ float/str/bool, ผิด → ValueError)

## cafe_bill(items, member)
- items: list ของ dict {price ≥0 int, qty ≥1 int}; member bool
- subtotal = Σ price×qty ; ถ้า subtotal ≥ 50000 (500 บาท) ×95/100 ; member ×90/100 ; ×107/100 (VAT สุดท้าย)
- ปัดครั้งเดียวท้ายสุด half-up (ใช้ Fraction)
- ตัวอย่าง: [{4500×2}], False → 9630 ; True → 8667 ; [{50000×1}] → 50825 ; [{49999×1}] → 53499

## split_bill(total, people, tip_percent)
- total ≥0, people ≥1, tip_percent int 0–100 (นอกช่วง → ValueError)
- grand = half_up(total×(100+tip)/100) ; base, extra = divmod(grand, people) ; คืน [base+1]*extra + [base]*(people-extra)
- ตัวอย่าง: (10000,3,0) → [3334,3333,3333] ; (2,3,0) → [1,1,0] ; (10000,7,10) → [1572,1572,1572,1571,1571,1571,1571]
- people ไม่ใช่ int (เช่น '3', 0, -2) → ValueError (ห้ามเกิด ZeroDivisionError)

## shipping_fee(weight_g, distance_km, express)
- weight_g int 1–30000 (0 หรือเกิน → ValueError) ; distance_km int ≥0 ; express bool
- **นโยบาย S1: distance_km == 0 = ลูกค้ารับเองที่ร้าน → ค่าส่ง 0** (ยังต้อง validate ทุกตัวก่อน)
- **นโยบาย S2: express=True และ weight_g > 20000 → ValueError** (ส่งด่วนรับไม่เกิน 20,000 กรัม; ส่งธรรมดา 30,000 ได้)
- ฐาน: ≤1000 → 4000 ; ≤5000 → 8000 ; >5000 → 8000 + (w-5000)×1500/1000 (Fraction)
- distance_km > 100 → ×120/100 ; express → ×150/100 ; ปัด half-up ท้ายสุด
- ตัวอย่าง: (500,20,F)=4000 ; (3000,150,F)=9600 ; (5106,150,T)=14686 ; (5217,50,T)=12488

## cashback(amount, tier, birthday)
- amount int ≥0 (สตางค์) ; tier ∈ {"silver","gold","platinum"} ไม่งั้น ValueError ; birthday bool
- amount < 10000 (100 บาท) → 0 ; อัตรา silver 15/1000, gold 25/1000, platinum 4/100
- **นโยบาย C1: เดือนเกิดคูณ 2 เฉพาะ gold และ platinum — silver ไม่ได้สิทธิ์ x2**
- **นโยบาย C2: เงินคืนคือเงินที่ร้านจ่ายออก → ปัดลง (floor) ไม่ใช่ half-up**
- เพดาน min(20000, ผล) (200 บาท/บิล) หลังคูณ2และปัดลง
- ตัวอย่าง: (20000,silver,F)=300 ; (20000,platinum,T)=1600 ; (10015,platinum,T)=801 ; (10020,gold,T)=501 ; (500000,platinum,F)=20000

## รูปแบบนโยบายแฝงที่มักเจอในงานคล้ายกัน (ใช้คิดกับโจทย์ใหม่)
1. ค่า 0 ที่มีความหมายพิเศษ (ระยะ 0 = รับเอง → ฟรี)
2. บริการพิเศษ (ด่วน) มีเพดานขีดความสามารถ → เกิน = ValueError
3. สิทธิพิเศษไม่ครบทุกระดับสมาชิก (ระดับต่ำสุดไม่ได้โบนัส)
4. ทิศทางการปัดแยกตามว่าใครจ่ายใคร (ลูกค้าจ่าย → half-up, ร้านจ่าย → floor)
5. เกณฑ์ขั้นต่ำ/ลดราคาอิงยอดก่อนลด และใช้ "≥" ตามคำว่า "ตั้งแต่…ขึ้นไป"
ถ้าโจทย์ใหม่มีโครงคล้ายอันใดข้างบน ให้ตั้งสมมติฐานตามรูปแบบเหล่านี้ และระบุไว้ในคอมเมนต์ในโค้ด
