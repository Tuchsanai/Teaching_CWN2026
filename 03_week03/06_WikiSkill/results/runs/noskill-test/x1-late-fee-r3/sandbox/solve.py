def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (หน่วยสตางค์, จำนวนเต็ม)"""
    if days_late <= 3:
        return 0
    # 0.75% ต่อวัน = 75/10000 ; เพดาน 15% = 1500/10000 (ใช้เลขจำนวนเต็มเพื่อเลี่ยง float)
    rate_bp100 = min(75 * days_late, 1500)
    return amount * rate_bp100 // 10000
