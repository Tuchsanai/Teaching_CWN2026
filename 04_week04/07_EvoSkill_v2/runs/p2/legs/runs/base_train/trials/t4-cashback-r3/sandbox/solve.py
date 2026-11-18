RATES_PER_1000 = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100_00   # 100 baht in satang
MAX_CASHBACK = 200_00  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_PER_1000:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    multiplier = 2 if birthday else 1
    result = amount * RATES_PER_1000[tier] * multiplier // 1000
    return min(result, MAX_CASHBACK)
