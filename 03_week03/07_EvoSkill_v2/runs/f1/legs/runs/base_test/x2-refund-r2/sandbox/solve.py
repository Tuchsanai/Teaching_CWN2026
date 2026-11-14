def refund(paid, used_percent, restock):
    """คืนเงิน (สตางค์, จำนวนเต็ม) ของคอร์ส BaanKafe"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หัก 12.5% => เหลือ 87.5% = 7/8
        num *= 7
        den *= 8
    # ปัดครึ่งขึ้น ด้วยจำนวนเต็มล้วน (ปัดเศษครั้งเดียวที่ผลลัพธ์สุดท้าย)
    return (2 * num + den) // (2 * den)
