from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(3, 2)  # 15 baht/kg = 1.5 satang/g
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    n, d = fee.numerator, fee.denominator
    return -(-n // d)
