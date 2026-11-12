RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
MIN_AMOUNT = 10_000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20_000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if tier not in RATES_BP:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES_BP[tier] * mult // 10_000  # ปัดลงเป็นสตางค์เต็ม
    return min(result, MAX_CASHBACK)
