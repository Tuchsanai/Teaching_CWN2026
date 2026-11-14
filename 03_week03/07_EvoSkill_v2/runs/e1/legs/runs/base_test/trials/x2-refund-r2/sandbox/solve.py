def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์) เป็นจำนวนเต็ม

    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - เรียนเกิน 80% ไม่คืน
    - restock=True หัก 12.5% ของยอดที่จะคืน
    คำนวณด้วยจำนวนเต็มล้วน ปัดเศษลง (floor) ครั้งเดียวตอนท้าย
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875   # 1 - 0.125 = 875/1000
        den *= 1000
    return num // den
