RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (amount is in satang)."""
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES_PERMILLE[tier] * mult // 1000  # integer math, floor
    return min(result, MAX_CASHBACK)
