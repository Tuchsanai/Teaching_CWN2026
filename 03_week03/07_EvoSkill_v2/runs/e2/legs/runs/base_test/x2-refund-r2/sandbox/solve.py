def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์ เป็นจำนวนเต็ม) ใช้เลขจำนวนเต็มล้วน ไม่มี float error"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # หาร 100 ภายหลัง
    den = 100
    if restock:
        num *= 7  # คูณ (1 - 0.125) = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
