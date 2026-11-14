import math
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """ค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดขึ้นครั้งเดียวตอนจบ)"""
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be 1-30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(3, 2)  # 15 บาท/กก. = 1.5 สตางค์/กรัม

    if Fraction(distance_km) > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return math.ceil(fee)
