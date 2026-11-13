RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 บาท เป็นสตางค์
MAX_CASHBACK = 200 * 100  # 200 บาท เป็นสตางค์


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดเศษลง)"""
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PER_MILLE[tier]
    if birthday:
        rate *= 2
    result = amount * rate // 1000  # คิดด้วยจำนวนเต็ม ไม่มีปัญหา float
    return min(result, MAX_CASHBACK)
