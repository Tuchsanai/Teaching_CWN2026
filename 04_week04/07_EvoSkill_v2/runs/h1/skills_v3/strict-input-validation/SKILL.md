---
name: strict-input-validation
description: ใช้เมื่อเขียนฟังก์ชันที่รับ input ซึ่งโจทย์กำหนดชนิดหรือช่วงค่า (จำนวนเต็ม, True/False, ค่าที่เลือกได้เฉพาะบางค่า, รายการของ dict, ช่วงตัวเลข) เพื่อปฏิเสธ input ที่ผิดด้วย ValueError แทนการแปลงค่าเงียบ ๆ
---

# ตรวจ input แบบเข้มงวด

## หลักการ

- ถ้า input ไม่ตรงกับที่โจทย์กำหนด ให้ **ปฏิเสธ** ไม่ใช่พยายามแปลงให้ใช้ได้
- **ห้าม** แปลงค่าเพื่อความสะดวก: `int(x)`, `float(x)`, `str(x)`, `Fraction(str(x))`, `.strip()`, `.lower()` ทำให้ `4500.0`, `"2"`, `" Gold "` ผ่านไปเงียบ ๆ ซึ่งผิดสัญญาของฟังก์ชัน
- ใช้ **ValueError** กับ input ผิดทุกกรณี รวมถึงชนิดผิด ไม่ใช้ TypeError เพราะผู้ตรวจคาดหวัง ValueError
- `bool` เป็นลูกของ `int` ใน Python: `isinstance(True, int)` ได้ True จึงต้องใช้ `type(x) is int` และตรวจ bool แยกต่างหาก
- พารามิเตอร์ที่เป็น flag (เช่น member, express, birthday) ต้องเป็น `bool` จริงเท่านั้น ค่าอย่าง `1`, `0`, `None`, `"yes"` ต้องถูกปฏิเสธ
- **กฎ float:** พารามิเตอร์ตัวเลขรับเฉพาะ `int` เสมอ เว้นแต่โจทย์เขียนชัดว่ารับทศนิยมหรือเศษส่วน (เช่น "ทศนิยม", "ตัวเลขใดก็ได้", "เศษกิโลเมตร") ถ้าโจทย์ไม่ได้เขียนแบบนั้น ให้ปฏิเสธ float ทั้งหมด แม้ค่าจะเป็นจำนวนเต็มในรูปทศนิยม (`1000.0`) หรือดูสมเหตุสมผล (`100.5`)
- ห้ามเขียนตัวตรวจแบบ `isinstance(x, (int, float))`, `Fraction(str(x))` หรือ `Decimal(str(x))` กับพารามิเตอร์ที่ควรเป็น int เพราะจะรับ float ให้โดยปริยาย- ค่า key ที่ขาดหายใน dict ต้องกลายเป็น ValueError ไม่ใช่ KeyError: ใช้ `item.get("price")` แล้วให้ตัวตรวจ type จับ None
- ตรวจ input **ก่อน** คำนวณ ไม่คืนผลลัพธ์บางส่วน

## รูปแบบโค้ดตรวจ

```python
def require_int(value, name, low=None, high=None):
    if type(value) is not int:          # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value

def require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value

def require_choice(value, name, choices):
    if type(value) is not str or value not in choices:   # ไม่ normalize
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value

def require_list_of_dicts(value, name):
    if type(value) is not list:
        raise ValueError(f"{name} ต้องเป็น list")
    for entry in value:
        if type(entry) is not dict:
            raise ValueError(f"แต่ละรายการใน {name} ต้องเป็น dict")
    return value
```

ใช้ตัวช่วยเหล่านี้กับทุกพารามิเตอร์ในฟังก์ชันหลัก ก่อนบรรทัดคำนวณแรก

## การแปลงช่วงจากโจทย์เป็นเงื่อนไข

| ข้อความในโจทย์ | เงื่อนไข |
|---|---|
| ตั้งแต่ X ขึ้นไป / ไม่น้อยกว่า X | `value >= X` |
| เกิน X | `value > X` |
| ไม่เกิน X | `value <= X` |
| ต่ำกว่า X | `value < X` |
| ช่วง A–B | `A <= value <= B` |

ถ้าโจทย์ระบุว่า "ตั้งแต่ 0" ค่า 0 ต้องผ่าน ถ้า "ตั้งแต่ 1" ค่า 0 ต้องถูกปฏิเสธ

## Checklist ของ input

- [ ] ทุกพารามิเตอร์ตรวจ type ด้วย `type(x) is ...`
- [ ] bool ถูกปฏิเสธในพารามิเตอร์ที่เป็นตัวเลข
- [ ] float ที่ค่าเป็นจำนวนเต็ม (เช่น `1000.0`) ถูกปฏิเสธ ถ้าโจทย์บอกว่าเป็นจำนวนเต็ม
- [ ] string ที่หน้าตาเป็นตัวเลข (เช่น `"2"`) ถูกปฏิเสธ
- [ ] ค่าที่เลือกได้เฉพาะบางค่า ถูกเทียบแบบตรงตัว (ไม่ lower/strip)
- [ ] ค่าที่ขอบของช่วง (min, max) ผ่าน และค่าที่ออกไปนอกช่วง (min-1, max+1) ถูกปฏิเสธ
- [ ] ทุกกรณีผิดคือ `ValueError` (ไม่ใช่ TypeError, KeyError หรือ AttributeError)
