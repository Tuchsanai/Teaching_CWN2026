RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 10_000  # 100 baht in satang
MAX_CASHBACK = 20_000  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (amount is in satang)."""
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PER_MILLE[tier] * (2 if birthday else 1)
    result = amount * rate // 1000  # integer math, rounds down
    return min(result, MAX_CASHBACK)
