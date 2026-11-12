# Trace t4-cashback-r4 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก
- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = "silver" "gold" หรือ "platinum" · `birthday` = True คือซื้อในเดือนเกิด
- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%
- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
- เดือนเกิด ได้เงินคืน 2 เท่า
- เงินคืนสูงสุด 200 บาทต่อบิล
- คืนเงินคืน เป็นจำนวนเต็มสตางค์

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
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
cafe_solve_checklist
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
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo
…(ตัด 1967 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
import json
import sys
from fractions import Fraction

_RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}
_MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
_CAP = 20000          # 200 บาท (สตางค์)


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


def cashback(amount, tier, birthday):
    _int(amount, lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"invalid tier: {tier!r}")
    _flag(birthday)
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier] * (2 if birthday else 1)
    num, den = value.numerator, value.denominator
    rounded = (num * 2 + den) // (den * 2)  # half up ครั้งเดียว
    return int(min(rounded, _CAP))


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10001, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(1000000, "gold", False), 20000 if False else 25000 and 20000)

    def test_rounding_half(self):
        # 10100*0.015 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        # 10020*0.025 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_reject(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False), (True, "gold", False),
                     ("100", "gold", False), (20000, "bronze", False), (20000, None, False),
                     (20000, "gold", 1), (20000, "gold", None), (-1, "x", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
sed -i 's/20000 if False else 25000 and 20000/20000/' test_solve.py
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":-1,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "out of range: -1"}
2
```

**Agent พูด:** เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว ทดสอบผ่านทั้ง 5 เคสและลองรันแบบ CLI แล้ว ตามเช็กลิสต์ใน `./skills/cafe_solve_checklist`

- **ตรวจอินพุตก่อนทุกอย่าง:**
  - `amount` ต้องเป็น int ตั้งแต่ 0 ขึ้นไป (ไม่รับ float หรือ bool)
  - `tier` ต้องเป็น silver, gold หรือ platinum
  - `birthday` ต้องเป็น bool
  - ถ้าผิดจะ `raise ValueError`
- **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0 ส่วนยอดพอดี 10,000 ได้เงินคืน
- **การคิดเงินคืน:** คิดด้วย `Fraction` (silver 3/200, gold 1/40, platinum 1/25) คูณ 2 ถ้าเป็นเดือนเกิด แล้วปัดครึ่งขึ้นครั้งเดียว
- **เพดาน:** จำกัดไม่เกิน 20,000 สตางค์ (200 บาท) หลังปัดเศษ
- **CLI:** รับ JSON ทาง stdin ถ้าสำเร็จจะพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าผิดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2
  - ตัวอย่างที่ลอง: gold ยอด 20,000 เดือนเกิด
…(ตัด 193 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว ทดสอบผ่านทั้ง 5 เคสและลองรันแบบ CLI แล้ว ตามเช็กลิสต์ใน `./skills/cafe_solve_checklist`

- **ตรวจอินพุตก่อนทุกอย่าง:**
  - `amount` ต้องเป็น int ตั้งแต่ 0 ขึ้นไป (ไม่รับ float หรือ bool)
  - `tier` ต้องเป็น silver, gold หรือ platinum
  - `birthday` ต้องเป็น bool
  - ถ้าผิดจะ `raise ValueError`
- **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0 ส่วนยอดพอดี 10,000 ได้เงินคืน
- **การคิดเงินคืน:** คิดด้วย `Fraction` (silver 3/200, gold 1/40, platinum 1/25) คูณ 2 ถ้าเป็นเดือนเกิด แล้วปัดครึ่งขึ้นครั้งเดียว
- **เพดาน:** จำกัดไม่เกิน 20,000 สตางค์ (200 บาท) หลังปัดเศษ
- **CLI:** รับ JSON ทาง stdin ถ้าสำเร็จจะพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าผิดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2
  - ตัวอย่างที่ลอง: gold ยอด 20,000 เดือนเกิด ได้ 1000
  - ยอด -1 ได้ error และ exit 2

เคสทดสอบครอบคลุมค่าขอบที่ 9,999 / 10,000 / 10,001 เพดาน เคสปัดเศษที่เศษ .5 พอดี (10,100 silver ได้ 152, 10,020 gold ได้ 251) และอินพุตที่ต้องถูกปฏิเสธ
