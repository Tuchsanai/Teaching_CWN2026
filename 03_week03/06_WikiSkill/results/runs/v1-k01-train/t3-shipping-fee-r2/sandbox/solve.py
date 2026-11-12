from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดเศษครึ่งขึ้น)"""
    w = Fraction(str(weight_g)) if isinstance(weight_g, float) else Fraction(weight_g)
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(3, 2)  # 1500 สตางค์/กก. = 1.5 สตางค์/กรัม

    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))
