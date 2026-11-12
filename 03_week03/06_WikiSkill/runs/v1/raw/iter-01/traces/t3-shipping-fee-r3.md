# Trace t3-shipping-fee-r3 · iteration 1

- ผล: **FAIL** · คะแนน 0.50 (ผ่าน 5 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
ERROR Exit code 2
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
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))  # round half up
EOF
python3 -c "
from solve import shipping_fee as s
print(s(1000,0,False),s(5000,101,False),s(6000,0,True),s(5001,100,False))"
```

ผลที่ได้:

```
4000 9600 14250 8002
```

**Agent พูด:** สร้าง `solve.py` แล้ว (ไม่มีโฟลเดอร์ `./skills` จึงไม่มีสกิลให้อ่านก่อน)

ฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` คืนค่าส่งเป็นจำนวนเต็มสตางค์:
- **ค่าส่งตามน้ำหนัก:** ไม่เกิน 1,000 กรัม 4,000 สตางค์ ไม่เกิน 5,000 กรัม 8,000 สตางค์ ส่วนที่เกิน 5,000 กรัม คิดเพิ่มกรัมละ 1.5 สตางค์ (15 บาทต่อกิโลกรัม)
- **ระยะทาง:** เกิน 100 กม. คูณ 1.2
- **ส่งด่วน:** คูณ 1.5 ต่อจากข้อก่อน
- **การปัดเศษ:** คำนวณด้วย `Fraction` เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยม แล้วปัดครึ่งขึ้นตอนท้าย

ลองรันกับตัวอย่าง 4 กรณีแล้ว ผลเป็นไปตามที่คาด:

| weight_g | distance_km | express | ผล (สตางค์) |
|---|---|---|---|
| 1000 | 0 | False | 4000 |
| 5000 | 101 | False | 9600 |
| 6000 | 0 | True | 14250 |
| 5001 | 100 | False | 8002 |

กรณีสุดท้ายผลจริงคือ 8001.5 ปัดเป็น 8002 (ปัดครึ่งขึ้น) โจทย์ไม่ได้ระบุว
…(ตัด 70 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` แล้ว (ไม่มีโฟลเดอร์ `./skills` จึงไม่มีสกิลให้อ่านก่อน)

ฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` คืนค่าส่งเป็นจำนวนเต็มสตางค์:
- **ค่าส่งตามน้ำหนัก:** ไม่เกิน 1,000 กรัม 4,000 สตางค์ ไม่เกิน 5,000 กรัม 8,000 สตางค์ ส่วนที่เกิน 5,000 กรัม คิดเพิ่มกรัมละ 1.5 สตางค์ (15 บาทต่อกิโลกรัม)
- **ระยะทาง:** เกิน 100 กม. คูณ 1.2
- **ส่งด่วน:** คูณ 1.5 ต่อจากข้อก่อน
- **การปัดเศษ:** คำนวณด้วย `Fraction` เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยม แล้วปัดครึ่งขึ้นตอนท้าย

ลองรันกับตัวอย่าง 4 กรณีแล้ว ผลเป็นไปตามที่คาด:

| weight_g | distance_km | express | ผล (สตางค์) |
|---|---|---|---|
| 1000 | 0 | False | 4000 |
| 5000 | 101 | False | 9600 |
| 6000 | 0 | True | 14250 |
| 5001 | 100 | False | 8002 |

กรณีสุดท้ายผลจริงคือ 8001.5 ปัดเป็น 8002 (ปัดครึ่งขึ้น) โจทย์ไม่ได้ระบุวิธีปัดเศษ ถ้าต้องการวิธีอื่น เช่น ปัดลง ให้แก้บรรทัดสุดท้ายของฟังก์ชัน
