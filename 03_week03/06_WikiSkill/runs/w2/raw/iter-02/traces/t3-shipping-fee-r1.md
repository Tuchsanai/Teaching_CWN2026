# Trace t3-shipping-fee-r1 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 5 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ
- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน
- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
- คืนค่าส่ง เป็นจำนวนเต็มสตางค์

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


def shipping_fee(weight_g, distance_km, express):
    weight_g = _int(weight_g, 1, 30000)
    distance_km = _int(distance_km, 0)
    express = _flag(express)

    if weight_g <= 1000:
        fee = Fraction(40)
    elif weight_g <= 5000:
        fee = Fraction(80)
    else:
        fee = 80 + Fraction((weight_g - 5000) * 15, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    satang = fee * 100
    return (satang.numerator * 2 + satang.denominator) // (satang.denominator * 2)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)

    def test_edges(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 80.015 -> 8001.5 half up
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)
        self.assertEqual(f(30000, 0, False), 41500)

    def test_combo(self):
        self.assertEqual(f(500, 101, True), 7200)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5001, 0, True), 12002)  # 12002.25

    def test_reject(self):
        for args in [(0, 1, False), (30001, 1, False), (1, -1, False),
                     (1000.0, 1, False), (True, 1, False), ("5", 1, False),
                     (1, 1.0, False), (1, 1, 1), (1, 1, None), (1, None, False)]:
            with self.assertRaises(ValueError):
                f(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"weight_g":500,"distance_km":10,"express":false}' | python3 solve.py; echo $?
echo '{"weight_g":0,"distance_km":10,"express":false}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1)
{"ok": true, "result": 4000}
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
..F..
======================================================================
FAIL: test_edges (test_solve.T.test_edges)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/w2-k02-train/t3-shipping-fee-r1/sandbox/test_solve.py", line 18, in test_edges
    self.assertEqual(f(30000, 0, False), 41500)
AssertionError: 45500 != 41500

----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1)
```

**Agent พูด:** My test expectation was wrong: 80 + 25×15 = 455 baht, so 45500 satang is correct. I'll fix the test.

### ขั้น 5 · Bash

```
sed -i 's/41500/45500/' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** I wrote `shipping_fee` in `solve.py` and a unit test file, `test_solve.py`. All 5 tests pass, and I ran `solve.py` from the command line once with valid input and once with invalid input.

- **Fee rules:** It follows your tiers, the 20% surcharge over 100 km and the 50% express surcharge. The calculation uses exact fractions and rounds half up once at the end. The result is an integer in satang.
- **Invalid input:** Following the checklist in `./skills`, it raises `ValueError` for weight outside 1–30,000, negative distance, floats such as `1000.0`, booleans passed as numbers, and an `express` value that isn't a bool. That means a distance given as a float, like `10.0`, is rejected too.
- **Command line:** `echo '{...}' | python3 solve.py` prints `{"ok": true, "result": ...}` and exits 0. I
…(ตัด 211 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

I wrote `shipping_fee` in `solve.py` and a unit test file, `test_solve.py`. All 5 tests pass, and I ran `solve.py` from the command line once with valid input and once with invalid input.

- **Fee rules:** It follows your tiers, the 20% surcharge over 100 km and the 50% express surcharge. The calculation uses exact fractions and rounds half up once at the end. The result is an integer in satang.
- **Invalid input:** Following the checklist in `./skills`, it raises `ValueError` for weight outside 1–30,000, negative distance, floats such as `1000.0`, booleans passed as numbers, and an `express` value that isn't a bool. That means a distance given as a float, like `10.0`, is rejected too.
- **Command line:** `echo '{...}' | python3 solve.py` prints `{"ok": true, "result": ...}` and exits 0. Invalid input prints `{"ok": false, "error": ...}` and exits 2.

One wrong test expectation of mine (30,000 g should cost 455 baht, not 415) turned up and I fixed it in the test. The function was already correct.
