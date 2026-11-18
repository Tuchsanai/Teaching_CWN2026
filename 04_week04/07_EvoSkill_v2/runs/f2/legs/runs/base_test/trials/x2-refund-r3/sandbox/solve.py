def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้น)"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # เงินคืนตามสัดส่วน = num / 100
    den = 100
    if restock:
        num *= 7  # หัก 12.5% => เหลือ 87.5% = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)
