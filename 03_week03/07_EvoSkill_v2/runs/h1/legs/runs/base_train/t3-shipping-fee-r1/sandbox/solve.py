"""BaanKafe shipping fee calculator.

ฟังก์ชัน shipping_fee(weight_g, distance_km, express) คำนวณค่าส่งเมล็ดกาแฟ
และคืนค่าเป็นจำนวนเต็มสตางค์

กติกา
- น้ำหนัก 1–30,000 กรัม, ระยะทาง >= 0 กม., express = True คือส่งด่วน
- ไม่เกิน 1,000 กรัม  : 40 บาท
- ไม่เกิน 5,000 กรัม  : 80 บาท
- เกิน 5,000 กรัม     : 80 บาท + (น้ำหนักส่วนที่เกิน 5,000 กรัม) × 15 บาท/กก. (คิดตามสัดส่วนกรัม)
- ระยะทางเกิน 100 กม. : คิดเพิ่ม 20% (×1.2)
- ส่งด่วน            : คิดเพิ่ม 50% (×1.5) คูณต่อจากข้อก่อนหน้า
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)

คำนวณด้วย Fraction เพื่อหลีกเลี่ยงความคลาดเคลื่อนของจุดทศนิยม (floating point)
"""

import math
from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000
LONG_DISTANCE_KM = 100


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (int)."""
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(
            f"weight_g must be between {MIN_WEIGHT_G} and {MAX_WEIGHT_G}, got {weight_g}"
        )
    if distance_km < 0:
        raise ValueError(f"distance_km must be >= 0, got {distance_km}")

    weight = Fraction(weight_g)
    distance = Fraction(distance_km)

    # ค่าส่งฐานตามน้ำหนัก (หน่วยเป็นบาท)
    if weight <= 1000:
        fee = Fraction(40)
    elif weight <= 5000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + (weight - 5000) / 1000 * 15

    # ระยะทางเกิน 100 กม. เพิ่ม 20%
    if distance > LONG_DISTANCE_KM:
        fee *= Fraction(120, 100)

    # ส่งด่วนเพิ่ม 50% (คูณต่อจากข้อก่อนหน้า)
    if express:
        fee *= Fraction(150, 100)

    # แปลงเป็นสตางค์แล้วปัดเศษแบบครึ่งขึ้นให้เป็นจำนวนเต็ม
    satang = fee * 100
    return math.floor(satang + Fraction(1, 2))
