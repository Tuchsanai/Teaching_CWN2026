# Trace t2-split-bill-r3 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
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
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

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
    grand = (2 * num + 100) // 200  # half-up
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]


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
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 1, 10), [1100])

    def test_half_up(self):
        # 25 * 110% = 27.5 -> 28
        self.assertEqual(split_bill(25, 1, 10), [28])
        # 5*110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_edges(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(100, 1, 0), [100])
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_types(self):
        for args in [(10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0), (True, 1, 0),
                     (10, True, 0), (10, 1, False), ("10", 1, 0), (None, 1, 0)]:
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
Ran 5 tests in 0.000s

OK
{"ok": true, "result": [367, 367, 366]}
0
{"ok": false, "error": "people out of range"}
2
```

**Agent พูด:** เขียน `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ทำตามสกิล `billing_function_contract` ที่อยู่ใน `./skills`

- **การคำนวณ:** ยอดที่ต้องหารคือ `total × (100 + tip) / 100` ใช้จำนวนเต็มล้วนและปัดเศษแบบ half-up ครั้งเดียว เช่น 27.5 สตางค์ ปัดเป็น 28 จากนั้นหารเท่ากัน ถ้าเหลือเศษ คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- **การตรวจอินพุต:** ทุกพารามิเตอร์ต้องเป็น `int` จริง ปฏิเสธ float, str, None และ bool ค่านอกช่วงก็ไม่รับ (`total` < 0, `people` < 1, `tip_percent` นอก 0–100) โดย raise `ValueError`
- **CLI:** รับ JSON ทาง stdin แล้วพิมพ์ JSON บรรทัดเดียว กรณีสำเร็จได้ `{"ok": true, "result": ...}` และ exit 0 กรณีผิดพลาดได้ `{"ok": false, "error": ...}` และ exit 2

ผลการรัน:
- `python3 -m unittest test_solve` ผ่านทั้ง 5 เทสต์
- อินพุต `{"total":1000,"people":3,"tip_percent":10}` ได้ `[367
…(ตัด 111 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ทำตามสกิล `billing_function_contract` ที่อยู่ใน `./skills`

- **การคำนวณ:** ยอดที่ต้องหารคือ `total × (100 + tip) / 100` ใช้จำนวนเต็มล้วนและปัดเศษแบบ half-up ครั้งเดียว เช่น 27.5 สตางค์ ปัดเป็น 28 จากนั้นหารเท่ากัน ถ้าเหลือเศษ คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- **การตรวจอินพุต:** ทุกพารามิเตอร์ต้องเป็น `int` จริง ปฏิเสธ float, str, None และ bool ค่านอกช่วงก็ไม่รับ (`total` < 0, `people` < 1, `tip_percent` นอก 0–100) โดย raise `ValueError`
- **CLI:** รับ JSON ทาง stdin แล้วพิมพ์ JSON บรรทัดเดียว กรณีสำเร็จได้ `{"ok": true, "result": ...}` และ exit 0 กรณีผิดพลาดได้ `{"ok": false, "error": ...}` และ exit 2

ผลการรัน:
- `python3 -m unittest test_solve` ผ่านทั้ง 5 เทสต์
- อินพุต `{"total":1000,"people":3,"tip_percent":10}` ได้ `[367, 367, 366]` และ exit 0
- อินพุต `people` เป็น 0 ได้ `{"ok": false, "error": "people out of range"}` และ exit 2
