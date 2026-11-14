from fractions import Fraction
from math import floor


def _frac(x):
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วยเศษส่วนแท้ ปัดครึ่งขึ้นตอนท้าย)"""
    w = _frac(weight_g)
    d = _frac(distance_km)
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        fee = 80 + (w - 5000) * 15 / 1000  # บาท

    if d > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(3, 2)

    satang = fee * 100
    return int(floor(satang + Fraction(1, 2)))
