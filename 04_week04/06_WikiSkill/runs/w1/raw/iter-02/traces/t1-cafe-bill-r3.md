# Trace t1-cafe-bill-r3 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

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
from fractions import Fraction


def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    total = 0
    for i, it in enumerate(items):
        if type(it) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError(f"items[{i}] ต้องมี price และ qty")
        _need_int(f"items[{i}].price", it["price"], lo=0)
        _need_int(f"items[{i}].qty", it["qty"], lo=1)
        total += it["price"] * it["qty"]

    amount = Fraction(total)
    if total >= 50000:  # 500 บาท = 50,000 สตางค์ (พอดีเกณฑ์ได้ส่วนลด)
        amount *= Fraction(95, 100)
    if member:  # ลดสมาชิกต่อจากยอดหลังลด 5%
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    # ปัดครั้งเดียว half-up
    return int((amount * 2 + 1) // 2)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = cafe_bill(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([I(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([I(6000, 2), I(3000)], False), 16050)
        self.assertEqual(cafe_bill([I(10000)], True), 10700)

    def test_threshold(self):
        # สมมติ: ยอดพอดี 500 บาท ได้ลด 5%
        self.assertEqual(cafe_bill([I(50000)], False), 50825)  # 47500*1.07
        self.assertEqual(cafe_bill([I(49999)], False), 53499)  # ไม่ลด
        self.assertEqual(cafe_bill([I(50001)], False), 50826)  # 47500.95*1.07=50825.97

    def test_member_stack(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill([I(100000)], True), 91485)

    def test_rounding(self):
        # 105*1.07 = 112.35 -> 112 ; 150*1.07=160.5 -> 161 (half up)
        self.assertEqual(cafe_bill([I(105)], False), 112)
        self.assertEqual(cafe_bill([I(150)], False), 161)
        self.assertIs(type(cafe_bill([I(105)], False)), int)

    def test_reject(self):
        bad = [
            ("x", False), ([I(1)], 1), ([I(1)], None),
            ([I(1.0)], False), ([I(1, 0)], False), ([I(1, -1)], False),
            ([I(1, 1.0)], False), ([I(True)], False), ([I(1, True)], False),
            ([I(-1)], False), ([{"price": 1}], False), ([5], False),
            ([I(1), {"price": "a", "qty": 1}], False),
        ]
        for items, m in bad:
            with self.subTest(items=items, m=m):
                with self.assertRaises(ValueError):
                    cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -15
echo '{"items":[{"price":10000,"qty":2}],"member":false}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":1.5,"qty":2}],"member":false}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
.F...
======================================================================
FAIL: test_normal (test_solve.TestSolve.test_normal)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/runs/w1/rollouts/runs/k02-train/trials/t1-cafe-bill-r3/sandbox/test_solve.py", line 13, in test_normal
    self.assertEqual(cafe_bill([I(10000)], True), 10700)
AssertionError: 9630 != 10700

----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1)
{"ok": true, "result": 21400}
exit=0
{"ok": false, "error": "items[0].price ต้องเป็นจำนวนเต็ม"}
exit=2
```

**Agent พูด:** My test expectation was wrong (member discount applies: 10000×0.9×1.07 = 9630). Fixing the test.

### ขั้น 3 · Bash

```
sed -i 's/I(10000)\], True), 10700/I(10000)], True), 9630/' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -4
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.001s

OK
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` แล้ว ทำตามสกิล `solve-py-contract` ใน `./skills` เทสต์ผ่านครบ 5 ข้อ และลองรันโหมด CLI ทั้งกรณีสำเร็จ (exit 0) กับกรณีผิดพลาด (exit 2) แล้ว

**วิธีคิดเงินใน `cafe_bill(items, member)`**
- ยอดรวมคิดเป็นสตางค์ ถ้าถึง 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้าเป็นสมาชิก ลดอีก 10% ต่อจากยอดที่ลด 5% แล้ว ไม่ได้บวกเป็น 15%
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้ `Fraction` คำนวณ และปัดเศษครั้งเดียวตอนท้าย แบบ half-up ผลที่คืนเป็น `int`

**การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError`
- `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty` เป็นจำนวนเต็ม
- `qty` ต้องตั้งแต่ 1 ขึ้นไป
- float, bool และค่าติดลบถูกปฏิเสธ
- `member` ต้องเป็น bool

**ข้อสมมติที่โจทย์ไม่ได้บอก**
- ยอดรวมพอดี 500 บาทได้ส่วนลด 5%
- `price` เป็น 0 ได้
- list ว่างคืน 0 ถ้าต้องการให้ list ว่างเป็น error แจ้งได้

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` แล้ว ทำตามสกิล `solve-py-contract` ใน `./skills` เทสต์ผ่านครบ 5 ข้อ และลองรันโหมด CLI ทั้งกรณีสำเร็จ (exit 0) กับกรณีผิดพลาด (exit 2) แล้ว

**วิธีคิดเงินใน `cafe_bill(items, member)`**
- ยอดรวมคิดเป็นสตางค์ ถ้าถึง 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้าเป็นสมาชิก ลดอีก 10% ต่อจากยอดที่ลด 5% แล้ว ไม่ได้บวกเป็น 15%
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้ `Fraction` คำนวณ และปัดเศษครั้งเดียวตอนท้าย แบบ half-up ผลที่คืนเป็น `int`

**การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError`
- `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty` เป็นจำนวนเต็ม
- `qty` ต้องตั้งแต่ 1 ขึ้นไป
- float, bool และค่าติดลบถูกปฏิเสธ
- `member` ต้องเป็น bool

**ข้อสมมติที่โจทย์ไม่ได้บอก**
- ยอดรวมพอดี 500 บาทได้ส่วนลด 5%
- `price` เป็น 0 ได้
- list ว่างคืน 0 ถ้าต้องการให้ list ว่างเป็น error แจ้งได้
