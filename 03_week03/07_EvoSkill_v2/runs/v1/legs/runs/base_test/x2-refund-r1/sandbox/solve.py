def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์ เป็นจำนวนเต็ม ปัดลงเสมอ)"""
    if used_percent > 80:
        return 0
    # สัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used) / 100
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หักค่าดำเนินการ 12.5% => คงเหลือ 87.5% = 7/8
        num *= 7
        den *= 8
    return num // den  # ใช้จำนวนเต็มล้วน ไม่มีปัญหา float
