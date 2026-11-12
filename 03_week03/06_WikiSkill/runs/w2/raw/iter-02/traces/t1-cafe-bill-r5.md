# Trace t1-cafe-bill-r5 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
cafe_solve_checklist

./skills/cafe_solve_checklist:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/*.md
```

ผลที่ได้:

```
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด ret
…(ตัด 2579 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    member = _flag(member)
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("each item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        total += _int(it["price"], lo=0) * _int(it["qty"], lo=1)

    num, den = total, 1
    if total >= 50000:          # 500 baht in satang
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (num * 2 + den) // (den * 2)   # half up, once


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)

    def test_threshold(self):
        # 49999 -> no discount: 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000 -> 5%: 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)
        # 50000 member: *0.95*0.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)

    def test_reject(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": 100}], False),
            (["x"], False),
            ("x", False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": "100", "qty": 1}], False),
        ]
        for items, m in bad:
            with self.subTest(items=items, m=m):
                with self.assertRaises(ValueError):
                    cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":10000,"qty":0}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 19260}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว ชุดทดสอบ 5 ชุดใน `test_solve.py` ผ่านหมด และรันผ่าน CLI ได้ทั้งกรณีปกติ (exit 0) กับกรณีอินพุตผิด (exit 2)

ฉันอ่านสกิล `cafe_solve_checklist` ก่อนเริ่มและทำตามนั้น จึงมีส่วนที่เกินโจทย์: การตรวจอินพุต, CLI ที่รับ JSON ทาง stdin และไฟล์ทดสอบ

**การคิดเงิน**
- ยอดรวม = ผลรวมของ `price × qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float และปัดเศษแบบ half up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตัวอย่างที่ตรวจแล้ว**
- สินค้า 10,000 สตางค์ 2 ชิ้น ไม่เป็นสมาชิก ได้ 21,400
- ชุดเดียวกันแต่เป็นสมาชิก ได้ 19,260
- ยอด 49,999 ไม่ลด ได้ 53,499 ส่วนยอด 50,000 ลด 5% ได้ 50,825
- ยอด 50 บวก VAT ได้ 53.5 ปัดเป็น 54

**การตรวจอินพ
…(ตัด 428 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว ชุดทดสอบ 5 ชุดใน `test_solve.py` ผ่านหมด และรันผ่าน CLI ได้ทั้งกรณีปกติ (exit 0) กับกรณีอินพุตผิด (exit 2)

ฉันอ่านสกิล `cafe_solve_checklist` ก่อนเริ่มและทำตามนั้น จึงมีส่วนที่เกินโจทย์: การตรวจอินพุต, CLI ที่รับ JSON ทาง stdin และไฟล์ทดสอบ

**การคิดเงิน**
- ยอดรวม = ผลรวมของ `price × qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float และปัดเศษแบบ half up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตัวอย่างที่ตรวจแล้ว**
- สินค้า 10,000 สตางค์ 2 ชิ้น ไม่เป็นสมาชิก ได้ 21,400
- ชุดเดียวกันแต่เป็นสมาชิก ได้ 19,260
- ยอด 49,999 ไม่ลด ได้ 53,499 ส่วนยอด 50,000 ลด 5% ได้ 50,825
- ยอด 50 บวก VAT ได้ 53.5 ปัดเป็น 54

**การตรวจอินพุต** ค่าที่ผิดจะ `raise ValueError`:
- `price` ต้องเป็น int ตั้งแต่ 0
- `qty` ต้องเป็น int ตั้งแต่ 1
- float, bool, string และ item ที่ขาด key เช่น `price` หรือ `qty` ถูกปฏิเสธ
- `member` ต้องเป็น bool

ข้อกำหนดบางอย่างโจทย์ไม่ได้ระบุ ฉันจึงตั้งเองดังนี้:
- `price` เป็น 0 ได้
- `items` เป็น list ว่างได้ และคืน 0

ถ้าต้องการให้ list ว่างหรือราคา 0 ถูกปฏิเสธ บอกได้เลย

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`
