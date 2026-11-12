# Trace t1-cafe-bill-r3 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 5 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls -R ./skills 2>/dev/null | head -50
```

ผลที่ได้:

```
./skills:
cafe_solve_checklist

./skills/cafe_solve_checklist:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/*.md
```

ผลที่ได้:

```
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
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

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด ret
…(ตัด 2579 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys


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

    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (num * 2 + den) // (den * 2)


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


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(50001)], False), 50826)

    def test_member_discount_threshold(self):
        # 50000*.95*.9*1.07 = 45732.5 -> half up 45733
        self.assertEqual(cafe_bill([it(50000)], True), 45733)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
            ([it(100, True)], False), ([it(100)], 1), ([it(100)], None),
            ("x", False), ([1], False), ([{"price": 1}], False),
            ([it("1")], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":10000,"qty":0}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 6 tests in 0.001s

FAILED (failures=1)
{"ok": true, "result": 19260}
0
{"ok": false, "error": "out of range: 0"}
2
```

### ขั้น 4 · Bash

```
python3 -m unittest test_solve 2>&1 | head -15
```

ผลที่ได้:

```
...F..
======================================================================
FAIL: test_member_discount_threshold (test_solve.T.test_member_discount_threshold)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/w2-k02-train/t1-cafe-bill-r3/sandbox/test_solve.py", line 21, in test_member_discount_threshold
    self.assertEqual(cafe_bill([it(50000)], True), 45733)
AssertionError: 45743 != 45733

----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
```

**Agent พูด:** My test's arithmetic was wrong: 50000×0.95×0.9×1.07 = 45742.5, which rounds to 45743, so the code is right. I'll fix the test.

### ขั้น 5 · Bash

```
sed -i 's/45732.5 -> half up 45733/45742.5 -> half up 45743/; s/True), 45733)/True), 45743)/' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ unittest ทั้ง 6 ข้อใน `test_solve.py` ผ่านหมด ผมรัน CLI ทดสอบด้วย: อินพุตปกติได้ exit 0 และอินพุตผิดได้ exit 2

**วิธีคิดเงิน**
- ยอดรวม 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- `member=True` ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยเศษส่วนจำนวนเต็มตลอด แล้วปัดครั้งเดียวตอนท้ายแบบ half up (ปัดครึ่งขึ้น)

**ตามสกิล `cafe_solve_checklist`**
- ตรวจอินพุตก่อนคิดเงิน ถ้าผิดจะ raise `ValueError`
  - `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty`
  - `qty` ต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป
  - `price` ต้องเป็นจำนวนเต็มตั้งแต่ 0 ขึ้นไป โจทย์ไม่ได้กำหนดช่วงของราคา ผมจึงตั้งขั้นต่ำเป็น 0 เอง
  - ปฏิเสธ float และ bool
  - `member` ต้องเป็น bool เท่านั้น
- `items` เป็น list ว่างได้ และคืน 0
- `solve.py` รันเป็น CLI ได้ โดยอ่าน
…(ตัด 251 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ unittest ทั้ง 6 ข้อใน `test_solve.py` ผ่านหมด ผมรัน CLI ทดสอบด้วย: อินพุตปกติได้ exit 0 และอินพุตผิดได้ exit 2

**วิธีคิดเงิน**
- ยอดรวม 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- `member=True` ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยเศษส่วนจำนวนเต็มตลอด แล้วปัดครั้งเดียวตอนท้ายแบบ half up (ปัดครึ่งขึ้น)

**ตามสกิล `cafe_solve_checklist`**
- ตรวจอินพุตก่อนคิดเงิน ถ้าผิดจะ raise `ValueError`
  - `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty`
  - `qty` ต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป
  - `price` ต้องเป็นจำนวนเต็มตั้งแต่ 0 ขึ้นไป โจทย์ไม่ได้กำหนดช่วงของราคา ผมจึงตั้งขั้นต่ำเป็น 0 เอง
  - ปฏิเสธ float และ bool
  - `member` ต้องเป็น bool เท่านั้น
- `items` เป็น list ว่างได้ และคืน 0
- `solve.py` รันเป็น CLI ได้ โดยอ่าน JSON จาก stdin แล้วคืน `{"ok": true, "result": ...}` ถ้าผิดจะคืน `{"ok": false, "error": ...}` และ exit 2

ตอนเขียนเทส ผมคำนวณค่าคาดหวังของเคสสมาชิกที่ยอด 50,000 พอดีผิดไปก่อน (ควรเป็น 45,743 ไม่ใช่ 45,733) ผมแก้ที่เทสแล้ว โค้ดใน `solve.py` ไม่ได้แก้
