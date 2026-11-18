RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 100 * 100   # satang
CAP = 200 * 100          # satang


def cashback(amount, tier, birthday):
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # integer math (no float error); truncate fractional satang
    value = amount * RATES_PERMILLE[tier] * mult // 1000
    return min(value, CAP)
