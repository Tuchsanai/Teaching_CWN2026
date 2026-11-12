# Trace t1-cafe-bill-r6 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน
- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`
- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%
- `member` = True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && head -c 3000 ./skills/*/SKILL.md ./skills/* 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
cafe_solve_checklist
==> ./skills/cafe_solve_checklist/SKILL.md <==
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
- 
…(ตัด 552 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/SKILL.md | tail -n +38; ls ./skills/cafe_solve_checklist .
```

ผลที่ได้:

```
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
ต้องมีอย่างน้อย: กรณีปกติ 2–3 ตัว · ค่าขอบทุกเกณฑ์ (พอดี, ต่ำกว่า 1, สูงกว่า 1) · เคสปัดเศษที่เศษ = .5 พอดี · `assertRaises(ValueError)` สำหรับค่านอกช่วง, float (`1000.0`), bool, ชนิดผิด
```python
import unittest
from solve import FUNC

class T(unittest.TestCase):
    def test_basic(self): ...
    def test_reject(self):
        with self.assertRaises(ValueError):
            FUNC(...)

if _
…(ตัด 247 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    member = _flag(member)
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        total += _int(it["price"], lo=0) * _int(it["qty"], lo=1)
    num, den = total * 107, 100
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    return (2 * num + den) // (2 * den)  # half up, once, integer-only


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


def I(p, q=1):
    return [{"price": p, "qty": q}]


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill(I(10000, 2), False), 21400)
        self.assertEqual(cafe_bill(I(10000, 2), True), 19260)
        self.assertEqual(cafe_bill([], False), 0)

    def test_threshold(self):
        self.assertEqual(cafe_bill(I(49999), False), 53499)  # 53498.93
        self.assertEqual(cafe_bill(I(50000), False), 50825)  # 50000*.95*1.07
        self.assertEqual(cafe_bill(I(50001), False), 50826)  # 50825.9 -> 50826
        self.assertEqual(cafe_bill(I(50000), True), 45743)   # 45742.5 half up

    def test_half(self):
        self.assertEqual(cafe_bill(I(50), False), 54)  # 53.5 -> 54

    def test_reject(self):
        for items, m in [(I(1000.0), False), (I(100, 0), False), (I(-1), False),
                         (I(True), False), (I(100, 1.0), False), ("x", False),
                         ([1], False), ([{"price": 1}], False), (I(100), 1),
                         (I(100), None), (I("1"), False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":1.5,"qty":2}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 19260}
0
{"ok": false, "error": "expected int, got 1.5"}
2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ unittest ผ่านทั้งหมด

ผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตามนั้นด้วย

**การคิดเงิน**
- ยอดรวมคือผลรวมของ `price*qty`
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5% โดยดูยอดก่อนลด
- ถ้าเป็นสมาชิกลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้ายแบบ half up และคืนค่าเป็น `int`

**ตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError`
- `qty` ต้องเป็น int ตั้งแต่ 1
- `price` ต้องเป็น int ตั้งแต่ 0 ผมตั้งขอบล่างเองเพราะโจทย์ไม่ได้ระบุ
- ปฏิเสธ float, bool, ชนิดผิด และ dict ที่ขาด key
- `member` ต้องเป็น bool เท่านั้น

**CLI:** รัน `solve.py` ได้โดยรับ JSON ทาง stdin ผลลัพธ์ปกติ exit 0 ส่วนอินพุตผิด exit 2 พร้อม JSON แจ้ง error

**ผลทดสอบ**
- ตัวอย่างสินค้า 100 บาท 2 ชิ้น: คิดได้ 21,400 
…(ตัด 313 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ unittest ผ่านทั้งหมด

ผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตามนั้นด้วย

**การคิดเงิน**
- ยอดรวมคือผลรวมของ `price*qty`
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5% โดยดูยอดก่อนลด
- ถ้าเป็นสมาชิกลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้ายแบบ half up และคืนค่าเป็น `int`

**ตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError`
- `qty` ต้องเป็น int ตั้งแต่ 1
- `price` ต้องเป็น int ตั้งแต่ 0 ผมตั้งขอบล่างเองเพราะโจทย์ไม่ได้ระบุ
- ปฏิเสธ float, bool, ชนิดผิด และ dict ที่ขาด key
- `member` ต้องเป็น bool เท่านั้น

**CLI:** รัน `solve.py` ได้โดยรับ JSON ทาง stdin ผลลัพธ์ปกติ exit 0 ส่วนอินพุตผิด exit 2 พร้อม JSON แจ้ง error

**ผลทดสอบ**
- ตัวอย่างสินค้า 100 บาท 2 ชิ้น: คิดได้ 21,400 สตางค์ ถ้าเป็นสมาชิกได้ 19,260 สตางค์
- ผมรัน CLI ทั้งกรณีปกติและกรณีผิดด้วย (อินพุตมี `price` เป็น 1.5 ได้ exit 2)
- `test_solve.py` ครอบคลุมค่าขอบที่ 49,999 / 50,000 / 50,001 และเคสเศษ .5 พอดี (50,000 สตางค์แบบสมาชิกได้ 45,743 จาก 45,742.5)

ไฟล์ที่สร้างอยู่ในโฟลเดอร์ปัจจุบัน คือ `solve.py` และ `test_solve.py`
