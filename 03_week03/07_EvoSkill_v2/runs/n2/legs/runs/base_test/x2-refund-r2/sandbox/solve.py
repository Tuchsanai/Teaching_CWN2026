def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ปัดเศษลง) ด้วยเลขจำนวนเต็มล้วน"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875   # หัก 12.5% => เหลือ 87.5%
        den *= 1000
    return num // den
