RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10_000   # 100 baht in satang
CAP = 20_000          # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down, integer math)."""
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    return min(amount * RATES_PERMILLE[tier] * mult // 1000, CAP)
