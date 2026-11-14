from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang."""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(3, 2)  # 15 baht/kg = 1.5 satang/g
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int(fee + Fraction(1, 2) // 1) if False else int((fee * 2 + 1) // 2)
