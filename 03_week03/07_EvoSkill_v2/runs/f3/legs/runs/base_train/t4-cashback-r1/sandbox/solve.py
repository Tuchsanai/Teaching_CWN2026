RATES_BPS = {"silver": 150, "gold": 250, "platinum": 400}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (rounded down)."""
    if tier not in RATES_BPS:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    bps = RATES_BPS[tier] * (2 if birthday else 1)
    return min(amount * bps // 10000, MAX_CASHBACK)
