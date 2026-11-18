from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee as an integer number of satang."""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang/kg = 1.5 satang/g
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))  # round half up
