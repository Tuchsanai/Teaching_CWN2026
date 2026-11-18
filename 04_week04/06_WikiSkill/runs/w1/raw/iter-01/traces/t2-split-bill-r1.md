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
/workspace/wklab/runs/w1/rollouts/runs/k01-train/trials/t2-split-bill-r1/sandbox/solve.py
def split_bill(total, people, tip_percent):
    # ยอดรวมหลังบวกทิป (จำนวนเต็มสตางค์, ปัดครึ่งขึ้น ด้วยเลขจำนวนเต็มล้วน)
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/runs/w1/rollouts/runs/k01-train/trials/t2-split-bill-r1/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

**Agent พูด:** สร้างไฟล์ `solve.py` ที่มีฟังก์ชัน `split_bill` แล้ว แต่ยังไม่ได้รันทดสอบ ใน `./skills` ไม่มีสกิล จึงเริ่มเขียนได้เลย

ฟังก์ชันคิดยอดรวมเป็น `total * (100 + tip_percent) / 100` แล้วหารเท่ากันทุกคน เศษที่เหลือให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ ผลลัพธ์เป็น list ของจำนวนเต็มสตางค์ตามลำดับคน

โจทย์ไม่ได้บอกว่าทิปที่ได้เศษสตางค์ต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น เช่น บิล 1 สตางค์ ทิป 50% ได้ 1.5 ปัดเป็น 2 ถ้าต้องการปัดลง ให้เปลี่ยน `+ 50` เป็น `+ 0` ในบรรทัดที่คำนวณ `grand`

## คำตอบสุดท้ายของ Agent

สร้างไฟล์ `solve.py` ที่มีฟังก์ชัน `split_bill` แล้ว แต่ยังไม่ได้รันทดสอบ ใน `./skills` ไม่มีสกิล จึงเริ่มเขียนได้เลย

ฟังก์ชันคิดยอดรวมเป็น `total * (100 + tip_percent) / 100` แล้วหารเท่ากันทุกคน เศษที่เหลือให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ ผลลัพธ์เป็น list ของจำนวนเต็มสตางค์ตามลำดับคน

โจทย์ไม่ได้บอกว่าทิปที่ได้เศษสตางค์ต้องปัดอย่างไร ผมเลือกปัดครึ่งขึ้น เช่น บิล 1 สตางค์ ทิป 50% ได้ 1.5 ปัดเป็น 2 ถ้าต้องการปัดลง ให้เปลี่ยน `+ 50` เป็น `+ 0` ในบรรทัดที่คำนวณ `grand`
