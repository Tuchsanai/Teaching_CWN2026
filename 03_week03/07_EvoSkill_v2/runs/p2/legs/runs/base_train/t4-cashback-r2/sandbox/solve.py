RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (integer math, rounded down)."""
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PERMILLE[tier]
    if birthday:
        rate *= 2
    return min(amount * rate // 1000, MAX_CASHBACK)
