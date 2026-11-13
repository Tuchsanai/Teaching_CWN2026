from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นเมื่อสิ้นสุดการคำนวณ)"""
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1.5 สตางค์/กรัม
        fee = Fraction(8000) + (Fraction(weight_g) - 5000) * Fraction(3, 2)

    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)

    return int(floor(fee + Fraction(1, 2)))
