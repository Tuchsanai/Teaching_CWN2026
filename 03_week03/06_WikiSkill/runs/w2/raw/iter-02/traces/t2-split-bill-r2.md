# Trace t2-split-bill-r2 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล
- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)
- ยอดที่ต้องหาร = ยอดบิลบวกทิป
- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ
- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน

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
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/*.md 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
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
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์
…(ตัด 1985 ตัวอักษร)
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


def split_bill(total, people, tip_percent):
    total = _int(total, lo=0)
    people = _int(people, lo=1)
    tip_percent = _int(tip_percent, lo=0, hi=100)
    num = total * (100 + tip_percent)
    grand = (num * 2 + 100) // 200  # half up, ครั้งเดียว
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = split_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(5, 2, 0), [3, 2])

    def test_half_up(self):
        # 10*105/100 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        # 30*105/100 = 31.5 -> 32
        self.assertEqual(split_bill(30, 1, 5), [32])

    def test_reject(self):
        for args in [(-1, 1, 0), (100, 0, 0), (100, 1, -1), (100, 1, 101),
                     (100.0, 1, 0), (100, 1.0, 0), (100, 1, 5.0),
                     (True, 1, 0), (100, True, 0), ("100", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"total":10000,"people":3,"tip_percent":10}' | python3 solve.py; echo $?
echo '{"total":10000,"people":0,"tip_percent":10}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
{"ok": true, "result": [3667, 3667, 3666]}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว unittest 4 ข้อผ่านทั้งหมด และ CLI ให้ exit 0 กับอินพุตปกติ และ exit 2 กับอินพุตผิด

ผมทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ซึ่งโจทย์ไม่ได้ระบุไว้เอง:

- **ยอดที่หาร:** คิดจาก `total × (100 + tip_percent) / 100` แล้วปัดครึ่งขึ้น (half up) ครั้งเดียวด้วยจำนวนเต็ม ไม่ใช้ float
- **หารไม่ลงตัว:** เศษที่เหลือแจกคนลำดับแรก ๆ คนละ 1 สตางค์ เช่น 10000 สตางค์ หาร 3 คน ทิป 10% ได้ `[3667, 3667, 3666]`
- **ตรวจอินพุต:** `total` ≥ 0, `people` ≥ 1, `tip_percent` อยู่ระหว่าง 0–100 ถ้าเป็นค่านอกช่วง float, bool หรือชนิดอื่นจะ `raise ValueError`
- **CLI:** อ่าน JSON จาก stdin โดยใช้ชื่อพารามิเตอร์เป็น key เช่น `{"total":10000,"people":3,"tip_percent":10}` ถ้าผิดจะพิมพ์ `{"ok": false, "error": ...}` แล้ว exit 2 โดยไม่มี traceback

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว unittest 4 ข้อผ่านทั้งหมด และ CLI ให้ exit 0 กับอินพุตปกติ และ exit 2 กับอินพุตผิด

ผมทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ซึ่งโจทย์ไม่ได้ระบุไว้เอง:

- **ยอดที่หาร:** คิดจาก `total × (100 + tip_percent) / 100` แล้วปัดครึ่งขึ้น (half up) ครั้งเดียวด้วยจำนวนเต็ม ไม่ใช้ float
- **หารไม่ลงตัว:** เศษที่เหลือแจกคนลำดับแรก ๆ คนละ 1 สตางค์ เช่น 10000 สตางค์ หาร 3 คน ทิป 10% ได้ `[3667, 3667, 3666]`
- **ตรวจอินพุต:** `total` ≥ 0, `people` ≥ 1, `tip_percent` อยู่ระหว่าง 0–100 ถ้าเป็นค่านอกช่วง float, bool หรือชนิดอื่นจะ `raise ValueError`
- **CLI:** อ่าน JSON จาก stdin โดยใช้ชื่อพารามิเตอร์เป็น key เช่น `{"total":10000,"people":3,"tip_percent":10}` ถ้าผิดจะพิมพ์ `{"ok": false, "error": ...}` แล้ว exit 2 โดยไม่มี traceback
