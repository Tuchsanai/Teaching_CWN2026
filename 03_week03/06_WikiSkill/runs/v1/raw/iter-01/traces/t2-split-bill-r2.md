# Trace t2-split-bill-r2 · iteration 1

- ผล: **FAIL** · คะแนน 0.50 (ผ่าน 5 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ไม่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล
- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)
- ยอดที่ต้องหาร = ยอดบิลบวกทิป
- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ
- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✗ `reject_value`: split_bill(10000, 0, 0) ต้อง raise ValueError แต่ raise ZeroDivisionError · พลาด 5 จาก 5 กรณี
- ✗ `reject_type`: split_bill(10000.0, 2, 0) ต้อง raise ValueError แต่คืนค่า [5000.0, 5000.0] · พลาด 4 จาก 4 กรณี
- ✗ `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- ✗ `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- ✗ `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1; ls
```

ผลที่ได้:

```
ls: cannot access './skills': No such file or directory
```

### ขั้น 2 · Write

```
/workspace/wklab/suite/runs/v1-k01-train/t2-split-bill-r2/sandbox/solve.py
def split_bill(total, people, tip_percent):
    # ทิป = total * tip_percent / 100 ปัดเศษครึ่งขึ้นเป็นสตางค์ (ใช้จำนวนเต็มล้วน ไม่มีปัญหา float)
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/suite/runs/v1-k01-train/t2-split-bill-r2/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

**Agent พูด:** สร้าง `solve.py` แล้ว แต่ยังไม่ได้รันทดสอบ ไม่มีโฟลเดอร์ `./skills` จึงไม่มีสกิลให้อ่านก่อนเริ่ม

- **ยอดที่หาร:** ยอดบิลบวกทิป
- **การหารไม่ลงตัว:** ใช้ `divmod` แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ ผลรวมที่คืนมาจึงเท่ากับยอดที่หารพอดี
- **การปัดทิป:** โจทย์ไม่ได้บอกว่าทิปที่เป็นเศษสตางค์ต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น (เช่น 1 สตางค์ × 50% = 0.5 → 1) ถ้าต้องการปัดลงหรือปัดขึ้นเสมอ บอกได้ แล้วผมจะแก้บรรทัดเดียว

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` แล้ว แต่ยังไม่ได้รันทดสอบ ไม่มีโฟลเดอร์ `./skills` จึงไม่มีสกิลให้อ่านก่อนเริ่ม

- **ยอดที่หาร:** ยอดบิลบวกทิป
- **การหารไม่ลงตัว:** ใช้ `divmod` แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ ผลรวมที่คืนมาจึงเท่ากับยอดที่หารพอดี
- **การปัดทิป:** โจทย์ไม่ได้บอกว่าทิปที่เป็นเศษสตางค์ต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น (เช่น 1 สตางค์ × 50% = 0.5 → 1) ถ้าต้องการปัดลงหรือปัดขึ้นเสมอ บอกได้ แล้วผมจะแก้บรรทัดเดียว
