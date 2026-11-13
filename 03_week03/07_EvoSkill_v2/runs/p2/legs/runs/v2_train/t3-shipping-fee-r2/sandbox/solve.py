# validation policy r2
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if not (1 <= weight_g <= 30000):
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        fee = 80 + (w - 5000) * 15 / 1000
    fee *= 100  # satang
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int((fee * 2 + 1) // 2)
