# Trace t3-shipping-fee-r1 · iteration 2

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
ls ./skills 2>&1 | head; ls
```

ผลที่ได้:

```
cafe_function_checklist
skills
```

### ขั้น 2 · Bash

```
find skills -type f | head; cat skills/*/* 2>/dev/null | head -100
```

ผลที่ได้:

```
skills/cafe_function_checklist/PURPOSE.md
skills/cafe_function_checklist/SKILL.md
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได
…(ตัด 3060 ตัวอักษร)
```

### ขั้น 3 · Bash

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

    # ค่าฐานเป็นสตางค์ x1000 (ตัวส่วน 1000)
    if weight_g <= 1000:
        n = 4000 * 1000
    elif weight_g <= 5000:
        n = 8000 * 1000
    else:
        n = 8000 * 1000 + (weight_g - 5000) * 1500  # 15 บาท/กก. = 1.5 สตางค์/กรัม
    d = 1000
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
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)

    def test_fraction_and_half_up(self):
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 8001.5 -> 8002
        self.assertEqual(shipping_fee(5003, 0, False), 8005)  # 8004.5 -> 8005

    def test_distance_express(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (-1, 0, False), (100, -1, False),
                  (100.0, 0, False), (100, 1.5, False), (True, 0, False),
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
{"ok": true, "result": 17100}
exit=0
{"ok": false, "error": "weight_g out of range"}
exit=2
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

**Agent พูด:** เขียน `shipping_fee(weight_g, distance_km, express)` เสร็จแล้วใน `solve.py` ตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` รัน 3 คำสั่งตรวจตามสกิลแล้วผ่านทั้งหมด

- **ผลที่ตรวจ:** กรณี 6,000 กรัม, 150 กม., ส่งด่วน ได้ 17,100 สตางค์ (exit 0) ส่วนกรณีผิด (น้ำหนัก 0) ได้ `{"ok": false}` (exit 2) และ `python3 -m unittest -q` ผ่าน 4 เทสต์
- **การคำนวณ:** ใช้จำนวนเต็มล้วน คูณ +20% และ +50% ต่อกันแล้วปัดแบบ half-up ครั้งเดียวตอนท้าย เช่น 5,001 กรัม ได้ 8,002 สตางค์
- **การตรวจ input:** ค่าผิดจะ `raise ValueError` คือ น้ำหนักนอก 1–30,000, ระยะทางติดลบ, float, bool ที่ส่งมาแทนตัวเลข, หรือ `express` ที่ไม่ใช่ bool
- **เพิ่มตามสกิล:** ต่อท้าย `solve.py` ด้วย CLI ที่อ่าน JSON จาก stdin และสร้าง `test_solve.py` ไว้ข้างกัน

ระยะทางต้องเป็นจำนวนเต็มกิโลเมตร ถ้าส่งทศนิยมเช่น 100.5 จะถูกปฏิเสธ เพรา
…(ตัด 167 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `shipping_fee(weight_g, distance_km, express)` เสร็จแล้วใน `solve.py` ตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` รัน 3 คำสั่งตรวจตามสกิลแล้วผ่านทั้งหมด

- **ผลที่ตรวจ:** กรณี 6,000 กรัม, 150 กม., ส่งด่วน ได้ 17,100 สตางค์ (exit 0) ส่วนกรณีผิด (น้ำหนัก 0) ได้ `{"ok": false}` (exit 2) และ `python3 -m unittest -q` ผ่าน 4 เทสต์
- **การคำนวณ:** ใช้จำนวนเต็มล้วน คูณ +20% และ +50% ต่อกันแล้วปัดแบบ half-up ครั้งเดียวตอนท้าย เช่น 5,001 กรัม ได้ 8,002 สตางค์
- **การตรวจ input:** ค่าผิดจะ `raise ValueError` คือ น้ำหนักนอก 1–30,000, ระยะทางติดลบ, float, bool ที่ส่งมาแทนตัวเลข, หรือ `express` ที่ไม่ใช่ bool
- **เพิ่มตามสกิล:** ต่อท้าย `solve.py` ด้วย CLI ที่อ่าน JSON จาก stdin และสร้าง `test_solve.py` ไว้ข้างกัน

ระยะทางต้องเป็นจำนวนเต็มกิโลเมตร ถ้าส่งทศนิยมเช่น 100.5 จะถูกปฏิเสธ เพราะสกิลกำหนดให้ปฏิเสธ float โจทย์ไม่ได้ระบุเรื่องนี้ ถ้าต้องการรับทศนิยม ต้องแก้การตรวจ `distance_km`

ไฟล์ที่สร้างอยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`
