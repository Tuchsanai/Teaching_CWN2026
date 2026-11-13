def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น คำนวณด้วยจำนวนเต็มล้วน)."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หักค่าดำเนินการ 12.5% => เหลือ 87.5% = 7/8
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)
