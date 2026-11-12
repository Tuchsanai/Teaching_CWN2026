# Trace t1-cafe-bill-r1 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
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
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
billing_function_contract
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/billing_function_contract/* 2>/dev/null
```

ผลที่ได้:

```
./skills/billing_function_contract/PURPOSE.md
./skills/billing_function_contract/SKILL.md
# PURPOSE

## Origin
สร้างจาก Trace iteration 1 (t1–t4 ทุก rollout) ที่ไม่มีสกิล Agent เขียนฟังก์ชันถูกตรงตามโจทย์ แต่ตัวตรวจต้องการสิ่งที่โจทย์ไม่ได้บอก

## Problems Addressed
- `reject_value` / `reject_type`: ไม่ตรวจอินพุต ปล่อย float, bool, ค่านอกช่วงผ่าน หรือเกิด ZeroDivisionError แทน ValueError
- `cli_ok` / `cli_error`: ไม่มี `__main__` ที่อ่าน stdin JSON และพิมพ์ `{ok,result|error}` พร้อม exit 2
- `tests`: ไม่มี test_solve.py
- `half_up` / `no_drift`: บาง rollout ปัดลงด้วย `//` ทำให้ 250.5 เป็น 250

## Evolution History
- v1: สร้างครั้งแรก
---
name: billing_function_contract
description: ขั้นตอนเขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินของร้าน BaanKafe ให้ผ่านตัวตรวจครบ ได้แก่ ปัดเศษ half-up, ปฏิเสธอินพุตผิด, CLI JSON และไฟล์ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชันคิดเงิน, ส่วนลด, VAT, ค่าส่ง, เงินคืน หรือหารบิล ในไฟล์ `solve.py`
- ตัวตรวจจะเรียกฟังก์ชันตรง ๆ, รัน `python3 solve.py` ทาง stdin และหาไฟล์ `test_solve.py` ข้าง `solve.py` แม้โจทย์ไม่ได้เขียนไว้ก็ตาม

# When NOT to Apply
- งานที่ไม่ใช่ฟังก์ชันคิดเงินใน `solve.py`

# Instructions

ต้องทำครบทั้ง 4 ข้อ ทั้งที่โจ
…(ตัด 2826 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
from fractions import Fraction


def _int(x, name, lo=None, hi=None):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"{name} out of range")
    return x


def _bool(x, name):
    if type(x) is not bool:
        raise ValueError(f"{name} must be a boolean")
    return x


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be a list")
    _bool(member, "member")
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("each item must be a dict with price and qty")
        price = _int(it["price"], "price", 0)
        qty = _int(it["qty"], "qty", 1)
        total += price * qty
    amount = Fraction(total)
    if total >= 50000:  # 500 baht = 50000 satang
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    return (2 * amount.numerator + amount.denominator) // (2 * amount.denominator)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold(self):
        # 49999 -> no discount: 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000 -> 5%: 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50825)

    def test_member(self):
        # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for items, m in [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100}], False),
            ("x", False),
            ([{"price": 100, "qty": 1}], 1),
        ]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"items":[{"price":50000,"qty":1}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":50000,"qty":0}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 5 tests in 0.001s

FAILED (failures=1)
{"ok": true, "result": 45743}
0
{"ok": false, "error": "qty out of range"}
2
```

### ขั้น 4 · Bash

```
python3 -m unittest test_solve 2>&1 | head -15
```

ผลที่ได้:

```
....F
======================================================================
FAIL: test_threshold (test_solve.T.test_threshold)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/n1-k02-train/t1-cafe-bill-r1/sandbox/test_solve.py", line 14, in test_threshold
    self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50825)
AssertionError: 50826 != 50825

----------------------------------------------------------------------
Ran 5 tests in 0.000s

FAILED (failures=1)
```

**Agent พูด:** My test's expectation was wrong: 50001×0.95×1.07 = 50826.0, so the code is correct. I'll fix the test.

### ขั้น 5 · Bash

```
sed -i 's/"qty": 1}\], False), 50825)\n//' test_solve.py && python3 - <<'EOF'
s=open('test_solve.py').read()
s=s.replace('cafe_bill([{"price": 50001, "qty": 1}], False), 50825','cafe_bill([{"price": 50001, "qty": 1}], False), 50826')
open('test_solve.py','w').write(s)
EOF
python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` unit test ผ่านครบ 5 ข้อ และรัน CLI จริงแล้วได้ผลตามที่คาด

`cafe_bill(items, member)` คำนวณตามลำดับนี้:
1. รวมยอด `price × qty` เป็นสตางค์
2. ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
3. ถ้าเป็นสมาชิก ลดอีก 10%
4. บวก VAT 7%
5. ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย แล้วคืนเป็นจำนวนเต็มสตางค์

การคำนวณใช้เศษส่วนแบบเป๊ะ ไม่ใช้ float และไม่ใช้ `round()` ตัวอย่างเช่น ยอด 50,000 สตางค์แบบสมาชิกได้ 45,742.5 ซึ่งปัดเป็น 45,743

ส่วนที่สกิลสั่งเพิ่มและโจทย์ไม่ได้บอก:
- **ตรวจอินพุต:** ถ้า `price` หรือ `qty` เป็น float, bool หรือค่าติดลบ, `qty` ต่ำกว่า 1, รายการขาด key, `items` ไม่ใช่ list หรือ `member` ไม่ใช่ bool จะ raise `ValueError`
- **CLI:** รับ JSON ทาง stdin แล้วพิม
…(ตัด 228 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` unit test ผ่านครบ 5 ข้อ และรัน CLI จริงแล้วได้ผลตามที่คาด

`cafe_bill(items, member)` คำนวณตามลำดับนี้:
1. รวมยอด `price × qty` เป็นสตางค์
2. ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
3. ถ้าเป็นสมาชิก ลดอีก 10%
4. บวก VAT 7%
5. ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย แล้วคืนเป็นจำนวนเต็มสตางค์

การคำนวณใช้เศษส่วนแบบเป๊ะ ไม่ใช้ float และไม่ใช้ `round()` ตัวอย่างเช่น ยอด 50,000 สตางค์แบบสมาชิกได้ 45,742.5 ซึ่งปัดเป็น 45,743

ส่วนที่สกิลสั่งเพิ่มและโจทย์ไม่ได้บอก:
- **ตรวจอินพุต:** ถ้า `price` หรือ `qty` เป็น float, bool หรือค่าติดลบ, `qty` ต่ำกว่า 1, รายการขาด key, `items` ไม่ใช่ list หรือ `member` ไม่ใช่ bool จะ raise `ValueError`
- **CLI:** รับ JSON ทาง stdin แล้วพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าอินพุตผิดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2

ระหว่างทดสอบ test ข้อแรกที่ผมเขียนคาดค่าผิดเอง (ยอด 50001 ควรได้ 50826 ไม่ใช่ 50825) ตัวโค้ดคำนวณถูกอยู่แล้ว ผมแก้ที่ test
