---
name: cafe_solve_contract
description: เช็กลิสต์และโค้ดแม่แบบสำหรับงานเขียน solve.py คิดเงินของ BaanKafe (ปัดเศษ half up ครั้งเดียว, validate ด้วย ValueError, CLI stdin JSON, test_solve.py)
---

# cafe_solve_contract

## When to Apply
- งานที่ให้เขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืน ใน `solve.py` ที่รับค่าเป็นสตางค์และคืนจำนวนเต็มสตางค์
- ใช้ทุกครั้งแม้โจทย์ไม่พูดถึง CLI, การ validate หรือไฟล์ทดสอบ เพราะตัวตรวจตรวจสิ่งเหล่านี้เสมอ

## When NOT to Apply
- งานที่ไม่เกี่ยวกับการคำนวณเงิน หรือไม่ได้ให้เขียน `solve.py`

## Instructions

### 1. การปัดเศษ
- ปัดแบบ half up เท่านั้น ห้ามใช้ `//` (floor) ห้ามใช้ `round()` ห้ามใช้ float
- ปัดเศษ **ครั้งเดียวตอนท้าย** ห้ามปัดทุกขั้น: เก็บค่ากลางเป็น `Fraction` หรือเก็บเป็นตัวเศษ/ตัวส่วนจำนวนเต็มที่ยังไม่หาร แล้วค่อยปัดเมื่อได้ผลสุดท้าย
- ถ้ามีเพดาน (cap) หรือขั้นต่ำ ให้ปัดก่อนแล้วจึงเทียบเพดาน
- ถ้าต้องเทียบเกณฑ์ (เช่น ยอดตั้งแต่ X ขึ้นไป) ให้เทียบด้วยค่าที่ยังไม่ปัด
- สูตร half up จากเศษส่วน n/d (n,d จำนวนเต็มไม่ติดลบ): `(2*n + d) // (2*d)`
- ส่วนที่ต้อง "แบ่งเศษให้คนแรก ๆ คนละ 1 สตางค์" ใช้ `divmod` ได้ แต่ยอดรวมที่นำไปหารต้องปัด half up ก่อน (ถ้าโจทย์มีขั้นที่เป็นเศษส่วน เช่น เปอร์เซ็นต์)
- ตัวอย่าง:
```python
from fractions import Fraction
def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)
# อัตรา 2.5% -> Fraction(25, 1000); ลด 5% -> Fraction(95, 100); คูณต่อกันได้เลยโดยไม่ปัดระหว่างทาง
```

### 2. Validate ทุกพารามิเตอร์ แล้ว raise ValueError อย่างเดียว (ห้าม TypeError)
- ก่อนคำนวณ ตรวจ **ทุกตัว** รวมสมาชิกใน list/dict
```python
def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v
def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v
```
- ปฏิเสธ float (แม้ 4500.0), bool ในช่องตัวเลข, None, str, และ int ในช่อง flag
- ช่วงค่าให้ดึงจากโจทย์ทุกคำ เช่น "ตั้งแต่ 1", "0–100", "1–30,000" ถ้าขอบเขตผิดต้อง raise ไม่ใช่คืน 0
- ค่าชุดปิด (เช่น tier) ต้องเป็น `str` และอยู่ในชุดที่โจทย์ระบุเป๊ะ ๆ ไม่ normalize ตัวพิมพ์
- list ต้องเป็น `list`, แต่ละตัวเป็น `dict` ที่มี key ครบ ไม่ใช้ `int(x)`/`float(x)` แปลงเงียบ ๆ

### 3. CLI ท้าย solve.py (ตัวตรวจรัน `python solve.py` ส่ง JSON ทาง stdin)
- key ใน JSON คือชื่อพารามิเตอร์ของฟังก์ชัน; ห้ามมี `print` ตัวอย่าง/demo ใน `__main__`
```python
import sys, json
def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = FUNC(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0
if __name__ == "__main__":
    sys.exit(main())
```
- แทน `FUNC` ด้วยชื่อฟังก์ชันที่โจทย์กำหนด สำเร็จ: stdout บรรทัดเดียว exit 0; ผิด: `{"ok": false, ...}` exit 2 ไม่มี traceback

### 4. สร้าง test_solve.py ข้าง solve.py ทุกครั้ง
- ใช้ `unittest` มี `from solve import FUNC` และอย่างน้อย: เคสปกติ, ขอบเขตของเกณฑ์ (ค่าก่อน/ที่/หลังเกณฑ์), เคสเศษ .5 พอดีที่ต้องปัดขึ้น, เคสหลายขั้นตอนที่ปัดครั้งเดียว, `assertRaises(ValueError)` สำหรับ float/bool/str/None/ค่านอกช่วงของทุกพารามิเตอร์, และ CLI ผ่าน `subprocess.run([sys.executable, "solve.py"], input=..., capture_output=True, text=True)` ทั้ง exit 0 และ exit 2
- ค่าคาดในเทสต์ต้องคำนวณด้วยมือ/`Fraction` แยกจากโค้ด ไม่ใช่คัดลอกผลจากฟังก์ชัน
- รันจากโฟลเดอร์งาน: `python3 -m unittest -v` (ห้ามใช้ `python3 -I` เพราะ import solve ไม่เจอ) แก้จนผ่านก่อนจบ

### 5. เช็กลิสต์ก่อนจบ
- [ ] ไม่มี `//` หรือ `round()` ในขั้นคำนวณเงิน (ยกเว้นสูตร half up และ divmod แบ่งหาร)
- [ ] ปัดครั้งเดียวตอนท้าย ก่อนเทียบเพดาน
- [ ] ทุกพารามิเตอร์ถูก validate และ raise เฉพาะ ValueError
- [ ] `echo '<json ตัวอย่าง>' | python3 solve.py; echo $?` ได้ผลลัพธ์ JSON exit 0 และอินพุตผิดได้ exit 2
- [ ] มี `test_solve.py` และ `python3 -m unittest` ผ่าน
