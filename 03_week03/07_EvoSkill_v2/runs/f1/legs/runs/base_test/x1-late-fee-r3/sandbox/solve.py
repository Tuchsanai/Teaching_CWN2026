def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม)"""
    if days_late <= 3:
        return 0
    # หน่วย: 1/10000 ของยอด (0.75% = 75, 15% = 1500) ใช้จำนวนเต็มล้วนเลี่ยง float error
    rate = min(75 * days_late, 1500)
    # ปัดครึ่งขึ้น
    return (amount * rate + 5000) // 10000
