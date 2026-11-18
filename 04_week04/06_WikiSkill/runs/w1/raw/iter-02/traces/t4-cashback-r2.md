# Trace t4-cashback-r2 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก
- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = "silver" "gold" หรือ "platinum" · `birthday` = True คือซื้อในเดือนเกิด
- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%
- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
- เดือนเกิด ได้เงินคืน 2 เท่า
- เงินคืนสูงสุด 200 บาทต่อบิล
- คืนเงินคืน เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✓ `tests`
- ✗ `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 6 จาก 6 กรณี

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1; ls
```

ผลที่ได้:

```
solve-py-contract
skills
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/*/SKILL.md
```

ผลที่ได้:

```
./skills/solve-py-contract/PURPOSE.md
./skills/solve-py-contract/SKILL.md
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
RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5% 2.5% 4%
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES_PERMILLE:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # ปัดครั้งเดียว แบบครึ่งปัดขึ้น (ข้อสมมติ) ด้วยจำนวนเต็ม
    value = (amount * RATES_PERMILLE[tier] * mult + 500) // 1000
    return min(value, MAX_CASHBACK)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = cashback(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday_double(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_min_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        # 200 บาท = 20000 สตางค์; ตรวจเพดานหลังคูณ 2
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 19999 + 1)  # 19999.96 -> 20000
        self.assertEqual(cashback(300000, "platinum", True), 20000)

    def test_rounding(self):
        # 10010*15/1000 = 150.15 -> 150 ; 10040*15/1000=150.6 -> 151
        self.assertEqual(cashback(10010, "silver", False), 150)
        self.assertEqual(cashback(10040, "silver", False), 151)
        # ครึ่งพอดี (สมมติปัดขึ้น): 10010*25/1000 = 250.25 ; 10030*15=150.45 ; 10100*15/1000=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertIs(type(cashback(12345, "gold", True)), int)

    def test_reject(self):
        for args in [(100.0, "gold", False), (True, "gold", False), (-1, "gold", False),
                     ("100", "gold", False), (None, "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)
        for t in ["bronze", "Gold", 1, None]:
            with self.assertRaises(ValueError):
                cashback(20000, t, False)
        for b in [1, 0, "True", None]:
            with self.assertRaises(ValueError):
                cashback(20000, "gold", b)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
echo '{"amount":2.5,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 1000}
exit=0
{"ok": false, "error": "amount ต้องเป็นจำนวนเต็ม"}
exit=2
```

**Agent พูด:** เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` อยู่ข้างกัน เทสต์ผ่านทั้ง 6 รายการ ผมลองรันโหมด CLI ผ่าน stdin แล้ว: อินพุตถูกได้ `{"ok": true, "result": 1000}` (exit 0) และอินพุตผิดได้ `{"ok": false, "error": ...}` (exit 2) โดยไม่มี traceback

ผมอ่านสกิล `solve-py-contract` ก่อนเริ่มและทำตามแล้ว ซึ่งทำให้มีส่วนที่โจทย์ไม่ได้บอกตรง ๆ เพิ่มมา 3 อย่าง:
- **ตรวจอินพุต:** ถ้า `amount` ไม่ใช่ int จริง (float หรือ bool ไม่ผ่าน) หรือติดลบ, `tier` ไม่ใช่ 3 ค่านี้ หรือ `birthday` ไม่ใช่ bool จะ raise `ValueError`
- **โหมด CLI:** อ่าน JSON จาก stdin ตามรูปแบบที่สกิลกำหนด
- **ไฟล์เทสต์:** ครอบคลุมกรณีปกติ ค่าขอบ การปัดเศษ และอินพุตผิด

**ลำดับการคิดเงิน:**
1. ถ้ายอดต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
2. นำยอดไปคูณอัตรา แล้วคูณ 2 ถ้าซื้อในเดือนเกิด
3. ตัดเพดานที่ 20,000 สตางค์ (200 บาท) หลังคูณ 2 แล้ว
4. ผลเป็นจำนวนเต็มสตางค์ ปัดเศษครั้งเดียวตอนท้าย ด้วยเลขจำนวนเต็มล้วน

**ข้อสมมติที่โจทย์ไม่ได้บอก:**
- **ปัดเศษ:** ถ้าเศษสตางค์พอดีครึ่ง ผมปัดขึ้น เช่น ยอด 10,100 สตางค์ระดับ silver ได้ 151.5 แล้วปัดเป็น 152
- **ยอดพอดี 100 บาท:** ได้เงินคืน เพราะโจทย์บอกว่า "ต่ำกว่า" 100 บาทจึงไม่ได้

ถ้าร้านต้องการปัดเศษแบบอื่น เช่น ปัดลงเสมอ แก้ที่บรรทัดคำนวณ `value` บรรทัดเดียวใน `solve.py`

## คำตอบสุดท้ายของ Agent

เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` อยู่ข้างกัน เทสต์ผ่านทั้ง 6 รายการ ผมลองรันโหมด CLI ผ่าน stdin แล้ว: อินพุตถูกได้ `{"ok": true, "result": 1000}` (exit 0) และอินพุตผิดได้ `{"ok": false, "error": ...}` (exit 2) โดยไม่มี traceback

ผมอ่านสกิล `solve-py-contract` ก่อนเริ่มและทำตามแล้ว ซึ่งทำให้มีส่วนที่โจทย์ไม่ได้บอกตรง ๆ เพิ่มมา 3 อย่าง:
- **ตรวจอินพุต:** ถ้า `amount` ไม่ใช่ int จริง (float หรือ bool ไม่ผ่าน) หรือติดลบ, `tier` ไม่ใช่ 3 ค่านี้ หรือ `birthday` ไม่ใช่ bool จะ raise `ValueError`
- **โหมด CLI:** อ่าน JSON จาก stdin ตามรูปแบบที่สกิลกำหนด
- **ไฟล์เทสต์:** ครอบคลุมกรณีปกติ ค่าขอบ การปัดเศษ และอินพุตผิด

**ลำดับการคิดเงิน:**
1. ถ้ายอดต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
2. นำยอดไปคูณอัตรา แล้วคูณ 2 ถ้าซื้อในเดือนเกิด
3. ตัดเพดานที่ 20,000 สตางค์ (200 บาท) หลังคูณ 2 แล้ว
4. ผลเป็นจำนวนเต็มสตางค์ ปัดเศษครั้งเดียวตอนท้าย ด้วยเลขจำนวนเต็มล้วน

**ข้อสมมติที่โจทย์ไม่ได้บอก:**
- **ปัดเศษ:** ถ้าเศษสตางค์พอดีครึ่ง ผมปัดขึ้น เช่น ยอด 10,100 สตางค์ระดับ silver ได้ 151.5 แล้วปัดเป็น 152
- **ยอดพอดี 100 บาท:** ได้เงินคืน เพราะโจทย์บอกว่า "ต่ำกว่า" 100 บาทจึงไม่ได้

ถ้าร้านต้องการปัดเศษแบบอื่น เช่น ปัดลงเสมอ แก้ที่บรรทัดคำนวณ `value` บรรทัดเดียวใน `solve.py`
