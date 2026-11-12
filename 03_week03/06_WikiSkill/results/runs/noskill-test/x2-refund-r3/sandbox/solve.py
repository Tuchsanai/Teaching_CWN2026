def refund(paid, used_percent, restock):
    """คืนเงินเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วยเลขจำนวนเต็มล้วน ปัดเศษลง"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # หัก 12.5% = คูณ 7/8
        den *= 8
    return num // den
