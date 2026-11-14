"""ค่าส่งเมล็ดกาแฟ BaanKafe

กติกา:
- น้ำหนัก 1–30,000 กรัม, ระยะทาง >= 0 กม., express=True คือส่งด่วน
- ค่าฐานตามน้ำหนัก:
    * ไม่เกิน 1,000 กรัม  -> 40 บาท
    * ไม่เกิน 5,000 กรัม  -> 80 บาท
    * เกิน 5,000 กรัม     -> 80 บาท + (กรัมที่เกิน 5,000) * 15 บาท / 1,000 กรัม (คิดตามสัดส่วน)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อก่อนหน้า)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)

คำนวณด้วย Fraction ทั้งหมด เพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยมของ float
"""

import math
from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    weight = Fraction(weight_g)
    distance = Fraction(distance_km)

    # ค่าฐานหน่วยเป็นสตางค์ (1 บาท = 100 สตางค์)
    if weight <= 1000:
        fee = Fraction(40 * 100)
    elif weight <= 5000:
        fee = Fraction(80 * 100)
    else:
        # 15 บาท/กก. = 1500 สตางค์ / 1000 กรัม
        fee = Fraction(80 * 100) + (weight - 5000) * Fraction(1500, 1000)

    if distance > 100:
        fee *= Fraction(6, 5)  # +20%

    if express:
        fee *= Fraction(3, 2)  # +50%

    # ปัดเศษครึ่งขึ้นให้เป็นจำนวนเต็มสตางค์
    return math.floor(fee + Fraction(1, 2))
