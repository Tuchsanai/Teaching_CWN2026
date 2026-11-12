# Trace t3-shipping-fee-r2 · iteration 2

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
ls ./skills 2>/dev/null && head -50 ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
billing_function_contract
==> ./skills/billing_function_contract/SKILL.md <==
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

ต้องทำครบทั้ง 4 ข้อ ทั้งที่โจทย์ไม่ได้บอก

## 1. คำนวณด้วยจำนวนเต็ม และปัดเศษ half-up
- ห้ามใช้ float และห้ามใช้ `round()` เพราะ `round` ปัดแบบ banker's
- ใช้ `Fraction` หรือเลขจำนวนเต็ม คูณทุกอัตราเป็นเศษส่วน เช่น 2.5% = 25/1000 และ 7% = 107/100
- ปัดครั้งเดียวตอนท้าย สูตร half-up ของ `num/den` ที่ไม่ติดลบ: `(2*num + den) // (2*den)`
- การปัดลง (`//` อย่างเดียว) ผิด เช่น 250.5 ต้องได้ 251
- ทำตามลำดับขั้นที่โจทย์ระบุ (ลด → บวก → เพดาน/ขั้นต่ำ) และดูว่า "ตั้งแต่" หรือ "เกิน" ใช้ >= หรือ >
- ถ้าโจทย์สั่งให้ปัดทีละขั้นจึงค่อยปัดทีละขั้น

## 2. ตรวจอินพุตก่อนคำนวณ แล้ว raise ValueError เท่
…(ตัด 1301 ตัวอักษร)
```

### ขั้น 2 · Bash

```
sed -n 50,200p ./skills/billing_function_contract/SKILL.md; ls -R .
```

ผลที่ได้:

```
- ผิดพลาด: `{"ok": false, "error": "<ข้อความ>"}` และ exit 2 ห้ามมี traceback
- JSON พัง, key ขาด หรือ ValueError ทุกกรณี ให้ไปทางผิดพลาด

```python
if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = FUNC(**data)          # เปลี่ยน FUNC เป็นชื่อฟังก์ชันของโจทย์
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
```

## 4. เขียน test_solve.py ไว้ข้าง solve.py
ใช้ `unittest` หรือ `pytest` ที่รันได้เอง ต้องมีอย่างน้อย: กรณีทั่วไป, ค่าขอบ (พอดีเกณฑ์ ±1), เศษที่ลงท้าย .5 ต้องปัดขึ้น, `assertRaises(ValueError)` สำหรับค่านอกช่วง, float และ bool

## 5. ก่อนจบงาน ต้องรันจริง
- `python3 -m unittest test_solve` (หรือ pytest) ต้องผ่าน
- `echo '<json ปกติ>' | python3 solve.py` ต้องได้ ok true และ exit 0
- `echo '<json ค่าผิด>' | python3 solve.py; echo $?` ต้องได้ ok false และ exit 2
.:
skills

./skills:
billing_function_contract

./skills/billing_function_contract:
PURPOSE.md
SKILL.md
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import math
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int:
        raise ValueError("weight_g must be an integer")
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g out of range")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km must be a number")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km must be finite")
    if distance_km < 0:
        raise ValueError("distance_km out of range")
    if type(express) is not bool:
        raise ValueError("express must be a boolean")

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
    num, den = (fee * 100).numerator, (fee * 100).denominator
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
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
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)

    def test_multipliers(self):
        self.assertEqual(f(500, 10, True), 6000)
        self.assertEqual(f(500, 200, True), 7200)

    def test_half_up(self):
        # 80.025*1.5 = 120.0375 -> 12004 ; 5003g: 80.045 -> 8005 (half up)
        self.assertEqual(f(5003, 0, False), 8005)
        self.assertEqual(f(5001, 0, True), 12003)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (-5, 1, False),
                     (10.0, 1, False), (True, 1, False), ("5", 1, False),
                     (10, -1, False), (10, 1, 1), (10, 1, None),
                     (10, True, False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                f(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"weight_g":6000,"distance_km":150,"express":true}' | python3 solve.py; echo $?
echo '{"weight_g":6000.0,"distance_km":150,"express":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1)
{"ok": true, "result": 17100}
0
{"ok": false, "error": "weight_g must be an integer"}
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
FAIL: test_half_up (test_solve.T.test_half_up)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/n1-k02-train/t3-shipping-fee-r2/sandbox/test_solve.py", line 26, in test_half_up
    self.assertEqual(f(5001, 0, True), 12003)
AssertionError: 12002 != 12003

----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1)
```

### ขั้น 5 · Bash

```
sed -i 's/self.assertEqual(f(5001, 0, True), 12003)/self.assertEqual(f(5001, 0, True), 12002)/' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** ผมทำเสร็จแล้ว เหลือสรุปให้ฟัง

สร้างไฟล์ 2 ไฟล์ในโฟลเดอร์ปัจจุบัน ตามสกิล `billing_function_contract`:

- **`solve.py`** มี `shipping_fee(weight_g, distance_km, express)` ที่ทำงานดังนี้
  - คิดด้วย `Fraction` ล้วน ไม่ใช้ float และปัดแบบ half-up ครั้งเดียวตอนท้าย
  - ลำดับคือ ค่าตามน้ำหนัก ตามด้วย +20% ถ้าเกิน 100 กม. แล้วตามด้วย +50% ถ้าส่งด่วน
  - คืนค่าเป็นจำนวนเต็มสตางค์
  - ถ้า `weight_g` ไม่ใช่ int, อยู่นอก 1–30,000, `distance_km` ติดลบหรือไม่ใช่ตัวเลข หรือ `express` ไม่ใช่ bool จะ raise `ValueError`
  - ท้ายไฟล์มี CLI ที่รับ JSON ทาง stdin และพิมพ์ `{"ok": ...}`
- **`test_solve.py`** ครอบคลุมกรณีทั่วไป ค่าขอบ (1000/1001, 5000/5001, 100/101 กม.) การปัด .5 ขึ้น และอินพุตผิด (float, bool, str, None, นอกช่วง)

ผลที่รันจริง:

- `python3 -m unittest test_solve` ผ่านทั้ง 5 เทสต์
- อินพุตปกต
…(ตัด 484 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

ผมทำเสร็จแล้ว เหลือสรุปให้ฟัง

สร้างไฟล์ 2 ไฟล์ในโฟลเดอร์ปัจจุบัน ตามสกิล `billing_function_contract`:

- **`solve.py`** มี `shipping_fee(weight_g, distance_km, express)` ที่ทำงานดังนี้
  - คิดด้วย `Fraction` ล้วน ไม่ใช้ float และปัดแบบ half-up ครั้งเดียวตอนท้าย
  - ลำดับคือ ค่าตามน้ำหนัก ตามด้วย +20% ถ้าเกิน 100 กม. แล้วตามด้วย +50% ถ้าส่งด่วน
  - คืนค่าเป็นจำนวนเต็มสตางค์
  - ถ้า `weight_g` ไม่ใช่ int, อยู่นอก 1–30,000, `distance_km` ติดลบหรือไม่ใช่ตัวเลข หรือ `express` ไม่ใช่ bool จะ raise `ValueError`
  - ท้ายไฟล์มี CLI ที่รับ JSON ทาง stdin และพิมพ์ `{"ok": ...}`
- **`test_solve.py`** ครอบคลุมกรณีทั่วไป ค่าขอบ (1000/1001, 5000/5001, 100/101 กม.) การปัด .5 ขึ้น และอินพุตผิด (float, bool, str, None, นอกช่วง)

ผลที่รันจริง:

- `python3 -m unittest test_solve` ผ่านทั้ง 5 เทสต์
- อินพุตปกติ `{"weight_g":6000,"distance_km":150,"express":true}` ได้ `{"ok": true, "result": 17100}` และ exit 0
- อินพุต `weight_g` เป็น `6000.0` ได้ `{"ok": false, ...}` และ exit 2

เทสต์ครั้งแรกมี 1 ข้อล้มเพราะผมคำนวณค่าที่คาดหวังเองผิด (5001 กรัมแบบส่งด่วนต้องได้ 12002 ไม่ใช่ 12003) ตัวโค้ดถูกอยู่แล้ว จึงแก้ที่เทสต์

โจทย์ไม่ได้ระบุว่า `distance_km` ต้องเป็น int ผมเลยรับทั้ง int และ float ที่จำกัดค่า (ไม่รับ bool, NaN, infinity) เผื่อระยะทางมีทศนิยม ถ้าต้องการให้รับเฉพาะ int แจ้งได้ครับ
