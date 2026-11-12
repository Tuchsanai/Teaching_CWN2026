# missing-test-file

## อาการ
- `tests` ล้มทุก trace: "ไม่มีไฟล์ test_solve.py ข้าง solve.py"

## สาเหตุ
- โจทย์ไม่ได้ขอไฟล์ทดสอบ Agent ส่งมอบแค่ `solve.py` และตรวจด้วย `python3 -c` ชั่วคราวที่ไม่ได้เก็บไว้
- Agent บางตัวยอมรับตรง ๆ ว่า "ไม่ได้เขียนชุดทดสอบเต็มรูปแบบ" แต่ถือเป็นเรื่องปกติ ไม่ใช่ข้อบกพร่อง

## หลักฐาน
- iter 1 · ล้ม 5/5: t1-cafe-bill-r1, t2-split-bill-r4, t3-shipping-fee-r2, t4-cashback-r2, t4-cashback-r3
- ทุก trace ใช้คำสั่งแค่ 2 ครั้ง (ls skills กับเขียนไฟล์พร้อมรัน) ไม่มีขั้นสร้างหรือรันไฟล์ทดสอบ

## วิธีแก้
สร้าง `test_solve.py` ไว้ในโฟลเดอร์เดียวกับ `solve.py` แล้วรันให้ผ่านก่อนจบงาน
```python
import unittest
from solve import FUNC

class T(unittest.TestCase):
    def test_basic(self): self.assertEqual(FUNC(...), EXPECTED)
    def test_boundary(self): ...   # ค่าขอบทุกเกณฑ์ในโจทย์ (เท่ากับ, น้อยกว่า 1)
    def test_half_up(self): ...    # ค่าที่เศษลงตัวที่ .5 พอดี
    def test_reject(self):
        for bad in [...]:          # ค่านอกช่วง, float, bool, enum ผิด
            with self.assertRaises(ValueError): FUNC(*bad)
```
- ครอบคลุมอย่างน้อย: ปกติ · ขอบของแต่ละเกณฑ์ · ปัดเศษ · ปฏิเสธอินพุต
- รัน `python3 -m unittest -q` (หรือ `pytest -q`) แล้วแก้จนผ่าน
## อัปเดต iter 2: แก้ได้แล้ว
- สกิล `cafe_solve_checklist` ทำให้ Agent สร้าง test_solve.py ครบ 8/8 trace และรันผ่านทุกตัว ไม่มี trace ใดล้มเพราะไม่มีไฟล์
- ปัญหาที่เหลือของข้อ `tests` คือจำนวนเทสต์ไม่ถึง 6 (5 จาก 8 trace) ดู test-count-below-minimum
