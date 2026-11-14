from fractions import Fraction
from math import floor


def _frac(x):
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (1 baht = 100 satang)."""
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
        # 15 baht per kg = 1500 satang per 1000 g, proportional by gram
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)

    if d > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    # round half up to whole satang
    return int(floor(fee + Fraction(1, 2)))
