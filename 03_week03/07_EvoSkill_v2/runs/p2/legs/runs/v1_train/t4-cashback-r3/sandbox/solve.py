# กติกาปัดเศษแบบ C: ปัดครึ่งขึ้นเป็นสตางค์เต็มหลังคิดเงินคืนก่อนคูณ 2 (จำนวนเต็มล้วน)
RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}


def cashback(amount, tier, birthday):
    if amount < 10000:  # ต่ำกว่า 100 บาท ไม่ได้เงินคืน (พอดี 100 บาทได้)
        return 0
    n, d = RATES[tier]
    cb = (2 * amount * n + d) // (2 * d)  # ปัดครึ่งขึ้น
    if birthday:
        cb *= 2
    return min(cb, 20000)  # เพดาน 200 บาทต่อบิล หลังคูณ 2
