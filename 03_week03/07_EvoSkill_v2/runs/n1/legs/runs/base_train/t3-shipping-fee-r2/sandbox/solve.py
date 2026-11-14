from fractions import Fraction
from math import floor


def _frac(x):
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นเมื่อสุดท้ายได้เศษสตางค์)"""
    w = _frac(weight_g)
    d = _frac(distance_km)
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 ก. ตามสัดส่วนกรัม
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)

    if d > 100:
        fee *= Fraction(12, 10)
    if express:
        fee *= Fraction(3, 2)

    return int(floor(fee + Fraction(1, 2)))
