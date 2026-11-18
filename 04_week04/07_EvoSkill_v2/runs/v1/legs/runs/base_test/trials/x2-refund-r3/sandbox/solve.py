def refund(paid, used_percent, restock):
    """คืนเงินเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ไม่มีความคลาดเคลื่อนของ float"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:  # หักค่าดำเนินการ 12.5% => เหลือ 87.5% = 7/8
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
