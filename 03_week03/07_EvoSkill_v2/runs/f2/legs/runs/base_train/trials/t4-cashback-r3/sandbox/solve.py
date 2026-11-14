RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 10000   # 100 baht in satang
CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # exact integer math; fractions of a satang are floored
    return min(amount * RATES_PER_MILLE[tier] * mult // 1000, CAP)
