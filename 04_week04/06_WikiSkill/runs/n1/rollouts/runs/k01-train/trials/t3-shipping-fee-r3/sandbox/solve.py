from fractions import Fraction
from math import floor


def _frac(x):
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee as integer satang."""
    w = _frac(weight_g)
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    d = _frac(distance_km)
    if d < 0:
        raise ValueError("distance_km must be >= 0")

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

    return int(floor(fee + Fraction(1, 2)))  # round half up
