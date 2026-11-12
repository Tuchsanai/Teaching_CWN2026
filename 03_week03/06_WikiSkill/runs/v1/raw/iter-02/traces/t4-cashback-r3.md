# Trace t4-cashback-r3 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
import json
import sys

# อัตราเป็นเศษส่วน (n, d)
_RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}
_MIN_AMOUNT = 10000  # 100 บาท (สตางค์)
_CAP = 20000         # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")

    if amount < _MIN_AMOUNT:
        return 0
    n, d = _RATES[tier]
    n *= amount * (2 if birthday else 1)
    result = (2 * n + d) // (2 * d)  # half-up ครั้งเดียว
    return min(result, _CAP)


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
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "gold", False), 0)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_half_up(self):
        # 10100*3/200 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, "gold", None),
                     ("100", "gold", False), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
echo '{"amount":-5,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 1000}
exit=0
{"ok": false, "error": "amount must be int >= 0"}
exit=2
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และรันตรวจแล้ว: กรณีปกติได้ exit 0, กรณี input ผิดได้ exit 2 ไม่มี traceback, unit test ผ่านทั้ง 6 ชุด

ผมอ่านสกิล `cafe_function_checklist` ก่อนเริ่ม และทำตามนั้น คือ ตรวจ input, ปัดแบบ half-up, ใส่ CLI และเขียน `test_solve.py`

**การคำนวณ**
- ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) ได้ 0
- อัตราเป็นเศษส่วนจำนวนเต็ม: silver 3/200, gold 1/40, platinum 1/25 ถ้าเป็นเดือนเกิดคูณ 2
- ปัดแบบ half-up ครั้งเดียวด้วยจำนวนเต็ม แล้วจำกัดไม่เกิน 20,000 สตางค์ (200 บาท)

**ตรวจ input**
- ค่าผิดจะ `raise ValueError`: `amount` ไม่ใช่ int (รวม float และ bool) หรือติดลบ, `tier` ไม่อยู่ในสามระดับ, `birthday` ไม่ใช่ bool

**CLI**
- `python solve.py` อ่าน JSON จาก stdin
- สำเร็จได้ `{"ok": true, "result": ...}` exit 0
- input ผิดได้ `{"ok": false, "
…(ตัด 145 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และรันตรวจแล้ว: กรณีปกติได้ exit 0, กรณี input ผิดได้ exit 2 ไม่มี traceback, unit test ผ่านทั้ง 6 ชุด

ผมอ่านสกิล `cafe_function_checklist` ก่อนเริ่ม และทำตามนั้น คือ ตรวจ input, ปัดแบบ half-up, ใส่ CLI และเขียน `test_solve.py`

**การคำนวณ**
- ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) ได้ 0
- อัตราเป็นเศษส่วนจำนวนเต็ม: silver 3/200, gold 1/40, platinum 1/25 ถ้าเป็นเดือนเกิดคูณ 2
- ปัดแบบ half-up ครั้งเดียวด้วยจำนวนเต็ม แล้วจำกัดไม่เกิน 20,000 สตางค์ (200 บาท)

**ตรวจ input**
- ค่าผิดจะ `raise ValueError`: `amount` ไม่ใช่ int (รวม float และ bool) หรือติดลบ, `tier` ไม่อยู่ในสามระดับ, `birthday` ไม่ใช่ bool

**CLI**
- `python solve.py` อ่าน JSON จาก stdin
- สำเร็จได้ `{"ok": true, "result": ...}` exit 0
- input ผิดได้ `{"ok": false, "error": ...}` exit 2

ตัวอย่างที่รัน: gold, 20,000 สตางค์, เดือนเกิด ได้ 1,000 สตางค์

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`
