from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (1 บาท = 100 สตางค์)"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(40 * 100)
    elif w <= 5000:
        fee = Fraction(80 * 100)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        fee = Fraction(80 * 100) + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return math.floor(fee + Fraction(1, 2))  # ปัดครึ่งขึ้น
