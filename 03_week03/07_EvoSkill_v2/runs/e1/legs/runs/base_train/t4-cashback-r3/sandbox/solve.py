RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    multiplier = 2 if birthday else 1
    # integer math avoids float errors; floor to whole satang
    result = amount * RATES_PERMILLE[tier] * multiplier // 1000
    return min(result, MAX_CASHBACK)
