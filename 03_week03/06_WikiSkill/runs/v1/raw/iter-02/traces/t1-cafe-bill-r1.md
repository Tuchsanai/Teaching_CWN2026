# Trace t1-cafe-bill-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && head -c 3000 ./skills/* 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
cafe_function_checklist
```

### ขั้น 2 · Bash

```
ls -R ./skills; cat ./skills/cafe_function_checklist/* 2>/dev/null
```

ผลที่ได้:

```
./skills:
cafe_function_checklist

./skills/cafe_function_checklist:
PURPOSE.md
SKILL.md
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
- ตัวตรวจจะตรวจสิ่งที่โจท
…(ตัด 3067 ตัวอักษร)
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
    if type(items) is not list or not items:
        raise ValueError("items must be a non-empty list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        subtotal += _int("price", it["price"], 0) * _int("qty", it["qty"], 1)

    n, d = subtotal, 1
    if subtotal >= 50000:  # 500 baht
        n, d = n * 95, d * 100
    if member:
        n, d = n * 90, d * 100
    n, d = n * 107, d * 100  # VAT last
    return (2 * n + d) // (2 * d)  # half-up, single rounding


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
        # 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        ok = [{"price": 100, "qty": 1}]
        for items, m in [([], False), ([{"price": 100, "qty": 0}], False),
                         ([{"price": -1, "qty": 1}], False),
                         ([{"price": 100.0, "qty": 1}], False),
                         ([{"price": 100, "qty": True}], False),
                         ([{"price": 100}], False), (ok, 1), (None, False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"items":[{"price":50000,"qty":1}],"member":true}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":50000,"qty":0}],"member":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 45743}
exit=0
{"ok": false, "error": "qty out of range"}
exit=2
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว รันทดสอบแล้วผ่านทั้งหมด ได้แก่ `test_solve.py` 6 เคส และการรัน CLI ทั้งกรณีปกติ (exit=0) กับกรณีผิด (exit=2 ไม่มี traceback)

**วิธีคิดเงิน**
- รวมยอดเป็นสตางค์ ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว ไม่ได้บวกเป็น 15% ตรงนี้โจทย์ไม่ได้ระบุ ผมตีความว่า "ลดอีก" คือคิดต่อกัน
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้เศษส่วนจำนวนเต็มทั้งหมด แล้วปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int` เช่น ยอด 50,000 สตางค์ สมาชิก ได้ 45,743 (จาก 45,742.5)

**ส่วนที่เพิ่มตาม skill `cafe_function_checklist`**
- ตรวจ input แล้ว `raise ValueError` เมื่อ `price` ติดลบ, `qty` น้อยกว่า 1, ค่าเป็น float หรือ bool, `member` ไม่ใช่ bool หรือ item ขาด key
- มี CLI อ่าน JSON จาก stdin
- มี `t
…(ตัด 200 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว รันทดสอบแล้วผ่านทั้งหมด ได้แก่ `test_solve.py` 6 เคส และการรัน CLI ทั้งกรณีปกติ (exit=0) กับกรณีผิด (exit=2 ไม่มี traceback)

**วิธีคิดเงิน**
- รวมยอดเป็นสตางค์ ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว ไม่ได้บวกเป็น 15% ตรงนี้โจทย์ไม่ได้ระบุ ผมตีความว่า "ลดอีก" คือคิดต่อกัน
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้เศษส่วนจำนวนเต็มทั้งหมด แล้วปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int` เช่น ยอด 50,000 สตางค์ สมาชิก ได้ 45,743 (จาก 45,742.5)

**ส่วนที่เพิ่มตาม skill `cafe_function_checklist`**
- ตรวจ input แล้ว `raise ValueError` เมื่อ `price` ติดลบ, `qty` น้อยกว่า 1, ค่าเป็น float หรือ bool, `member` ไม่ใช่ bool หรือ item ขาด key
- มี CLI อ่าน JSON จาก stdin
- มี `test_solve.py`

**สมมติฐานที่โจทย์ไม่ได้ระบุ:** ถ้า `items` เป็น list ว่าง ผมให้ raise `ValueError` ไม่ได้คืนค่า 0 ถ้าต้องการให้คืน 0 แก้ได้ง่าย

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py`, `test_solve.py`
