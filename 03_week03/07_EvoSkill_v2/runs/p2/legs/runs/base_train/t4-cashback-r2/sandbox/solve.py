# อัตราเป็นต่อพัน (per mille) เพื่อใช้เลขจำนวนเต็ม ไม่มีปัญหา float
RATES = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]  # หน่วย: สตางค์ x 1000
    if birthday:
        value *= 2
    return min(value // 1000, MAX_CASHBACK)  # ปัดลงเป็นสตางค์เต็ม
