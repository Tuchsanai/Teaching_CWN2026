# Trace t4-cashback-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
find ./skills -type f | head; cat ./skills/*/SKILL.md ./skills/*.md 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
./skills/billing_function_contract/PURPOSE.md
./skills/billing_function_contract/SKILL.md
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

## 2. ตรวจอินพุตก่อนค
…(ตัด 2292 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (4, 100)}
MIN_AMOUNT = 10000   # 100 baht in satang
CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative integer")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a boolean")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("unknown tier")
    if amount < MIN_AMOUNT:
        return 0
    n, d = RATES[tier]
    if birthday:
        n *= 2
    result = (2 * amount * n + d) // (2 * d)  # half-up, rounded once
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
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(10**6, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)

    def test_half_up(self):
        # 10100*15/1000 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        # 10020*25/1000 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_invalid(self):
        for args in [(100.0, "gold", False), ("1", "gold", False), (True, "gold", False),
                     (-1, "gold", False), (10000, "bronze", False), (10000, None, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":2.5,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "amount must be a non-negative integer"}
2
```

**Agent พูด:** ผมเขียน `cashback(amount, tier, birthday)` ไว้ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกันแล้ว unit test ผ่านทั้ง 6 ข้อ และ CLI ให้ผลตามที่คาดทั้งกรณีปกติและกรณีอินพุตผิด

ผมอ่านสกิล `billing_function_contract` ใน `./skills` ก่อนเริ่ม และทำตามนั้น ซึ่งมีหลายข้อที่โจทย์ไม่ได้เขียนไว้:
- **การคำนวณ:** ใช้เลขจำนวนเต็มล้วน ไม่ใช้ float และปัดเศษแบบ half-up ครั้งเดียวตอนท้าย เช่น 250.5 สตางค์ได้ 251
- **ลำดับขั้น:** ตรวจเกณฑ์ขั้นต่ำก่อน (ยอดต่ำกว่า 10,000 สตางค์ได้ 0) จากนั้นคิดอัตราตามระดับสมาชิก แล้วคูณ 2 ถ้าเป็นเดือนเกิด ปัดเศษ และจำกัดเพดาน 20,000 สตางค์ เพดานจึงคิดหลังคูณ 2
- **การตรวจอินพุต:** ถ้า `amount` ไม่ใช่ `int` หรือติดลบ, `tier` ไม่รู้จัก หรือ `birthday` ไม่ใช่ `bool` จะ raise `ValueError` รวมถึง float และ bool ที่ส่งมาแทน int
- **CLI:** รับ JSON ทาง stdin แล้วพิมพ์ `{"ok": t
…(ตัด 232 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

ผมเขียน `cashback(amount, tier, birthday)` ไว้ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกันแล้ว unit test ผ่านทั้ง 6 ข้อ และ CLI ให้ผลตามที่คาดทั้งกรณีปกติและกรณีอินพุตผิด

ผมอ่านสกิล `billing_function_contract` ใน `./skills` ก่อนเริ่ม และทำตามนั้น ซึ่งมีหลายข้อที่โจทย์ไม่ได้เขียนไว้:
- **การคำนวณ:** ใช้เลขจำนวนเต็มล้วน ไม่ใช้ float และปัดเศษแบบ half-up ครั้งเดียวตอนท้าย เช่น 250.5 สตางค์ได้ 251
- **ลำดับขั้น:** ตรวจเกณฑ์ขั้นต่ำก่อน (ยอดต่ำกว่า 10,000 สตางค์ได้ 0) จากนั้นคิดอัตราตามระดับสมาชิก แล้วคูณ 2 ถ้าเป็นเดือนเกิด ปัดเศษ และจำกัดเพดาน 20,000 สตางค์ เพดานจึงคิดหลังคูณ 2
- **การตรวจอินพุต:** ถ้า `amount` ไม่ใช่ `int` หรือติดลบ, `tier` ไม่รู้จัก หรือ `birthday` ไม่ใช่ `bool` จะ raise `ValueError` รวมถึง float และ bool ที่ส่งมาแทน int
- **CLI:** รับ JSON ทาง stdin แล้วพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าผิดพลาดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2

ตัวอย่างที่ลองรัน: `{"amount":20000,"tier":"gold","birthday":true}` ได้ 1000 และ exit 0 ส่วน `{"amount":2.5,...}` ได้ `ok: false` และ exit 2
