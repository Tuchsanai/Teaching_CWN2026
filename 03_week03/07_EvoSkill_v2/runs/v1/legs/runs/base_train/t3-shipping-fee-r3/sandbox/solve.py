from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วย Fraction เพื่อเลี่ยง float error)"""
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    weight = Fraction(weight_g)
    if weight <= 1000:
        fee = Fraction(4000)
    elif weight <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        fee = Fraction(8000) + (weight - 5000) * Fraction(1500, 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    # ปัดครึ่งขึ้น เป็นจำนวนเต็มสตางค์
    return int(floor(fee + Fraction(1, 2)))
