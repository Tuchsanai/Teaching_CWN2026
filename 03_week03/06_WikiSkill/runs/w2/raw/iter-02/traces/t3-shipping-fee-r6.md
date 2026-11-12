# Trace t3-shipping-fee-r6 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 4 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
- ✗ `tests`: unittest พบ 3 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/*.md 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
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
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์
…(ตัด 1985 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
from fractions import Fraction
import json, sys


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
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    s = fee * 100  # satang
    return (s.numerator * 2 + s.denominator) // (s.denominator * 2)


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
        self.assertEqual(f(5001, 0, False), 8002)  # 80.015 -> 8001.5 -> half up
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)
        self.assertEqual(f(1, 0, True), 6000)
        self.assertEqual(f(1, 101, True), 7200)
        self.assertEqual(f(30000, 0, False), 41500)

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (1.0, 1, False), (True, 1, False),
                  (1, -1, False), (1, 1.0, False), (1, 1, 1), ("1", 1, False), (1, None, False)]:
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
Ran 3 tests in 0.001s

FAILED (failures=1)
{"ok": true, "result": 17100}
0
{"ok": false, "error": "out of range: 0"}
2
```

### ขั้น 3 · Bash

```
python3 -m unittest test_solve 2>&1 | head -12
```

ผลที่ได้:

```
.F.
======================================================================
FAIL: test_edges (test_solve.T.test_edges)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/w2-k02-train/t3-shipping-fee-r6/sandbox/test_solve.py", line 20, in test_edges
    self.assertEqual(f(30000, 0, False), 41500)
AssertionError: 45500 != 41500

----------------------------------------------------------------------
Ran 3 tests in 0.000s
```

### ขั้น 4 · Bash

```
sed -i 's/41500/45500/' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 3 tests in 0.000s

OK
```

**Agent พูด:** เขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และเทสต์ใน `test_solve.py` ผ่านทั้ง 3 ชุด ผมทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ด้วย

- **การคิดเงิน:** ใช้เศษส่วน (`Fraction`) ตลอด แล้วปัดครั้งเดียวตอนท้ายแบบ half up เป็นสตางค์ ผลลัพธ์เป็น `int` เสมอ ลำดับคือค่าน้ำหนัก แล้วคูณ 1.2 ถ้าเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **การตรวจอินพุต:** ค่านอกช่วง ค่า float เช่น `1000.0` ค่า bool และชนิดผิดจะ raise `ValueError` น้ำหนักต้องอยู่ที่ 1–30,000 และระยะทางต้องตั้งแต่ 0 ขึ้นไป `express` ต้องเป็น bool
- **ระยะทาง:** เช็กลิสต์ให้ตรวจเป็นจำนวนเต็ม ระยะทางที่เป็นทศนิยม เช่น `12.5` จึงถูกปฏิเสธ ถ้าร้านต้องการรับทศนิยม ต้องเปลี่ยนการตรวจตรงนี้
- **CLI:** รับ JSON ทาง stdin เช่น `{"weight_g":6000,"distance_km":150,"express":true}` ได้ผล `17100` และ exit 0 ถ้าอินพุตผิดจะพิมพ์ JSON บอกข้อผิดพล
…(ตัด 338 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และเทสต์ใน `test_solve.py` ผ่านทั้ง 3 ชุด ผมทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ด้วย

- **การคิดเงิน:** ใช้เศษส่วน (`Fraction`) ตลอด แล้วปัดครั้งเดียวตอนท้ายแบบ half up เป็นสตางค์ ผลลัพธ์เป็น `int` เสมอ ลำดับคือค่าน้ำหนัก แล้วคูณ 1.2 ถ้าเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **การตรวจอินพุต:** ค่านอกช่วง ค่า float เช่น `1000.0` ค่า bool และชนิดผิดจะ raise `ValueError` น้ำหนักต้องอยู่ที่ 1–30,000 และระยะทางต้องตั้งแต่ 0 ขึ้นไป `express` ต้องเป็น bool
- **ระยะทาง:** เช็กลิสต์ให้ตรวจเป็นจำนวนเต็ม ระยะทางที่เป็นทศนิยม เช่น `12.5` จึงถูกปฏิเสธ ถ้าร้านต้องการรับทศนิยม ต้องเปลี่ยนการตรวจตรงนี้
- **CLI:** รับ JSON ทาง stdin เช่น `{"weight_g":6000,"distance_km":150,"express":true}` ได้ผล `17100` และ exit 0 ถ้าอินพุตผิดจะพิมพ์ JSON บอกข้อผิดพลาดและ exit 2
- **เทสต์:** ครอบคลุมกรณีปกติ ค่าขอบของทุกเกณฑ์ (1,000 / 5,000 กรัม และ 100 กม.) เคสปัดเศษ .5 และอินพุตที่ต้องถูกปฏิเสธ

ระหว่างเขียนเทสต์ ผมคำนวณค่าคาดหวังของน้ำหนัก 30,000 กรัมผิดเอง ค่าที่ถูกคือ 45,500 สตางค์ (80 + 25×15 = 455 บาท) ผมแก้ที่เทสต์ ไม่ได้แก้ที่โค้ด

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`
