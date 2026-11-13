MIN_AMOUNT = 10_000  # 100 baht in satang
MAX_CASHBACK = 20_000  # 200 baht in satang
# rate in per-mille (integer math avoids float errors)
RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PERMILLE[tier] * (2 if birthday else 1)
    result = amount * rate // 1000
    return min(result, MAX_CASHBACK)
