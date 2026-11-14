from fractions import Fraction
import math


def _num(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} must be a number")
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"{name} must be finite")


def shipping_fee(weight_g, distance_km, express):
    _num(weight_g, "weight_g")
    _num(distance_km, "distance_km")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if not (1 <= weight_g <= 30000):
        raise ValueError("weight_g out of range 1-30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)  # satang
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    # floor once at the end -> integer satang
    return fee.numerator // fee.denominator
