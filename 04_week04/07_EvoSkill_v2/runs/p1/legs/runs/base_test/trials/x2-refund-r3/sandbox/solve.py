def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม) — คำนวณด้วยจำนวนเต็มล้วน ไม่มีปัญหา float"""
    if used_percent > 80:
        return 0
    # ยอดตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used) / 100
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หักค่าดำเนินการ 12.5% => เหลือ 87.5% = 7/8
        num *= 7
        den *= 8
    return num // den  # ปัดลง ไม่คืนเกินสิทธิ์
