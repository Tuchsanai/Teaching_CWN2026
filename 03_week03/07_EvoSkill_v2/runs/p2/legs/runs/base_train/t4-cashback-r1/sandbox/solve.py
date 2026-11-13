RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5% / 2.5% / 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (amount in satang)."""
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PERMILLE[tier] * (2 if birthday else 1)
    result = amount * rate // 1000  # integer math, floor to whole satang
    return min(result, MAX_CASHBACK)
