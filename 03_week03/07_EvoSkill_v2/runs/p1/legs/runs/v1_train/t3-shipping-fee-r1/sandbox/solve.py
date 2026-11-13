from fractions import Fraction
import math


def _num(name, v):
    if isinstance(v, bool) or not isinstance(v, (int, float, Fraction)):
        raise TypeError(f"{name} must be a number, got {v!r}")
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{name} must be finite")
        return Fraction(str(v))
    return Fraction(v)


def shipping_fee(weight_g, distance_km, express):
    w = _num("weight_g", weight_g)
    d = _num("distance_km", distance_km)
    if not isinstance(express, bool):
        raise TypeError("express must be a bool")
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    # satang
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(3, 2)  # 15 baht/kg = 1.5 satang/g
    if d > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
