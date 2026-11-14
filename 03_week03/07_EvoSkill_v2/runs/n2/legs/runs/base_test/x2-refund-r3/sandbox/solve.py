def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม) ปัดเศษครั้งเดียวตอนท้าย แบบ half-up"""
    if used_percent > 80:
        return 0
    # ยอดคืน = paid * (100 - used) / 100 ; หักดำเนินการ 12.5% => คูณ 7/8
    num = paid * (100 - used_percent) * (7 if restock else 8)
    den = 800
    return (2 * num + den) // (2 * den)
