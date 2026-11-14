from fractions import Fraction
import math


def _num(v, name):
    # หน่วยวัด: รับ int/float เท่านั้น (ไม่รับ bool, NaN, inf)
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} must be a number")
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return Fraction(v)


def shipping_fee(weight_g, distance_km, express):
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be in 1..30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    # หน่วยสตางค์; 15 บาท/กก. = 1.5 สตางค์/กรัม
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(3, 2)
    if d > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(3, 2)
    # ไม่ปัดกลางทาง ปัดลง (floor) ครั้งเดียวตอนจบ
    return fee.numerator // fee.denominator
