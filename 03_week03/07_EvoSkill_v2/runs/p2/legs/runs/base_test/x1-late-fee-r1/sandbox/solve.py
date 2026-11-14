def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (หน่วยสตางค์, ปัดครึ่งขึ้นเป็นจำนวนเต็ม)"""
    if days_late <= 3:
        return 0
    # 0.75% ต่อวัน = 75/10000, เพดาน 15% = 1500/10000 (คำนวณด้วยจำนวนเต็มล้วน)
    numerator = min(amount * 75 * days_late, amount * 1500)
    return (numerator * 2 + 10000) // 20000
