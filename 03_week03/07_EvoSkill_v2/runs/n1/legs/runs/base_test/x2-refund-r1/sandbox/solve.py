def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม)

    - เรียนเกิน 80% -> 0
    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    คำนวณด้วยจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half-up)
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent) * (875 if restock else 1000)
    den = 100 * 1000
    return (2 * num + den) // (2 * den)
