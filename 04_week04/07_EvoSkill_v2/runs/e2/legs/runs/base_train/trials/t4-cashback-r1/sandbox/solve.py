RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100_00   # 100 baht in satang
MAX_CASHBACK = 200_00  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if amount < MIN_AMOUNT:
        return 0
    per_mille = RATES_PERMILLE[tier] * (2 if birthday else 1)
    return min(amount * per_mille // 1000, MAX_CASHBACK)
