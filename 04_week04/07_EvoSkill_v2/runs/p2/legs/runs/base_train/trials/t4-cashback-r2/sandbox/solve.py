MIN_AMOUNT = 10_000  # 100 บาท (สตางค์)
CAP = 20_000         # 200 บาท (สตางค์)
# อัตราเป็นเศษส่วน (numerator, denominator) เพื่อเลี่ยง float
RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (4, 100)}


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    num, den = RATES[tier]
    if birthday:
        num *= 2
    return min(amount * num // den, CAP)  # ปัดลงเป็นสตางค์เต็ม แล้วจำกัดเพดาน
