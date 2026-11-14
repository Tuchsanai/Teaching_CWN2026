MIN_AMOUNT = 10000   # 100 baht in satang
MAX_CASHBACK = 20000  # 200 baht in satang
# rate as per-mille (integer math avoids float errors)
RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PER_MILLE[tier] * (2 if birthday else 1)
    return min(amount * rate // 1000, MAX_CASHBACK)
