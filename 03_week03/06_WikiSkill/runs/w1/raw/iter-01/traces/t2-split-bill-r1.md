# Trace t2-split-bill-r1 · iteration 1

- ผล: **FAIL** · คะแนน 0.40 (ผ่าน 4 จาก 10 ข้อตรวจ)
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
- ✗ `half_up`: split_bill(1010, 1, 5) คาด [1061] ได้ [1060] · พลาด 3 จาก 3 กรณี
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
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
ls: cannot access './skills': No such file or directory
```

### ขั้น 2 · Bash

```
cat > solve.py <<'E'
def split_bill(total, people, tip_percent):
    grand = total + total * tip_percent // 100  # ทิปปัดเศษลงเป็นสตางค์เต็ม
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
E
python3 -I -c "from solve import split_bill as s;print(s(1000,3,10),s(0,2,0))" 2>&1 || python3 -c "from solve import split_bill as s;print(s(1000,3,10),s(0,2,0))"
```

ผลที่ได้:

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'solve'
[367, 367, 366] [0, 0]
```

**Agent พูด:** บันทึก `solve.py` แล้ว (ไม่มีโฟลเดอร์ `./skills` จึงไม่มีสกิลให้อ่าน) ฟังก์ชันผ่านการทดลองรัน 2 กรณี:

- `split_bill(1000, 3, 10)` ได้ `[367, 367, 366]`
- `split_bill(0, 2, 0)` ได้ `[0, 0]`

```python
def split_bill(total, people, tip_percent):
    grand = total + total * tip_percent // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
```

โจทย์ไม่ได้บอกว่าให้ปัดเศษทิปอย่างไรเมื่อทิปไม่เป็นสตางค์เต็ม ผมเลือกปัดลง เช่น ทิป 10% ของ 1005 สตางค์ได้ 100 สตางค์ ถ้าต้องการปัดแบบอื่น แก้ได้ที่บรรทัดคำนวณ `grand` บรรทัดเดียว

## คำตอบสุดท้ายของ Agent

บันทึก `solve.py` แล้ว (ไม่มีโฟลเดอร์ `./skills` จึงไม่มีสกิลให้อ่าน) ฟังก์ชันผ่านการทดลองรัน 2 กรณี:

- `split_bill(1000, 3, 10)` ได้ `[367, 367, 366]`
- `split_bill(0, 2, 0)` ได้ `[0, 0]`

```python
def split_bill(total, people, tip_percent):
    grand = total + total * tip_percent // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
```

โจทย์ไม่ได้บอกว่าให้ปัดเศษทิปอย่างไรเมื่อทิปไม่เป็นสตางค์เต็ม ผมเลือกปัดลง เช่น ทิป 10% ของ 1005 สตางค์ได้ 100 สตางค์ ถ้าต้องการปัดแบบอื่น แก้ได้ที่บรรทัดคำนวณ `grand` บรรทัดเดียว
