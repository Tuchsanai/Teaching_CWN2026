def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม)"""
    if days_late <= 3 or amount <= 0:
        return 0
    # 0.75% ต่อวัน = 75/10000 ; เพดาน 15% = 1500/10000 (คำนวณด้วยจำนวนเต็มล้วน)
    num = amount * min(75 * days_late, 1500)
    return (2 * num + 10000) // 20000  # ปัดครึ่งขึ้น
