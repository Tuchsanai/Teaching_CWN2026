def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม)

    - เรียนเกิน 80% ไม่คืน
    - คืนตามสัดส่วนที่ยังไม่เรียน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    - ปัดเศษลง (floor) ด้วยเลขจำนวนเต็ม ไม่ใช้ float
    """
    if used_percent > 80:
        return 0
    remaining = 100 - used_percent
    if restock:
        # paid * remaining/100 * (1 - 1/8) = paid * remaining * 7 / 800
        return paid * remaining * 7 // 800
    return paid * remaining // 100
