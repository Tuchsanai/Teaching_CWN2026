# Trace t3-shipping-fee-r1 · iteration 2

- ผล: **FAIL** · คะแนน 0.91 (ผ่าน 10 จาก 11 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ
- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน
- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
- คืนค่าส่ง เป็นจำนวนเต็มสตางค์

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
- ✗ `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี

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
import math
from fractions import Fraction


def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    _need_int("weight_g", weight_g, 1, 30000)
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นตัวเลขจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่น้อยกว่า 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น bool")

    # หน่วยสตางค์; 15 บาท/กก. = 1500 สตางค์/1000 กรัม
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(1500 * (weight_g - 5000), 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
    return math.floor(fee + Fraction(1, 2))


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = shipping_fee(**data)
    except Exception as e:  # ValueError, TypeError, KeyError, JSONDecodeError
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)  # 80 + 5*15 = 155 บาท
        self.assertEqual(f(500, 150, True), 7200)     # 40*1.2*1.5 = 72 บาท

    def test_weight_boundaries(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8000 + 2)  # 1.5 สตางค์ -> ปัดขึ้น 2
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_distance_boundaries(self):
        self.assertEqual(f(500, 100, False), 4000)  # ข้อสมมติ: เกิน 100 จริงจึงคิดเพิ่ม
        self.assertEqual(f(500, 100.5, False), 4800)
        self.assertEqual(f(500, 101, False), 4800)

    def test_rounding(self):
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> 8002
        self.assertEqual(f(5003, 0, False), 8005)  # 8004.5 -> 8005
        self.assertEqual(f(5001, 101, True), 14403)  # 8001.5*1.8=14402.7

    def test_type_int(self):
        self.assertIs(type(f(5001, 0, True)), int)

    def test_reject(self):
        bad = [
            (0, 1, False), (-5, 1, False), (30001, 1, False), (500.0, 1, False),
            (True, 1, False), ("500", 1, False), (None, 1, False),
            (500, -1, False), (500, "10", False), (500, True, False),
            (500, float("nan"), False), (500, float("inf"), False), (500, None, False),
            (500, 1, 1), (500, 1, None), (500, 1, "yes"),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    f(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"weight_g":500,"distance_km":150,"express":true}' | python3 solve.py; echo "exit=$?"
echo '{"weight_g":0,"distance_km":1,"express":true}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
......
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 7200}
exit=0
{"ok": false, "error": "weight_g ต้องไม่น้อยกว่า 1"}
exit=2
```

**Agent พูด:** สร้างไฟล์ `solve.py` และ `test_solve.py` ไว้ในโฟลเดอร์ปัจจุบันแล้ว ทำตามสกิล `solve-py-contract` ที่อยู่ใน `./skills` ด้วย เทสต์ผ่านทั้ง 6 ชุด และลองรันโหมด CLI ทั้งกรณีสำเร็จ (exit 0) และกรณีอินพุตผิด (exit 2) แล้ว

**วิธีคิดค่าส่งใน `shipping_fee`**
- คิดเป็นสตางค์ด้วย `Fraction` แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย ผลที่คืนเป็น `int`
- ค่าส่วนที่เกิน 5,000 กรัมคิดตามสัดส่วนกรัม คือ 1.5 สตางค์ต่อกรัม
- เกิน 100 กม. คูณ 1.2 และส่งด่วนคูณ 1.5 ต่อจากนั้น

**การตรวจอินพุต** ถ้าผิดจะ raise `ValueError`
- `weight_g` ต้องเป็น int ช่วง 1–30,000 (float และ bool ไม่ผ่าน)
- `distance_km` ต้องเป็น int หรือ float ที่ไม่ติดลบ (ไม่รับ bool, NaN และ inf)
- `express` ต้องเป็น bool

**ข้อสมมติ** ระยะทางพอดี 100 กม. ไม่คิดเพิ่ม เพราะโจทย์บอกว่า "เกิน 100 กม." ผมใส่คอมเมนต์ไว้ในเทสต์แล้ว

**ตัวอย่างผล** น้ำหนัก 500 กรัม ระยะ 150 กม. ส่งด่วน ได้ 7,200 สตางค์ (72 บาท)

## คำตอบสุดท้ายของ Agent

สร้างไฟล์ `solve.py` และ `test_solve.py` ไว้ในโฟลเดอร์ปัจจุบันแล้ว ทำตามสกิล `solve-py-contract` ที่อยู่ใน `./skills` ด้วย เทสต์ผ่านทั้ง 6 ชุด และลองรันโหมด CLI ทั้งกรณีสำเร็จ (exit 0) และกรณีอินพุตผิด (exit 2) แล้ว

**วิธีคิดค่าส่งใน `shipping_fee`**
- คิดเป็นสตางค์ด้วย `Fraction` แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย ผลที่คืนเป็น `int`
- ค่าส่วนที่เกิน 5,000 กรัมคิดตามสัดส่วนกรัม คือ 1.5 สตางค์ต่อกรัม
- เกิน 100 กม. คูณ 1.2 และส่งด่วนคูณ 1.5 ต่อจากนั้น

**การตรวจอินพุต** ถ้าผิดจะ raise `ValueError`
- `weight_g` ต้องเป็น int ช่วง 1–30,000 (float และ bool ไม่ผ่าน)
- `distance_km` ต้องเป็น int หรือ float ที่ไม่ติดลบ (ไม่รับ bool, NaN และ inf)
- `express` ต้องเป็น bool

**ข้อสมมติ** ระยะทางพอดี 100 กม. ไม่คิดเพิ่ม เพราะโจทย์บอกว่า "เกิน 100 กม." ผมใส่คอมเมนต์ไว้ในเทสต์แล้ว

**ตัวอย่างผล** น้ำหนัก 500 กรัม ระยะ 150 กม. ส่งด่วน ได้ 7,200 สตางค์ (72 บาท)
