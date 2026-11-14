# อัตราเงินคืนเป็นหน่วย 1/1000 (silver 1.5% = 15/1000)
RATES = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 100 * 100   # 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100  # 200 บาท = 20,000 สตางค์


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES[tier]
    if birthday:
        rate *= 2
    # คำนวณด้วยจำนวนเต็มล้วน ปัดเศษลง แล้วจำกัดเพดานต่อบิล
    return min(amount * rate // 1000, MAX_CASHBACK)
