# rounding policy r3 (banker's / half-even, exact via Fraction)
from fractions import Fraction


def late_fee(amount, days_late):
    if type(amount) is not int or type(days_late) is not int:
        raise ValueError("amount and days_late must be int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late must be 0-365")
    if days_late <= 3:
        return 0
    fee = Fraction(amount * days_late * 75, 10000)
    cap = Fraction(amount * 15, 100)
    return int(round(min(fee, cap)))
