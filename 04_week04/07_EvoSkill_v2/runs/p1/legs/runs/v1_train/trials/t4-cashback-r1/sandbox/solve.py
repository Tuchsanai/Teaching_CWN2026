RATES = {"silver": 15, "gold": 25, "platinum": 40}  # ส่วนในพัน


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดลง)"""
    if tier not in RATES:
        raise ValueError("invalid tier: %r" % (tier,))
    if amount < 10000:  # ต่ำกว่า 100 บาท
        return 0
    mult = 2 if birthday else 1
    cb = amount * RATES[tier] * mult // 1000
    return min(cb, 20000)  # เพดาน 200 บาท
