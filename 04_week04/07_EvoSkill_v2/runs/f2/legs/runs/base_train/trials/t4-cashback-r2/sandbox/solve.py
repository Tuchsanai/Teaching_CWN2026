RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 10_000  # 100 บาท (สตางค์)
MAX_CASHBACK = 20_000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดเศษลง)"""
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PER_MILLE[tier]
    if birthday:
        rate *= 2
    return min(amount * rate // 1000, MAX_CASHBACK)
