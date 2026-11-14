from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น) ด้วยเลขคณิตแบบแม่นยำ"""
    w = Fraction(weight_g)
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)  # สตางค์
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        fee = 8000 + (w - 5000) * 1500 / 1000

    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)

    return int(floor(fee + Fraction(1, 2)))
