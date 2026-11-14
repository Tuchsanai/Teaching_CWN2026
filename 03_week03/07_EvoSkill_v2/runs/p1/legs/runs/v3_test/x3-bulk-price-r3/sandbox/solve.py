from fractions import Fraction


def _rnd_even(x):
    """Round to nearest int, ties to even (same as Python round()); done once at the end."""
    x = Fraction(x)
    q, r = divmod(x.numerator, x.denominator)
    twice = 2 * r
    if twice > x.denominator or (twice == x.denominator and q % 2 == 1):
        q += 1
    return q


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def bulk_price(unit_price, qty, coupon):
    if not _is_int(unit_price) or unit_price < 0:
        raise ValueError("unit_price must be int >= 0")
    if not _is_int(qty) or not 1 <= qty <= 1000:
        raise ValueError("qty must be int in 1..1000")
    if not isinstance(coupon, bool):
        raise ValueError("coupon must be bool")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)   # 7.5% (single rate)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)   # 3.5%
    if coupon:
        total *= Fraction(975, 1000)         # extra 2.5%
    total *= Fraction(107, 100)              # VAT last
    return _rnd_even(total)                  # round once at the end
