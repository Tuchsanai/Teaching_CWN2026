---
name: baankafe-strict-validation
description: ใช้ทุกครั้งที่เขียนฟังก์ชันคิดเงิน/ราคา/ค่าส่ง/ส่วนลด/หารบิล/เงินคืนใน solve.py ตัวตรวจจะลองส่งอินพุตผิดชนิดและนอกช่วงเข้ามา ฟังก์ชันต้อง raise ValueError ให้ครบ
---

# ตรวจอินพุตให้เข้มก่อนคำนวณ (จุดที่เสียคะแนนมากที่สุด)

ใน epoch 0 สูตรคำนวณถูกเกือบทุกข้อ แต่ได้คะแนนแค่ ~0.5 เพราะ **ไม่มีการตรวจอินพุต** ตัวตรวจมีกลุ่มเทสต์ "reject" ที่คาดหวัง `ValueError` เสมอ แม้โจทย์ไม่ได้สั่งให้ตรวจก็ตาม

## กฎ
1. **ตรวจทุกพารามิเตอร์ ก่อนคำนวณอะไรทั้งสิ้น** และ raise `ValueError` (ไม่ใช่ TypeError/AssertionError/คืน None/คืน 0)
2. **ชนิดต้องเป๊ะ**: จำนวนเต็มให้ตรวจ `type(v) is int` — ห้ามใช้ `isinstance(v, int)` เพราะ `True`/`False` จะผ่าน
   - ปฏิเสธ `float` (แม้ `1000.0`), `str` (`'3'`), `None`, `bool` ในช่องที่ต้องเป็น int
   - ช่อง True/False ให้ตรวจ `type(v) is bool` (ปฏิเสธ 0/1/'yes')
   - ช่อง enum (เช่น tier) ให้ตรวจ `type(v) is str and v in ALLOWED` — ค่าที่ไม่อยู่ในรายการ (เช่น `'bronze'`, ตัวพิมพ์ใหญ่ผิด) = ValueError
3. **ช่วงค่า** ตามที่โจทย์เขียน เช่น "ตั้งแต่ 0" → `>= 0`, "ตั้งแต่ 1" → `>= 1`, "0–100" → `0 <= v <= 100`, "1–30,000" → ปฏิเสธ 0 และ 30001 ระวังให้ครบทั้งขอบล่างและบน
4. **โครงสร้างซ้อน** (เช่น list ของ dict): ตรวจว่า `type(items) is list`, แต่ละตัว `type(it) is dict`, มี key ครบ (ขาด key = ValueError ไม่ใช่ KeyError), ตรวจ field แต่ละตัวด้วยกฎข้อ 2–3 ในทุกรายการ
   - list ว่างให้ถือว่าถูกต้อง (ยอด 0) เว้นแต่โจทย์ห้าม
5. ตรวจ**ก่อน**ทุกกรณีพิเศษ/early return (เช่น ยอดต่ำกว่าเกณฑ์แล้วคืน 0) — อินพุตผิดต้อง error แม้อยู่ในเงื่อนไขที่จะคืน 0

## แม่แบบ helper (วางไว้ใน solve.py)
```python
def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v

def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v
```

## ก่อนส่งงาน ทดสอบเอง
รัน (ใช้ `PYTHONPATH=.` — `python3 -I` จะ import solve ไม่เจอ) ด้วยอินพุตเหล่านี้แล้วยืนยันว่าได้ ValueError: ค่าติดลบ, 0 ในช่องที่ต้อง ≥1, เกินขอบบน, `1000.0`, `'1000'`, `True` ในช่อง int, `1` ในช่อง bool, enum แปลก, item ขาด key
