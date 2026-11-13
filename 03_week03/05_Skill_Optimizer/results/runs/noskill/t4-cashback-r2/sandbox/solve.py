RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points (1/10000)
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_BP:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if amount < MIN_AMOUNT:
        return 0
    multiplier = 2 if birthday else 1
    result = amount * RATES_BP[tier] * multiplier // 10000  # integer math, no float error
    return min(result, MAX_CASHBACK)
