from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วย Fraction แล้วปัดครึ่งขึ้นตอนท้าย)"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์ / 1000 กรัม
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    return int(floor(fee + Fraction(1, 2)))
