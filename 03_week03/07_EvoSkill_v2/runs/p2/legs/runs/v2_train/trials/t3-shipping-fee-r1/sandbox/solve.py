from fractions import Fraction
import math

# หน่วย: weight_g กรัม, distance_km กม., ผลลัพธ์เป็นสตางค์ (int)
# ลำดับ: ค่าฐานตามน้ำหนัก -> ระยะ >100 กม. x1.2 -> ด่วน x1.5 -> แปลงเป็นสตางค์ ปัดครึ่งขึ้นครั้งเดียว


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def _num(x, name):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise InvalidInput(f"{name} must be a number")
    if isinstance(x, float) and not math.isfinite(x):
        raise InvalidInput(f"{name} must be finite")
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not isinstance(express, bool):
        raise InvalidInput("express must be bool")
    if w < 1 or w > 30000:
        raise InvalidInput("weight_g must be in 1..30000")
    if d < 0:
        raise InvalidInput("distance_km must be >= 0")

    if w <= 1000:
        baht = Fraction(40)
    elif w <= 5000:
        baht = Fraction(80)
    else:
        baht = 80 + (w - 5000) * 15 / 1000
    if d > 100:
        baht *= Fraction(120, 100)
    if express:
        baht *= Fraction(3, 2)
    s = baht * 100
    return int((2 * s.numerator + s.denominator) // (2 * s.denominator))
