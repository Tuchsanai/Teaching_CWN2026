# อัตราเงินคืน หน่วย 1/1000 (silver 1.5%, gold 2.5%, platinum 4%)
RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 100_00   # 100 บาท (สตางค์)
MAX_CASHBACK = 200_00  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดเศษลง)"""
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    value = amount * RATES_PERMILLE[tier] * mult // 1000
    return min(value, MAX_CASHBACK)
