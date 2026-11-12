# Trace t4-cashback-r5 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ไม่

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
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
cafe_solve_checklist
```

### ขั้น 2 · Bash

```
find ./skills -type f | xargs -I{} sh -c 'echo "== {}"; cat {}'
```

ผลที่ได้:

```
== ./skills/cafe_solve_checklist/PURPOSE.md
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
== ./skills/cafe_solve_checklist/SKILL.md
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โ
…(ตัด 2665 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys
from fractions import Fraction


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


_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN_AMOUNT = 10000  # 100 baht in satang
_CAP = 20000         # 200 baht in satang


def cashback(amount, tier, birthday):
    amount = _int(amount, lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"invalid tier: {tier!r}")
    birthday = _flag(birthday)

    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier]
    if birthday:
        value *= 2
    num, den = value.numerator, value.denominator
    result = (num * 2 + den) // (den * 2)  # half up
    return int(min(result, _CAP))


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

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_half_up(self):
        # 10010 * 0.015 = 150.15 -> 150 ; 10100*0.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertEqual(cashback(10010, "silver", False), 150)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)

    def test_reject(self):
        bad = [(-1, "gold", False), (20000.0, "gold", False),
               (True, "gold", False), ("100", "gold", False),
               (None, "gold", False), (20000, "bronze", False),
               (20000, None, False), (20000, "gold", 1),
               (20000, "gold", None)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":-1,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "out of range: -1"}
2
```

**Agent พูด:** สร้างไฟล์ `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ครบทุกข้อ รัน unittest ผ่านทั้ง 6 เทสต์ และลองรันเป็น CLI แล้ว ได้ exit 0 กรณีปกติ และ exit 2 กรณีอินพุตผิด

`cashback(amount, tier, birthday)` ทำงานตามลำดับนี้:
1. **ตรวจอินพุต:**
   - `amount` ต้องเป็น int ตั้งแต่ 0 (ไม่รับ float, bool หรือค่าติดลบ)
   - `tier` ต้องเป็น silver, gold หรือ platinum
   - `birthday` ต้องเป็น bool
   - ถ้าผิดจะ `raise ValueError`
2. **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0
3. **คำนวณ:** ใช้ `Fraction` คูณอัตรา (1.5%, 2.5% หรือ 4%) แล้วคูณ 2 ถ้าเป็นเดือนเกิด
4. **ปัดเศษ:** half up ครั้งเดียวเป็นจำนวนเต็มสตางค์
5. **เพดาน:** ไม่เกิน 20,000 สตางค์ (200 บาท)

ผ่าน CLI ด้วย JSON ที่ใช้ชื่อพารามิเตอร์เป็น key ผลลัพธ์จะเป็น `{"ok": true, "result": ..
…(ตัด 197 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้างไฟล์ `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ครบทุกข้อ รัน unittest ผ่านทั้ง 6 เทสต์ และลองรันเป็น CLI แล้ว ได้ exit 0 กรณีปกติ และ exit 2 กรณีอินพุตผิด

`cashback(amount, tier, birthday)` ทำงานตามลำดับนี้:
1. **ตรวจอินพุต:**
   - `amount` ต้องเป็น int ตั้งแต่ 0 (ไม่รับ float, bool หรือค่าติดลบ)
   - `tier` ต้องเป็น silver, gold หรือ platinum
   - `birthday` ต้องเป็น bool
   - ถ้าผิดจะ `raise ValueError`
2. **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0
3. **คำนวณ:** ใช้ `Fraction` คูณอัตรา (1.5%, 2.5% หรือ 4%) แล้วคูณ 2 ถ้าเป็นเดือนเกิด
4. **ปัดเศษ:** half up ครั้งเดียวเป็นจำนวนเต็มสตางค์
5. **เพดาน:** ไม่เกิน 20,000 สตางค์ (200 บาท)

ผ่าน CLI ด้วย JSON ที่ใช้ชื่อพารามิเตอร์เป็น key ผลลัพธ์จะเป็น `{"ok": true, "result": ...}` ถ้าอินพุตผิดจะได้ `{"ok": false, "error": ...}` และ exit 2

เทสต์ครอบคลุมกรณีปกติ เดือนเกิด ค่าขอบ 9,999 และ 10,000 เศษ .5 พอดี (10,100 สตางค์ของ silver ได้ 152) เพดาน และอินพุตที่ต้องถูกปฏิเสธ
