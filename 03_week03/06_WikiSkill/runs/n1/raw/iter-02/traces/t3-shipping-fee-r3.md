# Trace t3-shipping-fee-r3 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/*.md 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
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
- ตัวเลขทุกตัวที่ควรเป็น int
…(ตัด 2228 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
import math
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be an integer in 1..30000")
    if type(distance_km) not in (int, float) or not math.isfinite(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be a non-negative number")
    if type(express) is not bool:
        raise ValueError("express must be a boolean")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 15 * 100, 1000)
    if Fraction(distance_km) > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
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
    def test_tiers(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8150)
        self.assertEqual(f(10000, 0, False), 15500)

    def test_distance_express(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 101, True), 7200)

    def test_half_up(self):
        # 5001g: 8150*1.5 = 12225 ; 5003g: 8450 ->; check .5 case
        self.assertEqual(f(5001, 101, False), 9780)
        self.assertEqual(f(5001, 0, True), 12225)
        self.assertEqual(f(5003, 0, True), 12226)  # 8450*... 8004.5*1.5=12006.75->12007? see below

    def test_invalid(self):
        for args in [(0, 0, False), (30001, 0, False), (5.0, 0, False), (True, 0, False),
                     (10, -1, False), (10, 0, 1), (10, 0, None), (10, "1", False)]:
            with self.assertRaises(ValueError):
                f(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -c "
from solve import shipping_fee as f
print(f(5003,0,True),f(5001,0,True),f(5001,101,False),f(5001,101,True))"
```

ผลที่ได้:

```
12007 12002 9602 14403
```

### ขั้น 3 · Bash

```
python3 - <<'EOF'
s=open('test_solve.py').read()
s=s.replace("self.assertEqual(f(5001, 0, False), 8150)","self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half-up")
a=s.index("    def test_half_up"); b=s.index("    def test_invalid")
s=s[:a]+"""    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5001, 0, True), 12002)
        self.assertEqual(f(5003, 0, True), 12007)
        self.assertEqual(f(5001, 101, False), 9602)

"""+s[b:]
open('test_solve.py','w').write(s)
EOF
python3 -m unittest test_solve 2>&1|tail -3
echo '{"weight_g":6000,"distance_km":150,"express":true}'|python3 solve.py
echo '{"weight_g":6000.0,"distance_km":1,"express":true}'|python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 17100}
{"ok": false, "error": "weight_g must be an integer in 1..30000"}
2
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` unit test ผ่านครบ 4 ข้อ และรันผ่าน CLI แล้ว

- **การคำนวณ:** ใช้ `Fraction` ทั้งหมด ไม่ใช้ float และไม่ใช้ `round()` ปัดแบบ half-up ครั้งเดียวตอนท้าย แล้วคืนค่าเป็นจำนวนเต็มสตางค์
- **ลำดับการคิด:** คิดค่าส่งตามน้ำหนัก แล้วคูณ 1.2 ถ้าระยะทางเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **ตัวอย่าง:** 6,000 กรัม, 150 กม., ส่งด่วน ได้ 17,100 สตางค์ (171 บาท) ส่วน 5,001 กรัม ไม่ด่วน ใกล้ ๆ ไม่ถึง 100 กม. ได้ 8,002 สตางค์ ซึ่งมาจาก 8,001.5 ปัดขึ้น
- **อินพุตผิด:** raise `ValueError` เมื่อ `weight_g` ไม่ใช่ `int` จริงหรืออยู่นอกช่วง 1–30,000, เมื่อ `express` ไม่ใช่ `bool` หรือเมื่อ `distance_km` ติดลบ
- **CLI:** รับ JSON ทาง stdin ถ้าสำเร็จพิมพ์ `{"ok": true, ...}` ถ้าผิดพลาดพิมพ์ `{"ok":
…(ตัด 250 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` unit test ผ่านครบ 4 ข้อ และรันผ่าน CLI แล้ว

- **การคำนวณ:** ใช้ `Fraction` ทั้งหมด ไม่ใช้ float และไม่ใช้ `round()` ปัดแบบ half-up ครั้งเดียวตอนท้าย แล้วคืนค่าเป็นจำนวนเต็มสตางค์
- **ลำดับการคิด:** คิดค่าส่งตามน้ำหนัก แล้วคูณ 1.2 ถ้าระยะทางเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **ตัวอย่าง:** 6,000 กรัม, 150 กม., ส่งด่วน ได้ 17,100 สตางค์ (171 บาท) ส่วน 5,001 กรัม ไม่ด่วน ใกล้ ๆ ไม่ถึง 100 กม. ได้ 8,002 สตางค์ ซึ่งมาจาก 8,001.5 ปัดขึ้น
- **อินพุตผิด:** raise `ValueError` เมื่อ `weight_g` ไม่ใช่ `int` จริงหรืออยู่นอกช่วง 1–30,000, เมื่อ `express` ไม่ใช่ `bool` หรือเมื่อ `distance_km` ติดลบ
- **CLI:** รับ JSON ทาง stdin ถ้าสำเร็จพิมพ์ `{"ok": true, ...}` ถ้าผิดพลาดพิมพ์ `{"ok": false, ...}` แล้ว exit 2 ทดสอบแล้วว่า `weight_g` เป็น `6000.0` ได้ exit 2

`distance_km` รับทั้ง `int` และ `float` เพราะโจทย์ไม่ได้บอกว่าต้องเป็นจำนวนเต็ม แต่ปฏิเสธ `bool` และ str ถ้าตัวตรวจต้องการให้ปฏิเสธ float ด้วย ต้องแก้เงื่อนไขนี้ใน `solve.py`
