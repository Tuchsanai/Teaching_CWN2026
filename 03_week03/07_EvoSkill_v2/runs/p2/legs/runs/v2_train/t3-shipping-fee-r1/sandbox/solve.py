# validation policy r1
from fractions import Fraction
import math


def _num(x, name):
    if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)):
        raise ValueError(f"{name} must be a number")
    if isinstance(x, float) and not math.isfinite(x):
        raise ValueError(f"{name} must be finite")
    return Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be in 1..30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        fee = 80 + (w - 5000) * 15 / 1000
    if d > 100:
        fee = fee * 120 / 100
    if express:
        fee = fee * 150 / 100
    s = fee * 100
    return (2 * s.numerator + s.denominator) // (2 * s.denominator)
