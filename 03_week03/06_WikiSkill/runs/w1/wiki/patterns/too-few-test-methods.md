# too-few-test-methods: มี test_solve.py แล้วแต่นับได้น้อยกว่า 6 เทสต์ จึงตก `tests`

## อาการ
- `tests` ตกด้วยข้อความ `unittest พบ N เทสต์ (ต้องมีอย่างน้อย 6)`
  - `t4-cashback-r3` พบ 5
  - `t3-shipping-fee-r3` พบ 4
  - `t1-cafe-bill-r3` พบ 5
  - `t2-split-bill-r2` พบ 4
- ใน `t1-cafe-bill-r3` และ `t2-split-bill-r2` ข้อ `tests` เป็นข้อเดียวที่ตก (0.90, ผ่าน 9 จาก 10)
- ข้ออื่นของสัญญาไฟล์ (`reject_value`, `reject_type`, `cli_ok`, `cli_error`) ผ่านครบทุก Trace ของรอบนี้ ปัญหานี้จึงแยกจาก `missing-test-file.md` (ไฟล์มีแล้ว แต่จำนวนเทสต์ไม่ถึงเกณฑ์)

## สาเหตุ
- ตัวตรวจนับจำนวน test method ที่ unittest รายงาน ตัวเลขตรงกับบรรทัด `Ran N tests` ที่ Agent เห็นเองในทุก Trace ที่ตก (4, 5, 4, 5) เทสต์ที่วนด้วย `subTest` นับเป็นเมธอดเดียว เช่น `test_reject` ของ `t1-cafe-bill-r3` ที่วนผ่านอินพุตผิด 13 ชุด ก็นับเป็น 1 เทสต์
- `SKILL.md` บอกหมวดที่ต้องครอบคลุม (กรณีปกติอย่างน้อย 3 กรณี, ค่าขอบ, ปัดเศษ, อินพุตผิด) แต่ไม่บอกจำนวนเมธอดขั้นต่ำ Agent ทุกตัวอ่านสกิลและทำตาม โดยเขียนหนึ่งเมธอดต่อหนึ่งหมวด (`test_normal`, `test_edges`/`test_threshold`, `test_rounding`, `test_reject`) แล้วยัด assert หลายตัวไว้ในเมธอดเดียว จึงได้ 4–5 เมธอด
- ดังนั้นสาเหตุคือสกิลไม่ได้บอกเกณฑ์ ไม่ใช่ Agent ละเลยสกิล
- ยังไม่ยืนยัน: ตัวตรวจนับแค่จำนวนเมธอด หรือดูความครอบคลุมด้วย (เห็นแค่ข้อความเรื่องจำนวน)

## หลักฐาน
งานที่ล้ม:
- `t2-split-bill-r2`: เมธอดคือ `test_normal`, `test_remainder`, `test_edges`, `test_reject` ผลรัน `Ran 4 tests ... OK` แล้วตอบว่า "เทสต์ 4 ชุดผ่านทั้งหมด" โดยไม่ได้ตรวจเทียบกับเกณฑ์
- `t3-shipping-fee-r3`: `Ran 4 tests` ค่าขอบทั้งหมดอยู่ใน `test_edges` เมธอดเดียว
- `t1-cafe-bill-r3`: `test_normal`, `test_threshold`, `test_member_stack`, `test_rounding`, `test_reject` = 5
- `t4-cashback-r3`: `Ran 5 tests`

งานที่ผ่าน (โจทย์เดียวกับ `t2-split-bill-r2` คือ split_bill):
- `t2-split-bill-r3`: `Ran 7 tests` แยกเมธอดเป็น `test_even`, `test_remainder_first_pay_more`, `test_tip`, `test_tip_remainder`, `test_rounding_half_up`, `test_edges`, `test_reject` ผ่าน `tests`
- `t2-split-bill-r1`: `Ran 9 tests` (แยก `test_single`, `test_zero_total`, `test_more_people_than_satang`, `test_tip_bounds` ออกเป็นเมธอดของตัวเอง) ผ่าน `tests`
- `t4-cashback-r1`: `Ran 6 tests` ผ่าน `tests` (ผ่านพอดีเกณฑ์)

ข้อสังเกต: ความต่างระหว่าง `t2-split-bill-r2` (ตก) กับ `t2-split-bill-r3` (ผ่าน) อยู่ที่การแตกเมธอดเท่านั้น โค้ด solve.py และการตรวจอินพุตผ่านเหมือนกัน

ข้อสรุปเชิงคาดการณ์ (inference): ถ้า `tests` ผ่าน `t1-cafe-bill-r3` และ `t2-split-bill-r2` จะได้ 10 จาก 10

## วิธีแก้
- เขียนเทสต์อย่างน้อย 8 เมธอด (เผื่อจากเกณฑ์ 6) แต่ละเมธอดเป็น `def test_...` แยกกัน การวนลูปหรือ `subTest` ในเมธอดเดียวไม่เพิ่มจำนวน
- แยกตามหมวดแบบทั่วไป ใช้ได้กับทุกโจทย์:
  - กรณีปกติ แยกเป็นหลายเมธอดตามสถานการณ์ (เช่น แบบไม่มีส่วนลด แบบมีส่วนลดซ้อน)
  - ค่าขอบ หนึ่งเมธอดต่อหนึ่งเกณฑ์ในโจทย์ (ต่ำกว่า พอดี สูงกว่า)
  - เคสปัดเศษ และเคสผลลัพธ์ต้องเป็น `int` จริง
  - อินพุตผิด หนึ่งเมธอดต่อหนึ่งพารามิเตอร์ เช่น `test_reject_<ชื่อพารามิเตอร์>` ครอบ float, bool, ค่านอกช่วง, ชนิดผิด
  - ผลทาง CLI ถ้าทดสอบผ่าน subprocess ได้
- หลังรัน `python3 -m unittest test_solve -v` ให้อ่านบรรทัด `Ran N tests` แล้วต้องได้ N ≥ 8 ก่อนตอบ ถ้าไม่ถึงให้แตกเมธอดเพิ่ม
- ไม่ต้องเพิ่มเทสต์ซ้ำซ้อนเพื่อให้ครบจำนวน แต่ละเมธอดควรตรวจสิ่งที่ต่างกันจริง และต้องอ่านค่าที่คาดให้ถูกก่อนเขียน (ดู `shallow-self-check.md`)
- ให้ใส่ข้อนี้ในรายการตรวจก่อนตอบของสกิลเป็นข้อตัวเลข เพราะเกณฑ์นี้ Agent มองไม่เห็นเอง
