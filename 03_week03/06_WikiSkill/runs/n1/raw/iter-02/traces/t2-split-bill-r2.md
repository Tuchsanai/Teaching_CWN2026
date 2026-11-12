# Trace t2-split-bill-r2 · iteration 2

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
find ./skills -type f | head; cat ./skills/*/SKILL.md
```

ผลที่ได้:

```
./skills/billing_function_contract/PURPOSE.md
./skills/billing_function_contract/SKILL.md
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

ต้องทำครบทั้ง 4 ข้อ ทั้งที่โจทย์ไม่ได้บอก

## 1. คำนวณด้วยจำนวนเต็ม และปัดเศษ half-up
- ห้ามใช้ float และห้ามใช้ `round()` เพราะ `round` ปัดแบบ banker's
- ใช้ `Fraction` หรือเลขจำนวนเต็ม คูณทุกอัตราเป็นเศษส่วน เช่น 2.5% = 25/1000 และ 7% = 107/100
- ปัดครั้งเดียวตอนท้าย สูตร half-up ของ `num/den` ที่ไม่ติดลบ: `(2*num + den) // (2*den)`
- การปัดลง (`//` อย่างเดียว) ผิด เช่น 250.5 ต้องได้ 251
- ทำตามลำดับขั้นที่โจทย์ระบุ (ลด → บวก → เพดาน/ขั้นต่ำ) และดูว่า "ตั้งแต่" หรือ "เกิน" ใช้ >= หรือ >
- ถ้าโจทย์สั่งให้ปัดทีละขั้นจึงค่อยปัดทีละขั้น

## 2. ตรวจอินพุตก่อนคำนวณ แล้ว raise Va
…(ตัด 2274 ตัวอักษร)
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
    _int(total, "total", 0)
    _int(people, "people", 1)
    _int(tip_percent, "tip_percent", 0, 100)
    num = total * (100 + tip_percent)
    grand = (2 * num + 100) // 200  # half-up, rounded once
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
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 1 * 150/100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 201*1.05 = 211.05 -> 211
        self.assertEqual(sum(split_bill(201, 1, 5)), 211)

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0),
                     (True, 1, 0), (1, True, 0), (1, 1, True), ("1", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"total":100,"people":3,"tip_percent":0}' | python3 solve.py; echo $?
echo '{"total":100,"people":0,"tip_percent":0}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
{"ok": true, "result": [34, 33, 33]}
0
{"ok": false, "error": "people out of range"}
2
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ผมทำตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` และรันทดสอบจริงแล้ว

- **สูตรคำนวณ:** ยอดรวมคือ `total*(100+tip)/100` ใช้จำนวนเต็มล้วนและปัดแบบ half-up ครั้งเดียว (ไม่ใช้ float หรือ `round()`)
- **การหาร:** ใช้ `divmod` แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ตามจำนวนเศษที่เหลือ เช่น `split_bill(100, 3, 0)` ได้ `[34, 33, 33]`
- **ตรวจอินพุต:** ถ้าไม่ใช่ `int` จริง (รวม float, bool, str, None) หรือค่าอยู่นอกช่วง จะ raise `ValueError`
- **CLI:** อ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": true, "result": ...}` เมื่อสำเร็จ ถ้าผิดพลาดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2

ผลที่รันได้:
- `python3 -m unittest test_solve` ผ่านทั้ง 6 เทสต์
- อินพุตปกติได้ `ok: true` และ exit 0
- อินพุตผิด (`people` = 0) ได้ `ok: false`
…(ตัด 11 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ผมทำตามสกิล `billing_function_contract` ที่อยู่ใน `./skills` และรันทดสอบจริงแล้ว

- **สูตรคำนวณ:** ยอดรวมคือ `total*(100+tip)/100` ใช้จำนวนเต็มล้วนและปัดแบบ half-up ครั้งเดียว (ไม่ใช้ float หรือ `round()`)
- **การหาร:** ใช้ `divmod` แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ตามจำนวนเศษที่เหลือ เช่น `split_bill(100, 3, 0)` ได้ `[34, 33, 33]`
- **ตรวจอินพุต:** ถ้าไม่ใช่ `int` จริง (รวม float, bool, str, None) หรือค่าอยู่นอกช่วง จะ raise `ValueError`
- **CLI:** อ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": true, "result": ...}` เมื่อสำเร็จ ถ้าผิดพลาดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2

ผลที่รันได้:
- `python3 -m unittest test_solve` ผ่านทั้ง 6 เทสต์
- อินพุตปกติได้ `ok: true` และ exit 0
- อินพุตผิด (`people` = 0) ได้ `ok: false` และ exit 2
