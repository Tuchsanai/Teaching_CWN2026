from fractions import Fraction


def bulk_price(unit_price, qty, coupon):
    # H2: any invalid input -> ValueError
    if isinstance(unit_price, bool) or not isinstance(unit_price, int) or unit_price < 0:
        raise ValueError("unit_price")
    if isinstance(qty, bool) or not isinstance(qty, int) or not (1 <= qty <= 1000):
        raise ValueError("qty")
    if not isinstance(coupon, bool):
        raise ValueError("coupon")

    total = Fraction(unit_price * qty)
    # volume discount (single rate, based on qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)
    # coupon: compounded
    if coupon:
        total *= Fraction(1000 - 25, 1000)
    # VAT last
    total *= Fraction(107, 100)
    # single round-half-up at the end
    return (2 * total.numerator + total.denominator) // (2 * total.denominator)
