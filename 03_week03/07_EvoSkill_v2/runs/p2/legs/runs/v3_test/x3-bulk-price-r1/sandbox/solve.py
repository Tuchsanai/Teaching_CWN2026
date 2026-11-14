from fractions import Fraction


def bulk_price(unit_price, qty, coupon):
    # H1: wrong type -> TypeError, out of range -> ValueError
    for v in (unit_price, qty):
        if isinstance(v, bool) or not isinstance(v, int):
            raise TypeError("unit_price and qty must be int")
    if not isinstance(coupon, bool):
        raise TypeError("coupon must be bool")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be 1..1000")

    # exact arithmetic; tier rates are not stacked (50+ uses 7.5% only)
    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)
    if coupon:
        total *= Fraction(975, 1000)
    total *= Fraction(107, 100)

    # round half up once, at the end
    return (2 * total.numerator + total.denominator) // (2 * total.denominator)
