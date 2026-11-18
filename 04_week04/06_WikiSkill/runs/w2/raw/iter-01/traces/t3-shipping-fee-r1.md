# Trace t3-shipping-fee-r1 · iteration 1

- ผล: **FAIL** · คะแนน 0.45 (ผ่าน 5 จาก 11 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ไม่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ
- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน
- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
- คืนค่าส่ง เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✗ `reject_value`: shipping_fee(0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 4 จาก 4 กรณี
- ✗ `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 5 จาก 5 กรณี
- ✗ `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- ✗ `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- ✗ `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- ✗ `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls -R ./skills 2>/dev/null | head -50
```

ผลที่ได้:

```
(Bash completed with no output)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (1 baht = 100 satang)."""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang per 1000 g, prorated by gram
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return math.floor(fee + Fraction(1, 2))  # round half up, exact
EOF
python3 -c "
from solve import shipping_fee as f
print(f(500,0,False),f(5000,0,False),f(10000,101,True),f(5001,0,False))"
```

ผลที่ได้:

```
4000 8000 27900 8002
```

**Agent พูด:** สร้างไฟล์ `solve.py` แล้ว และไม่มีสกิลในโฟลเดอร์ `./skills` จึงเขียนตามโจทย์โดยตรง

ฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` คืนค่าส่งเป็นจำนวนเต็มสตางค์ (1 บาท = 100 สตางค์) ตามนี้:
- **ค่าส่งตามน้ำหนัก:**
  - ไม่เกิน 1,000 กรัม คิด 4,000 สตางค์
  - ไม่เกิน 5,000 กรัม คิด 8,000 สตางค์
  - เกิน 5,000 กรัม คิด 8,000 สตางค์ บวกส่วนที่เกิน กรัมละ 1.5 สตางค์ (กิโลกรัมละ 15 บาท คิดตามสัดส่วนกรัม)
- **ระยะทาง:** เกิน 100 กม. คูณ 1.2
- **ส่งด่วน:** คูณ 1.5 ต่อจากข้อก่อน
- **ปัดเศษ:** คำนวณด้วย `Fraction` เพื่อไม่ให้ทศนิยมคลาดเคลื่อน แล้วปัดครึ่งขึ้นเพียงครั้งเดียวตอนท้าย

ลองรันกับตัวอย่างสี่ค่า ได้ตามที่คำนวณด้วยมือ:

| weight_g | distance_km | express | ผลลัพธ์ (สตางค์) |
|---|---|---|---|
| 500 | 0 | False | 4000 |
| 5000 | 0 | False | 8000 |
| 5001 | 0 | False | 8002 (1.5 สตางค์ ปัดขึ้น) |
| 10000 | 101 | True | 27900 |

ยังไม่ได้ทดสอบกรณีขอบอื่น เช่น ระยะทางเท่ากับ 100 กม. พอดี

## คำตอบสุดท้ายของ Agent

สร้างไฟล์ `solve.py` แล้ว และไม่มีสกิลในโฟลเดอร์ `./skills` จึงเขียนตามโจทย์โดยตรง

ฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` คืนค่าส่งเป็นจำนวนเต็มสตางค์ (1 บาท = 100 สตางค์) ตามนี้:
- **ค่าส่งตามน้ำหนัก:**
  - ไม่เกิน 1,000 กรัม คิด 4,000 สตางค์
  - ไม่เกิน 5,000 กรัม คิด 8,000 สตางค์
  - เกิน 5,000 กรัม คิด 8,000 สตางค์ บวกส่วนที่เกิน กรัมละ 1.5 สตางค์ (กิโลกรัมละ 15 บาท คิดตามสัดส่วนกรัม)
- **ระยะทาง:** เกิน 100 กม. คูณ 1.2
- **ส่งด่วน:** คูณ 1.5 ต่อจากข้อก่อน
- **ปัดเศษ:** คำนวณด้วย `Fraction` เพื่อไม่ให้ทศนิยมคลาดเคลื่อน แล้วปัดครึ่งขึ้นเพียงครั้งเดียวตอนท้าย

ลองรันกับตัวอย่างสี่ค่า ได้ตามที่คำนวณด้วยมือ:

| weight_g | distance_km | express | ผลลัพธ์ (สตางค์) |
|---|---|---|---|
| 500 | 0 | False | 4000 |
| 5000 | 0 | False | 8000 |
| 5001 | 0 | False | 8002 (1.5 สตางค์ ปัดขึ้น) |
| 10000 | 101 | True | 27900 |

ยังไม่ได้ทดสอบกรณีขอบอื่น เช่น ระยะทางเท่ากับ 100 กม. พอดี
