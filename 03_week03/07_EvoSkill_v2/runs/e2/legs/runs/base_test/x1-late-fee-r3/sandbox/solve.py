def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float"""
    if days_late <= 3:
        return 0
    # 0.75% ต่อวัน = 75/10000 ; เพดาน 15% = 1500/10000
    num = min(amount * 75 * days_late, amount * 1500)
    return (num * 2 + 10000) // 20000  # ปัดครึ่งขึ้น
