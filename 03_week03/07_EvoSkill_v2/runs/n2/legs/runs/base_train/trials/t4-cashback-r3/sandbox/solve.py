RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
CAP = 200 * 100          # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES_PER_MILLE[tier] * mult // 1000  # integer math, floor
    return min(result, CAP)
