# Trace t2-split-bill-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
cafe_function_checklist
```

### ขั้น 2 · Bash

```
ls -R ./skills; cat ./skills/cafe_function_checklist/* 2>&1
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
import json
import sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def split_bill(total, people, tip_percent):
    _int("total", total, 0)
    _int("people", people, 1)
    _int("tip_percent", tip_percent, 0, 100)
    # total * (100 + tip) / 100, rounded half-up once
    n = total * (100 + tip_percent)
    grand = (2 * n + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = split_bill(**data)
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
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 5*1.10=5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_edges(self):
        self.assertEqual(sum(split_bill(999, 7, 100)), 1998)

    def test_invalid(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1),
                  (10, 1, 101), (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                  (True, 1, 0), (10, True, 0), (10, 1, True), ("10", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"total":1000,"people":3,"tip_percent":10}' | python3 solve.py; echo "exit=$?"
echo '{"total":1000,"people":0,"tip_percent":10}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": [367, 367, 366]}
exit=0
{"ok": false, "error": "people out of range"}
exit=2
----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

**Agent พูด:** ผมสร้าง `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และรันตามขั้นตอนตรวจในสกิล `cafe_function_checklist` ครบทั้งสามคำสั่ง ผ่านหมด

- **การคำนวณ:** ยอดที่ต้องหารคือ `total × (100 + tip_percent) / 100` ปัดครั้งเดียวแบบ half-up ด้วยจำนวนเต็ม ไม่ใช้ float จากนั้นหารเท่ากันทุกคน ส่วนเศษที่เหลือให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- **การตรวจ input:** ค่าที่ไม่ใช่ `int` (รวม float และ bool) หรืออยู่นอกช่วง จะ `raise ValueError` ช่วงที่ตรวจคือ `total >= 0`, `people >= 1`, `tip_percent` อยู่ระหว่าง 0–100
- **CLI (เพิ่มตามสกิล):** `python solve.py` อ่าน JSON จาก stdin ถ้าสำเร็จ stdout เป็น `{"ok": true, "result": ...}` และ exit 0 ถ้า input ผิด stdout เป็น `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback
- **ผลการรัน:**
  - `{"total":1000,"people":3,"tip_percent":10}` ให้ `[36
…(ตัด 160 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

ผมสร้าง `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และรันตามขั้นตอนตรวจในสกิล `cafe_function_checklist` ครบทั้งสามคำสั่ง ผ่านหมด

- **การคำนวณ:** ยอดที่ต้องหารคือ `total × (100 + tip_percent) / 100` ปัดครั้งเดียวแบบ half-up ด้วยจำนวนเต็ม ไม่ใช้ float จากนั้นหารเท่ากันทุกคน ส่วนเศษที่เหลือให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- **การตรวจ input:** ค่าที่ไม่ใช่ `int` (รวม float และ bool) หรืออยู่นอกช่วง จะ `raise ValueError` ช่วงที่ตรวจคือ `total >= 0`, `people >= 1`, `tip_percent` อยู่ระหว่าง 0–100
- **CLI (เพิ่มตามสกิล):** `python solve.py` อ่าน JSON จาก stdin ถ้าสำเร็จ stdout เป็น `{"ok": true, "result": ...}` และ exit 0 ถ้า input ผิด stdout เป็น `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback
- **ผลการรัน:**
  - `{"total":1000,"people":3,"tip_percent":10}` ให้ `[367, 367, 366]` และ exit 0
  - `people` เป็น 0 ให้ `{"ok": false, "error": "people out of range"}` และ exit 2
  - `python3 -m unittest -q` รัน 7 เทสต์ ผ่านทั้งหมด
