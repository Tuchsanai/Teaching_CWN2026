"""refund(paid, used_percent, restock) - BaanKafe course refund (satang).

Rounding mode r3: round half up at every money step.
Assumptions: refund = paid*(100-used)/100 (rounded to satang);
used > 80 -> 0; if restock, fee = 12.5% of that refund (rounded), refund - fee.
"""


class InputError(ValueError, TypeError):
    pass


def _half_up(num, den):
    return (2 * num + den) // (2 * den)


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def refund(paid, used_percent, restock):
    if not _is_int(paid) or paid < 0:
        raise InputError("paid must be int >= 0")
    if not _is_int(used_percent) or not 0 <= used_percent <= 100:
        raise InputError("used_percent must be int 0-100")
    if not isinstance(restock, bool):
        raise InputError("restock must be bool")
    if used_percent > 80:
        return 0
    amount = _half_up(paid * (100 - used_percent), 100)
    if restock:
        amount -= _half_up(amount * 125, 1000)
    return int(amount)
