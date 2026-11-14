from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นเมื่อเศษสตางค์ตอนท้าย)"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(40 * 100)
    elif w <= 5000:
        fee = Fraction(80 * 100)
    else:
        # ส่วนเกิน 5,000 กรัม กก.ละ 15 บาท = 1.5 สตางค์/กรัม
        fee = Fraction(80 * 100) + (w - 5000) * Fraction(3, 2)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))
