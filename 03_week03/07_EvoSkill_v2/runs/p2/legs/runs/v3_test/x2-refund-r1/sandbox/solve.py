from fractions import Fraction


def refund(paid, used_percent, restock):
    # H1: wrong type -> TypeError, out of range -> ValueError
    for v in (paid, used_percent):
        if isinstance(v, bool) or not isinstance(v, int):
            raise TypeError("paid and used_percent must be int")
    if not isinstance(restock, bool):
        raise TypeError("restock must be bool")
    if paid < 0:
        raise ValueError("paid must be >= 0")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent must be 0-100")
    if used_percent > 80:
        return 0
    amt = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amt *= Fraction(875, 1000)  # fee 12.5%
    # round half up once at the end
    return (2 * amt.numerator + amt.denominator) // (2 * amt.denominator)
