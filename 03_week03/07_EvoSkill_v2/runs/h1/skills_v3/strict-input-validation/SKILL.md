---
name: strict-input-validation
description: ตรวจ input ของฟังก์ชันตามสเปกอย่างเข้มงวด ปฏิเสธชนิดผิด (bool, float, str แทน int) และค่านอกช่วงด้วย ValueError เสมอ ใช้เมื่อสเปกกำหนดช่วงหรือชนิดของ input หรือเมื่อฟังก์ชันรับข้อมูลจากภายนอก
---

# ตรวจ input อย่างเข้มงวด

ทุกฟังก์ชันที่สเปกกำหนดช่วงหรือชนิดของ input ต้องปฏิเสธค่าที่ผิดด้วย `ValueError` เท่านั้น

## กติกา

- **จำนวนเต็ม:** ใช้ `type(x) is int` ไม่ใช้ `isinstance(x, int)` อย่างเดียว เพราะ `bool` เป็น subclass ของ `int` และ `True` จะหลุดเข้ามาเป็น 1
- **ค่าเริ่มต้นคือจำนวนเต็ม:** ถ้าสเปกไม่ได้เขียนว่า "ทศนิยม" หรือ "จำนวนจริง" ให้ถือว่าตัวเลขทุกตัวเป็น int รวมถึงระยะทาง น้ำหนัก ราคา เปอร์เซ็นต์ จำนวนชิ้น และจำนวนคน ไม่ยอมรับ float แม้ค่าเป็นจำนวนเต็มเช่น `100.0`
- **ถ้าสเปกระบุทศนิยมชัดเจน** เท่านั้นจึงรับ float ได้ และต้องปฏิเสธ `nan`, `inf` และค่าติดลบ
- **ชนิด int ที่มีค่าเท่ากัน** ห้ามเปลี่ยนไปเป็น float ในขั้นกลาง (เช่น `/` ของ Python ได้ float เสมอ ใช้ `Fraction` หรือ `//` แทน)
- **str ต้องถูกปฏิเสธ** แม้หน้าตาเป็นตัวเลข เช่น `'2'`
- **flag ต้องเป็น bool จริง:** `type(x) is bool` มิฉะนั้น raise
- **เช็คช่วงตามสเปก:** ค่าต่ำสุด (เช่น ตั้งแต่ 1 ปฏิเสธ 0 และค่าติดลบ), ค่าสูงสุด, และขอบทั้งสองฝั่ง
- **ตัวเลือก (enum) ที่ไม่รู้จัก:** raise ValueError รับเฉพาะค่าที่สเปกระบุตรงตัว
- **อย่า raise TypeError** แม้ชนิดจะผิด เพราะ `TypeError` ไม่ใช่ subclass ของ `ValueError` และการทดสอบส่วนใหญ่ใช้ `assertRaises(ValueError)`
- **ตรวจก่อนคำนวณ** อย่าปล่อยให้ `KeyError`, `IndexError`, `ZeroDivisionError` หลุดออกมาจากขั้นกลาง ให้ตรวจเองแล้ว raise ValueError ที่มีข้อความชัด
- **ตรวจทุกสมาชิกของ list** ว่าเป็น dict, มี field ครบ, และ field แต่ละตัวผ่านกติกาชนิดและช่วง

## ตัวอย่างตัวตรวจ

```python
def require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value

def require_flag(value, label):
    if type(value) is not bool:
        raise ValueError(f"{label} ต้องเป็น True หรือ False")
    return value
```

## ทดสอบการปฏิเสธ

ทุกฟังก์ชันควรมีการทดสอบว่า input ผิดถูกปฏิเสธ อย่างน้อยครอบคลุม:

- ค่าต่ำกว่าขอบล่าง เช่น 0 หรือ -1 เมื่อเกณฑ์เริ่มที่ 1
- float ที่ค่าเท่ากับจำนวนเต็ม เช่น `4500.0`
- str ที่เป็นตัวเลข เช่น `'2'`
- bool แทนจำนวนเต็ม เช่น `True` แทน 1

```python
import unittest

class Reject(unittest.TestCase):
    def test_float_rejected(self):
        with self.assertRaises(ValueError):
            f(4500.0, 1)
```
