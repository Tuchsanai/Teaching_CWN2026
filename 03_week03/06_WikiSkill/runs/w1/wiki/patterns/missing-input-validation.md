# missing-input-validation: ฟังก์ชันไม่ตรวจอินพุต ค่านอกช่วงและชนิดผิดไม่ถูก raise ValueError

## อาการ
- `reject_value` ตกทั้ง 3 โจทย์ที่เห็น พลาดทุกกรณี (3/3, 4/4, 5/5)
  - `cafe_bill([{"price": 4500, "qty": 0}], false)` ต้อง raise ValueError แต่คืนค่า 0
  - `cashback(-1, "gold", false)` ต้อง raise ValueError แต่คืนค่า 0
  - `shipping_fee(0, 10, false)` ต้อง raise ValueError แต่คืนค่า 4000
  - `split_bill(10000, 0, 0)` ต้อง raise ValueError แต่ได้ ZeroDivisionError
- `reject_type` ตกทั้งหมด (5/5, 5/5, 4/4, 5/5): ส่ง float เข้าไปแล้วได้ผลคืนมาเป็น float
  - `cafe_bill([{"price": 4500.0, "qty": 1}], false)` คืน 4815.0
  - `cashback(20000.0, "gold", false)` คืน 500.0
  - `split_bill(10000.0, 2, 0)` คืน [5000.0, 5000.0]
  - `shipping_fee(1000.0, 10, false)` คืน 4000

## สาเหตุ
- โค้ดของ Agent ทั้ง 4 โจทย์เป็นสูตรคำนวณล้วน ไม่มี `if ... raise ValueError` เลย
- ตัวตรวจเรียกฟังก์ชันด้วยอินพุตผิดแล้วคาดว่าจะได้ ValueError แต่โจทย์ไม่ได้เขียนไว้ตรง ๆ ช่วงที่ระบุในโจทย์ (เช่น "ตั้งแต่ 1", "1–30,000", "0–100", ชื่อ tier ที่อนุญาต) คือข้อมูลที่ต้องใช้ตรวจ Agent อ่านเป็นแค่คำอธิบายข้อมูล
- ในโจทย์ `split_bill` ค่า `people=0` ไปถึงบรรทัด `divmod(grand, people)` แล้วเกิด ZeroDivisionError ซึ่งไม่ใช่ ValueError การปล่อยให้ข้อผิดพลาดภายในหลุดออกมาจึงไม่นับเป็นการ reject
- ไม่มีสกิลใช้งานในรอบนี้ จึงไม่มีอะไรบอก Agent เรื่องนี้
- เมื่อ float ผ่านเข้าไป สูตรจำนวนเต็มยังคำนวณต่อได้และคืนค่าเป็น float ผลคือผิดสัญญาที่ต้องคืนจำนวนเต็มสตางค์ด้วย

## หลักฐาน
งานที่ล้ม (ทั้งหมดไม่มีการตรวจอินพุต):
- `t1-cafe-bill-r1`: `total = sum(i["price"] * i["qty"] for i in items)` ไม่มีการเช็ก qty หรือชนิด
- `t2-split-bill-r1`: `base, extra = divmod(grand, people)` ได้ ZeroDivisionError เมื่อ people=0
- `t3-shipping-fee-r3`: ใช้ `Fraction(weight_g)` ตรง ๆ ทำให้ float และ 0 ผ่านเข้าไป
- `t4-cashback-r1`, `t4-cashback-r3`: `RATES_BP[tier]` ไม่มีการเช็ก tier ก่อน และ amount ติดลบตกไปที่ `amount < MIN_AMOUNT: return 0`

งานที่ผ่าน: ไม่มีใน Trace ที่สุ่มมารอบนี้ ยังไม่มีตัวอย่างที่แก้สำเร็จ

ยังไม่ยืนยัน: ตัวตรวจจะนับ `True/False` (bool) ว่าเป็นชนิดผิดด้วยหรือไม่ ข้อความของตัวตรวจที่เห็นมีแต่กรณี float

## วิธีแก้
- ใส่ขั้นตรวจอินพุตไว้ต้นฟังก์ชัน ก่อนคำนวณใด ๆ แล้ว raise `ValueError` พร้อมข้อความที่อ่านรู้เรื่อง
- แปลงทุกช่วงและเงื่อนไขในโจทย์เป็นการตรวจ ได้แก่ ขอบล่าง/ขอบบน (เช่น qty ≥ 1, น้ำหนัก 1–30,000, tip 0–100, people ≥ 1, amount ≥ 0), ค่าที่อนุญาต (เช่น tier), โครงสร้าง (list ของ dict ต้องมี key ครบ)
- ตรวจชนิดแบบเข้มด้วย `type(x) is int` สำหรับค่าที่ควรเป็นจำนวนเต็ม เพื่อให้ float ถูกปฏิเสธ และปฏิเสธ bool ไปด้วยเพื่อความปลอดภัย (ส่วนนี้ยังไม่ยืนยันว่าตัวตรวจต้องการ) ส่วนพารามิเตอร์ที่ควรเป็น bool ให้ตรวจว่าเป็น bool จริง
- อย่าปล่อยให้ ZeroDivisionError, KeyError, TypeError ภายในหลุดออกมาแทน ValueError ตรวจก่อนถึงบรรทัดที่หารหรือค้นตาราง
- ทดสอบเองก่อนตอบด้วยอินพุตผิด 1 ตัวต่อ 1 พารามิเตอร์ และดูว่าได้ ValueError จริง (ดู `shallow-self-check.md`)
## อัปเดตรอบ 2: แก้ได้แล้ว
- `reject_value` และ `reject_type` ผ่านครบในทั้ง 7 Trace ที่สุ่มมา (`t1-cafe-bill-r3`, `t2-split-bill-r1`, `t2-split-bill-r2`, `t2-split-bill-r3`, `t3-shipping-fee-r3`, `t4-cashback-r1`, `t4-cashback-r3`) หลังมีสกิล `solve-py-contract` ซึ่ง Agent ทุกตัวอ่านก่อนเริ่มงาน (รันคำสั่ง `cat ./skills/*/SKILL.md`)
- สิ่งที่ Agent ทำตามสกิล: คัดตัวช่วย `_need_int` ไปใช้ (`type(v) is not int` -> ValueError) ตรวจ `type(birthday) is not bool` ตรวจ `type(tier) is not str or tier not in RATES` และตรวจ list ของ dict ทุกรายการ (`t1-cafe-bill-r3`: ตรวจ `items[i]` เป็น dict มี price/qty และ qty >= 1)
- ผลทาง CLI ที่เห็น: `t2-split-bill-r2` ส่ง people=0 ได้ `{"ok": false, "error": "people ต้องไม่น้อยกว่า 1"}` exit=2 (เดิมรอบ 1 หลุดเป็น ZeroDivisionError)
- ยังไม่ยืนยัน: ตัวตรวจนับ bool เป็นชนิดผิดหรือไม่ ทุก Trace ปฏิเสธ bool อยู่แล้วและผ่าน จึงคงวิธีนี้ไว้ได้
- หมายเหตุ: `t3-shipping-fee-r3` รับ distance_km เป็น float ได้ (`type(distance_km) not in (int, float)`) และยังผ่าน `reject_type` ซึ่งสอดคล้องว่าตัวตรวจน่าจะลอง float กับพารามิเตอร์จำนวนเต็มอย่าง weight_g ส่วนการรับ float ของ distance_km เป็นข้อสมมติของ Agent ไม่ใช่ข้อกำหนดในโจทย์
