def late_fee(amount, days_late):
    # H1: wrong type -> TypeError, out of range -> ValueError
    for v in (amount, days_late):
        if isinstance(v, bool) or not isinstance(v, int):
            raise TypeError("amount and days_late must be int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late must be in 0..365")
    if days_late <= 3:
        return 0
    # rate in basis points: 0.75% per day (all days), capped at 15%
    bp = min(75 * days_late, 1500)
    n, d = amount * bp, 10000
    # exact arithmetic, round half up once at the end
    return (2 * n + d) // (2 * d)
