# rounding policy r2 (ceiling)
from fractions import Fraction


def late_fee(amount, days_late):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be int")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise ValueError("days_late must be int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late must be 0-365")
    if days_late <= 3:
        return 0
    fee = min(Fraction(amount * 75 * days_late, 10000), Fraction(amount * 15, 100))
    return -(-fee.numerator // fee.denominator)
