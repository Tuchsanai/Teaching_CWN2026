# Trace t1-cafe-bill-r1 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

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
ls -R ./skills 2>/dev/null | head -50
```

ผลที่ได้:

```
./skills:
solve-py-contract

./skills/solve-py-contract:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/solve-py-contract/*.md
```

ผลที่ได้:

```
# PURPOSE: solve-py-contract

## ที่มา
สร้างในรอบ 1 (iteration 1) ตอนยังไม่มีสกิลใช้งานเลย

## หลักฐาน
ทั้ง 12 Trace ในรอบ 1 ตกข้อตรวจ `reject_value`, `reject_type`, `cli_ok`, `cli_error`, `tests` เหมือนกันทุกโจทย์ (คะแนนเฉลี่ย 46.4%) ขณะที่ข้อตรวจเรื่องการคำนวณ (`basic`, `no_drift`, `boundary`, `half_up`) ผ่านหมด เปิดดู `t1-cafe-bill-r1`, `t2-split-bill-r2`, `t3-shipping-fee-r1`, `t4-cashback-r2` แล้วพบว่า Agent เขียนแต่สูตรคำนวณ ไม่มี `raise ValueError`, ไม่มีบล็อก `__main__` อ่าน stdin, ไม่มี test_solve.py และทดสอบด้วย `python3 -c` ทิ้ง (t4-cashback-r2 ไม่ได้รันเลย)

## pattern ใน wiki ที่แก้
- `wiki/patterns/missing-input-validation.md`
- `wiki/patterns/missing-cli-entrypoint.md`
- `wiki/patterns/missing-test-file.md`
- `wiki/patterns/shallow-self-check.md` (ส่วนรายการตรวจก่อนตอบ)

ไม่ได้แตะ `wiki/patterns/policy-ambiguous-edge-cases.md` เพราะยังไม่ยืนยันสาเหตุ และคงแนวทางจำนวนเต็มจาก `wiki/patterns/integer-money-arithmetic.md` ไว้

## ประวัติการแก้
- รอบ 1: สร้างสกิล รวม 3 ส่วนของสัญญาไฟล์ solve.py ที่โจทย์ไม่ได้บอก (ตรวจอินพุต, CLI, test_solve.py) เพราะเป็นกลุ่มข้อตรวจที่ตกพร้อมกันทุก Trace
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

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
from fractions import Fraction

THRESHOLD = 50000  # 500 บาท = 50,000 สตางค์ (ตั้งแต่เกณฑ์ขึ้นไปได้ลด)


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

    amt = Fraction(total)
    if total >= THRESHOLD:
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)  # ลดต่อจากส่วนลดแรก (ลดซ้อน)
    amt *= Fraction(107, 100)  # VAT เป็นขั้นสุดท้าย
    # ปัดครั้งเดียวตอนท้าย แบบ half-up
    return int(amt + Fraction(1, 2) // 1) if False else (amt.numerator * 2 + amt.denominator) // (amt.denominator * 2)


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
python3 - <<'EOF'
import re
s=open('solve.py').read()
s=s.replace("    return int(amt + Fraction(1, 2) // 1) if False else (amt.numerator * 2 + amt.denominator) // (amt.denominator * 2)","    return (amt.numerator * 2 + amt.denominator) // (amt.denominator * 2)")
open('solve.py','w').write(s)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000)], False), 10700)
        self.assertEqual(cafe_bill([it(6000, 2)], False), 12840)
        self.assertEqual(cafe_bill([it(10000), it(5000, 2)], True), 19260)

    def test_member_small(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_boundary(self):
        # พอดี 50000 ได้ลด 5% (สมมติ "ตั้งแต่" รวมค่าเกณฑ์)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 49999*1.07=53498.93
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50001*.95*1.07=50825.5 -> half up

    def test_rounding(self):
        self.assertEqual(cafe_bill([it(50001)], False), 50826)
        self.assertEqual(cafe_bill([it(1)], False), 1)  # 1.07
        self.assertEqual(cafe_bill([it(50)], False), 54)  # 53.5 half up

    def test_reject(self):
        bad = [
            ("x", False), ([it(1)], 1), ([it(1)], None),
            ([1], False), ([{"price": 1}], False), ([{"qty": 1}], False),
            ([it(1.0)], False), ([it(True)], False), ([it(-1)], False),
            ([it(1, 0)], False), ([it(1, -1)], False), ([it(1, 1.0)], False),
            ([it(1, True)], False), ([it("1")], False),
        ]
        for items, m in bad:
            with self.subTest(items=items, m=m):
                with self.assertRaises(ValueError):
                    cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -15
echo '{"items":[{"price":10000,"qty":1}],"member":true}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":1.5,"qty":1}],"member":true}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 9630}
exit=0
{"ok": false, "error": "items[0].price ต้องเป็นจำนวนเต็ม"}
exit=2
```

**Agent พูด:** ผมเขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และอ่านสกิล `solve-py-contract` ก่อนเริ่มตามที่โจทย์สั่ง unittest ผ่านทั้ง 5 เทสต์ ผมลองรัน CLI ทางstdin ด้วย โดยกรณีสำเร็จได้ exit 0 และกรณีอินพุตผิดได้ exit 2

**วิธีคิดเงิน**
- ยอดรวม = ผลรวมของ `price × qty` เป็นสตางค์
- ถ้ายอดรวม ≥ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% ต่อจากส่วนลดแรก
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วย `Fraction` แล้วปัดเศษครั้งเดียวตอนท้ายแบบ half-up จึงได้จำนวนเต็มสตางค์

**ข้อสมมติที่โจทย์ไม่ได้บอก**
- ยอดพอดี 500 บาทได้ส่วนลด 5% เพราะโจทย์เขียนว่า "ตั้งแต่ 500 บาทขึ้นไป"
- ส่วนลด 10% ของสมาชิกคิดต่อจากยอดที่ลด 5% แล้ว (ลดซ้อน) ไม่ได้บวกเป็น 15%
- เกณฑ์ 500 บาทตัดสินจากยอดรวมก่อนลด

**การตรวจอินพุต**
- ถ้าอินพุตผิด ฟังก์ชันจะ raise `ValueError`
- `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty` และตรวจทุกรายการ
- `price` ต้องเป็น int และไม่ติดลบ ผมให้ราคา 0 ผ่านได้ เพราะโจทย์ไม่ได้ห้าม
- `qty` ต้องเป็น int และ ≥ 1
- float และ bool ถูกปฏิเสธ
- `member` ต้องเป็น bool

**ไฟล์ที่ได้ในโฟลเดอร์ปัจจุบัน**
- `solve.py`: ฟังก์ชัน `cafe_bill` และบล็อก CLI ท้ายไฟล์ ซึ่งอ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": ..., ...}`
- `test_solve.py`: เทสต์กรณีปกติ ค่าขอบที่ 49,999, 50,000 และ 50,001 เคสปัดเศษ และอินพุตผิดหลายแบบ

## คำตอบสุดท้ายของ Agent

ผมเขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และอ่านสกิล `solve-py-contract` ก่อนเริ่มตามที่โจทย์สั่ง unittest ผ่านทั้ง 5 เทสต์ ผมลองรัน CLI ทางstdin ด้วย โดยกรณีสำเร็จได้ exit 0 และกรณีอินพุตผิดได้ exit 2

**วิธีคิดเงิน**
- ยอดรวม = ผลรวมของ `price × qty` เป็นสตางค์
- ถ้ายอดรวม ≥ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% ต่อจากส่วนลดแรก
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วย `Fraction` แล้วปัดเศษครั้งเดียวตอนท้ายแบบ half-up จึงได้จำนวนเต็มสตางค์

**ข้อสมมติที่โจทย์ไม่ได้บอก**
- ยอดพอดี 500 บาทได้ส่วนลด 5% เพราะโจทย์เขียนว่า "ตั้งแต่ 500 บาทขึ้นไป"
- ส่วนลด 10% ของสมาชิกคิดต่อจากยอดที่ลด 5% แล้ว (ลดซ้อน) ไม่ได้บวกเป็น 15%
- เกณฑ์ 500 บาทตัดสินจากยอดรวมก่อนลด

**การตรวจอินพุต**
- ถ้าอินพุตผิด ฟังก์ชันจะ raise `ValueError`
- `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty` และตรวจทุกรายการ
- `price` ต้องเป็น int และไม่ติดลบ ผมให้ราคา 0 ผ่านได้ เพราะโจทย์ไม่ได้ห้าม
- `qty` ต้องเป็น int และ ≥ 1
- float และ bool ถูกปฏิเสธ
- `member` ต้องเป็น bool

**ไฟล์ที่ได้ในโฟลเดอร์ปัจจุบัน**
- `solve.py`: ฟังก์ชัน `cafe_bill` และบล็อก CLI ท้ายไฟล์ ซึ่งอ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": ..., ...}`
- `test_solve.py`: เทสต์กรณีปกติ ค่าขอบที่ 49,999, 50,000 และ 50,001 เคสปัดเศษ และอินพุตผิดหลายแบบ
