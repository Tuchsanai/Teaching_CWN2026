def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยง float"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # หน่วย: สตางค์ x 100
    den = 100
    if restock:  # หักค่าดำเนินการ 12.5% => เหลือ 7/8
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)  # round half up
