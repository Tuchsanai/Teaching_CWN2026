# rounding policy r1: half-up applied once at the end


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def refund(paid, used_percent, restock):
    if not _is_int(paid) or not _is_int(used_percent) or not isinstance(restock, bool):
        raise ValueError("invalid input type")
    if paid < 0 or not (0 <= used_percent <= 100):
        raise ValueError("input out of range")
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875
        den *= 1000
    return (2 * num + den) // (2 * den)
