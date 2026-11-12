# Trace t4-cashback-r2 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 5 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
billing_function_contract
skills
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/*/* 2>/dev/null
```

ผลที่ได้:

```
./skills/billing_function_contract/PURPOSE.md
./skills/billing_function_contract/SKILL.md
# PURPOSE

## Origin
สร้างจาก Trace iteration 1 (t1–t4 ทุก rollout) ที่ไม่มีสกิล Agent เขียนฟังก์ชันถูกตรงตามโจทย์ แต่ตัวตรวจต้องการสิ่งที่โจทย์ไม่ได้บอก

## Problems Addressed
- `reject_value` / `reject_type`: ไม่ตรวจอินพุต ปล่อย float, bool, ค่านอกช่วงผ่าน หรือเกิด ZeroDivisionError แทน ValueError
- `cli_ok` / `cli_error`: ไม่มี `__main__` ที่อ่าน stdin JSON และพิมพ์ `{ok,result|error}` พร้อม exit 2
- `tests`: ไม่มี test_solve.py
- `half_up` / `no_drift`: บาง rollout ปัดลงด้วย `//` ทำให้ 250.5 เป็น 250

## Evolution History
- v1: สร้างครั้งแรก
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

ต้องทำครบทั้ง 4 ข้อ ทั้งที่โจ
…(ตัด 2826 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (4, 100)}
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount must be an integer")
    if amount < 0:
        raise ValueError("amount out of range")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a boolean")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("unknown tier")
    if amount < MIN_AMOUNT:
        return 0
    n, d = RATES[tier]
    num = amount * n * (2 if birthday else 1)
    # half-up ครั้งเดียว
    result = (2 * num + d) // (2 * d)
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class TestCashback(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10033*.025=250.825 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)  # 250.5
        self.assertEqual(cashback(10010, "gold", False), 250)  # 250.25
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10050, "silver", False), 151)  # 150.75

    def test_invalid(self):
        for args in [(100.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     ("1", "gold", False), (None, "gold", False),
                     (10000, "bronze", False), (10000, None, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":1.5,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo 'xx' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
{"ok": true, "result": 1000}
0
{"ok": false, "error": "amount must be an integer"}
2
{"ok": false, "error": "Expecting value: line 1 column 1 (char 0)"}
2
```

### ขั้น 4 · Bash

```
python3 -m unittest test_solve 2>&1 | head -15
```

ผลที่ได้:

```
..F...
======================================================================
FAIL: test_cap (test_solve.TestCashback.test_cap)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/n1-k02-train/t4-cashback-r2/sandbox/test_solve.py", line 22, in test_cap
    self.assertEqual(cashback(499999, "platinum", False), 19999)
AssertionError: 20000 != 19999

----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
```

### ขั้น 5 · Bash

```
sed -i 's/cashback(499999, "platinum", False), 19999/cashback(499987, "platinum", False), 19999/' test_solve.py; python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** ผมเขียน `cashback(amount, tier, birthday)` ไว้ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกัน เทสต์ผ่านทั้ง 6 ชุด ตอนแรกมีเทสต์ที่ล้มหนึ่งข้อ เพราะผมคำนวณค่าที่คาดไว้ผิดเอง ไม่ใช่โค้ดผิด ผมแก้ค่าในเทสต์แล้ว

ผมอ่านสกิล `billing_function_contract` ใน `./skills` แล้วทำตามนั้น ซึ่งรวมถึงส่วนที่โจทย์ไม่ได้ระบุ คือการตรวจอินพุตและ CLI

- **การคำนวณ:** ใช้จำนวนเต็มล้วน ไม่ใช้ float และปัดแบบ half-up ครั้งเดียวตอนท้าย
  - อัตราคือ silver 15/1000, gold 25/1000 และ platinum 4/100
  - ยอดต่ำกว่า 10000 สตางค์ (100 บาท) ได้ 0
  - เดือนเกิดคูณ 2 ก่อนปัด
  - เพดานคือ 20000 สตางค์ (200 บาท)
- **การตรวจอินพุต:** ถ้า `amount` ไม่ใช่ `int` จริง (float, bool, str, None) หรือติดลบ จะ raise `ValueError` เช่นเดียวกับ `birthday` ที่ไม่ใช่ `bool` และ `tier` ที่ไม่รู้จัก
- **CLI:** อ่าน JSON จาก stdin แล้วพิมพ์ 
…(ตัด 313 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

ผมเขียน `cashback(amount, tier, birthday)` ไว้ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกัน เทสต์ผ่านทั้ง 6 ชุด ตอนแรกมีเทสต์ที่ล้มหนึ่งข้อ เพราะผมคำนวณค่าที่คาดไว้ผิดเอง ไม่ใช่โค้ดผิด ผมแก้ค่าในเทสต์แล้ว

ผมอ่านสกิล `billing_function_contract` ใน `./skills` แล้วทำตามนั้น ซึ่งรวมถึงส่วนที่โจทย์ไม่ได้ระบุ คือการตรวจอินพุตและ CLI

- **การคำนวณ:** ใช้จำนวนเต็มล้วน ไม่ใช้ float และปัดแบบ half-up ครั้งเดียวตอนท้าย
  - อัตราคือ silver 15/1000, gold 25/1000 และ platinum 4/100
  - ยอดต่ำกว่า 10000 สตางค์ (100 บาท) ได้ 0
  - เดือนเกิดคูณ 2 ก่อนปัด
  - เพดานคือ 20000 สตางค์ (200 บาท)
- **การตรวจอินพุต:** ถ้า `amount` ไม่ใช่ `int` จริง (float, bool, str, None) หรือติดลบ จะ raise `ValueError` เช่นเดียวกับ `birthday` ที่ไม่ใช่ `bool` และ `tier` ที่ไม่รู้จัก
- **CLI:** อ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าอินพุตผิดหรือ JSON พัง จะพิมพ์ `{"ok": false, "error": ...}` และ exit 2

ผมลองรัน CLI สามกรณี:
- อินพุตปกติ (20000, gold, `birthday` เป็น true) ได้ `ok: true`, result 1000 และ exit 0
- `amount` เป็น float ได้ `ok: false` และ exit 2
- JSON พัง ได้ `ok: false` และ exit 2
