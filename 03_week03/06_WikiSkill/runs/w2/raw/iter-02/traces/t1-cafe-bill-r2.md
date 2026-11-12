# Trace t1-cafe-bill-r2 · iteration 2

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
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
cafe_solve_checklist
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

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด return 0)
ทุกอินพุตผิดช่วง/ผิดชนิดต้อง `raise ValueError` (ห้ามปล่อยให้เป็น ZeroDivisionError/TypeError/KeyError)
```python
def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):   # ปฏิเสธ bool และ float เช่น 20000.0
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x

def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x
```
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo
…(ตัด 1967 ตัวอักษร)
```

### ขั้น 2 · Bash

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
    _flag(member)
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        total += _int(it["price"], lo=0) * _int(it["qty"], lo=1)

    num, den = total, 1
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (num * 2 + den) // (den * 2)


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
        self.assertEqual(cafe_bill([], False), 0)

    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_half_up(self):
        # 5 * 107 / 100 = 5.35 -> 5 ; 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)
        self.assertEqual(cafe_bill([{"price": 5, "qty": 1}], False), 5)

    def test_reject(self):
        bad = [
            ([{"price": 1000.0, "qty": 1}], False),
            ([{"price": 1000, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": 1}], False),
            (["x"], False),
            ("x", False),
            ([], 1),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"items":[{"price":60000,"qty":1}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":6.5,"qty":1}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 54891}
0
{"ok": false, "error": "expected int, got 6.5"}
2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` เสร็จแล้วใน `solve.py` และเทสผ่านทั้งหมด (4 เทส) ตามเช็กลิสต์ใน `./skills`

- **การคิดเงิน:** ยอดรวม = Σ ราคา × จำนวน (หน่วยสตางค์) ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5% ถ้าเป็นสมาชิกลดอีก 10% แล้วบวก VAT 7% เป็นขั้นสุดท้าย
- **การปัดเศษ:** คิดด้วยเศษส่วนจำนวนเต็ม ไม่ใช้ float และปัดแบบ half up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError`
  - `price` ต้องเป็น int ตั้งแต่ 0 ขึ้นไป (ผมเลือกให้ราคา 0 ผ่านได้ เพราะโจทย์ไม่ได้ห้าม)
  - `qty` ต้องเป็น int ตั้งแต่ 1 ขึ้นไป
  - `member` ต้องเป็น bool
  - float, bool และ item ที่ขาด key ถูกปฏิเสธทั้งหมด
- **CLI:** ต่อท้าย `solve.py` ให้รันจาก stdin เป็น JSON ได้ ถ้าผิดปกติจะพิมพ์ JSON แจ้ง error แล้ว exit 2 ผมลองแล้ว: สมาชิกที่ซื้อ 60,000 สตางค์ได้ 54,891
…(ตัด 170 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` เสร็จแล้วใน `solve.py` และเทสผ่านทั้งหมด (4 เทส) ตามเช็กลิสต์ใน `./skills`

- **การคิดเงิน:** ยอดรวม = Σ ราคา × จำนวน (หน่วยสตางค์) ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5% ถ้าเป็นสมาชิกลดอีก 10% แล้วบวก VAT 7% เป็นขั้นสุดท้าย
- **การปัดเศษ:** คิดด้วยเศษส่วนจำนวนเต็ม ไม่ใช้ float และปัดแบบ half up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError`
  - `price` ต้องเป็น int ตั้งแต่ 0 ขึ้นไป (ผมเลือกให้ราคา 0 ผ่านได้ เพราะโจทย์ไม่ได้ห้าม)
  - `qty` ต้องเป็น int ตั้งแต่ 1 ขึ้นไป
  - `member` ต้องเป็น bool
  - float, bool และ item ที่ขาด key ถูกปฏิเสธทั้งหมด
- **CLI:** ต่อท้าย `solve.py` ให้รันจาก stdin เป็น JSON ได้ ถ้าผิดปกติจะพิมพ์ JSON แจ้ง error แล้ว exit 2 ผมลองแล้ว: สมาชิกที่ซื้อ 60,000 สตางค์ได้ 54,891 (exit 0) และราคา `6.5` ถูกปฏิเสธ (exit 2)
- **เทส:** `test_solve.py` ครอบคลุมเคสปกติ ค่าขอบที่ 49,999 / 50,000 / 50,001 การปัดเศษที่เศษ .5 พอดี และอินพุตที่ต้องถูกปฏิเสธ
