def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น, ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยง float)"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # ตัวหาร 100
    den = 100
    if restock:
        num *= 7  # หัก 12.5% => คูณ 7/8
        den *= 8
    return (2 * num + den) // (2 * den)
