MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)
# อัตราเป็นส่วนในหนึ่งพัน เพื่อเลี่ยงปัญหา float
RATE_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}


def cashback(amount, tier, birthday):
    if tier not in RATE_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATE_PER_MILLE[tier] * mult // 1000  # ปัดลงเป็นสตางค์
    return min(result, MAX_CASHBACK)
