# Trace t1-cafe-bill-r3 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 4 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
ls -R ./skills 2>/dev/null | head -50
```

ผลที่ได้:

```
./skills:
cafe_function_checklist

./skills/cafe_function_checklist:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_function_checklist/*.md
```

ผลที่ได้:

```
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
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบทั้ง 4 ข้อด้านล่างทุกครั้ง แม้โจทย์ไม่สั่ง

## When NOT to 
…(ตัด 2978 ตัวอักษร)
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


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item must be dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item missing key")
        price = _int("price", it["price"], 0)
        qty = _int("qty", it["qty"], 1)
        total += price * qty

    n, d = total, 1
    if total >= 50000:  # 500 baht
        n *= 95
        d *= 100
    if member:
        n *= 90
        d *= 100
    n *= 107
    d *= 100
    return (2 * n + d) // (2 * d)  # half-up, rounded once


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cafe_bill(**data)
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
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45742)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": 100}], False),
            ([1], False),
            ({}, False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": 100, "qty": 1}], None),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"items":[{"price":30000,"qty":2}],"member":true}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":300,"qty":0}],"member":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
ERROR Exit code 1
{"ok": true, "result": 54891}
exit=0
{"ok": false, "error": "qty out of range"}
exit=2
======================================================================
FAIL: test_member (test_solve.T.test_member)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/v1-k02-train/t1-cafe-bill-r3/sandbox/test_solve.py", line 15, in test_member
    self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45742)
AssertionError: 45743 != 45742

----------------------------------------------------------------------
Ran 5 tests in 0.000s

FAILED (failures=1)
```

### ขั้น 4 · Bash

```
sed -i 's/45742)/45743)/' test_solve.py && python3 -m unittest -q
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` เสร็จแล้วใน `solve.py` พร้อม `test_solve.py` และรันทดสอบผ่านทั้ง 5 เทสต์

ผมอ่านและทำตามสกิล `cafe_function_checklist` ก่อนเริ่ม ตามที่โจทย์สั่ง

**วิธีคิดเงิน**
- ยอดรวมคือผลรวมของ `price*qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว (ตีความ "ลดอีก" เป็นการลดซ้อน ไม่ใช่รวมเป็น 15%)
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้จำนวนเต็มล้วนและปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตรวจ input**
- `items` ต้องเป็น list ของ dict ที่มี key `price` และ `qty` ครบ ส่วน `member` ต้องเป็น `bool`
- `price` ต้องเป็น int และ `>= 0` ส่วน `qty` ต้องเป็น int และ `>= 1`
- float และ bool ถูกปฏิเสธ ค่าผิดทุกกรณี raise `ValueError`
- โจทย์ไม่ได้ระบุว่า `items` ว่างได้หรือไม่ โค้ด
…(ตัด 529 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` เสร็จแล้วใน `solve.py` พร้อม `test_solve.py` และรันทดสอบผ่านทั้ง 5 เทสต์

ผมอ่านและทำตามสกิล `cafe_function_checklist` ก่อนเริ่ม ตามที่โจทย์สั่ง

**วิธีคิดเงิน**
- ยอดรวมคือผลรวมของ `price*qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว (ตีความ "ลดอีก" เป็นการลดซ้อน ไม่ใช่รวมเป็น 15%)
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้จำนวนเต็มล้วนและปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตรวจ input**
- `items` ต้องเป็น list ของ dict ที่มี key `price` และ `qty` ครบ ส่วน `member` ต้องเป็น `bool`
- `price` ต้องเป็น int และ `>= 0` ส่วน `qty` ต้องเป็น int และ `>= 1`
- float และ bool ถูกปฏิเสธ ค่าผิดทุกกรณี raise `ValueError`
- โจทย์ไม่ได้ระบุว่า `items` ว่างได้หรือไม่ โค้ดจึงยอมรับ list ว่างและคืน 0

**CLI**
- `python solve.py` อ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": true, "result": ...}` พร้อม exit 0
- ถ้า input ผิดจะพิมพ์ `{"ok": false, "error": ...}` พร้อม exit 2 และไม่มี traceback

**ผลที่รันจริง**
- ตัวอย่างปกติ (สินค้า 300 บาท 2 ชิ้น เป็นสมาชิก) ได้ 54891 สตางค์ และ exit=0
- ตัวอย่างผิด (`qty` เป็น 0) ได้ `"ok": false` และ exit=2
- เทสต์ครั้งแรกล้ม 1 ข้อ เพราะผมคาดค่าผิดเอง กรณี 50,000 สตางค์ เป็นสมาชิก ได้ 45742.5 ซึ่งปัดขึ้นเป็น 45743 ฟังก์ชันถูกต้อง ผมจึงแก้ค่าที่คาดในเทสต์แล้วรันผ่าน
