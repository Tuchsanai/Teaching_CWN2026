def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หัก 12.5% => คูณ 7/8
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)
