def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม) — คำนวณด้วยจำนวนเต็มล้วน ไม่มีปัญหา float"""
    if days_late <= 3:
        return 0
    # 0.75% ต่อวัน = 75/10000 ; เพดาน 15% = 1500/10000
    rate_bp100 = min(75 * days_late, 1500)  # หน่วย 1/10000
    # ปัดเศษครึ่งขึ้น (half up)
    return (amount * rate_bp100 + 5000) // 10000
