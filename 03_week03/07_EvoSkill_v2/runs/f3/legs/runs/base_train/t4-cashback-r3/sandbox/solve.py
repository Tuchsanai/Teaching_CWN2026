RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per mille (1.5%, 2.5%, 4%)
MIN_AMOUNT = 10000   # 100 baht in satang
MAX_CASHBACK = 20000  # 200 baht in satang


def cashback(amount, tier, birthday):
    if tier not in RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    num = amount * RATES[tier] * (2 if birthday else 1)
    result = (2 * num + 1000) // 2000  # integer round-half-up of num/1000
    return min(result, MAX_CASHBACK)
