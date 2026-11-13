def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (สตางค์, จำนวนเต็ม) — คำนวณด้วยจำนวนเต็มล้วน ปัดเศษลง"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:  # หักค่าดำเนินการ 12.5% => คงเหลือ 7/8
        num *= 7
        den *= 8
    return num // den
