RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000
MIN_AMOUNT = 10000   # 100 baht in satang
MAX_CASHBACK = 20000  # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # exact integer math; round down once at the end (after doubling)
    result = amount * RATES[tier] * mult // 1000
    return min(result, MAX_CASHBACK)
