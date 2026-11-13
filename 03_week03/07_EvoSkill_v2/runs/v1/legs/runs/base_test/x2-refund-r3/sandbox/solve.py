def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม) — ใช้เลขจำนวนเต็มล้วน ไม่มี float error"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หัก 12.5% => เหลือ 87.5% = 7/8
        num *= 7
        den *= 8
    return num // den  # ปัดลงเป็นสตางค์เต็ม
