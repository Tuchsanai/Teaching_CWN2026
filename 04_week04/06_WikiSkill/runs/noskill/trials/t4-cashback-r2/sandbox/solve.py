RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points
MIN_AMOUNT = 10_000   # 100 baht in satang
MAX_CASHBACK = 20_000  # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES_BP:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    bp = RATES_BP[tier] * (2 if birthday else 1)
    # integer math, round down to whole satang, then cap per bill
    return min(amount * bp // 10_000, MAX_CASHBACK)
