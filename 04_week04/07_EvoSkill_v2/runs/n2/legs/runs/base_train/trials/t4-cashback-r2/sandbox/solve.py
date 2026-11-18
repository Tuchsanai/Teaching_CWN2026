RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10_000   # 100 baht in satang
MAX_CASHBACK = 20_000  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES_PER_MILLE[tier] * mult // 1000  # exact integer math
    return min(result, MAX_CASHBACK)
