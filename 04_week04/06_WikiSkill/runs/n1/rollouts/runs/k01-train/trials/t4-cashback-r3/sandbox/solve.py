RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points (1/10000)
MIN_AMOUNT = 10_000  # 100 baht in satang
CAP = 20_000  # 200 baht in satang


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # integer math, round half up to whole satang
    value = (amount * RATES_BP[tier] * mult * 2 + 10_000) // 20_000
    return min(value, CAP)
