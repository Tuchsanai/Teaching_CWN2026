from fractions import Fraction
from math import floor


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee as integer satang (1 baht = 100 satang)."""
    if weight_g <= 1000:
        fee = Fraction(40 * 100)
    elif weight_g <= 5000:
        fee = Fraction(80 * 100)
    else:
        # 15 baht per kg = 1.5 satang per gram over 5,000 g
        fee = Fraction(80 * 100) + (Fraction(weight_g) - 5000) * Fraction(15 * 100, 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    # exact arithmetic, round half up to whole satang
    return int(floor(fee + Fraction(1, 2)))
