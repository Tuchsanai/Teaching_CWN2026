from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee as integer satang."""
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang/kg -> 1.5 satang per gram over 5000
        fee = Fraction(8000) + (Fraction(weight_g) - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))  # round half up
