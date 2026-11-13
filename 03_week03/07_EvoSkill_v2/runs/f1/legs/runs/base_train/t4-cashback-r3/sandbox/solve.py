RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points
MIN_AMOUNT = 10_000  # 100 baht in satang
CAP = 20_000  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_BP:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES_BP[tier] * mult // 10_000
    return min(result, CAP)
