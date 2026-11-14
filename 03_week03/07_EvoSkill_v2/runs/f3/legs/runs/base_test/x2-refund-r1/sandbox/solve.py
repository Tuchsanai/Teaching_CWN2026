def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float"""
    if used_percent > 80:
        return 0
    # สัดส่วนที่ยังไม่ได้เรียน; หักค่าดำเนินการ 12.5% = คูณ 875/1000
    factor = 875 if restock else 1000
    num = paid * (100 - used_percent) * factor
    den = 100 * 1000
    # ปัดเศษครึ่งขึ้น (half up)
    return (2 * num + den) // (2 * den)
