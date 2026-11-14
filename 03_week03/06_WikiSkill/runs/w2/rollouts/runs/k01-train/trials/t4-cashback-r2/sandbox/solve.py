RATES_BPS = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น, คำนวณด้วยจำนวนเต็มล้วน)"""
    if amount < MIN_AMOUNT:
        return 0
    bps = RATES_BPS[tier]
    mult = 2 if birthday else 1
    num = amount * bps * mult
    result = (num * 2 + 10000) // 20000  # round half up ของ num/10000
    return min(result, MAX_CASHBACK)
