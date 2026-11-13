RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 10_000  # 100 baht in satang
MAX_CASHBACK = 20_000  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    multiplier = 2 if birthday else 1
    # integer math avoids floating-point errors; floor to whole satang
    result = amount * RATES_PER_MILLE[tier] * multiplier // 1000
    return min(result, MAX_CASHBACK)
