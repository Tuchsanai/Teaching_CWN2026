# Trace t3-shipping-fee-r1 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
billing_function_contract
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

## 2. ตรวจอินพุตก่อนคำนวณ แล้ว raise ValueError เท่านั้น
- ตัวเลขทุกตัวที่ควรเป็น int ต้องเป็น `int` จร
…(ตัด 2210 ตัวอักษร)
```

### ขั้น 2 · Bash

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

    # satang
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if Fraction(distance_km) > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


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
    def test_base(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 satang -> half-up
        self.assertEqual(f(10000, 0, False), 15500)
        self.assertEqual(f(30000, 0, False), 45500)

    def test_distance_express(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 150, True), 7200)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5003, 0, False), 8005)  # 8004.5

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (1.0, 0, False), (True, 0, False),
                  (100, -1, False), (100, None, False), (100, "5", False),
                  (100, 0, 1), (100, 0, None), (100, float("nan"), False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"weight_g":6000,"distance_km":120,"express":true}' | python3 solve.py; echo $?
echo '{"weight_g":0,"distance_km":1,"express":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 17100}
0
{"ok": false, "error": "weight_g out of range"}
2
```

**Agent พูด:** เขียน `shipping_fee` ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกัน ตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` ผลทดสอบคือ unittest ผ่านครบ 4 เคส และรัน CLI จริงได้ผลตามที่ควร

- **หน่วยและการปัดเศษ:** ค่าที่คืนเป็นจำนวนเต็มสตางค์ คำนวณด้วย `Fraction` แล้วปัดแบบ half-up ครั้งเดียวตอนท้าย ไม่ใช้ float หรือ `round()`
- **ขั้นน้ำหนัก:**
  - ไม่เกิน 1,000 กรัม = 4,000 สตางค์
  - ไม่เกิน 5,000 กรัม = 8,000 สตางค์
  - ส่วนที่เกิน 5,000 กรัม คิดกรัมละ 1.5 สตางค์
- **ตัวคูณ:** ระยะทางเกิน 100 กม. คูณ 1.2 แล้วส่งด่วนคูณ 1.5 ต่อจากนั้น ระยะทางพอดี 100 กม. ไม่ถูกบวกเพิ่ม
- **ตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError`
  - `weight_g` ต้องเป็น `int` ในช่วง 1–30,000
  - `express` ต้องเป็น `bool`
  - `distance_km` เป็น `int` หรือ `float` ที่ไม่ติดลบและไม่ใช่ nan/inf
- **CLI:** รัน `py
…(ตัด 438 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `shipping_fee` ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกัน ตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` ผลทดสอบคือ unittest ผ่านครบ 4 เคส และรัน CLI จริงได้ผลตามที่ควร

- **หน่วยและการปัดเศษ:** ค่าที่คืนเป็นจำนวนเต็มสตางค์ คำนวณด้วย `Fraction` แล้วปัดแบบ half-up ครั้งเดียวตอนท้าย ไม่ใช้ float หรือ `round()`
- **ขั้นน้ำหนัก:**
  - ไม่เกิน 1,000 กรัม = 4,000 สตางค์
  - ไม่เกิน 5,000 กรัม = 8,000 สตางค์
  - ส่วนที่เกิน 5,000 กรัม คิดกรัมละ 1.5 สตางค์
- **ตัวคูณ:** ระยะทางเกิน 100 กม. คูณ 1.2 แล้วส่งด่วนคูณ 1.5 ต่อจากนั้น ระยะทางพอดี 100 กม. ไม่ถูกบวกเพิ่ม
- **ตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError`
  - `weight_g` ต้องเป็น `int` ในช่วง 1–30,000
  - `express` ต้องเป็น `bool`
  - `distance_km` เป็น `int` หรือ `float` ที่ไม่ติดลบและไม่ใช่ nan/inf
- **CLI:** รัน `python3 solve.py` โดยส่ง JSON ทาง stdin ได้ ถ้าสำเร็จจะพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าผิดพลาดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2
- **ตัวอย่างที่รันจริง:** น้ำหนัก 6,000 กรัม ระยะ 120 กม. ส่งด่วน ได้ 17,100 สตางค์ ส่วนน้ำหนัก 0 กรัมได้ ok false และ exit 2

โจทย์ไม่ได้ระบุว่า `distance_km` ต้องเป็นจำนวนเต็มหรือไม่ ผมจึงรับทศนิยมได้ ถ้าต้องการให้รับเฉพาะ `int` ตามสกิล บอกได้ แก้แค่เงื่อนไขตรวจชนิดบรรทัดเดียว
