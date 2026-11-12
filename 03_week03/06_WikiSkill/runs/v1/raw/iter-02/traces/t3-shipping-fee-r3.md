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
- ✗ `tests`: unittest พบ 3 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
cafe_function_checklist
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบทั้ง 4 ข้อด้านล่างทุกครั้ง แม้โจทย์ไม่สั่ง

## When NOT to Apply
- งานที่ไม่ใช่ฟังก์ชันคำนวณใน `solve.py` (เช่น แก้เอกสาร จัดรูปแบบข้อความ)
- ถ้าโจทย์ระบุวิธีปัด/รูปแบบ CLI/การ reject ไว้ชัดเจนและต่างจากนี้ ให้ทำตามโจทย์

## Instructions

### 1. ตรวจ input ที่ต้นฟังก์ชัน (ก่อนคำนวณ และก่อน early-return ทุกชนิด)
ตัวตรวจคาดว่าค่าผิดต้อง `raise ValueError` เสมอ ไม่ใช่คืนค่า 0 และไม่ใช่ `ZeroDivisionError`/`TypeError`/`KeyError`
- ตัวเลขทุกตัว: `type(x) is int` (ปฏิเสธ float เช่น `1000.0` และ `bool`)
- flag (member/express/birthday ฯลฯ): `type(x) is bool`
- ช่วงค่า: ตรวจทุกขอบเขตที่โจทย์ระบุ เช่น "ตั้งแต่ 0" -> `x >= 0`, "ตั้งแต่ 1" -> `x >= 1`, "1–30,000" -> `1 <= x <= 30000`, "0–100" -> `0 <= x <= 100`
- enum 
…(ตัด 2320 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def shipping_fee(weight_g, distance_km, express):
    _int("weight_g", weight_g, 1, 30000)
    _int("distance_km", distance_km, 0)
    if type(express) is not bool:
        raise ValueError("express must be bool")

    # fee in satang as fraction n/d
    if weight_g <= 1000:
        n, d = 4000, 1
    elif weight_g <= 5000:
        n, d = 8000, 1
    else:
        n, d = (80000 + 15 * (weight_g - 5000)) * 100, 1000
    if distance_km > 100:
        n, d = n * 6, d * 5
    if express:
        n, d = n * 3, d * 2
    return (2 * n + d) // (2 * d)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import shipping_fee


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 satang -> 2
        self.assertEqual(shipping_fee(30000, 0, False), 41000)

    def test_modifiers(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (-1, 0, False), (100, -1, False),
                  (100.0, 0, False), (100, 1.0, False), (True, 0, False),
                  (100, 0, 1), (100, 0, None), ("5", 0, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"weight_g":6000,"distance_km":150,"express":true}' | python3 solve.py; echo "exit=$?"
echo '{"weight_g":0,"distance_km":1,"express":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
ERROR Exit code 1
{"ok": true, "result": 17100}
exit=0
{"ok": false, "error": "weight_g out of range"}
exit=2
======================================================================
FAIL: test_tiers (test_solve.T.test_tiers)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/v1-k02-train/t3-shipping-fee-r3/sandbox/test_solve.py", line 12, in test_tiers
    self.assertEqual(shipping_fee(30000, 0, False), 41000)
AssertionError: 45500 != 41000

----------------------------------------------------------------------
Ran 3 tests in 0.000s

FAILED (failures=1)
```

### ขั้น 3 · Bash

```
sed -i 's/, 41000)/, 45500)/' test_solve.py && python3 -m unittest -q
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

**Agent พูด:** เขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และ `test_solve.py` ผ่านทั้งหมด (3 เทสต์) ฟังก์ชันคืนค่าส่งเป็นจำนวนเต็มสตางค์

ผมอ่านสกิล `cafe_function_checklist` ก่อนเริ่มและทำตามนั้น ซึ่งมีส่วนที่โจทย์ไม่ได้สั่ง:
- **ตรวจ input:** ถ้าค่าผิดจะ `raise ValueError` ได้แก่ น้ำหนักนอก 1–30,000, ระยะทางติดลบ, ค่าที่เป็น float หรือ bool แทนตัวเลข, และ `express` ที่ไม่ใช่ bool
- **ปัดเศษ:** คำนวณด้วยเศษส่วนจำนวนเต็มแล้วปัดครั้งเดียวตอนท้ายแบบ half-up เช่น 5,001 กรัมได้ 8,002 สตางค์ (จริง 8,001.5)
- **CLI:** `python solve.py` อ่าน JSON จาก stdin ถ้าสำเร็จพิมพ์ `{"ok": true, "result": ...}` แล้ว exit 0 ถ้า input ผิดพิมพ์ `{"ok": false, ...}` แล้ว exit 2 โดยไม่มี traceback

ผมรันตัวอย่างจริงแล้ว: น้ำหนัก 6,000 กรัม ระยะ 150 กม. ส่งด่วน ได้ 17,100 สตางค์ (ok, exit 0) ส่วนน้ำหนัก 0 ได้ `{"ok": false, "
…(ตัด 333 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และ `test_solve.py` ผ่านทั้งหมด (3 เทสต์) ฟังก์ชันคืนค่าส่งเป็นจำนวนเต็มสตางค์

ผมอ่านสกิล `cafe_function_checklist` ก่อนเริ่มและทำตามนั้น ซึ่งมีส่วนที่โจทย์ไม่ได้สั่ง:
- **ตรวจ input:** ถ้าค่าผิดจะ `raise ValueError` ได้แก่ น้ำหนักนอก 1–30,000, ระยะทางติดลบ, ค่าที่เป็น float หรือ bool แทนตัวเลข, และ `express` ที่ไม่ใช่ bool
- **ปัดเศษ:** คำนวณด้วยเศษส่วนจำนวนเต็มแล้วปัดครั้งเดียวตอนท้ายแบบ half-up เช่น 5,001 กรัมได้ 8,002 สตางค์ (จริง 8,001.5)
- **CLI:** `python solve.py` อ่าน JSON จาก stdin ถ้าสำเร็จพิมพ์ `{"ok": true, "result": ...}` แล้ว exit 0 ถ้า input ผิดพิมพ์ `{"ok": false, ...}` แล้ว exit 2 โดยไม่มี traceback

ผมรันตัวอย่างจริงแล้ว: น้ำหนัก 6,000 กรัม ระยะ 150 กม. ส่งด่วน ได้ 17,100 สตางค์ (ok, exit 0) ส่วนน้ำหนัก 0 ได้ `{"ok": false, "error": "weight_g out of range"}` (exit 2)

ตอนรันครั้งแรกมีเทสต์ล้มหนึ่งข้อ เพราะผมคาดค่าผิดเอง น้ำหนัก 30,000 กรัมต้องเป็น 80 + 25×15 = 455 บาท = 45,500 สตางค์ ไม่ใช่ 41,000 `solve.py` ถูกอยู่แล้ว จึงแก้ค่าที่คาดไว้ใน test

ผมตีความว่า `distance_km` ต้องเป็นจำนวนเต็มตามสกิล ถ้าส่ง float เช่น `150.5` จะถูก reject ด้วย `ValueError`
