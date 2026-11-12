# rounding-exact-half-up

มีทั้งแบบที่พลาดและแบบที่สำเร็จ

## อาการ
- พลาด: `half_up` และ `no_drift` ล้มใน cashback `cashback(10020, "gold", false)` คาด 251 ได้ 250 · `cashback(10020, "silver", true)` คาด 301 ได้ 300
- สำเร็จ: cafe_bill, split_bill, shipping_fee ผ่านทั้ง `half_up`, `no_drift`, `boundary`

## สาเหตุ
- โจทย์ไม่ได้บอกวิธีปัดเศษสตางค์ แต่ตัวตรวจคาดว่าเป็น half up (ปัดครึ่งขึ้น) และปัดครั้งเดียวตอนท้าย
- cashback: Agent เลือก `amount * rate // 1000` (ปัดลง) แล้วเขียนว่า "โจทย์ไม่ได้ระบุ จึงเลือกปัดลง" โดยไม่ได้เทียบกับ trace ข้ออื่น
- ข้อที่ผ่านใช้เลขจำนวนเต็มหรือ `Fraction` คำนวณทุกขั้นแบบเป๊ะ แล้วปัด half up ครั้งเดียวตอนท้าย ไม่ใช้ float

## หลักฐาน
- iter 1 · t4-cashback-r3, t4-cashback-r2: ใช้ `//` ปัดลง · half_up พลาด 3/3, no_drift พลาด 2/3
- iter 1 · t1-cafe-bill-r1: `(total*num*2 + den) // (den*2)` ผ่านครบ
- iter 1 · t3-shipping-fee-r2: `Fraction` แล้ว `math.floor(fee + Fraction(1, 2))` ผ่านครบ
- iter 1 · t2-split-bill-r4: `(total*tip_percent + 50) // 100` ผ่านครบ

## วิธีแก้
เมื่อโจทย์ไม่ระบุการปัด ให้ใช้ half up เสมอ ห้ามเลือกปัดลงเอง
- คิดเป็นเศษส่วน `num/den` ด้วยจำนวนเต็มทุกขั้น (ส่วนลดคูณ `95/100` ไม่ปัดระหว่างทาง) แล้วปัดครั้งเดียวสุดท้าย
- สำหรับค่าไม่ติดลบ: `(num * 2 + den) // (den * 2)`
- ตัวอย่าง cashback: `(amount * rate + 500) // 1000` แล้วค่อย `min(..., CAP)` ตรวจ 10020 gold → 251 ✓
- ห้ามใช้ `round()` (ปัดแบบ banker's) และห้ามใช้ float
