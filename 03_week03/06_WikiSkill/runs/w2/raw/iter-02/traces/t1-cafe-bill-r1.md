# Trace t1-cafe-bill-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
        self.assertEqual(cafe_bill([it(6000), it(4000, 2)], False), 14980)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 53498.93
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50825
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50825.95

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        self.assertEqual(cafe_bill([it(50000)], True), 45742.5 and 45743)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
            ([it(100, 1.0)], False), ([it(True)], False), ([{"price": 1}], False),
            ("x", False), ([5], False), ([it(100)], 1), ([it(100)], None),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":10000,"qty":0}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
......
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 19260}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` ข้างกัน unittest ผ่านทั้ง 6 เคส ส่วนการรันเป็น CLI ก็ทดสอบแล้ว: อินพุตปกติ exit 0 และอินพุตผิด exit 2 พร้อม JSON

ก่อนเริ่มผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตาม ซึ่งเป็นที่มาของการตรวจอินพุต CLI และไฟล์ทดสอบ ที่โจทย์ไม่ได้ขอ

- **ลำดับการคิด:** รวมยอด (`price × qty`) → ลด 5% ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป → ลดอีก 10% ถ้าเป็นสมาชิก → บวก VAT 7%
- **การปัดเศษ:** คิดเป็นเศษส่วนด้วยจำนวนเต็มทุกขั้น แล้วปัดครั้งเดียวตอนท้ายแบบ half up คืนค่าเป็น `int` สตางค์
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError` ได้แก่
  - `price` ต่ำกว่า 0 (ผมตั้งช่วงนี้เอง เพราะโจทย์ไม่ได้ระบุราคาขั้นต่ำ)
  - `qty` ต่ำกว่า 1
  - ค่าที่เป็น float หรือ bool
  - item ที่ขาด key
  - `items` ที่ไม่ใช
…(ตัด 159 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` ข้างกัน unittest ผ่านทั้ง 6 เคส ส่วนการรันเป็น CLI ก็ทดสอบแล้ว: อินพุตปกติ exit 0 และอินพุตผิด exit 2 พร้อม JSON

ก่อนเริ่มผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตาม ซึ่งเป็นที่มาของการตรวจอินพุต CLI และไฟล์ทดสอบ ที่โจทย์ไม่ได้ขอ

- **ลำดับการคิด:** รวมยอด (`price × qty`) → ลด 5% ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป → ลดอีก 10% ถ้าเป็นสมาชิก → บวก VAT 7%
- **การปัดเศษ:** คิดเป็นเศษส่วนด้วยจำนวนเต็มทุกขั้น แล้วปัดครั้งเดียวตอนท้ายแบบ half up คืนค่าเป็น `int` สตางค์
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError` ได้แก่
  - `price` ต่ำกว่า 0 (ผมตั้งช่วงนี้เอง เพราะโจทย์ไม่ได้ระบุราคาขั้นต่ำ)
  - `qty` ต่ำกว่า 1
  - ค่าที่เป็น float หรือ bool
  - item ที่ขาด key
  - `items` ที่ไม่ใช่ list
  - `member` ที่ไม่ใช่ bool
- **รายการว่าง:** `items=[]` ให้ผลเป็น 0

ตัวอย่างที่รันดู: สินค้าราคา 10000 สตางค์ จำนวน 2 ชิ้น เป็นสมาชิก ได้ 19260 สตางค์
