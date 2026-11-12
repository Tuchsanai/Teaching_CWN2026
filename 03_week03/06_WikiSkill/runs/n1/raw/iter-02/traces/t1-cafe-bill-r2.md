# Trace t1-cafe-bill-r2 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 4 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
ls ./skills 2>&1; cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
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


def _bool(x, name):
    if type(x) is not bool:
        raise ValueError(f"{name} must be a boolean")
    return x


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be a list")
    _bool(member, "member")
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("each item must be a dict with price and qty")
        total += _int(it["price"], "price", 0) * _int(it["qty"], "qty", 1)
    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)


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
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45742)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for items, m in [([{"price": 100, "qty": 0}], False),
                         ([{"price": 100.0, "qty": 1}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 100, "qty": 1}], 1),
                         ([{"price": -1, "qty": 1}], False),
                         ([{"price": 1}], False), (None, False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"items":[{"price":10000,"qty":2}],"member":false}' | python3 solve.py; echo $?
echo '{"items":[{"price":1.5,"qty":2}],"member":false}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

FAILED (failures=1)
{"ok": true, "result": 21400}
0
{"ok": false, "error": "price must be an integer"}
2
```

### ขั้น 3 · Bash

```
python3 -m unittest test_solve 2>&1 | head -15
```

ผลที่ได้:

```
...F.
======================================================================
FAIL: test_member (test_solve.T.test_member)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/n1-k02-train/t1-cafe-bill-r2/sandbox/test_solve.py", line 16, in test_member
    self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45742)
AssertionError: 45743 != 45742

----------------------------------------------------------------------
Ran 5 tests in 0.000s

FAILED (failures=1)
```

### ขั้น 4 · Bash

```
sed -i 's/45742/45743/' test_solve.py; python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกันตามสกิล `billing_function_contract` เทสต์ผ่านทั้ง 5 ข้อ

รัน CLI ผ่าน stdin แล้วได้ผลตามที่คาด
- ข้อมูลปกติ (ราคา 10000 สตางค์ × 2 ชิ้น ไม่เป็นสมาชิก) ได้ `{"ok": true, "result": 21400}` และ exit 0
- ราคาเป็น float ได้ `{"ok": false, ...}` และ exit 2

**วิธีคิดเงิน**
- ยอดรวมคือผลรวมของ price × qty ถ้าตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป คูณ 0.95
- ถ้าเป็นสมาชิก คูณ 0.90 ซ้อนต่อจากส่วนลดแรก ผมตีความ "ลดอีก 10%" เป็นการลดซ้อนกัน ไม่ใช่รวมเป็น 15%
- สุดท้ายคูณ 1.07 (VAT)
- คำนวณด้วยจำนวนเต็มทั้งหมดและปัดเศษครั้งเดียวตอนท้ายแบบ half-up เช่น 45742.5 ได้ 45743

**การตรวจอินพุต**
- ถ้า price หรือ qty ไม่ใช่ `int` จริง (รวม float และ bool) จะ raise `ValueError`
- qty ต้องไม่ต่ำกว่า 1 และ price ต้องไม่ติดลบ
- `memb
…(ตัด 176 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` และเขียน `test_solve.py` ไว้ข้างกันตามสกิล `billing_function_contract` เทสต์ผ่านทั้ง 5 ข้อ

รัน CLI ผ่าน stdin แล้วได้ผลตามที่คาด
- ข้อมูลปกติ (ราคา 10000 สตางค์ × 2 ชิ้น ไม่เป็นสมาชิก) ได้ `{"ok": true, "result": 21400}` และ exit 0
- ราคาเป็น float ได้ `{"ok": false, ...}` และ exit 2

**วิธีคิดเงิน**
- ยอดรวมคือผลรวมของ price × qty ถ้าตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป คูณ 0.95
- ถ้าเป็นสมาชิก คูณ 0.90 ซ้อนต่อจากส่วนลดแรก ผมตีความ "ลดอีก 10%" เป็นการลดซ้อนกัน ไม่ใช่รวมเป็น 15%
- สุดท้ายคูณ 1.07 (VAT)
- คำนวณด้วยจำนวนเต็มทั้งหมดและปัดเศษครั้งเดียวตอนท้ายแบบ half-up เช่น 45742.5 ได้ 45743

**การตรวจอินพุต**
- ถ้า price หรือ qty ไม่ใช่ `int` จริง (รวม float และ bool) จะ raise `ValueError`
- qty ต้องไม่ต่ำกว่า 1 และ price ต้องไม่ติดลบ
- `member` ต้องเป็น `bool` และ `items` ต้องเป็น list ของ dict ที่มี key ครบ

ระหว่างทำมีเทสต์ข้อหนึ่งล้มเพราะผมใส่ค่าคาดหวังผิด (45742 แทนที่จะเป็น 45743) จึงแก้ที่เทสต์ ไม่ได้แก้โค้ด
