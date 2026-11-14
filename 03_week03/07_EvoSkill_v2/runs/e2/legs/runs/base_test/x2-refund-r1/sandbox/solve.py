def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม)

    - เรียนเกิน 80% -> 0
    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    คำนวณด้วยจำนวนเต็มล้วน (ไม่มีความคลาดเคลื่อนของ float)
    ปัดเศษสตางค์แบบครึ่งปัดขึ้น
    """
    if used_percent > 80:
        return 0
    # refund = paid * (100 - used) / 100 * (7/8 ถ้า restock)  ->  ส่วนร่วม 800
    num = paid * (100 - used_percent) * (7 if restock else 8)
    return (2 * num + 800) // 1600
