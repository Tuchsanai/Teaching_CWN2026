# Trace t3-shipping-fee-r5 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1; ls
```

ผลที่ได้:

```
cafe_solve_checklist
skills
```

### ขั้น 2 · Bash

```
find skills -type f | head; cat skills/*/* 2>/dev/null | head -100
```

ผลที่ได้:

```
skills/cafe_solve_checklist/PURPOSE.md
skills/cafe_solve_checklist/SKILL.md
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
…(ตัด 2655 ตัวอักษร)
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
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return (fee.numerator * 2 + fee.denominator) // (fee.denominator * 2)


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
        self.assertEqual(f(500, 200, True), 7200)

    def test_edges(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 100, False), 8000)
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half up
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(30000, 0, False), 45500)

    def test_half(self):
        self.assertEqual(f(5001, 0, True), 12002)  # 12002.25
        self.assertEqual(f(5003, 0, False), 8005)  # 8004.5

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (1000.0, 1, False),
                  (True, 1, False), ("5", 1, False), (100, -1, False),
                  (100, 1.0, False), (100, 1, 1), (100, 1, None)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"weight_g":6000,"distance_km":150,"express":true}' | python3 solve.py; echo $?
echo '{"weight_g":0,"distance_km":1,"express":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 17100}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `shipping_fee(weight_g, distance_km, express)` ใน `solve.py` เสร็จแล้ว และทดสอบผ่านทั้งหมด ผมทำตามสกิล `cafe_solve_checklist` ใน `./skills` ด้วย

- **การคิดเงิน:** คิดเป็นสตางค์ด้วยเศษส่วนจำนวนเต็ม ไม่ใช้ float และปัดแบบ half up ครั้งเดียวตอนท้าย ลำดับคือค่าน้ำหนัก แล้วคูณ 1.2 ถ้าระยะทางเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **ตรวจอินพุต:** ค่าที่ผิดจะ `raise ValueError` ได้แก่ น้ำหนักนอกช่วง 1–30,000, ระยะทางติดลบ, ค่า float, bool และชนิดข้อมูลผิด
- **ระยะทาง:** สกิลให้ตรวจเป็นจำนวนเต็ม ผมจึงรับ `distance_km` เป็น int เท่านั้น ถ้าต้องการให้รับทศนิยมได้ บอกผมได้ครับ
- **CLI:** `solve.py` รับ JSON ทาง stdin แล้วพิมพ์ผลเป็น JSON ถ้าอินพุตผิดจะ exit 2
- **การทดสอบ:** `test_solve.py` ครอบคลุมกรณีปกติ ค่าขอบของแต่ละเกณฑ์ เคสปัดเศษที่ลงที่ .5 พอดี และอินพุตที่ต้องถูกปฏิเสธ รัน unittest ผ่าน
…(ตัด 211 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `shipping_fee(weight_g, distance_km, express)` ใน `solve.py` เสร็จแล้ว และทดสอบผ่านทั้งหมด ผมทำตามสกิล `cafe_solve_checklist` ใน `./skills` ด้วย

- **การคิดเงิน:** คิดเป็นสตางค์ด้วยเศษส่วนจำนวนเต็ม ไม่ใช้ float และปัดแบบ half up ครั้งเดียวตอนท้าย ลำดับคือค่าน้ำหนัก แล้วคูณ 1.2 ถ้าระยะทางเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **ตรวจอินพุต:** ค่าที่ผิดจะ `raise ValueError` ได้แก่ น้ำหนักนอกช่วง 1–30,000, ระยะทางติดลบ, ค่า float, bool และชนิดข้อมูลผิด
- **ระยะทาง:** สกิลให้ตรวจเป็นจำนวนเต็ม ผมจึงรับ `distance_km` เป็น int เท่านั้น ถ้าต้องการให้รับทศนิยมได้ บอกผมได้ครับ
- **CLI:** `solve.py` รับ JSON ทาง stdin แล้วพิมพ์ผลเป็น JSON ถ้าอินพุตผิดจะ exit 2
- **การทดสอบ:** `test_solve.py` ครอบคลุมกรณีปกติ ค่าขอบของแต่ละเกณฑ์ เคสปัดเศษที่ลงที่ .5 พอดี และอินพุตที่ต้องถูกปฏิเสธ รัน unittest ผ่านทั้ง 4 ชุด
- **ตัวอย่างที่รันจริง:** `{"weight_g":6000,"distance_km":150,"express":true}` ได้ 17100 สตางค์ และ `weight_g` เป็น 0 ได้ error พร้อม exit 2

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`
