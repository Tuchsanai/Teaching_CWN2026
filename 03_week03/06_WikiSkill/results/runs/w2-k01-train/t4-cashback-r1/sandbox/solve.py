RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES_BP:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # integer math, round down to whole satang, then cap
    value = amount * RATES_BP[tier] * mult // 10000
    return min(value, MAX_CASHBACK)
