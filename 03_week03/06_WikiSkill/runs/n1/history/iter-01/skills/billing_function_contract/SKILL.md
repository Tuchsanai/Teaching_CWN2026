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

## 2. ตรวจอินพุตก่อนคำนวณ แล้ว raise ValueError เท่านั้น
- ตัวเลขทุกตัวที่ควรเป็น int ต้องเป็น `int` จริง: `type(x) is int` ปฏิเสธ float (เช่น `4500.0`), str, None และ bool ทั้งหมดด้วย `ValueError`
- พารามิเตอร์แบบ flag (member, birthday, express) ต้องเป็น `bool` จริง ถ้าไม่ใช่ให้ raise `ValueError`
- ค่านอกช่วงที่โจทย์กำหนด raise `ValueError` เช่น qty < 1, people < 1, น้ำหนักนอกช่วง, ค่าติดลบ, tip นอก 0–100
- ค่าที่ไม่อยู่ในรายการ (เช่น tier ที่ไม่รู้จัก) หรือ items ที่ไม่ใช่ list ของ dict ที่มี key ครบ ต้อง raise `ValueError`
- ตรวจทุกอย่างก่อนหาร ห้ามให้ `ZeroDivisionError`, `TypeError` หรือ `KeyError` หลุดออกมา
- ถ้าราคา/จำนวนในรายการเป็น float ให้ปฏิเสธเช่นกัน

```python
def _int(x, name, lo=None, hi=None):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"{name} out of range")
    return x

def _bool(x, name):
    if type(x) is not bool:
        raise ValueError(f"{name} must be a boolean")
    return x
```

## 3. CLI ท้าย solve.py
ชื่อ key ใน JSON คือชื่อพารามิเตอร์ของฟังก์ชัน ผลลัพธ์พิมพ์ JSON บรรทัดเดียวทาง stdout
- สำเร็จ: `{"ok": true, "result": <ค่าที่ฟังก์ชันคืน>}` และ exit 0
- ผิดพลาด: `{"ok": false, "error": "<ข้อความ>"}` และ exit 2 ห้ามมี traceback
- JSON พัง, key ขาด หรือ ValueError ทุกกรณี ให้ไปทางผิดพลาด

```python
if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = FUNC(**data)          # เปลี่ยน FUNC เป็นชื่อฟังก์ชันของโจทย์
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
```

## 4. เขียน test_solve.py ไว้ข้าง solve.py
ใช้ `unittest` หรือ `pytest` ที่รันได้เอง ต้องมีอย่างน้อย: กรณีทั่วไป, ค่าขอบ (พอดีเกณฑ์ ±1), เศษที่ลงท้าย .5 ต้องปัดขึ้น, `assertRaises(ValueError)` สำหรับค่านอกช่วง, float และ bool

## 5. ก่อนจบงาน ต้องรันจริง
- `python3 -m unittest test_solve` (หรือ pytest) ต้องผ่าน
- `echo '<json ปกติ>' | python3 solve.py` ต้องได้ ok true และ exit 0
- `echo '<json ค่าผิด>' | python3 solve.py; echo $?` ต้องได้ ok false และ exit 2
