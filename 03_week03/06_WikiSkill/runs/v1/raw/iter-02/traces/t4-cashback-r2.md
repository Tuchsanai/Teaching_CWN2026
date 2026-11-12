# Trace t4-cashback-r2 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1; ls
```

ผลที่ได้:

```
cafe_function_checklist
skills
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/*/* 2>/dev/null | head -100
```

ผลที่ได้:

```
./skills/cafe_function_checklist/PURPOSE.md
./skills/cafe_function_checklist/SKILL.md
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
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไ
…(ตัด 3064 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys

_RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000
_MIN_AMOUNT = 10000   # 100 baht in satang
_CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    n = amount * _RATES[tier] * (2 if birthday else 1)
    d = 1000
    return min((2 * n + d) // (2 * d), _CAP)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(**data)
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
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10040, "silver", False), 151)  # 150.6
        self.assertEqual(cashback(10100, "gold", False), 253)    # 252.5

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_invalid(self):
        for a in (-1, 1000.0, True, "5", None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", "", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, t, False)
        for b in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(-5, "bad", 1)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"amount":100000,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
echo '{"amount":1000.0,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 5000}
exit=0
{"ok": false, "error": "amount must be int >= 0"}
exit=2
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` เสร็จแล้ว ทำตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` ด้วย รัน unittest ผ่านทั้ง 5 เทสต์ และรัน CLI ทดสอบแล้วทั้งกรณีปกติและกรณีผิด

**วิธีคิดเงินคืนใน `cashback(amount, tier, birthday)`**
- **ยอดขั้นต่ำ:** ถ้ายอดซื้อต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
- **อัตรา:** คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float โดย silver คิดเป็น 15/1000, gold 25/1000, platinum 40/1000
- **เดือนเกิด:** คูณ 2 ก่อนปัด
- **การปัด:** ปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`
- **เพดาน:** สูงสุด 20,000 สตางค์ (200 บาท) ต่อบิล
- **ตรวจ input:** ถ้า input ผิดจะ raise `ValueError` ได้แก่
  - `amount` ไม่ใช่ `int` (รวม float และ bool) หรือติดลบ
  - `tier` ไม่อยู่ใน silver, gold, platinum
  - `birthday` ไม่ใช่ `bool`

**CLI:** `python solve.py` รับ JSON ทาง stdin
- ส
…(ตัด 302 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` เสร็จแล้ว ทำตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` ด้วย รัน unittest ผ่านทั้ง 5 เทสต์ และรัน CLI ทดสอบแล้วทั้งกรณีปกติและกรณีผิด

**วิธีคิดเงินคืนใน `cashback(amount, tier, birthday)`**
- **ยอดขั้นต่ำ:** ถ้ายอดซื้อต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
- **อัตรา:** คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float โดย silver คิดเป็น 15/1000, gold 25/1000, platinum 40/1000
- **เดือนเกิด:** คูณ 2 ก่อนปัด
- **การปัด:** ปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`
- **เพดาน:** สูงสุด 20,000 สตางค์ (200 บาท) ต่อบิล
- **ตรวจ input:** ถ้า input ผิดจะ raise `ValueError` ได้แก่
  - `amount` ไม่ใช่ `int` (รวม float และ bool) หรือติดลบ
  - `tier` ไม่อยู่ใน silver, gold, platinum
  - `birthday` ไม่ใช่ `bool`

**CLI:** `python solve.py` รับ JSON ทาง stdin
- สำเร็จ: ได้ `{"ok": true, "result": ...}` และ exit 0 เช่น gold, 100000 สตางค์, เดือนเกิด ได้ 5000
- input ผิด: ได้ `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback

**เทสต์:** `test_solve.py` ครอบคลุมกรณีปกติ ขอบ 9,999 กับ 10,000 สตางค์ เศษ .5 ที่ปัดขึ้น เพดาน 200 บาท และ input ที่ไม่ถูกต้อง
