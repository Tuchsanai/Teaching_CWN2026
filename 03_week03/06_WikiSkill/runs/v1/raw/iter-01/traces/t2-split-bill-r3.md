# Trace t2-split-bill-r3 · iteration 1

- ผล: **FAIL** · คะแนน 0.50 (ผ่าน 5 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/*.md 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 2
```

### ขั้น 2 · Write

```
/workspace/wklab/suite/runs/v1-k01-train/t2-split-bill-r3/sandbox/solve.py
def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (ปัดครึ่งขึ้นเป็นสตางค์เต็ม ด้วยเลขจำนวนเต็มล้วน)
    grand = total + (total * tip_percent + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/suite/runs/v1-k01-train/t2-split-bill-r3/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

**Agent พูด:** สร้าง `solve.py` แล้ว แต่ยังไม่ได้รันทดสอบ โฟลเดอร์ `./skills` ไม่มี จึงไม่มีสกิลให้ทำตาม

- ยอดที่ต้องหาร = `total` + ทิป โดยทิปคิดเป็นเลขจำนวนเต็มล้วน ไม่ใช้ทศนิยม
- หารด้วย `divmod` แล้วให้คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ตามเศษที่เหลือ
- ผลรวมของ list ที่คืนจึงเท่ากับยอดรวมพอดี

โจทย์ไม่ได้บอกว่าถ้าทิปเป็นเศษสตางค์ต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น เช่น `total=101`, `tip_percent=10` ได้ทิป 10.1 ซึ่งปัดเป็น 10 ถ้าต้องการปัดวิธีอื่น เช่น ปัดขึ้นเสมอหรือปัดลงเสมอ บอกได้ครับ

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` แล้ว แต่ยังไม่ได้รันทดสอบ โฟลเดอร์ `./skills` ไม่มี จึงไม่มีสกิลให้ทำตาม

- ยอดที่ต้องหาร = `total` + ทิป โดยทิปคิดเป็นเลขจำนวนเต็มล้วน ไม่ใช้ทศนิยม
- หารด้วย `divmod` แล้วให้คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ตามเศษที่เหลือ
- ผลรวมของ list ที่คืนจึงเท่ากับยอดรวมพอดี

โจทย์ไม่ได้บอกว่าถ้าทิปเป็นเศษสตางค์ต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น เช่น `total=101`, `tip_percent=10` ได้ทิป 10.1 ซึ่งปัดเป็น 10 ถ้าต้องการปัดวิธีอื่น เช่น ปัดขึ้นเสมอหรือปัดลงเสมอ บอกได้ครับ
