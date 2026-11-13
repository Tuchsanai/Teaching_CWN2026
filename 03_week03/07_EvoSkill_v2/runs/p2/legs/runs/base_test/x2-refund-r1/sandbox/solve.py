def refund(paid, used_percent, restock):
    """คิดเงินคืนคอร์ส (หน่วยสตางค์, คืนเป็นจำนวนเต็ม)

    - เรียนเกิน 80% ไม่คืนเงิน
    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    คำนวณด้วยจำนวนเต็มล้วน ปัดเศษลง (ไม่คืนเกิน) ครั้งเดียวตอนท้าย
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # 1 - 12.5% = 7/8
        den *= 8
    return num // den
