from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดขึ้นครั้งเดียวตอนจบ)"""
    if weight_g <= 1000:
        base = Fraction(4000)
    elif weight_g <= 5000:
        base = Fraction(8000)
    else:
        base = Fraction(8000) + (Fraction(weight_g) - 5000) * Fraction(3, 2)
    if distance_km > 100:
        base *= Fraction(120, 100)
    if express:
        base *= Fraction(150, 100)
    return int(math.ceil(base))
