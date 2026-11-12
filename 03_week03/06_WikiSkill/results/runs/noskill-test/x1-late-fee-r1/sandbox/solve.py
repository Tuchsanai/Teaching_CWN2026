def late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    # หน่วย 1/10000 ของยอด: 0.75% = 75 ต่อวัน, เพดาน 15% = 1500
    units = min(75 * days_late, 1500)
    # ปัดครึ่งขึ้นเป็นสตางค์ ด้วยเลขจำนวนเต็มล้วน (ไม่มี float error)
    return (amount * units * 2 + 10000) // 20000
