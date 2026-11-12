---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบทั้ง 4 ข้อด้านล่างทุกครั้ง แม้โจทย์ไม่สั่ง

## When NOT to Apply
- งานที่ไม่ใช่ฟังก์ชันคำนวณใน `solve.py` (เช่น แก้เอกสาร จัดรูปแบบข้อความ)
- ถ้าโจทย์ระบุวิธีปัด/รูปแบบ CLI/การ reject ไว้ชัดเจนและต่างจากนี้ ให้ทำตามโจทย์

## Instructions

### 1. ตรวจ input ที่ต้นฟังก์ชัน (ก่อนคำนวณ และก่อน early-return ทุกชนิด)
ตัวตรวจคาดว่าค่าผิดต้อง `raise ValueError` เสมอ ไม่ใช่คืนค่า 0 และไม่ใช่ `ZeroDivisionError`/`TypeError`/`KeyError`
- ตัวเลขทุกตัว: `type(x) is int` (ปฏิเสธ float เช่น `1000.0` และ `bool`)
- flag (member/express/birthday ฯลฯ): `type(x) is bool`
- ช่วงค่า: ตรวจทุกขอบเขตที่โจทย์ระบุ เช่น "ตั้งแต่ 0" -> `x >= 0`, "ตั้งแต่ 1" -> `x >= 1`, "1–30,000" -> `1 <= x <= 30000`, "0–100" -> `0 <= x <= 100`
- enum (tier ฯลฯ): ต้องอยู่ในชุดที่โจทย์กำหนด
- list ของ dict: ตรวจว่าเป็น `list`, แต่ละตัวเป็น `dict`, มี key ครบ, แต่ละฟิลด์ตรวจตามข้างบน
- ค่า 0 ที่ผิดช่วง (qty=0, people=0, weight=0) และค่าติดลบ ต้อง raise

```python
def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v
```

### 2. ปัดเศษ half-up ด้วยจำนวนเต็ม ครั้งเดียวตอนท้าย
- ห้ามใช้ float กับเงิน ห้ามใช้ `round()` ห้ามใช้ `//` ปัดลง (ถ้าโจทย์ไม่ระบุวิธีปัด ให้ถือว่า half-up)
- เก็บค่าเป็นเศษส่วน `n/d` (จำนวนเต็มบวก) แล้วปัดครั้งเดียว: `(2*n + d) // (2*d)`
- ขั้นตอนหลายชั้น (ลด %, VAT, คูณ) ให้คูณเศษส่วนต่อกันแล้วปัดทีเดียว ไม่ปัดระหว่างทาง ยกเว้นโจทย์สั่งให้ปัดเป็นขั้น
- เพดาน/ขั้นต่ำ ให้ดูโจทย์ว่าอยู่ก่อนหรือหลังปัด ถ้าเพดานเป็นจำนวนเต็มอยู่แล้ว ใช้ `min` กับค่าก่อนปัดหรือหลังปัดได้ผลเหมือนกัน
- ผลลัพธ์ต้องเป็น `int` ไม่ใช่ float

### 3. ต่อท้าย solve.py ด้วย CLI (ตัวตรวจรัน `python solve.py` ส่ง JSON ทาง stdin)
key ใน JSON ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์

```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = FUNC(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0

if __name__ == "__main__":
    sys.exit(_main())
```
- สำเร็จ: stdout `{"ok": true, "result": ...}` exit 0
- input ผิด: stdout `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback

### 4. สร้าง test_solve.py ข้าง solve.py แล้วรันจริง
- ใช้ `unittest` และ `from solve import FUNC`
- ครอบคลุม: กรณีปกติ · ค่าขอบพอดี (เช่น พอดีเกณฑ์ขั้นต่ำ/ขั้นบันได) · เศษ .5 พอดีที่ต้องปัดขึ้น · `assertRaises(ValueError)` สำหรับ ค่านอกช่วง, 0, ติดลบ, float, bool, enum ผิด
- **ตัวตรวจนับจำนวนเมธอด `def test_...` ต้องมีอย่างน้อย 6 เมธอด (ตั้งเป้า 8 ขึ้นไป)** ไม่ได้นับจำนวน assertion การรวม assertion หลายอย่างไว้ในเมธอดเดียวจะได้จำนวนไม่พอ
- เขียน 1 เมธอดต่อ 1 พฤติกรรม แยกเป็นอย่างน้อยดังนี้ (แต่ละข้อคือ 1 เมธอด):
  1. `test_normal` กรณีปกติ
  2. `test_boundary_lower` ขอบล่างพอดี (เช่น ค่าต่ำสุดที่อนุญาต หรือพอดีเกณฑ์ขั้นต่ำ)
  3. `test_boundary_upper` ขอบบน/ขั้นบันได/เพดานพอดี และค่าที่เกินไปนิดเดียว
  4. `test_half_up` เศษ .5 พอดีที่ต้องปัดขึ้น
  5. `test_reject_out_of_range` ค่านอกช่วง/0/ติดลบ -> `assertRaises(ValueError)`
  6. `test_reject_float` float -> `assertRaises(ValueError)`
  7. `test_reject_bool` bool -> `assertRaises(ValueError)`
  8. `test_reject_bad_enum_or_key` enum ผิด/key ขาด/ชนิด list-dict ผิด (ถ้าโจทย์ไม่มี ให้แยกกรณีปกติเพิ่มอีกเมธอด เช่น ค่ารวมหลายเงื่อนไขพร้อมกัน)
- ห้ามลบเทสต์ทิ้งเพื่อให้ผ่าน ถ้าลบต้องเพิ่มทดแทนให้จำนวนเมธอดไม่ลด
- ค่าที่คาดใน test ให้คำนวณด้วยมือจากโจทย์ ถ้า test ล้มให้ตรวจก่อนว่าผิดที่ solve.py หรือที่ค่าที่คาด แล้วแก้ฝั่งที่ผิดจริง (ห้ามแก้ solve.py ให้ตรงกับ test โดยไม่ดูโจทย์)
- รัน `python3 -m unittest -q` ต้องผ่านทั้งหมด และบรรทัด `Ran N tests` ต้อง N >= 6

### 5. ตรวจก่อนตอบ (ต้องรันจริง)
```
echo '<JSON กรณีปกติ>' | python3 solve.py; echo "exit=$?"   # ต้อง exit=0 และมี "ok": true
echo '<JSON กรณีผิด>'  | python3 solve.py; echo "exit=$?"   # ต้อง exit=2 และมี "ok": false ไม่มี Traceback
python3 -m unittest -q 2>&1 | grep -E "^Ran|OK|FAILED"
grep -c "def test_" test_solve.py   # ต้อง >= 6 (แนะนำ >= 8)
```
ห้ามรายงานว่าเสร็จถ้ายังไม่ได้รันทั้งหมดนี้ ถ้า `Ran N tests` ได้ N < 6 ให้แยกเมธอดเพิ่มก่อนตอบ ห้ามตอบทั้งที่ N < 6
