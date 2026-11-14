from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    # Rule A (-r1): exact Fraction arithmetic, floor once at the end.
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang per 1000 g, proportional by gram
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if Fraction(distance_km) > 100:  # "เกิน" = strictly greater
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int(fee.numerator // fee.denominator)
