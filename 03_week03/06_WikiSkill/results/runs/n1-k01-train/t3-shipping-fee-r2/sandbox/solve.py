from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang."""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee *= Fraction(12, 10)
    if express:
        fee *= Fraction(3, 2)
    # round half up to whole satang
    return int((fee * 2 + 1) // 2)
