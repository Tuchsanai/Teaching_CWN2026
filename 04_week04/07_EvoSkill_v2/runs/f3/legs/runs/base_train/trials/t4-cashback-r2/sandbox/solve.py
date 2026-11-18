RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 10000   # 100 baht in satang
MAX_CASHBACK = 20000  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if amount < MIN_AMOUNT:
        return 0
    mille = RATES_PER_MILLE[tier] * (2 if birthday else 1)
    return min(amount * mille // 1000, MAX_CASHBACK)
