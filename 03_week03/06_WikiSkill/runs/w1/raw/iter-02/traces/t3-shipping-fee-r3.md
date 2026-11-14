# Trace t3-shipping-fee-r3 · iteration 2

- ผล: **FAIL** · คะแนน 0.82 (ผ่าน 9 จาก 11 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 2 ครั้ง · อ่านสกิล: ใช่

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
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- ✗ `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี

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
echo '{...อินพ
…(ตัด 1222 ตัวอักษร)
```

### ขั้น 2 · bash

```
{"command": "cd . && cat > solve.py <<'EOF'\nimport math\nfrom fractions import Fraction\n\n\ndef _need_int(name, v, lo=None, hi=None):\n    if type(v) is not int:\n        raise ValueError(f\"{name} ต้องเป็นจำนวนเต็ม\")\n    if lo is not None and v < lo:\n        raise ValueError(f\"{name} ต้องไม่น้อยกว่า {lo}\")\n    if hi is not None and v > hi:\n        raise ValueError(f\"{name} ต้องไม่เกิน {hi}\")\n\n\ndef shipping_fee(weight_g, distance_km, express):\n    _need_int(\"weight_g\", weight_g, 1, 30000)\n    if type(distance_km) not in (int, float):\n        raise ValueError(\"distance_km ต้องเป็นตัวเลข\")\n    if type(distance_km) is float and not math.isfinite(distance_km):\n        raise ValueError(\"distance_km ต้องเป็นจำนวนจำกัด\")\n    if distance_km < 0:\n        raise ValueError(\"distance_km ต้องไม่น้อยกว่า 0\")\n    if type(express) is not bool:\n        raise ValueError(\"express ต้องเป็น bool\")\n\n    # คำนวณเป็นสตางค์ด้วย Fraction แล้วปัดครั้งเดียวตอนท้าย (half up)\n    if weight_g <= 1000:\n        fee = Fraction(4000)\n    elif weight_g <= 5000:\n        fee = Fraction(8000)\n    else:\n        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)\n    if distance_km > 100:\n        fee *= Fraction(6, 5)\n    if express:\n        fee *= Fraction(3, 2)\n    return int(math.floor(fee + Fraction(1, 2)))\n\n\nif __name__ == \"__main__\":\n    import json, sys\n    try:\n        data = json.loads(sys.stdin.read())\n        if type(data) is not dict:\n            raise ValueError(\"อินพุตต้องเป็น JSON object\")\n        result = shipping_fee(**data)\n    except Exception as e:\n        print(json.dumps({\"ok\": False, \"error\": str(e) or type(e).__name__}, ensure_ascii=False))\n        sys.exit(2)\n    print(json.dumps({\"ok\": True, \"result\": result}))\n    sys.exit(0)\nEOF\ncat > test_solve.py <<'EOF'\nimport unittest\nfrom solve import shipping_fee\n\n\nclass TestSolve(unittest.TestCase):\n    def test_normal(self):\n        self.assertEqual(shipping_fee(500, 10, False), 4000)\n        self.assertEqual(shipping_fee(3000, 50, False), 8000)\n        self.assertEqual(shipping_fee(10000, 50, False), 8000 + 7500)\n        self.assertEqual(shipping_fee(500, 200, True), 7200)\n\n    def test_edges(self):\n        self.assertEqual(shipping_fee(1, 0, False), 4000)\n        self.assertEqual(shipping_fee(1000, 0, False), 4000)\n        self.assertEqual(shipping_fee(1001, 0, False), 8000)\n        self.assertEqual(shipping_fee(5000, 0, False), 8000)\n        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 สตางค์ -> ปัด 2\n        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)\n        # ระยะ 100 พอดี ไม่เพิ่ม; เกิน 100 เพิ่ม 20%\n        self.assertEqual(shipping_fee(500, 100, False), 4000)\n        self.assertEqual(shipping_fee(500, 100.1, False), 4800)\n\n    def test_rounding(self):\n        # 8001.5*1.2 = 9601.8 -> 9602\n        self.assertEqual(shipping_fee(5001, 101, False), 9602)\n        # 8001.5
…(ตัด 960 ตัวอักษร)
```

ผลที่ได้:

```
ERROR <tool_use_error>Error: No such tool available: bash. Tool names are case-sensitive: call Bash instead.</tool_use_error>
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
    _need_int("weight_g", weight_g, 1, 30000)
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่น้อยกว่า 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น bool")

    # คำนวณเป็นสตางค์ด้วย Fraction แล้วปัดครั้งเดียวตอนท้าย (half up)
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return int(math.floor(fee + Fraction(1, 2)))


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = shipping_fee(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import shipping_fee


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)
        self.assertEqual(shipping_fee(3000, 50, False), 8000)
        self.assertEqual(shipping_fee(10000, 50, False), 8000 + 7500)
        self.assertEqual(shipping_fee(500, 200, True), 7200)

    def test_edges(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 สตางค์ -> ปัด 2
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)
        # ระยะ 100 พอดี ไม่เพิ่ม; เกิน 100 เพิ่ม 20%
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 100.1, False), 4800)

    def test_rounding(self):
        # 8001.5*1.2 = 9601.8 -> 9602
        self.assertEqual(shipping_fee(5001, 101, False), 9602)
        # 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)
        self.assertIs(type(shipping_fee(5
…(ตัด 784 ตัวอักษร)
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 7200}
exit=0
{"ok": false, "error": "weight_g ต้องไม่น้อยกว่า 1"}
exit=2
```

**Agent พูด:** เขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` อยู่ข้างกัน เทสต์ทั้ง 4 ชุดผ่าน และลองรันโหมด CLI ทั้งกรณีสำเร็จและกรณีผิดแล้ว ผลเป็นไปตามที่ควร

ฉันอ่านสกิล `solve-py-contract` ใน `./skills` ก่อนเริ่ม และทำตามนั้น ได้แก่ ตรวจอินพุตแล้ว raise `ValueError`, มีบล็อก CLI อ่าน JSON จาก stdin และมีไฟล์ทดสอบ

**วิธีคิดค่าส่ง**
- คิดเป็นสตางค์ด้วย `Fraction` แล้วปัดเศษครั้งเดียวตอนท้ายแบบปัดครึ่งขึ้น ผลที่คืนเป็น `int`
- ส่วนที่เกิน 5,000 กรัมคิด 1.5 สตางค์ต่อกรัม ตามสัดส่วน 15 บาทต่อกิโลกรัม
- ระยะทางเกิน 100 กม. คูณ 1.2 ส่วนส่งด่วนคูณ 1.5 ต่อจากนั้น
- ระยะทางพอดี 100 กม. ไม่คิดเพิ่ม เพราะโจทย์บอกว่า "เกิน 100"

**การตรวจอินพุต**
- `weight_g` ต้องเป็น `int` ในช่วง 1–30,000 โดย float และ bool ถูกปฏิเสธ
- `distance_km` เป็น `int` หรือ `float` ที่ไม่น้อยกว่า 0 และไม่รับ bool, nan หรือ inf
- `express` ต้องเป็น `bool`

**CLI:** สำเร็จได้ `{"ok": true, "result": ...}` และ exit 0 ส่วนอินพุตผิดได้ `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback

ข้อสมมติที่ฉันเลือกเองคือให้ `distance_km` เป็นทศนิยมได้ เพราะโจทย์ไม่ได้ระบุชนิด

## คำตอบสุดท้ายของ Agent

เขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` อยู่ข้างกัน เทสต์ทั้ง 4 ชุดผ่าน และลองรันโหมด CLI ทั้งกรณีสำเร็จและกรณีผิดแล้ว ผลเป็นไปตามที่ควร

ฉันอ่านสกิล `solve-py-contract` ใน `./skills` ก่อนเริ่ม และทำตามนั้น ได้แก่ ตรวจอินพุตแล้ว raise `ValueError`, มีบล็อก CLI อ่าน JSON จาก stdin และมีไฟล์ทดสอบ

**วิธีคิดค่าส่ง**
- คิดเป็นสตางค์ด้วย `Fraction` แล้วปัดเศษครั้งเดียวตอนท้ายแบบปัดครึ่งขึ้น ผลที่คืนเป็น `int`
- ส่วนที่เกิน 5,000 กรัมคิด 1.5 สตางค์ต่อกรัม ตามสัดส่วน 15 บาทต่อกิโลกรัม
- ระยะทางเกิน 100 กม. คูณ 1.2 ส่วนส่งด่วนคูณ 1.5 ต่อจากนั้น
- ระยะทางพอดี 100 กม. ไม่คิดเพิ่ม เพราะโจทย์บอกว่า "เกิน 100"

**การตรวจอินพุต**
- `weight_g` ต้องเป็น `int` ในช่วง 1–30,000 โดย float และ bool ถูกปฏิเสธ
- `distance_km` เป็น `int` หรือ `float` ที่ไม่น้อยกว่า 0 และไม่รับ bool, nan หรือ inf
- `express` ต้องเป็น `bool`

**CLI:** สำเร็จได้ `{"ok": true, "result": ...}` และ exit 0 ส่วนอินพุตผิดได้ `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback

ข้อสมมติที่ฉันเลือกเองคือให้ `distance_km` เป็นทศนิยมได้ เพราะโจทย์ไม่ได้ระบุชนิด
