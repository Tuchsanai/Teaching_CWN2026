def refund(paid, used_percent, restock):
    """คืนเงินเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ปัดเศษลงครั้งเดียวตอนท้าย"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # ยอดคืนก่อนหัก = num / 100
    if restock:
        # หัก 12.5% => เหลือ 87.5% = 7/8
        return num * 7 // 800
    return num // 100
