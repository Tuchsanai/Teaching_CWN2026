# Trace t3-shipping-fee-r2 · iteration 2

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
ls ./skills 2>/dev/null && find ./skills -type f | head -50
```

ผลที่ได้:

```
cafe_solve_checklist
./skills/cafe_solve_checklist/PURPOSE.md
./skills/cafe_solve_checklist/SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/SKILL.md ./skills/cafe_solve_checklist/PURPOSE.md
```

ผลที่ได้:

```
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
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo=0, "ตั้งแต่ 1" → lo=
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
        self.assertEqual(f(10000, 200, True), 27900)

    def test_edges(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half up
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)
        self.assertEqual(f(1, 0, True), 6000)
        self.assertEqual(f(30000, 0, False), 45500)

    def test_half(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5003, 0, False), 8005)

    def test_reject(self):
        for args in [(0, 1, False), (30001, 1, False), (-1, 1, False),
                     (1, -1, False), (1000.0, 1, False), (True, 1, False),
                     ("5", 1, False), (1, 1.0, False), (1, 1, 1),
                     (1, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                f(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"weight_g":10000,"distance_km":200,"express":true}' | python3 solve.py; echo $?
echo '{"weight_g":0,"distance_km":2,"express":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 27900}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว unittest 4 ตัวผ่านทั้งหมด และ CLI ทำงานตามที่คาด ตัวอย่าง 10,000 กรัม, 200 กม., ส่งด่วน ได้ 27900 สตางค์ (exit 0) ส่วนน้ำหนัก 0 กรัมได้ error JSON และ exit 2

ผมทำตามสกิล `cafe_solve_checklist` ใน `./skills` ซึ่งเพิ่มข้อที่โจทย์ไม่ได้เขียนไว้:

- **ตรวจอินพุต:** ถ้าอินพุตผิดช่วงหรือผิดชนิด ฟังก์ชันจะ `raise ValueError`
  - `weight_g` ต้องเป็นจำนวนเต็ม 1–30,000
  - `distance_km` ต้องเป็นจำนวนเต็มตั้งแต่ 0
  - `express` ต้องเป็น bool
  - ค่า float เช่น `1000.0` และ bool ที่ส่งมาแทนตัวเลขจะถูกปฏิเสธ
- **ปัดเศษ:** คิดเป็นเศษส่วนด้วย `Fraction` ตลอด แล้วปัดแบบ half up ครั้งเดียวตอนท้าย เช่น 5,001 กรัมได้ 8001.5 สตางค์ ปัดเป็น 8002
- **ลำดับคิด:** ค่าส่งตามน้ำหนัก แล้วคูณ 1.2 ถ้าเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **CLI:** `solve.py` อ่าน JSON จาก
…(ตัด 171 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว unittest 4 ตัวผ่านทั้งหมด และ CLI ทำงานตามที่คาด ตัวอย่าง 10,000 กรัม, 200 กม., ส่งด่วน ได้ 27900 สตางค์ (exit 0) ส่วนน้ำหนัก 0 กรัมได้ error JSON และ exit 2

ผมทำตามสกิล `cafe_solve_checklist` ใน `./skills` ซึ่งเพิ่มข้อที่โจทย์ไม่ได้เขียนไว้:

- **ตรวจอินพุต:** ถ้าอินพุตผิดช่วงหรือผิดชนิด ฟังก์ชันจะ `raise ValueError`
  - `weight_g` ต้องเป็นจำนวนเต็ม 1–30,000
  - `distance_km` ต้องเป็นจำนวนเต็มตั้งแต่ 0
  - `express` ต้องเป็น bool
  - ค่า float เช่น `1000.0` และ bool ที่ส่งมาแทนตัวเลขจะถูกปฏิเสธ
- **ปัดเศษ:** คิดเป็นเศษส่วนด้วย `Fraction` ตลอด แล้วปัดแบบ half up ครั้งเดียวตอนท้าย เช่น 5,001 กรัมได้ 8001.5 สตางค์ ปัดเป็น 8002
- **ลำดับคิด:** ค่าส่งตามน้ำหนัก แล้วคูณ 1.2 ถ้าเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **CLI:** `solve.py` อ่าน JSON จาก stdin ได้ ถ้าผิดพลาดจะพิมพ์ error JSON และ exit 2

เพราะสกิลกำหนดให้ตรวจเป็นจำนวนเต็ม ระยะทางที่เป็นทศนิยม เช่น `100.5` จึงถูกปฏิเสธ ถ้าต้องการรับระยะทางทศนิยม บอกได้ครับ
