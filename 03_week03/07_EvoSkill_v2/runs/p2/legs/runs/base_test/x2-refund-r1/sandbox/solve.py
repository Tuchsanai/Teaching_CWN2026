def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์) เป็นจำนวนเต็ม

    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - เรียนเกิน 80% ไม่คืน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    ใช้เลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half-up)
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # 1 - 0.125 = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)
