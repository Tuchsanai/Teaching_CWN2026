def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float"""
    if used_percent > 80:
        return 0
    rate = 875 if restock else 1000  # หักค่าดำเนินการ 12.5% => เหลือ 87.5%
    num = paid * (100 - used_percent) * rate
    den = 100 * 1000
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
