def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม)"""
    if days_late <= 3:
        return 0
    # อัตรา 0.75%/วัน = 75/10000 ต่อวัน, เพดาน 15% = 1500/10000
    rate = min(days_late * 75, 1500)
    # ใช้เลขจำนวนเต็มล้วน ปัดครึ่งขึ้น (half up) เลี่ยงปัญหา float
    return (amount * rate + 5000) // 10000
