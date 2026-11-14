def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (หน่วยสตางค์, คืนค่าเป็นจำนวนเต็ม)

    - ช้าไม่เกิน 3 วัน: 0
    - ช้าเกิน 3 วัน: 0.75% ต่อวัน นับทุกวันที่ช้า (รวม 3 วันแรก)
    - สูงสุด 15% ของยอดค้างชำระ
    คำนวณด้วยเลขจำนวนเต็มล้วน (ไม่มีปัญหา float) ปัดเศษแบบ half-up
    """
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days = amount * 75 * days / 10000
    # cap = amount * 15% = amount * 1500 / 10000
    rate_bp = min(75 * days_late, 1500)  # หน่วย 1/10000
    return (amount * rate_bp + 5000) // 10000
