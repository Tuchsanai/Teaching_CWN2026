RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points (1% = 100)
MIN_AMOUNT = 100 * 100   # 100 baht in satang
CAP = 200 * 100          # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_BP[tier]
    if birthday:
        rate *= 2
    return min(amount * rate // 10000, CAP)
