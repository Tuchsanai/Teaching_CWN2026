def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม)

    - ช้า <= 3 วัน: 0
    - ช้า > 3 วัน: 0.75% ของยอด ต่อวัน นับทุกวัน (รวม 3 วันแรก)
    - สูงสุด 15% ของยอด
    ใช้เลขจำนวนเต็มล้วน (ไม่มี float error) ปัดครึ่งขึ้น
    """
    if days_late <= 3 or amount <= 0:
        return 0
    # fee = amount * days * 0.75% = amount * days * 75 / 10000
    fee = (amount * days_late * 75 * 2 + 10000) // 20000  # round half up
    cap = (amount * 15 * 2 + 100) // 200  # 15% of amount, round half up
    return int(min(fee, cap))
