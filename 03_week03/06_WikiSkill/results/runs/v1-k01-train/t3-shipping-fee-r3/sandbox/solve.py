from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (1 baht = 100 satang)."""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))  # round half up
