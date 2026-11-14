RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per mille (1.5%, 2.5%, 4%)
MIN_AMOUNT = 10_000  # 100 baht in satang
CAP = 20_000         # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # integer math (no float error); floor to whole satang
    return min(amount * RATES[tier] * mult // 1000, CAP)
