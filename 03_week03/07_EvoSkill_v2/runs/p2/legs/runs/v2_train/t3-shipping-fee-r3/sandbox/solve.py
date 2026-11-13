# validation policy r3
from fractions import Fraction
from numbers import Real


def _num(x, name):
    if isinstance(x, bool) or not isinstance(x, Real):
        raise TypeError(f"{name} must be a number")
    try:
        return Fraction(x)
    except (ValueError, OverflowError):
        raise ValueError(f"{name} must be finite")


def shipping_fee(weight_g, distance_km, express):
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not isinstance(express, bool):
        raise TypeError("express must be bool")
    if not (1 <= w <= 30000):
        raise ValueError("weight_g must be in 1..30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * 1500 / 1000  # satang
    if d > 100:
        fee = fee * 120 / 100
    if express:
        fee = fee * 150 / 100
    return int((2 * fee.numerator + fee.denominator) // (2 * fee.denominator))
