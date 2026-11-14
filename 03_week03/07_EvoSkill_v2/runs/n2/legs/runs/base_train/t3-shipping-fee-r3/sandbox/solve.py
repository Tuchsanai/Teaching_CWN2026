from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น) โดยคำนวณด้วยเศษส่วนเพื่อไม่ให้เกิดความคลาดเคลื่อนของ float"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)           # 40 บาท
    elif w <= 5000:
        fee = Fraction(8000)           # 80 บาท
    else:
        # 15 บาท/กก. = 1500 สตางค์ต่อ 1000 กรัม
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    return int(floor(fee + Fraction(1, 2)))
