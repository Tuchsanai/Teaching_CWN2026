"""late_fee — BaanKafe. Rounding mode r3 (single money step -> same as r1: round half up once)."""
from fractions import Fraction


class InputError(ValueError, TypeError):
    pass


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def late_fee(amount, days_late):
    if not _is_int(amount) or amount < 0:
        raise InputError("amount must be int >= 0")
    if not _is_int(days_late) or not 0 <= days_late <= 365:
        raise InputError("days_late must be int in 0..365")
    if days_late <= 3:
        return 0
    # 0.75% per day counting all late days, capped at 15% of amount
    fee = min(Fraction(amount * 75 * days_late, 10000), Fraction(amount * 15, 100))
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
