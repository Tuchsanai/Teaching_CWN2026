# Trace t2-split-bill-r3 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
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
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/*.md 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
solve-py-contract
---
name: solve-py-contract
description: ข้อกำหนดที่ไม่ได้เขียนในโจทย์ของงานเขียนฟังก์ชันใน solve.py (ตรวจอินพุตแล้ว raise ValueError, โหมด CLI อ่าน JSON จาก stdin, ไฟล์ test_solve.py) ใช้ทุกครั้งที่ต้องสร้างหรือแก้ solve.py ก่อนตอบ
---

# solve.py ต้องมี 3 ส่วนเสมอ แม้โจทย์ไม่บอก

ตัวตรวจไม่ได้ดูแค่ว่าสูตรถูก แต่ตรวจสัญญาของไฟล์ด้วย ถ้าเขียนแต่สูตรคำนวณจะเสียคะแนนครึ่งหนึ่ง ทำทั้ง 3 ส่วนต่อไปนี้ทุกโจทย์

## 1) ตรวจอินพุตไว้ต้นฟังก์ชัน แล้ว raise ValueError

ช่วงค่าและชนิดที่โจทย์เขียนไว้ (เช่น "ตั้งแต่ 1", "0–100", "1–30,000", รายชื่อค่าที่อนุญาต) คือเงื่อนไขที่ต้องตรวจ ไม่ใช่แค่คำอธิบาย

- ก่อนคำนวณใด ๆ ให้แปลงทุกช่วงเป็น `if ... : raise ValueError("ข้อความที่อ่านรู้เรื่อง")` ทั้งขอบล่างและขอบบน (ตรวจค่า 0, ค่าติดลบ, ค่าเกินขอบ)
- พารามิเตอร์ที่ควรเป็นจำนวนเต็ม ให้ตรวจด้วย `type(x) is int` ซึ่งปฏิเสธ float (เช่น `4500.0`) และ bool (`True`) ไปพร้อมกัน ห้ามใช้ `isinstance(x, int)` เพราะ bool ผ่าน
- พารามิเตอร์ที่ควรเป็น bool ให้ตรวจ `type(x) is bool`
- พารามิเตอร์ที่เป็นข้อความที่มีค่าอนุญาตจำกัด (เช่น ระดับสมาชิก) ให้ตรวจ `type(x) is str and x in ALLOWED`
- พารามิเตอร์ที่เป็น list ของ dict ให้ตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ, และค่าในแต่ละ key ผ่านกฎชนิด/ช่วงเหมือนกัน (ตรวจทุกรายการ ไม่ใช่แค่รายการแรก)
- ห้ามปล่อยให้ `ZeroDivisionError`, `KeyError`, `TypeError` หลุดออกมาแทน ValueError ตรวจให้เสร็จก่อนถึงบรรทัดที่หารหรือค้นตาราง
- ผลที่คืนต้องเป็น `int` จริง (หรือ list ของ int) ตามที่โจทย์สั่ง ไม่ใช่ float

โครงตัวอย่าง:

```python
def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")
```

เรียกตัวช่วยนี้ที่ต้นฟังก์ชันหลักกับทุกพารามิเตอร์

## 2) โหมด CLI ท้าย solve.py

ตัวตรวจรัน `python3 solve.py` โดยส่ง JSON object ทาง stdin ที่มี key ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน ถ้าไม่มีบล็อกนี้จะได้ exit 0 และ stdout ว่าง ให้ต่อท้ายไฟล์เสมอ (เปลี่ยน `FUNC` เป็นชื่อฟังก์ชันของโจทย์):

```python
if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = FUNC(**data)
    except Exception as e:  # ValueError, TypeError, KeyError, JSONDecodeError
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
```

- สำเร็จ: stdout เป็น `{"ok": true, "result": ...}` exit 0
- ผิดพลาด: stdout เป็น `{"ok": false, "error": "..."}` exit 2 และห้ามมี traceback
- ต้องอยู่ใน `if __name__ == "__main__":` เพื่อให้ `import solve` จากไฟล์ทดสอบไม่ค้างรอ stdin
- ลองรันจริงทั้งกรณีสำเร็จและกรณีผิด แล้วดูทั้ง stdout และ exit code:

```bash
echo '{...อินพุตถูก...}' | python3 solve.py; echo "exit=$?"
echo '{...อินพุตผิด...}' | python3 solve.py; echo "exit=$?"
```

## 3) ไฟล์ test_solve.py ข้าง solve.py

ต้องมีไฟล์ `test_solve.py` (unittest) ในโฟลเดอร์เดียวกับ `solve.py` การรันทดสอบด้วย `python3 -c` แล้วทิ้งไม่นับ ให้ครอบคลุม:

- กรณีปกติอย่างน้อย 3 กรณี
- ค่าขอบของทุกเกณฑ์ในโจทย์ (ค่าที่พอดีเกณฑ์ ต่ำกว่า 1 หน่วย สูงกว่า 1 หน่วย) พร้อมคอมเมนต์ข้อสมมติเมื่อกติกาไม่ชัด
- เคสปัดเศษ
- อินพุตผิดอย่างน้อย 1 ตัวต่อ 1 พารามิเตอร์ ด้วย `with self.assertRaises(ValueError):` รวมกรณี float, ค่านอกช่วง, ค่า 0 และชนิดผิด

```python
import unittest
from solve import FUNC

class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(FUNC(...), ...)
    def test_reject(self):
        with self.assertRaises(ValueError):
            FUNC(...)

if __name__ == "__main__":
    unittest.main()
```

รัน `python3 -m unittest test_solve -v` ในโฟลเดอร์นั้นให้ผ่านทุกเทสต์ก่อนตอบ

## รายการตรวจก่อนตอบ

- [ ] ทุกพารามิเตอร์มีการตรวจชนิดและช่วง และ float/bool/0/ติดลบ/ค่าไม่อยู่ในรายการ ได้ ValueError
- [ ] ท้ายไฟล์มีบล็อก CLI และลองรัน stdin ทั้งกรณีสำเร็จและผิดแล้ว (exit 0 / exit 2, ไม่มี traceback)
- [ ] มี test_solve.py และรันผ่านครบ
- [ ] ผลลัพธ์เป็น int จริง และคำนวณด้วยจำนวนเต็มหรือ Fraction ปัดครั้งเดียวตอนท้าย
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def split_bill(total, people, tip_percent):
    _need_int("total", total, lo=0)
    _need_int("people", people, lo=1)
    _need_int("tip_percent", tip_percent, lo=0, hi=100)

    # ยอดรวมทิป: ปัดครึ่งขึ้นสตางค์ครั้งเดียว (ข้อสมมติ: โจทย์ไม่ระบุวิธีปัด)
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = split_bill(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import split_bill


class TestSolve(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_first_pay_more(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_tip_remainder(self):
        self.assertEqual(split_bill(1001, 2, 10), [551, 550])  # 1101.1 -> 1101

    def test_rounding_half_up(self):
        # 1005*1.10 = 1105.5 -> 1106 (สมมติปัดครึ่งขึ้น)
        self.assertEqual(sum(split_bill(1005, 1, 10)), 1106)

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_reject(self):
        bad = [
            (-1, 1, 0), (10.0, 1, 0), (True, 1, 0), ("10", 1, 0),
            (10, 0, 0), (10, -1, 0), (10, 1.0, 0), (10, True, 0), (10, None, 0),
            (10, 1, -1), (10, 1, 101), (10, 1, 5.0), (10, 1, False), (10, 1, "5"),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"total":1000,"people":3,"tip_percent":0}' | python3 solve.py; echo "exit=$?"
echo '{"total":1000,"people":0,"tip_percent":0}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
Ran 7 tests in 0.000s

OK
{"ok": true, "result": [334, 333, 333]}
exit=0
{"ok": false, "error": "people ต้องไม่น้อยกว่า 1"}
exit=2
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว เทสต์ผ่านครบ 7 ข้อ และลองรันโหมด CLI ทั้งกรณีสำเร็จ (exit 0) และกรณีอินพุตผิด (exit 2) แล้ว

ผมทำตามสกิล `solve-py-contract` ใน `./skills` ด้วย โดยเพิ่มส่วนที่โจทย์ไม่ได้เขียนไว้ 3 อย่าง:
- **ตรวจอินพุต:** `total`, `people` และ `tip_percent` ต้องเป็น int จริงและอยู่ในช่วงที่กำหนด ถ้าไม่ผ่านจะ raise `ValueError` float และ bool ก็ถูกปฏิเสธ
- **โหมด CLI:** อ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": ..., ...}` ออกทาง stdout
- **ไฟล์เทสต์:** `test_solve.py` ครอบคลุมกรณีปกติ ค่าขอบ เศษสตางค์ และอินพุตผิด

การคำนวณใช้จำนวนเต็มล้วน ยอดรวมทิปคือ `total*(100+tip)/100` ปัดครั้งเดียว แล้วแบ่งเศษให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์

โจทย์ไม่ได้บอกวิธีปัดเศษของทิป ผมเลือกปัดครึ่งขึ้น เช่น 1005 สตางค์ ทิป 10% เป็น 1105.5 ปัดเป็น 1106 ถ้าร้านต้องการปัดลงหรือวิธีอื่น แก้ที่บรรทัดคำนวณ `grand` ในไฟล์ `solve.py` ได้

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว เทสต์ผ่านครบ 7 ข้อ และลองรันโหมด CLI ทั้งกรณีสำเร็จ (exit 0) และกรณีอินพุตผิด (exit 2) แล้ว

ผมทำตามสกิล `solve-py-contract` ใน `./skills` ด้วย โดยเพิ่มส่วนที่โจทย์ไม่ได้เขียนไว้ 3 อย่าง:
- **ตรวจอินพุต:** `total`, `people` และ `tip_percent` ต้องเป็น int จริงและอยู่ในช่วงที่กำหนด ถ้าไม่ผ่านจะ raise `ValueError` float และ bool ก็ถูกปฏิเสธ
- **โหมด CLI:** อ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": ..., ...}` ออกทาง stdout
- **ไฟล์เทสต์:** `test_solve.py` ครอบคลุมกรณีปกติ ค่าขอบ เศษสตางค์ และอินพุตผิด

การคำนวณใช้จำนวนเต็มล้วน ยอดรวมทิปคือ `total*(100+tip)/100` ปัดครั้งเดียว แล้วแบ่งเศษให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์

โจทย์ไม่ได้บอกวิธีปัดเศษของทิป ผมเลือกปัดครึ่งขึ้น เช่น 1005 สตางค์ ทิป 10% เป็น 1105.5 ปัดเป็น 1106 ถ้าร้านต้องการปัดลงหรือวิธีอื่น แก้ที่บรรทัดคำนวณ `grand` ในไฟล์ `solve.py` ได้
