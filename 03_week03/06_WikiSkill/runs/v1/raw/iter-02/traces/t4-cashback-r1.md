# Trace t4-cashback-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
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
- ✓ `tests`

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
_RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}
_MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
_CAP = 20000          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if amount < _MIN_AMOUNT:
        return 0
    num, den = _RATES[tier]
    n = amount * num * (2 if birthday else 1)
    result = (2 * n + den) // (2 * den)  # half-up ครั้งเดียว
    return min(result, _CAP)


import json, sys


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

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10050*0.015=150.75 -> 151
        self.assertEqual(cashback(10010, "silver", False), 150)
        self.assertEqual(cashback(10050, "silver", False), 151)
        # 10020*0.025 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"amount":100000,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
echo '{"amount":-5,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 5000}
exit=0
{"ok": false, "error": "amount must be int >= 0"}
exit=2
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และรันตรวจจริงผ่านหมด

- **ทดสอบ:** `python3 -m unittest -q` ผ่านทั้ง 6 เทสต์ ส่ง JSON กรณีปกติผ่าน CLI ได้ `{"ok": true, "result": 5000}` exit 0 ส่งกรณีผิดได้ `{"ok": false, ...}` exit 2 ไม่มี traceback
- **ปัดเศษ:** คำนวณด้วยจำนวนเต็มล้วน แล้วปัดครั้งเดียวแบบ half-up เช่น ยอด 10,020 สตางค์ gold ได้เศษ 250.5 ปัดเป็น 251
- **ลำดับคิด:** ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0 ส่วนยอดที่ถึงเกณฑ์ใช้อัตราตาม tier คูณ 2 ถ้าเป็นเดือนเกิด แล้วจำกัดไม่เกิน 20,000 สตางค์ (200 บาท)
- **ตรวจ input:** ค่าที่ผิดจะ raise `ValueError` ได้แก่ amount ติดลบหรือไม่ใช่ int (รวม float และ bool) tier ที่ไม่อยู่ในสามระดับ และ birthday ที่ไม่ใช่ bool

ทำตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` จึงเพิ่มสองอย่างที่โจทย์ไม่ได้สั่ง คือ C
…(ตัด 65 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และรันตรวจจริงผ่านหมด

- **ทดสอบ:** `python3 -m unittest -q` ผ่านทั้ง 6 เทสต์ ส่ง JSON กรณีปกติผ่าน CLI ได้ `{"ok": true, "result": 5000}` exit 0 ส่งกรณีผิดได้ `{"ok": false, ...}` exit 2 ไม่มี traceback
- **ปัดเศษ:** คำนวณด้วยจำนวนเต็มล้วน แล้วปัดครั้งเดียวแบบ half-up เช่น ยอด 10,020 สตางค์ gold ได้เศษ 250.5 ปัดเป็น 251
- **ลำดับคิด:** ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0 ส่วนยอดที่ถึงเกณฑ์ใช้อัตราตาม tier คูณ 2 ถ้าเป็นเดือนเกิด แล้วจำกัดไม่เกิน 20,000 สตางค์ (200 บาท)
- **ตรวจ input:** ค่าที่ผิดจะ raise `ValueError` ได้แก่ amount ติดลบหรือไม่ใช่ int (รวม float และ bool) tier ที่ไม่อยู่ในสามระดับ และ birthday ที่ไม่ใช่ bool

ทำตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` จึงเพิ่มสองอย่างที่โจทย์ไม่ได้สั่ง คือ CLI อ่าน JSON จาก stdin ต่อท้าย `solve.py` และไฟล์ `test_solve.py`
