# Trace t2-split-bill-r5 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ไม่

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
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
cafe_solve_checklist
```

### ขั้น 2 · Bash

```
find ./skills -type f | xargs -I{} sh -c 'echo "== {}"; cat "{}"'
```

ผลที่ได้:

```
== ./skills/cafe_solve_checklist/PURPOSE.md
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
== ./skills/cafe_solve_checklist/SKILL.md
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โ
…(ตัด 2665 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def split_bill(total, people, tip_percent):
    total = _int(total, 0)
    people = _int(people, 1)
    tip_percent = _int(tip_percent, 0, 100)
    num = total * (100 + tip_percent)
    grand = (num * 2 + 100) // 200  # half up, once
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]


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
        self.assertEqual(split_bill(1, 5, 0), [1, 0, 0, 0, 0])

    def test_half_up(self):
        # 10*105/100 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        # 30*105/100 = 31.5 -> 32
        self.assertEqual(split_bill(30, 1, 5), [32])

    def test_reject(self):
        for args in [(-1, 1, 0), (100, 0, 0), (100, 1, -1), (100, 1, 101),
                     (1000.0, 1, 0), (100, 1.0, 0), (100, 1, 5.0),
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

**Agent พูด:** เขียน `split_bill` ใน `solve.py` เสร็จแล้ว และ unittest ผ่านทั้ง 4 ชุด ผมรัน CLI ทดสอบด้วย: อินพุตปกติได้ exit 0 และอินพุตผิดได้ exit 2 พร้อม JSON แจ้งข้อผิดพลาด

ผมอ่านและทำตามสกิล `cafe_solve_checklist` ก่อนเริ่ม ซึ่งสกิลกำหนดให้ทำเพิ่มจากโจทย์ 3 อย่าง:

- **ตรวจอินพุต:** ถ้าค่าอยู่นอกช่วง (`total` < 0, `people` < 1, `tip_percent` นอก 0–100) หรือเป็นชนิดผิด (float, bool, str, None) ฟังก์ชันจะ `raise ValueError`
- **CLI:** รับ JSON ทาง stdin แล้วพิมพ์ผลเป็น JSON
- **ไฟล์ทดสอบ:** `test_solve.py` ครอบคลุมกรณีปกติ ค่าขอบ ปัดเศษที่ .5 พอดี และอินพุตที่ต้องถูกปฏิเสธ

ยอดรวมทิปคำนวณเป็น `total × (100 + tip_percent) / 100` ด้วยจำนวนเต็ม แล้วปัดครึ่งขึ้นครั้งเดียว โจทย์ไม่ได้ระบุวิธีปัด ผมจึงใช้ half up ตามสกิล เช่น บิล 30 สตางค์ทิป 5% ได้ 31.5 ซึ่งปัดเป็น 32 จากนั้นหารเท่ากัน และเศษที่เหลือให้คน
…(ตัด 159 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `split_bill` ใน `solve.py` เสร็จแล้ว และ unittest ผ่านทั้ง 4 ชุด ผมรัน CLI ทดสอบด้วย: อินพุตปกติได้ exit 0 และอินพุตผิดได้ exit 2 พร้อม JSON แจ้งข้อผิดพลาด

ผมอ่านและทำตามสกิล `cafe_solve_checklist` ก่อนเริ่ม ซึ่งสกิลกำหนดให้ทำเพิ่มจากโจทย์ 3 อย่าง:

- **ตรวจอินพุต:** ถ้าค่าอยู่นอกช่วง (`total` < 0, `people` < 1, `tip_percent` นอก 0–100) หรือเป็นชนิดผิด (float, bool, str, None) ฟังก์ชันจะ `raise ValueError`
- **CLI:** รับ JSON ทาง stdin แล้วพิมพ์ผลเป็น JSON
- **ไฟล์ทดสอบ:** `test_solve.py` ครอบคลุมกรณีปกติ ค่าขอบ ปัดเศษที่ .5 พอดี และอินพุตที่ต้องถูกปฏิเสธ

ยอดรวมทิปคำนวณเป็น `total × (100 + tip_percent) / 100` ด้วยจำนวนเต็ม แล้วปัดครึ่งขึ้นครั้งเดียว โจทย์ไม่ได้ระบุวิธีปัด ผมจึงใช้ half up ตามสกิล เช่น บิล 30 สตางค์ทิป 5% ได้ 31.5 ซึ่งปัดเป็น 32 จากนั้นหารเท่ากัน และเศษที่เหลือให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ เช่น บิล 10000 สตางค์ ทิป 10% หาร 3 คนได้ `[3667, 3667, 3666]`

ไฟล์อยู่ที่ `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบัน
