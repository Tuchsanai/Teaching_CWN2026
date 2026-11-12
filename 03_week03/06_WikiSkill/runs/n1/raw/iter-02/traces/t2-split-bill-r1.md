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
billing_function_contract
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/billing_function_contract/* 2>&1
```

ผลที่ได้:

```
./skills/billing_function_contract/PURPOSE.md
./skills/billing_function_contract/SKILL.md
# PURPOSE

## Origin
สร้างจาก Trace iteration 1 (t1–t4 ทุก rollout) ที่ไม่มีสกิล Agent เขียนฟังก์ชันถูกตรงตามโจทย์ แต่ตัวตรวจต้องการสิ่งที่โจทย์ไม่ได้บอก

## Problems Addressed
- `reject_value` / `reject_type`: ไม่ตรวจอินพุต ปล่อย float, bool, ค่านอกช่วงผ่าน หรือเกิด ZeroDivisionError แทน ValueError
- `cli_ok` / `cli_error`: ไม่มี `__main__` ที่อ่าน stdin JSON และพิมพ์ `{ok,result|error}` พร้อม exit 2
- `tests`: ไม่มี test_solve.py
- `half_up` / `no_drift`: บาง rollout ปัดลงด้วย `//` ทำให้ 250.5 เป็น 250

## Evolution History
- v1: สร้างครั้งแรก
---
name: billing_function_contract
description: ขั้นตอนเขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินของร้าน BaanKafe ให้ผ่านตัวตรวจครบ ได้แก่ ปัดเศษ half-up, ปฏิเสธอินพุตผิด, CLI JSON และไฟล์ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชันคิดเงิน, ส่วนลด, VAT, ค่าส่ง, เงินคืน หรือหารบิล ในไฟล์ `solve.py`
- ตัวตรวจจะเรียกฟังก์ชันตรง ๆ, รัน `python3 solve.py` ทาง stdin และหาไฟล์ `test_solve.py` ข้าง `solve.py` แม้โจทย์ไม่ได้เขียนไว้ก็ตาม

# When NOT to Apply
- งานที่ไม่ใช่ฟังก์ชันคิดเงินใน `solve.py`

# Instructions

ต้องทำครบทั้ง 4 ข้อ ทั้งที่โจ
…(ตัด 2826 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
def _int(x, name, lo=None, hi=None):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"{name} out of range")
    return x


def split_bill(total, people, tip_percent):
    _int(total, "total", lo=0)
    _int(people, "people", lo=1)
    _int(tip_percent, "tip_percent", lo=0, hi=100)
    num = total * (100 + tip_percent)
    grand = (2 * num + 100) // 200  # half-up
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = split_bill(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 1001*1.05 = 1051.05 -> 1051 ; 10*1.05=10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        self.assertEqual(split_bill(1001, 1, 5), [1051])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_edges(self):
        self.assertEqual(sum(split_bill(999, 7, 100)), 1998)
        self.assertEqual(split_bill(5, 1, 100), [10])

    def test_invalid(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                  (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                  (True, 1, 0), (10, True, 0), (10, 1, False), ("1", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"total":1000,"people":3,"tip_percent":0}' | python3 solve.py; echo $?
echo '{"total":1000,"people":0,"tip_percent":0}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 7 tests in 0.001s

OK
{"ok": true, "result": [334, 333, 333]}
0
{"ok": false, "error": "people out of range"}
2
```

**Agent พูด:** สร้าง `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และทำตามสกิล `billing_function_contract` ที่อยู่ใน `./skills`

รัน `python3 -m unittest test_solve` ผ่านทั้ง 7 เทสต์ และลองรันผ่าน stdin แล้วได้ผลตามที่คาด
- อินพุตปกติ (`total=1000, people=3, tip_percent=0`) ได้ `{"ok": true, "result": [334, 333, 333]}` และ exit 0
- อินพุตผิด (`people=0`) ได้ `{"ok": false, "error": "people out of range"}` และ exit 2

ฟังก์ชัน `split_bill` ทำงานดังนี้
- **ยอดรวมทิป:** คำนวณด้วยจำนวนเต็มล้วนจาก `total × (100 + tip_percent) / 100` แล้วปัดครั้งเดียวแบบ half-up ไม่ใช้ float หรือ `round()` เช่น 10 สตางค์ ทิป 5% เป็น 10.5 ปัดเป็น 11
- **การหาร:** หารเท่ากัน แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบเศษ
- **ตรวจอินพุต:** ถ้า `total`, `people` หรือ `tip_percent` ไม่ใช่ `int` จริง (float, bool, str ก
…(ตัด 166 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และทำตามสกิล `billing_function_contract` ที่อยู่ใน `./skills`

รัน `python3 -m unittest test_solve` ผ่านทั้ง 7 เทสต์ และลองรันผ่าน stdin แล้วได้ผลตามที่คาด
- อินพุตปกติ (`total=1000, people=3, tip_percent=0`) ได้ `{"ok": true, "result": [334, 333, 333]}` และ exit 0
- อินพุตผิด (`people=0`) ได้ `{"ok": false, "error": "people out of range"}` และ exit 2

ฟังก์ชัน `split_bill` ทำงานดังนี้
- **ยอดรวมทิป:** คำนวณด้วยจำนวนเต็มล้วนจาก `total × (100 + tip_percent) / 100` แล้วปัดครั้งเดียวแบบ half-up ไม่ใช้ float หรือ `round()` เช่น 10 สตางค์ ทิป 5% เป็น 10.5 ปัดเป็น 11
- **การหาร:** หารเท่ากัน แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบเศษ
- **ตรวจอินพุต:** ถ้า `total`, `people` หรือ `tip_percent` ไม่ใช่ `int` จริง (float, bool, str ก็ไม่ผ่าน) หรืออยู่นอกช่วง จะ raise `ValueError`

สกิลกำหนดให้ใส่ส่วน CLI (อ่าน JSON จาก stdin) และไฟล์ `test_solve.py` ด้วย แม้โจทย์ไม่ได้ระบุ จึงเพิ่มให้ทั้งสองอย่าง
