def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม)"""
    if days_late <= 3:
        return 0
    # คำนวณด้วยจำนวนเต็มล้วน: หน่วยเป็น 1/10000 ของสตางค์
    raw = amount * 75 * days_late          # 0.75% ต่อวัน
    cap = amount * 1500                    # 15%
    fee = min(raw, cap)
    return (fee + 5000) // 10000           # ปัดครึ่งขึ้น
