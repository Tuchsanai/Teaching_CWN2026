from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)"""
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 ก. ตามสัดส่วนของกรัม
        fee = Fraction(8000) + (Fraction(weight_g) - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(12, 10)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))
