# missing-input-validation: ฟังก์ชันไม่ปฏิเสธอินพุตผิด จึงคืนค่าหรือ raise error ผิดชนิด

## อาการ
- `reject_value` ตก ตัวอย่างข้อความของตัวตรวจ:
  - `cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0`
  - `cafe_bill([{"price": 4500, "qty": 0}], false) ต้อง raise ValueError แต่คืนค่า 0`
  - `shipping_fee(0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000`
  - `split_bill(10000, 0, 0) ต้อง raise ValueError แต่ raise ZeroDivisionError`
- `reject_type` ตก ตัวอย่าง: `cashback(20000.0, "gold", false)` คืน 500.0, `cafe_bill([{"price": 4500.0, ...}])` คืน 4815.0, `split_bill(10000.0, 2, 0)` คืน `[5000.0, 5000.0]`
- ตกทั้ง 5 งาน (ครบทุกโจทย์ที่สุ่มมา: cashback, shipping_fee, cafe_bill, split_bill)

## สาเหตุ
- ตัวโจทย์ไม่ได้พูดถึงการปฏิเสธอินพุตเลย แต่ตัวตรวจคาดว่าอินพุตที่อยู่นอกช่วงที่โจทย์ระบุต้อง raise `ValueError` Agent เขียนเฉพาะ happy path ตามสูตรที่โจทย์ให้ จึงไม่มีการตรวจอินพุตเลย
- ค่านอกช่วงที่โจทย์บอกไว้ในวงเล็บ (เช่น `qty` ตั้งแต่ 1, `people` ตั้งแต่ 1, `weight_g` 1–30,000, `amount` ตั้งแต่ 0, `tip_percent` 0–100) ถูกอ่านเป็นแค่คำอธิบาย ไม่ถูกแปลงเป็นเงื่อนไขที่ต้องบังคับ
- เลขทศนิยมที่มีค่าเป็นจำนวนเต็ม (20000.0) ผ่านเข้าสูตรได้เงียบ ๆ ในภาษา Python จึงได้ผลเป็น float
- trace t4-cashback-r3 ที่ใส่ตรวจเฉพาะ `tier` พลาด `reject_value` น้อยลง (1 จาก 3 แทน 3 จาก 3) และ `reject_type` น้อยลง (4 จาก 5 แทน 5 จาก 5) แปลว่าการตรวจบางส่วนช่วยได้ แต่ที่เหลือคือ `amount` ติดลบและชนิดข้อมูลของตัวเลข ยังไม่ถูกตรวจ (ส่วน “ข้อที่ผ่านเพิ่มคือกรณีอะไร” ยังไม่ยืนยัน)
- ในโจทย์ split_bill การหารด้วย `people=0` ทำให้เกิด `ZeroDivisionError` ซึ่งไม่ใช่ `ValueError` จึงนับว่าตก

## หลักฐาน
งานที่ล้ม (ทุกงาน ไม่มีงานผ่านให้เทียบ):
- t4-cashback-r1: `if amount < MIN_AMOUNT: return 0` และ `RATES_PERMILLE[tier]` ไม่มีการตรวจ → พลาด 3/3 และ 5/5
- t4-cashback-r3: มีเฉพาะ `if tier not in RATES_PERMILLE: raise ValueError(...)` → ยังพลาด `reject_value` 1/3 และ `reject_type` 4/5
- t3-shipping-fee-r3: ใช้ `Fraction(weight_g)` ตรง ๆ ไม่ตรวจช่วง → `shipping_fee(0,10,false)` คืน 4000
- t1-cafe-bill-r1: `sum(i["price"] * i["qty"] ...)` ไม่ตรวจ qty/price → qty 0 คืน 0
- t2-split-bill-r1: `divmod(grand, people)` → people=0 เกิด ZeroDivisionError

## วิธีแก้
ให้เขียนฟังก์ชันตรวจอินพุต (validate) ไว้ต้นฟังก์ชัน ก่อนการคำนวณหรือ early return ใด ๆ ทั้งสิ้น:
1. อ่านช่วงค่าที่โจทย์ระบุไว้ทุกตัวแปร (ในวงเล็บ เช่น “ตั้งแต่ 0”, “ตั้งแต่ 1”, “1–30,000”, “0–100”, ชุดค่าที่อนุญาตอย่าง tier) แล้วแปลงเป็นเงื่อนไขตรวจทุกข้อ ค่านอกช่วงให้ `raise ValueError("...")` ที่มีข้อความอธิบาย
2. ตรวจชนิดแบบเข้ม: ตัวเลขที่ควรเป็นจำนวนเต็มต้องเป็น `int` จริง ๆ (`isinstance(x, int)`) และไม่รับ `bool` (`isinstance(x, bool)` ให้ปฏิเสธ) ไม่รับ `float` แม้ค่าเป็นจำนวนเต็มเช่น `20000.0` ส่วนค่าที่ควรเป็น bool (member, birthday, express) ต้องเป็น `bool` จริง และค่าที่ควรเป็น str ต้องเป็น str ผิดชนิดให้ raise `ValueError` (ตัวตรวจคาด `ValueError` ไม่ใช่ `TypeError`)
3. อินพุตซ้อน (เช่น `items` เป็น list ของ dict) ต้องตรวจว่าเป็น list/dict มี key ครบ และตรวจชนิดกับช่วงของค่าในทุกสมาชิก
4. ตรวจก่อน early return เช่น ก่อน `if amount < 10000: return 0` ไม่เช่นนั้นค่าติดลบจะหลุดไปเป็น 0
5. กันตัวหารเป็นศูนย์ด้วยการตรวจช่วงล่วงหน้า อย่าปล่อยให้ `ZeroDivisionError` เกิดเอง
6. ทดสอบเองอย่างน้อย: ค่าต่ำกว่าช่วง ค่าเกินช่วง float ที่มีค่าเป็นจำนวนเต็ม bool ในช่องตัวเลข ชนิดผิดในช่อง str/bool และ key ที่ขาดใน dict
