def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์) เป็นจำนวนเต็ม

    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - เรียนเกิน 80% ไม่คืน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    คำนวณด้วยจำนวนเต็มล้วน (ไม่มีปัญหา float) ปัดเศษลงครั้งเดียวตอนท้าย
    """
    if used_percent > 80:
        return 0
    remaining = 100 - used_percent
    if restock:
        # paid * remaining/100 * (1 - 1/8) = paid * remaining * 7 / 800
        return paid * remaining * 7 // 800
    return paid * remaining // 100
