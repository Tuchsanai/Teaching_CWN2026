def refund(paid, used_percent, restock):
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # หัก 12.5% = คูณ 7/8
        den *= 8
    return num // den  # ปัดลงเป็นสตางค์เต็ม ด้วยเลขจำนวนเต็มล้วน
