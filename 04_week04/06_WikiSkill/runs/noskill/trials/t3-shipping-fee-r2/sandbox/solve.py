from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(40 * 100)
    elif w <= 5000:
        fee = Fraction(80 * 100)
    else:
        fee = Fraction(80 * 100) + (w - 5000) * Fraction(15 * 100, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return floor(fee + Fraction(1, 2))
