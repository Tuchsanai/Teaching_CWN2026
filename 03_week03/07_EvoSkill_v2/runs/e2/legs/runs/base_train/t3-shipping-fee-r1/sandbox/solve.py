from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (1 baht = 100 satang)."""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang/kg = 1.5 satang/g
        fee = Fraction(8000) + (w - 5000) * Fraction(3, 2)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # round half up to whole satang
    return int((fee * 2 + 1) // 2)
