from fractions import Fraction


def _check_int(v, name):
    # H3: wrong type -> TypeError (bool and float are rejected too)
    if isinstance(v, bool) or not isinstance(v, int):
        raise TypeError(f"{name} must be an int")


def late_fee(amount, days_late):
    _check_int(amount, "amount")
    _check_int(days_late, "days_late")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late must be in 0..365")
    if days_late <= 3:
        return 0
    # 0.75% per day (every late day), capped at 15%; exact arithmetic
    fee = min(Fraction(75, 10000) * days_late, Fraction(15, 100)) * amount
    # round half up once at the end
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
