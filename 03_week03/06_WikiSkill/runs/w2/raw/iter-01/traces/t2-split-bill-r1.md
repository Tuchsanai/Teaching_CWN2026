# Trace t2-split-bill-r1 · iteration 1

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
/workspace/wklab/suite/runs/w2-k01-train/t2-split-bill-r1/sandbox/solve.py
def split_bill(total, people, tip_percent):
    # ยอดรวมทิป (สตางค์) ปัดเศษครึ่งขึ้นด้วยเลขจำนวนเต็มล้วน
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/suite/runs/w2-k01-train/t2-split-bill-r1/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

**Agent พูด:** สร้าง `solve.py` พร้อมฟังก์ชัน `split_bill` แล้ว แต่ยังไม่ได้รันทดสอบ ในโฟลเดอร์ `./skills` ไม่มีสกิลให้ทำตาม

- **ยอดรวม:** คำนวณเป็น `total × (100 + tip_percent) / 100` ด้วยเลขจำนวนเต็มล้วน
- **เศษสตางค์ของทิป:** โจทย์ไม่ได้บอกว่าต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น เช่น `total=101`, `tip_percent=5` ได้ 106.05 แล้วปัดเป็น 106 ถ้าต้องการปัดแบบอื่น แก้ที่บรรทัดคำนวณ `grand` ได้
- **การหาร:** ใช้ `divmod(grand, people)` ได้ฐานคนละเท่ากัน แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ตามจำนวนเศษที่เหลือ
- **ผลลัพธ์:** list จำนวนเต็มสตางค์ เรียงตามลำดับคน และผลรวมเท่ากับยอดรวมทิปพอดี

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` พร้อมฟังก์ชัน `split_bill` แล้ว แต่ยังไม่ได้รันทดสอบ ในโฟลเดอร์ `./skills` ไม่มีสกิลให้ทำตาม

- **ยอดรวม:** คำนวณเป็น `total × (100 + tip_percent) / 100` ด้วยเลขจำนวนเต็มล้วน
- **เศษสตางค์ของทิป:** โจทย์ไม่ได้บอกว่าต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น เช่น `total=101`, `tip_percent=5` ได้ 106.05 แล้วปัดเป็น 106 ถ้าต้องการปัดแบบอื่น แก้ที่บรรทัดคำนวณ `grand` ได้
- **การหาร:** ใช้ `divmod(grand, people)` ได้ฐานคนละเท่ากัน แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ตามจำนวนเศษที่เหลือ
- **ผลลัพธ์:** list จำนวนเต็มสตางค์ เรียงตามลำดับคน และผลรวมเท่ากับยอดรวมทิปพอดี
