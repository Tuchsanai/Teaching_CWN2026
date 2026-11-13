---
name: billing-function-spec
description: ใช้เมื่อโจทย์ให้เขียนฟังก์ชัน Python คำนวณเงิน/ราคา/ค่าส่ง/ส่วนลด/เงินคืน/หารบิล (หน่วยสตางค์ ใน solve.py) — บอกกติกาที่โจทย์ไม่ได้เขียนแต่ตัวตรวจเช็คเสมอ คือ การปัดเศษ half-up, เลขแม่นยำด้วย Fraction, การตรวจ input แล้ว raise ValueError
---

# เขียนฟังก์ชันคิดเงินให้ผ่านตัวตรวจ

ตัวตรวจของโจทย์กลุ่มนี้ทดสอบ 4 หมวด: ปกติ · ขอบเขต · ไม่คลาดเคลื่อน (no-drift = เศษสตางค์/ปัดเศษ) · ปฏิเสธ input ผิด (`ValueError`)
Solver ที่เขียนแค่ตามตัวอักษรของโจทย์ได้แค่ ~0.5 เพราะพลาด 2 หมวดหลัง ซึ่งโจทย์ไม่ได้บอกตรง ๆ

## กฎที่ต้องทำทุกครั้ง

1. **ปัดเศษแบบ half-up (ปัดครึ่งขึ้น) ครั้งเดียวตอนท้ายสุด** — ห้ามใช้ `//` ปัดลง, ห้าม `round()` ของ Python (เป็น banker's rounding), ห้าม float
   - ถ้าโจทย์ไม่ระบุวิธีปัด ให้ใช้ half-up เสมอ ห้ามเลือกปัดลงเอง และห้ามจบด้วยการถามผู้ใช้ — ตัดสินใจเอง
   - ห้ามปัดกลางทาง (เช่น ปัดทิป/ส่วนลดแยกก่อนแล้วค่อยบวก) ให้คำนวณทั้งสายด้วย `Fraction` แล้วปัดครั้งเดียว
   - ถ้าโจทย์มีหลายขั้นที่ "คูณต่อจากข้อก่อน" ให้คูณเป็น Fraction ต่อกันตามลำดับในโจทย์
2. **ใช้ `fractions.Fraction`** สำหรับเปอร์เซ็นต์ทุกตัว: 5% = `Fraction(95,100)` ฯลฯ
   ```python
   from fractions import Fraction
   def half_up(x):  # x >= 0
       return int((Fraction(x) * 2 + 1) // 2)
   ```
3. **ตรวจ input ทุกพารามิเตอร์ก่อนคำนวณ แล้ว `raise ValueError`** (อย่าให้เป็น TypeError/AttributeError/KeyError):
   - จำนวนเต็ม: ต้องเป็น `type(v) is int` เท่านั้น → `10000.0` (float), `'3'` (str), `True/False` (bool) ต้องถูกปฏิเสธ
   - ตรวจช่วงตามโจทย์: "ตั้งแต่ 0" → `>= 0`, "ตั้งแต่ 1" → `>= 1`, "1–30,000" → ช่วงปิดทั้งสองด้าน, "0–100" เช่นกัน ค่าติดลบต้อง raise
   - bool (เช่น `member`, `express`, `birthday`): ต้อง `type(v) is bool`
   - enum/สตริง (เช่น tier): ต้องเป็น `str` และอยู่ในชุดที่อนุญาต ไม่งั้น raise
   - list/dict: ตรวจ `type(items) is list`, แต่ละ item เป็น dict, มี key ครบ และค่าในแต่ละ key ตรวจแบบ int + ช่วง (เช่น qty ≥ 1, price ≥ 0); ต้องไม่ใช้ `item["x"]` ตรง ๆ ที่อาจเกิด KeyError — ใช้ `.get` แล้วตรวจ
   - ค่าที่โจทย์ไม่ได้ระบุช่วงเอง (เช่น distance ≥ 0) ก็ยังต้องตรวจ int + ช่วงที่บอก
4. **เกณฑ์ขอบเขต** ให้อ่านคำให้ตรง: "ตั้งแต่ X ขึ้นไป" = `>= X`, "ต่ำกว่า X" = `< X` (ได้ 0), "ไม่เกิน X" = `<= X`, "เกิน X" = `> X`, "สูงสุด X" = `min(X, ...)` ใช้หลังคูณทุกอย่างแล้ว
   - เกณฑ์ของยอดอิงยอด "ก่อน" ส่วนลดขั้นถัดไป (เช่น ยอดรวม ≥ 500 บาท วัดจากยอดรวมสินค้า ไม่ใช่หลังลด)
   - หน่วย: บาท→สตางค์ ×100 เสมอ (500 บาท = 50000)
5. **แปลงโจทย์เป็นเลขแล้วรันทดสอบเองก่อนจบ** — เขียนเทสเล็ก ๆ (unittest หรือ assert) อย่างน้อย:
   - กรณีปกติ 1–2 ข้อ คำนวณมือเทียบ
   - ค่าที่ขอบ (X-1, X, X+1)
   - กรณีที่ทำให้เกิดเศษครึ่งสตางค์ (เช่น ผลคูณลงท้าย .5) เพื่อเช็ค half-up
   - ข้อ reject: ค่าติดลบ, 0 (เมื่อต้อง ≥1), float, str, bool, tier ผิด
   อย่าจบด้วยคำว่า "ยังไม่ได้ทดสอบ"
   - รันเทสจากโฟลเดอร์ที่มี `solve.py` ด้วย `PYTHONPATH=. python3 ...` (อย่าใช้ `python3 -I` เพราะจะ import solve ไม่เจอ)
   - ก่อนจบ ให้ทบทวนโจทย์ทีละบรรทัดอีกครั้งว่าทุกประโยค (เกณฑ์ ขั้นลด เพดาน หน่วย) ถูกแปลงเป็นโค้ดครบ และชื่อฟังก์ชัน/ลำดับพารามิเตอร์ตรงตามโจทย์ทุกตัวอักษร

## ส่งมอบไฟล์เทสต์ไปด้วย (สำคัญ)

เฉลยอ้างอิงของโจทย์กลุ่มนี้มี **2 ไฟล์**: `solve.py` และ `test_solve.py` — อย่าเขียนเทสแบบรันแล้วทิ้งในคำสั่ง shell
- สร้าง `test_solve.py` ในโฟลเดอร์เดียวกับ `solve.py` (ใช้ `unittest`, `from solve import <ชื่อฟังก์ชัน>`) แยกคลาสเป็น 4 หมวด: `Normal` · `Boundary` · `NoDrift` · `Reject` อย่างน้อยหมวดละ 2–3 เคส โดยค่าที่คาดหวังต้องคำนวณมือ/ด้วย Fraction ไม่ใช่ copy ผลจากโค้ดตัวเอง
- รันด้วย `PYTHONPATH=. python3 -m unittest -q test_solve` ให้ผ่านทั้งหมดก่อนจบ
- ทดสอบทาง CLI ด้วย 1 ครั้ง: `echo '{...}' | python3 solve.py` ทั้งกรณี ok และกรณี error (exit code 2) แล้วรายงานตามจริงในสรุปท้าย
- ห้ามทิ้งไฟล์ขยะอื่น (เช่น `__pycache__` ไม่เป็นไร แต่ไม่ต้องมีสคริปต์ชั่วคราว)

## รูปแบบไฟล์ solve.py

- มีฟังก์ชันชื่อตามโจทย์ใน `solve.py` ที่ระดับ module (import ได้: `from solve import fn`) คืนค่าเป็น `int` (ไม่ใช่ Fraction/float); หารบิลคืน `list[int]`
- ควรเพิ่ม `main()` อ่าน JSON object จาก stdin → เรียกฟังก์ชันด้วย `**args` → พิมพ์ `{"ok": true, "result": ...}` หรือเมื่อ ValueError/TypeError พิมพ์ `{"ok": false, "error": ...}` และ exit code 2 (ห่อด้วย `if __name__ == "__main__": sys.exit(main())`) — ไม่เสียหายถ้าตัวตรวจเรียกผ่าน CLI

## แม่แบบ

```python
import json, sys
from fractions import Fraction

def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)

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

def fn(...):
    # 1) validate ทุก arg  2) คำนวณด้วย Fraction ต่อเนื่อง  3) return half_up(...)
    ...

def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = fn(**args)
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)})); return 2
    print(json.dumps({"ok": True, "result": result})); return 0

if __name__ == "__main__":
    sys.exit(main())
```

## เรื่องที่ต้องคิดเฉพาะโจทย์

- หารบิลแบบ "คนแรก ๆ จ่ายเพิ่ม 1 สตางค์": `base, extra = divmod(grand, n)` → `[base+1]*extra + [base]*(n-extra)` และ grand = half_up(total*(100+tip)/100) ผลรวมของ list ต้องเท่ากับ grand เสมอ
- ค่าส่งตามสัดส่วนกรัม: ใช้ Fraction(1500*(w-5000), 1000) ไม่ปัดก่อนคูณตัวคูณระยะทาง/ด่วน
- เงินคืน: ยอดต่ำกว่าเกณฑ์ → 0 ก่อน; คูณอัตรา → ×2 ถ้า birthday → half_up → `min(เพดาน, ...)`
- ส่วนลดหลายชั้น: ลดตามลำดับในโจทย์ แล้ว VAT เป็นขั้นสุดท้าย ปัดครั้งเดียว
