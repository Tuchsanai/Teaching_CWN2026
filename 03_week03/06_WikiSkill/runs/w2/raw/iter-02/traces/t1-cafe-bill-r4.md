# Trace t1-cafe-bill-r4 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 5 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
cafe_solve_checklist
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/cafe_solve_checklist/* 2>/dev/null
```

ผลที่ได้:

```
./skills/cafe_solve_checklist/PURPOSE.md
./skills/cafe_solve_checklist/SKILL.md
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
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม
…(ตัด 2659 ตัวอักษร)
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


def I(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([I(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([I(10000, 2)], True), 19260)
        self.assertEqual(cafe_bill([], False), 0)

    def test_threshold(self):
        self.assertEqual(cafe_bill([I(49999)], False), 53499)  # 53498.93
        self.assertEqual(cafe_bill([I(50000)], False), 50825)  # 50000*.95*1.07
        self.assertEqual(cafe_bill([I(50001)], False), 50826)  # 50826.07
        self.assertEqual(cafe_bill([I(50000)], True), 45742)   # 45742.5 half up

    def test_half_up(self):
        self.assertEqual(cafe_bill([I(50)], True), 48)  # 48.15 -> 48
        self.assertEqual(cafe_bill([I(50, 1)], False), 54)  # 53.5 -> 54

    def test_reject(self):
        for bad in [([I(100.0)], False), ([I(100, 0)], False), ([I(-1)], False),
                    ([I(True)], False), ([I(100)], 1), ("x", False),
                    ([{"price": 1}], False), ([5], False), ([I(100, 1.0)], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(*bad)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":1.5,"qty":2}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 4 tests in 0.000s

FAILED (failures=1)
{"ok": true, "result": 19260}
0
{"ok": false, "error": "expected int, got 1.5"}
2
```

### ขั้น 4 · Bash

```
python3 -m unittest test_solve 2>&1 | head -15
```

ผลที่ได้:

```
...F
======================================================================
FAIL: test_threshold (test_solve.T.test_threshold)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/w2-k02-train/t1-cafe-bill-r4/sandbox/test_solve.py", line 19, in test_threshold
    self.assertEqual(cafe_bill([I(50000)], True), 45742)   # 45742.5 half up
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 45743 != 45742

----------------------------------------------------------------------
Ran 4 tests in 0.000s

FAILED (failures=1)
```

**Agent พูด:** My test expectation was wrong (half up of 45742.5 is 45743), so I'm fixing the test.

### ขั้น 5 · Bash

```
sed -i 's/True), 45742)   # 45742.5 half up/True), 45743)   # 45742.5 half up/' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ `test_solve.py` ผ่านทั้ง 4 ชุดทดสอบ

ผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตาม ซึ่งทำให้มีส่วนที่โจทย์ไม่ได้ขอเพิ่มมา 3 อย่าง:

- **การคิดเงิน:** ยอดรวมในหน่วยสตางค์ ถ้าถึง 50,000 สตางค์ (500 บาท) ลด 5% ถ้า `member=True` ลดอีก 10% แล้วบวก VAT 7% ตามลำดับนี้ คิดด้วยจำนวนเต็มทุกขั้นและปัดครั้งเดียวตอนท้ายแบบ half up เช่น 45742.5 ปัดเป็น 45743
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError` ได้แก่ `price` ติดลบ, `qty` น้อยกว่า 1, ค่าที่เป็น float หรือ bool, `member` ที่ไม่ใช่ bool และ `items` ที่ไม่ใช่ list ของ dict ที่มี key ครบ ส่วน `items` ที่เป็น list ว่างจะคืน 0
- **CLI:** รันด้วย `echo '{"items":[...],"member":true}' | python3 solve.py` ได้ ผลปกติ exit 0 และพิมพ์ `{"ok": true, "result": ...}` ถ้าอินพุตผิ
…(ตัด 347 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ `test_solve.py` ผ่านทั้ง 4 ชุดทดสอบ

ผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตาม ซึ่งทำให้มีส่วนที่โจทย์ไม่ได้ขอเพิ่มมา 3 อย่าง:

- **การคิดเงิน:** ยอดรวมในหน่วยสตางค์ ถ้าถึง 50,000 สตางค์ (500 บาท) ลด 5% ถ้า `member=True` ลดอีก 10% แล้วบวก VAT 7% ตามลำดับนี้ คิดด้วยจำนวนเต็มทุกขั้นและปัดครั้งเดียวตอนท้ายแบบ half up เช่น 45742.5 ปัดเป็น 45743
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError` ได้แก่ `price` ติดลบ, `qty` น้อยกว่า 1, ค่าที่เป็น float หรือ bool, `member` ที่ไม่ใช่ bool และ `items` ที่ไม่ใช่ list ของ dict ที่มี key ครบ ส่วน `items` ที่เป็น list ว่างจะคืน 0
- **CLI:** รันด้วย `echo '{"items":[...],"member":true}' | python3 solve.py` ได้ ผลปกติ exit 0 และพิมพ์ `{"ok": true, "result": ...}` ถ้าอินพุตผิดจะ exit 2 พร้อม JSON ที่มีข้อความ error ไม่มี traceback

ผมลองรัน CLI ทั้งสองแบบแล้ว: อินพุตปกติได้ 19260 (exit 0) และ `price` เป็น 1.5 ได้ error (exit 2)

`price` ที่เป็น 0 ผมให้ผ่านได้ เพราะโจทย์ไม่ได้ห้าม ถ้าต้องการให้ราคาต้องมากกว่า 0 ให้เปลี่ยน `lo=0` เป็น `lo=1` ในฟังก์ชัน

ไฟล์ทั้งสองอยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`
