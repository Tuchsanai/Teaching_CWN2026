_RATES = {"silver": 15, "gold": 25, "platinum": 40}  # ส่วนในพัน


def cashback(amount, tier, birthday):
    if tier not in _RATES:
        raise ValueError("invalid tier")
    if amount < 10000:
        return 0
    mult = _RATES[tier] * (2 if birthday else 1)
    return min(amount * mult // 1000, 20000)
