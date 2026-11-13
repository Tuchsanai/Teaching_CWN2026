"""BaanKafe refund. Rounding mode: r1 (round half up, once at the final value).
Assumptions: used_percent > 80 -> 0 refund; restock fee = 12.5% of refundable amount.
"""
from fractions import Fraction


class InputError(ValueError, TypeError):
    pass


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def refund(paid, used_percent, restock):
    if isinstance(paid, bool) or not isinstance(paid, int):
        raise InputError(f"paid must be an int, got {paid!r}")
    if paid < 0:
        raise InputError("paid must be >= 0")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int):
        raise InputError(f"used_percent must be an int, got {used_percent!r}")
    if not 0 <= used_percent <= 100:
        raise InputError("used_percent must be in 0..100")
    if not isinstance(restock, bool):
        raise InputError(f"restock must be a bool, got {restock!r}")

    if used_percent > 80:
        return 0
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(7, 8)
    return int(_round_half_up(amount))
