def refund(paid, used_percent, restock):
    """คืนจำนวนเงินคืน (สตางค์, จำนวนเต็ม)"""
    if used_percent > 80:
        return 0
    # ยอดตามสัดส่วนที่ยังไม่ได้เรียน = paid*(100-u)/100
    # หักค่าดำเนินการ 12.5% => คูณ 7/8  (คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียว)
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7
        den *= 8
    # ปัดเศษครึ่งขึ้น (half up)
    return (2 * num + den) // (2 * den)
