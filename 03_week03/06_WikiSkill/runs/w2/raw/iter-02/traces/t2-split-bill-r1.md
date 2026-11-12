# Trace t2-split-bill-r1 · iteration 2

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
    grand = (num * 2 + 100) // 200  # half up ครั้งเดียว
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
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(sum(split_bill(999, 7, 100)), 1998)

    def test_half_up(self):
        # 1 * 1.5 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 10*1.05 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(split_bill(1, 1, 49), [1])

    def test_reject(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                     (1000.0, 1, 0), (10, 1.0, 0), (10, 1, 10.0),
                     (True, 1, 0), (10, True, 0), ("10", 1, 0), (None, 1, 0)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"total":1000,"people":3,"tip_percent":10}' | python3 solve.py; echo $?
echo '{"total":1000,"people":0,"tip_percent":10}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
{"ok": true, "result": [367, 367, 366]}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `split_bill` ใน `solve.py` เสร็จแล้ว และ unittest ผ่านทั้ง 4 ชุด ลองรันแบบ CLI แล้วด้วย: อินพุตปกติได้ exit 0 ส่วนอินพุตผิดได้ exit 2

ฟังก์ชันทำตามโจทย์ และเพิ่มตามสกิล `cafe_solve_checklist` ที่อยู่ใน `./skills` อีก 3 อย่าง:
- **ตรวจอินพุต:** ถ้าค่าผิดช่วงหรือผิดชนิด (รวม float และ bool) จะ raise `ValueError`
- **ปัดเศษ:** ยอดรวมหลังบวกทิปคิดด้วยจำนวนเต็ม ปัด half up ครั้งเดียว
- **รันเป็น CLI:** อ่าน JSON จาก stdin ได้ และถ้าผิดจะพิมพ์ JSON แจ้ง error แล้ว exit 2 โดยไม่มี traceback

ตัวอย่าง: บิล 1000 สตางค์ ทิป 10% หาร 3 คน ได้ `[367, 367, 366]` ยอดรวม 1100 สตางค์

ผมสร้าง `test_solve.py` ไว้ข้างกัน ครอบคลุมกรณีปกติ ค่าขอบ เศษ .5 พอดี และอินพุตที่ต้องถูกปฏิเสธ

ไฟล์ทั้งสองอยู่ในโฟลเดอร์ปัจจุบัน

## คำตอบสุดท้ายของ Agent

เขียน `split_bill` ใน `solve.py` เสร็จแล้ว และ unittest ผ่านทั้ง 4 ชุด ลองรันแบบ CLI แล้วด้วย: อินพุตปกติได้ exit 0 ส่วนอินพุตผิดได้ exit 2

ฟังก์ชันทำตามโจทย์ และเพิ่มตามสกิล `cafe_solve_checklist` ที่อยู่ใน `./skills` อีก 3 อย่าง:
- **ตรวจอินพุต:** ถ้าค่าผิดช่วงหรือผิดชนิด (รวม float และ bool) จะ raise `ValueError`
- **ปัดเศษ:** ยอดรวมหลังบวกทิปคิดด้วยจำนวนเต็ม ปัด half up ครั้งเดียว
- **รันเป็น CLI:** อ่าน JSON จาก stdin ได้ และถ้าผิดจะพิมพ์ JSON แจ้ง error แล้ว exit 2 โดยไม่มี traceback

ตัวอย่าง: บิล 1000 สตางค์ ทิป 10% หาร 3 คน ได้ `[367, 367, 366]` ยอดรวม 1100 สตางค์

ผมสร้าง `test_solve.py` ไว้ข้างกัน ครอบคลุมกรณีปกติ ค่าขอบ เศษ .5 พอดี และอินพุตที่ต้องถูกปฏิเสธ

ไฟล์ทั้งสองอยู่ในโฟลเดอร์ปัจจุบัน
