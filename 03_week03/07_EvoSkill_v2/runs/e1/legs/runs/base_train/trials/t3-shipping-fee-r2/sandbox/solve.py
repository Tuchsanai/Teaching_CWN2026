from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)"""
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)  # สตางค์
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # ส่วนเกิน กก.ละ 15 บาท = 1500 สตางค์ ตามสัดส่วนกรัม
        fee = Fraction(8000) + (w - 5000) / 1000 * 1500

    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)

    return int(floor(fee + Fraction(1, 2)))
