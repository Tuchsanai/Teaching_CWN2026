def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม) — ปัดเศษลง คำนวณด้วยเลขจำนวนเต็มล้วน"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หักค่าดำเนินการ 12.5% = คูณ 7/8
        num *= 7
        den *= 8
    return num // den
