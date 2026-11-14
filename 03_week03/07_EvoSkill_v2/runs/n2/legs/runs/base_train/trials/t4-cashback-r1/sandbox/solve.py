MIN_AMOUNT = 10_000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20_000  # 200 บาท (สตางค์)
# อัตราเป็นต่อพัน (per mille) เพื่อใช้เลขจำนวนเต็มล้วน ไม่มีปัญหาทศนิยม
RATE_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดเศษทิ้ง)"""
    if amount < MIN_AMOUNT:
        return 0
    rate = RATE_PER_MILLE[tier]
    if birthday:
        rate *= 2
    return min(amount * rate // 1000, MAX_CASHBACK)
