def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ใช้เลขจำนวนเต็มล้วน ไม่มีปัญหา float)."""
    if used_percent > 80:
        return 0
    # ยอดคืนตามสัดส่วน = paid * (100 - used) / 100
    # หลังหักค่าดำเนินการ 12.5% = x * 875 / 1000
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875
        den *= 1000
    # ปัดเศษครึ่งขึ้น (half up) ครั้งเดียวตอนท้าย
    return (2 * num + den) // (2 * den)
