RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points (1% = 100)
MIN_AMOUNT = 10_000   # 100 baht in satang
MAX_CASHBACK = 20_000  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES_BP[tier] * mult // 10_000  # integer math, no float error
    return min(result, MAX_CASHBACK)
