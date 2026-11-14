# Trace t4-cashback-r1 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 5 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
echo '{...อินพุตถูก...}' | python3 s
…(ตัด 1260 ตัวอักษร)
```

### ขั้น 3 · bash

```
{"command": "cat > solve.py <<'EOF'\nRATES_PERMILLE = {\"silver\": 15, \"gold\": 25, \"platinum\": 40}  # 1.5% 2.5% 4%\nMIN_AMOUNT = 10000   # 100 บาท (สตางค์)\nMAX_CASHBACK = 20000  # 200 บาท (สตางค์)\n\n\ndef _need_int(name, v, lo=None, hi=None):\n    if type(v) is not int:\n        raise ValueError(f\"{name} ต้องเป็นจำนวนเต็ม\")\n    if lo is not None and v < lo:\n        raise ValueError(f\"{name} ต้องไม่น้อยกว่า {lo}\")\n    if hi is not None and v > hi:\n        raise ValueError(f\"{name} ต้องไม่เกิน {hi}\")\n\n\ndef cashback(amount, tier, birthday):\n    _need_int(\"amount\", amount, lo=0)\n    if type(tier) is not str or tier not in RATES_PERMILLE:\n        raise ValueError(\"tier ต้องเป็น silver, gold หรือ platinum\")\n    if type(birthday) is not bool:\n        raise ValueError(\"birthday ต้องเป็น bool\")\n\n    if amount < MIN_AMOUNT:\n        return 0\n    mult = 2 if birthday else 1\n    num = amount * RATES_PERMILLE[tier] * mult  # หารด้วย 1000\n    result = (2 * num + 1000) // 2000  # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย\n    return min(result, MAX_CASHBACK)\n\n\nif __name__ == \"__main__\":\n    import json, sys\n    try:\n        data = json.loads(sys.stdin.read())\n        if type(data) is not dict:\n            raise ValueError(\"อินพุตต้องเป็น JSON object\")\n        result = cashback(**data)\n    except Exception as e:\n        print(json.dumps({\"ok\": False, \"error\": str(e) or type(e).__name__}, ensure_ascii=False))\n        sys.exit(2)\n    print(json.dumps({\"ok\": True, \"result\": result}))\n    sys.exit(0)\nEOF\ncat > test_solve.py <<'EOF'\nimport unittest\nfrom solve import cashback\n\n\nclass TestSolve(unittest.TestCase):\n    def test_normal(self):\n        self.assertEqual(cashback(50000, \"silver\", False), 750)\n        self.assertEqual(cashback(50000, \"gold\", False), 1250)\n        self.assertEqual(cashback(50000, \"platinum\", False), 2000)\n\n    def test_birthday(self):\n        self.assertEqual(cashback(50000, \"gold\", True), 2500)\n\n    def test_min_boundary(self):\n        self.assertEqual(cashback(9999, \"platinum\", True), 0)\n        self.assertEqual(cashback(10000, \"silver\", False), 150)  # พอดี 100 บาทได้\n        self.assertEqual(cashback(10001, \"silver\", False), 150)\n        self.assertEqual(cashback(0, \"gold\", False), 0)\n\n    def test_cap_boundary(self):\n        # platinum 4%: 500000 -> 20000 พอดี\n        self.assertEqual(cashback(500000, \"platinum\", False), 20000)\n        self.assertEqual(cashback(499999, \"platinum\", False), 19999)  # 19999.96\n        self.assertEqual(cashback(500001, \"platinum\", False), 20000)\n        self.assertEqual(cashback(250000, \"platinum\", True), 20000)\n        self.assertEqual(cashback(10**9, \"platinum\", True), 20000)\n        # cap ใช้หลังคูณ 2: 150000*4%=6000 -> x2=12000 ไม่ติดเพดาน\n        self.assertEqual(cashback(150000, \"platinum\", True), 12000)\n\n    def test_rounding(self):\n        # ข้อสมมติ: ปัดครึ่งขึ้น\n        self.assertEqual(ca
…(ตัด 1208 ตัวอักษร)
```

ผลที่ได้:

```
ERROR <tool_use_error>Error: No such tool available: bash. Tool names are case-sensitive: call Bash instead.</tool_use_error>
```

### ขั้น 4 · Bash

```
cat > solve.py <<'EOF'
RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5% 2.5% 4%
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def cashback(amount, tier, birthday):
    _need_int("amount", amount, lo=0)
    if type(tier) is not str or tier not in RATES_PERMILLE:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    num = amount * RATES_PERMILLE[tier] * mult  # หารด้วย 1000
    result = (2 * num + 1000) // 2000  # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
    return min(result, MAX_CASHBACK)


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
        self.assertEqual(cashback(50000, "silver", False), 750)
        self.assertEqual(cashback(50000, "gold", False), 1250)
        self.assertEqual(cashback(50000, "platinum", False), 2000)

    def test_birthday(self):
        self.assertEqual(cashback(50000, "gold", True), 2500)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)  # พอดี 100 บาทได้
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap_boundary(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96 -> 20000
        self.assertEqual(cashback(499990, "platinum", False), 19999.6 and 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(250000, "platinum", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)
        # cap ใช้หลังคูณ 2: 150000*4%=6000 -> x2=12000 ไม่ติดเพดาน
        self.assertEqual(cashback(150000, "platinum", True), 12000)

    def test_rounding(self):
        # ข้อสมมติ: ปัดครึ่งขึ้น
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10034, "silver", F
…(ตัด 1025 ตัวอักษร)
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 2500}
exit=0
{"ok": false, "error": "amount ต้องเป็นจำนวนเต็ม"}
exit=2
```

### ขั้น 5 · Bash

```
sed -i '/19999.6 and 20000/d' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เสร็จแล้ว: ผมแก้บรรทัดทดสอบที่เขียนแปลก ๆ ออกจาก `test_solve.py` แล้วรันซ้ำ ผ่านทั้ง 6 เทสต์

ไฟล์ที่ได้ในโฟลเดอร์ปัจจุบัน:
- `solve.py` มีฟังก์ชัน `cashback(amount, tier, birthday)` และโหมด CLI อ่าน JSON จาก stdin
- `test_solve.py` เป็น unittest

ผมทำตามสกิล `solve-py-contract` ใน `./skills` ซึ่งสั่งให้ตรวจอินพุต ทำโหมด CLI และเขียนไฟล์เทสต์ด้วย

**วิธีคิด**
- ยอดซื้อต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0 ส่วนยอดพอดี 100 บาทได้เงินคืน
- อัตราเงินคืนคือ silver 1.5%, gold 2.5%, platinum 4% และเดือนเกิดคูณ 2
- เพดาน 20,000 สตางค์ (200 บาท) ใช้หลังคูณ 2 แล้ว
- คำนวณด้วยจำนวนเต็มทั้งหมดและปัดเศษครั้งเดียวตอนท้าย ผลที่คืนเป็น `int`
- **ข้อสมมติ:** โจทย์ไม่ได้บอกวิธีปัดเศษ ผมเลือกปัดครึ่งขึ้น เช่น 252.5 เป็น 253 ถ้าต้องการปัดแบบอื่นแก้ที่บรรทัดคำนวณ `result` ได้

**การตรวจอินพุต**
- `amount` ต้องเป็น `int` และไม่ติดลบ float และ bool จะถูกปฏิเสธ
- `tier` ต้องเป็นข้อความที่ตรงกับ silver, gold หรือ platinum
- `birthday` ต้องเป็น bool
- ถ้าอินพุตผิดจะ raise `ValueError`

**ผลการรัน**
- อินพุตถูก: `{"ok": true, "result": 2500}` และ exit 0
- อินพุตผิด (`amount` เป็น float): `{"ok": false, "error": "..."}` และ exit 2 ไม่มี traceback

## คำตอบสุดท้ายของ Agent

เสร็จแล้ว: ผมแก้บรรทัดทดสอบที่เขียนแปลก ๆ ออกจาก `test_solve.py` แล้วรันซ้ำ ผ่านทั้ง 6 เทสต์

ไฟล์ที่ได้ในโฟลเดอร์ปัจจุบัน:
- `solve.py` มีฟังก์ชัน `cashback(amount, tier, birthday)` และโหมด CLI อ่าน JSON จาก stdin
- `test_solve.py` เป็น unittest

ผมทำตามสกิล `solve-py-contract` ใน `./skills` ซึ่งสั่งให้ตรวจอินพุต ทำโหมด CLI และเขียนไฟล์เทสต์ด้วย

**วิธีคิด**
- ยอดซื้อต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0 ส่วนยอดพอดี 100 บาทได้เงินคืน
- อัตราเงินคืนคือ silver 1.5%, gold 2.5%, platinum 4% และเดือนเกิดคูณ 2
- เพดาน 20,000 สตางค์ (200 บาท) ใช้หลังคูณ 2 แล้ว
- คำนวณด้วยจำนวนเต็มทั้งหมดและปัดเศษครั้งเดียวตอนท้าย ผลที่คืนเป็น `int`
- **ข้อสมมติ:** โจทย์ไม่ได้บอกวิธีปัดเศษ ผมเลือกปัดครึ่งขึ้น เช่น 252.5 เป็น 253 ถ้าต้องการปัดแบบอื่นแก้ที่บรรทัดคำนวณ `result` ได้

**การตรวจอินพุต**
- `amount` ต้องเป็น `int` และไม่ติดลบ float และ bool จะถูกปฏิเสธ
- `tier` ต้องเป็นข้อความที่ตรงกับ silver, gold หรือ platinum
- `birthday` ต้องเป็น bool
- ถ้าอินพุตผิดจะ raise `ValueError`

**ผลการรัน**
- อินพุตถูก: `{"ok": true, "result": 2500}` และ exit 0
- อินพุตผิด (`amount` เป็น float): `{"ok": false, "error": "..."}` และ exit 2 ไม่มี traceback
