from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """ค่าส่งเมล็ดกาแฟ คืนค่าเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(1500, 1000)  # 15 บาท/กก. = 1.5 สตางค์/กรัม
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return int(floor(fee + Fraction(1, 2)))
