# อัตราเงินคืนเป็นหน่วย 1/1000 (silver 1.5%, gold 2.5%, platinum 4%)
RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 100 * 100   # 100 บาท = 10,000 สตางค์
CAP = 200 * 100          # 200 บาท = 20,000 สตางค์


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดเศษลง)"""
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PER_MILLE[tier] * (2 if birthday else 1)
    return min(amount * rate // 1000, CAP)
