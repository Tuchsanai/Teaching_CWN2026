# Trace t4-cashback-r3 · iteration 2

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
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
billing_function_contract
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/billing_function_contract/* 2>&1 | head -100
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
MIN_AMOUNT = 10000  # 100 baht in satang
CAP = 20000         # 200 baht in satang


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
    if birthday:
        n *= 2
    num, den = amount * n, d
    result = (2 * num + den) // (2 * den)  # half-up
    return min(result, CAP)


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


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "silver", True), 600)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10050*0.025=251.25 -> 251
        self.assertEqual(cashback(10010, "silver", False), 150)
        # 10100*0.025 = 252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        # 10010*0.015=150.15 ; 10040*.025=251.0 ; 10100*.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_cap(self):
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_invalid(self):
        for args in [(-1, "gold", False), (100.0, "gold", False), (True, "gold", False),
                     ("1", "gold", False), (None, "gold", False), (10000, "bronze", False),
                     (10000, None, False), (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":-5,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 6 tests in 0.001s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "amount out of range"}
2
```

**Agent พูด:** เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว พร้อม `test_solve.py` ข้างกัน ผมอ่านสกิล `billing_function_contract` ก่อนเริ่มและทำตามนั้น

รัน `python3 -m unittest test_solve` ผ่านทั้ง 6 เทสต์ ลองรัน CLI ผ่าน stdin ด้วย: ค่าปกติได้ `{"ok": true, "result": 1000}` และ exit 0 ส่วน amount ติดลบได้ `{"ok": false, ...}` และ exit 2

**การคำนวณ**
- ใช้จำนวนเต็มล้วน ไม่ใช้ float หรือ `round()`
- ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
- อัตราเป็นเศษส่วน: silver 15/1000, gold 25/1000, platinum 4/100
- ถ้า `birthday` เป็น True คูณอัตราด้วย 2
- ปัดแบบ half-up ครั้งเดียวตอนท้าย เช่น 252.5 ได้ 253
- จำกัดเงินคืนไม่เกิน 20,000 สตางค์ (200 บาท) หลังปัดเศษ

**การตรวจอินพุต:** ถ้า amount ไม่ใช่ `int` จริง (float, str, None หรือ bool) หรือติดลบ, tier ไม่รู้จัก, หรือ birthday ไม่ใช่ `bool` 
…(ตัด 231 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว พร้อม `test_solve.py` ข้างกัน ผมอ่านสกิล `billing_function_contract` ก่อนเริ่มและทำตามนั้น

รัน `python3 -m unittest test_solve` ผ่านทั้ง 6 เทสต์ ลองรัน CLI ผ่าน stdin ด้วย: ค่าปกติได้ `{"ok": true, "result": 1000}` และ exit 0 ส่วน amount ติดลบได้ `{"ok": false, ...}` และ exit 2

**การคำนวณ**
- ใช้จำนวนเต็มล้วน ไม่ใช้ float หรือ `round()`
- ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
- อัตราเป็นเศษส่วน: silver 15/1000, gold 25/1000, platinum 4/100
- ถ้า `birthday` เป็น True คูณอัตราด้วย 2
- ปัดแบบ half-up ครั้งเดียวตอนท้าย เช่น 252.5 ได้ 253
- จำกัดเงินคืนไม่เกิน 20,000 สตางค์ (200 บาท) หลังปัดเศษ

**การตรวจอินพุต:** ถ้า amount ไม่ใช่ `int` จริง (float, str, None หรือ bool) หรือติดลบ, tier ไม่รู้จัก, หรือ birthday ไม่ใช่ `bool` จะ raise `ValueError`

**CLI:** ท้าย `solve.py` อ่าน JSON จาก stdin แล้วพิมพ์ `{ok, result|error}` ถ้าผิดพลาดจะ exit 2 และไม่มี traceback

ผมตีความว่ายอดพอดี 100 บาท (10,000 สตางค์) ได้เงินคืน เพราะโจทย์ว่า "ต่ำกว่า 100 บาท ไม่ได้"
