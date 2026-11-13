from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in whole satang (integer)."""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang/1000 g, proportional by gram
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # round half up to whole satang
    return math.floor(fee + Fraction(1, 2))
