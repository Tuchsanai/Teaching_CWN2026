# Trace t1-cafe-bill-r2 · iteration 2

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
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && head -50 ./skills/* 2>/dev/null
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
    if total >= 50000:
        n, d = n * 95, d * 100
    if member:
        n, d = n * 90, d * 100
    n, d = n * 107, d * 100
    return (2 * n + d) // (2 * d)


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


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        self.assertEqual(cafe_bill([it(50000)], True), 45742)  # 45742.5 -> up

    def test_half_up(self):
        self.assertEqual(cafe_bill([it(50000)], True), 45743 - 1 + 0 if False else 45742 + 0 if False else cafe_bill([it(50000)], True))

    def test_invalid(self):
        for items, m in [([it(100, 0)], False), ([it(100, -1)], False),
                         ([it(100.0)], False), ([it(100, True)], False),
                         ([it(-1)], False), ([it(100)], 1), ("x", False),
                         ([{"price": 1}], False), ([5], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -c "
from solve import cafe_bill
print(cafe_bill([{'price':50000,'qty':1}],True), 50000*.95*.9*1.07)"
```

ผลที่ได้:

```
45743 45742.5
```

**Agent พูด:** Half-up gives 45743; I'll fix the test (and remove the silly placeholder one).

### ขั้น 4 · Bash

```
python3 - <<'EOF'
s=open('test_solve.py').read()
s=s.replace("45742)  # 45742.5 -> up","45743)  # 45742.5 -> up")
import re
s=re.sub(r"    def test_half_up\(self\):\n.*?\n\n","",s,flags=re.S)
open('test_solve.py','w').write(s)
EOF
python3 -m unittest -q
echo '{"items":[{"price":10000,"qty":2}],"member":false}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":100,"qty":0}],"member":false}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 21400}
exit=0
{"ok": false, "error": "qty out of range"}
exit=2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และทดสอบผ่าน ผมทำตามสกิล `cafe_function_checklist` ใน `./skills` ด้วย

**วิธีคิดเงิน**
- รวมยอด `price × qty` ทุกรายการ
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป คูณ 0.95
- ถ้า `member` เป็น True คูณ 0.90 เพิ่ม
- คูณ VAT 1.07 เป็นขั้นสุดท้าย
- ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ใช้เลขจำนวนเต็มล้วน ผลลัพธ์เป็น `int` สตางค์
  - เช่น ยอดรวม 50,000 สตางค์ ที่เป็นสมาชิก ได้ 45742.5 ซึ่งปัดเป็น 45743

**ข้อมูลที่ไม่ถูกต้อง** ฟังก์ชันจะ `raise ValueError` ในกรณีต่อไปนี้
- `items` ไม่ใช่ list
- `member` ไม่ใช่ bool
- รายการไม่ใช่ dict หรือขาด key `price`/`qty`
- ราคาหรือจำนวนไม่ใช่ int (float และ bool ถูกปฏิเสธ)
- ราคาติดลบ
- `qty` ต่ำกว่า 1

**ส่วนที่เพิ่มตามสกิล**
- `solve.py` มี CLI อ่าน JSON จาก stdin
  - ถ้าสำเร็จ จะได้ `{"ok":
…(ตัด 503 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และทดสอบผ่าน ผมทำตามสกิล `cafe_function_checklist` ใน `./skills` ด้วย

**วิธีคิดเงิน**
- รวมยอด `price × qty` ทุกรายการ
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป คูณ 0.95
- ถ้า `member` เป็น True คูณ 0.90 เพิ่ม
- คูณ VAT 1.07 เป็นขั้นสุดท้าย
- ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ใช้เลขจำนวนเต็มล้วน ผลลัพธ์เป็น `int` สตางค์
  - เช่น ยอดรวม 50,000 สตางค์ ที่เป็นสมาชิก ได้ 45742.5 ซึ่งปัดเป็น 45743

**ข้อมูลที่ไม่ถูกต้อง** ฟังก์ชันจะ `raise ValueError` ในกรณีต่อไปนี้
- `items` ไม่ใช่ list
- `member` ไม่ใช่ bool
- รายการไม่ใช่ dict หรือขาด key `price`/`qty`
- ราคาหรือจำนวนไม่ใช่ int (float และ bool ถูกปฏิเสธ)
- ราคาติดลบ
- `qty` ต่ำกว่า 1

**ส่วนที่เพิ่มตามสกิล**
- `solve.py` มี CLI อ่าน JSON จาก stdin
  - ถ้าสำเร็จ จะได้ `{"ok": true, "result": ...}` และ exit 0
  - ถ้า input ผิด จะได้ `{"ok": false, ...}` และ exit 2 โดยไม่มี traceback
- `test_solve.py` มี 4 เทส ครอบคลุมกรณีปกติ ขอบ 500 บาท สมาชิก/half-up และ input ผิด

**ผลที่รันจริง**
- `python3 -m unittest -q` ผ่านทั้ง 4 เทส
- ตัวอย่างปกติ (`price` 10000, `qty` 2, ไม่เป็นสมาชิก) ได้ 21400 และ exit 0
- ตัวอย่างที่ `qty` เป็น 0 ได้ `ok: false` และ exit 2

โจทย์ไม่ได้บอกว่า `items` ว่างได้หรือไม่ โค้ดจึงรับ list ว่างและคืน 0 ถ้าต้องการให้ list ว่างเป็นข้อผิดพลาด แจ้งได้เลย
