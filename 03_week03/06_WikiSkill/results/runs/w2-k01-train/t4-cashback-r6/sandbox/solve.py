RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < 10000:  # under 100 baht
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES[tier] * mult // 1000
    return min(result, 20000)  # cap 200 baht per bill
