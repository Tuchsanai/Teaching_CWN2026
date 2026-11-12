# Trace t4-cashback-r1 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
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
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

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

_RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}


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


def cashback(amount, tier, birthday):
    amount = _int(amount, lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"invalid tier: {tier!r}")
    birthday = _flag(birthday)
    if amount < 10000:
        return 0
    n, d = _RATES[tier]
    num = amount * n * (2 if birthday else 1)
    den = d
    result = (num * 2 + den) // (den * 2)  # half up, once
    return min(result, 20000)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", True), 1600)

    def test_edges(self):
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "silver", True), 300)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)

    def test_half_up(self):
        # 10010*0.015 = 150.15 -> 150 ; 10033*0.015=150.495 ; 10100*.025=252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        # 10050*0.015=150.75 -> 151 ; 10034*0.015=150.51 ->151
        self.assertEqual(cashback(10034, "silver", False), 151)
        # exactly .5: 10010*0.025=250.25; 10030*.025=250.75; 10020*.015=150.3
        # 10100*0.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_reject(self):
        for args in [(-1, "gold", False), (20000.0, "gold", False),
                     (True, "gold", False), ("20000", "gold", False),
                     (20000, "bronze", False), (20000, None, False),
                     (20000, "gold", 1), (20000, "gold", None),
                     (-1, "bad", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest -v test_solve 2>&1 | tail -5
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":-1,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "out of range: -1"}
2
```

**Agent พูด:** เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว พร้อม `test_solve.py` รัน unittest ผ่านทั้ง 5 เคส และลองรันเป็น CLI แล้วได้ผลตามที่คาด ทั้งกรณีปกติ (exit 0) และกรณีอินพุตผิด (exit 2)

ผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตามนั้น ซึ่งทำให้มีส่วนที่โจทย์ไม่ได้ระบุไว้เพิ่มเข้ามา:

- **หน่วยเงิน:** ยอดเป็นสตางค์ ดังนั้นเกณฑ์ขั้นต่ำ 100 บาทคือ 10,000 สตางค์ และเพดาน 200 บาทคือ 20,000 สตางค์
- **การคิดเงินคืน:** ใช้เศษส่วนจำนวนเต็ม (silver 3/200, gold 1/40, platinum 1/25) คูณ 2 เมื่อเป็นเดือนเกิด แล้วปัดครั้งเดียวแบบ half up จากนั้นค่อยใช้เพดาน 20,000
- **ตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError` ได้แก่ amount ติดลบ, float, bool หรือ string, tier ที่ไม่ใช่ silver/gold/platinum และ birthday ที่ไม่ใช่ bool
- **CLI:** `solve.py` รับ JSON ทาง stdin ได้ ถ้าผิดจ
…(ตัด 110 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว พร้อม `test_solve.py` รัน unittest ผ่านทั้ง 5 เคส และลองรันเป็น CLI แล้วได้ผลตามที่คาด ทั้งกรณีปกติ (exit 0) และกรณีอินพุตผิด (exit 2)

ผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตามนั้น ซึ่งทำให้มีส่วนที่โจทย์ไม่ได้ระบุไว้เพิ่มเข้ามา:

- **หน่วยเงิน:** ยอดเป็นสตางค์ ดังนั้นเกณฑ์ขั้นต่ำ 100 บาทคือ 10,000 สตางค์ และเพดาน 200 บาทคือ 20,000 สตางค์
- **การคิดเงินคืน:** ใช้เศษส่วนจำนวนเต็ม (silver 3/200, gold 1/40, platinum 1/25) คูณ 2 เมื่อเป็นเดือนเกิด แล้วปัดครั้งเดียวแบบ half up จากนั้นค่อยใช้เพดาน 20,000
- **ตรวจอินพุต:** ถ้าอินพุตผิดจะ `raise ValueError` ได้แก่ amount ติดลบ, float, bool หรือ string, tier ที่ไม่ใช่ silver/gold/platinum และ birthday ที่ไม่ใช่ bool
- **CLI:** `solve.py` รับ JSON ทาง stdin ได้ ถ้าผิดจะพิมพ์ `{"ok": false, ...}` แล้ว exit 2 โดยไม่มี traceback

โจทย์ไม่ได้ระบุวิธีปัดเศษ ผมจึงใช้ half up ตามสกิล
