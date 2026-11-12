---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด return 0)
ทุกอินพุตผิดช่วง/ผิดชนิดต้อง `raise ValueError` (ห้ามปล่อยให้เป็น ZeroDivisionError/TypeError/KeyError)
```python
def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):   # ปฏิเสธ bool และ float เช่น 20000.0
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x

def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x
```
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo=0, "ตั้งแต่ 1" → lo=1, "1–30,000" → lo=1, hi=30000)
- ใช้ `_flag` กับพารามิเตอร์ True/False, ตรวจ enum (เช่น tier) ว่าอยู่ในรายการที่โจทย์ให้
- list/dict: ตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ, และค่าในนั้นผ่าน `_int` (ห้ามคืน KeyError)
- ตรวจ `-1` ก่อนเงื่อนไข "ต่ำกว่าเกณฑ์ → 0" เสมอ

## 2. ปัดเศษ: half up ครั้งเดียวตอนท้าย ด้วยจำนวนเต็ม
- โจทย์ไม่ระบุวิธีปัด = half up เสมอ ห้ามเลือกปัดลง (`//` ตรง ๆ) ห้าม `round()` ห้าม float
- คิดเป็นเศษส่วน `num/den` ด้วย int (หรือ `Fraction`) ทุกขั้น ไม่ปัดระหว่างทาง แล้วปัดครั้งเดียว: `(num*2 + den) // (den*2)` (ค่าไม่ติดลบ)
- ลำดับคูณ (ส่วนลด/ค่าธรรมเนียม/VAT) ตามลำดับในโจทย์ ส่วนเพดาน (`min`) ทำหลังปัดตามที่โจทย์เรียง
- คืนค่าเป็น `int` เสมอ

## 3. ต่อท้าย solve.py ให้รันเป็น CLI ได้ (key ของ JSON = ชื่อพารามิเตอร์ของฟังก์ชัน)
```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = FUNC(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))

if __name__ == "__main__":
    _main()
```
แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์ ผิดปกติต้อง exit 2 พร้อม JSON ไม่มี traceback

## 4. สร้าง test_solve.py ข้าง solve.py (unittest) แล้วรันให้ผ่าน
ตัวตรวจนับจำนวน method ที่ชื่อขึ้นต้นด้วย `test_` และต้องได้ **อย่างน้อย 6** แต่ `for` และ `subTest` ใน method เดียวนับเป็น 1 เท่านั้น ให้เขียน **อย่างน้อย 8 method แยกกัน** ดังนี้ (1 หมวด = 1 method):
`test_basic` · `test_boundary_exact` · `test_boundary_below` · `test_boundary_above` · `test_half_up` (เศษ .5 พอดี) · `test_reject_value` (นอกช่วง, ค่าติดลบ, ค่าที่ผิด enum) · `test_reject_type` (float เช่น `1000.0`, bool, str, None) · `test_zero_or_cap` (ค่า 0, list ว่าง หรือเพดาน แล้วแต่โจทย์)
ห้ามรวมหลายหมวดไว้ใน method เดียว ห้ามหวังพึ่ง `subTest` ให้นับเพิ่ม คำนวณค่าคาดหวังด้วยมือให้ถูกก่อนเขียน อย่าเขียนนิพจน์แปลก ๆ ถ้าเทสต์ล้มให้เช็กก่อนว่าผิดที่โค้ดหรือที่ค่าคาดหวัง
```python
import unittest
from solve import FUNC

class T(unittest.TestCase):
    def test_basic(self): ...
    def test_boundary_exact(self): ...
    def test_boundary_below(self): ...
    def test_boundary_above(self): ...
    def test_half_up(self): ...
    def test_reject_value(self): ...
    def test_reject_type(self): ...
    def test_zero_or_cap(self): ...
    def test_reject(self):
        with self.assertRaises(ValueError):
            FUNC(...)

if __name__ == "__main__":
    unittest.main()
```
รัน `python3 -m unittest -v test_solve` และ `echo '{...}' | python3 solve.py; echo $?` ทั้งกรณีปกติ (exit 0) และกรณีผิด (exit 2) ก่อนจบงาน
**ก่อนจบงานต้องดู `Ran N tests` จากผล `python3 -m unittest test_solve 2>&1 | tail -5` ถ้า N < 8 ให้เพิ่ม method แล้วรันใหม่ ห้ามสรุปว่าผ่านโดยไม่เทียบตัวเลขนี้**
