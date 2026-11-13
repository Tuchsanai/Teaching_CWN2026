# rounding policy r1 (half-up, rounded once at the end)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def late_fee(amount, days_late):
    if not _is_int(amount) or not _is_int(days_late):
        raise ValueError("amount and days_late must be int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if days_late < 0 or days_late > 365:
        raise ValueError("days_late must be in 0..365")
    if days_late <= 3:
        return 0
    # rate in basis points (0.75% per day), capped at 15%
    bp = min(days_late * 75, 1500)
    num = amount * bp
    den = 10000
    return (2 * num + den) // (2 * den)
