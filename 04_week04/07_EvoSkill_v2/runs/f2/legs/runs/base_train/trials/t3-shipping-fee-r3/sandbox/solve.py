from fractions import Fraction
import math


def _frac(x):
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang."""
    w = _frac(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(3, 2)  # 15 baht/kg = 1.5 satang/g
    if _frac(distance_km) > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # round half up to whole satang
    return math.floor(fee + Fraction(1, 2))
