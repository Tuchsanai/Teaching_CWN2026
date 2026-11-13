from fractions import Fraction
import math


class InputError(ValueError, TypeError):
    pass


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)."""
    if type(weight_g) is not int:
        raise InputError("weight_g must be int")
    if not 1 <= weight_g <= 30000:
        raise InputError("weight_g must be in 1..30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise InputError("distance_km must be a number")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise InputError("distance_km must be finite")
    if distance_km < 0:
        raise InputError("distance_km must be >= 0")
    if type(express) is not bool:
        raise InputError("express must be bool")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม = 3/2 สตางค์/กรัม
        fee = Fraction(8000) + Fraction(3, 2) * (weight_g - 5000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
