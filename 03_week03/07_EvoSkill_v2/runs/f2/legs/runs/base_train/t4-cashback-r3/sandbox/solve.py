RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PERMILLE[tier]
    mult = 2 if birthday else 1
    result = amount * rate * mult // 1000  # integer math, no float error
    return min(result, MAX_CASHBACK)
