# Trace t1-cafe-bill-r3 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน
- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`
- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%
- `member` = True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

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
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
billing_function_contract
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

## 2. ตรวจอินพุตก่อนคำนวณ แล้ว raise ValueError เท่านั้น
- ตัวเลขทุกตัวที่ควรเป็น int ต้องเป็น `int` จร
…(ตัด 2210 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
def _int(x, name, lo=None, hi=None):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"{name} out of range")
    return x


def cafe_bill(items, member):
    if type(member) is not bool:
        raise ValueError("member must be a boolean")
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("each item must be a dict with price and qty")
        price = _int(it["price"], "price", 0)
        qty = _int(it["qty"], "qty", 1)
        total += price * qty
    num, den = total, 1
    if total >= 50000:  # 500 baht in satang
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)  # half-up, rounded once


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for items, m in [([{"price": 100, "qty": 0}], False),
                         ([{"price": 100.0, "qty": 1}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 100, "qty": 1}], 1),
                         ([{"price": -1, "qty": 1}], False),
                         ("x", False), ([{"price": 1}], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"items":[{"price":50000,"qty":1}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":5.5,"qty":1}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 45743}
0
{"ok": false, "error": "price must be an integer"}
2
```

**Agent พูด:** สร้างไฟล์ `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และตามที่สกิล `billing_function_contract` กำหนด รันทดสอบแล้วผ่านทั้งหมด

**การคิดเงินใน `cafe_bill(items, member)`:**
- ยอดรวมคือผลรวมของ `price * qty`
- ยอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้า `member` เป็น True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยเลขจำนวนเต็มทั้งหมด ปัดเศษ half-up ครั้งเดียวตอนท้าย แล้วคืนเป็นจำนวนเต็มสตางค์

**การตรวจอินพุต:** ถ้า `price` หรือ `qty` ไม่ใช่ `int` จริง (float, str, None, bool), `qty` < 1, `price` ติดลบ, `member` ไม่ใช่ `bool` หรือ `items` ไม่ใช่ list ของ dict ที่มี key ครบ จะ raise `ValueError`

**CLI:** รับ JSON ทาง stdin แล้วพิมพ์ผลเป็น JSON บรรทัดเดียว
- สำเร็จ: `{"ok": true, "result": ...}` และ exit 0
- ผิดพลาด: `{"ok": false, "error": ...}` และ exit 2 ไม่มี
…(ตัด 302 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้างไฟล์ `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และตามที่สกิล `billing_function_contract` กำหนด รันทดสอบแล้วผ่านทั้งหมด

**การคิดเงินใน `cafe_bill(items, member)`:**
- ยอดรวมคือผลรวมของ `price * qty`
- ยอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้า `member` เป็น True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยเลขจำนวนเต็มทั้งหมด ปัดเศษ half-up ครั้งเดียวตอนท้าย แล้วคืนเป็นจำนวนเต็มสตางค์

**การตรวจอินพุต:** ถ้า `price` หรือ `qty` ไม่ใช่ `int` จริง (float, str, None, bool), `qty` < 1, `price` ติดลบ, `member` ไม่ใช่ `bool` หรือ `items` ไม่ใช่ list ของ dict ที่มี key ครบ จะ raise `ValueError`

**CLI:** รับ JSON ทาง stdin แล้วพิมพ์ผลเป็น JSON บรรทัดเดียว
- สำเร็จ: `{"ok": true, "result": ...}` และ exit 0
- ผิดพลาด: `{"ok": false, "error": ...}` และ exit 2 ไม่มี traceback

**ผลที่รันจริง:**
- `python3 -m unittest test_solve` ผ่านทั้ง 5 เทสต์ ครอบคลุมกรณีทั่วไป ค่าขอบ 49,999 / 50,000 / 50,001 เศษ .5 ที่ปัดขึ้น และอินพุตผิด
- สั่ง `{"items":[{"price":50000,"qty":1}],"member":true}` ได้ `45743` และ exit 0
- สั่งด้วย `price` เป็น `5.5` ได้ `ok: false` และ exit 2
