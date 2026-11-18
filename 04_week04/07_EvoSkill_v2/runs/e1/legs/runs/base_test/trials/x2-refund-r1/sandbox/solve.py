def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น ที่ขั้นสุดท้ายครั้งเดียว)"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875  # หักค่าดำเนินการ 12.5% => เหลือ 87.5%
        den *= 1000
    return (2 * num + den) // (2 * den)
