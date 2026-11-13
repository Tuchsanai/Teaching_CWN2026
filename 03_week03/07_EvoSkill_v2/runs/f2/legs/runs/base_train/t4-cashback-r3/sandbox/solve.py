RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100  # 200 บาท = 20,000 สตางค์


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดเศษลง)"""
    if tier not in RATES_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    multiplier = 2 if birthday else 1
    result = amount * RATES_PERMILLE[tier] * multiplier // 1000  # เลขจำนวนเต็มล้วน ไม่มีปัญหา float
    return min(result, MAX_CASHBACK)
