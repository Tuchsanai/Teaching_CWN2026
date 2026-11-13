# อัตราเงินคืนเป็นต่อพัน (1.5% = 15/1000) เพื่อใช้เลขจำนวนเต็มล้วน ไม่มีปัญหา float
RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 100 * 100   # 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100  # 200 บาท = 20,000 สตางค์


def cashback(amount, tier, birthday):
    if tier not in RATES_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < MIN_AMOUNT:
        return 0
    multiplier = 2 if birthday else 1
    # คูณก่อนแล้วปัดลงครั้งเดียว จากนั้นจึงจำกัดเพดานต่อบิล
    result = amount * RATES_PER_MILLE[tier] * multiplier // 1000
    return min(result, MAX_CASHBACK)
