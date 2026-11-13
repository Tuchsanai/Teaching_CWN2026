from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express=False):
    """Return shipping fee in integer satang (1 baht = 100 satang)."""
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        fee = 80 + (w - 5000) * 15 / 1000  # baht, proportional by gram

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    satang = fee * 100
    return int(floor(satang + Fraction(1, 2)))  # round half up
