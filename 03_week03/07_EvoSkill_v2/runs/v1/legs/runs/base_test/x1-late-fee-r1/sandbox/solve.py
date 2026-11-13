def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (หน่วยสตางค์, คืนค่าเป็นจำนวนเต็ม)

    - ช้าไม่เกิน 3 วัน: 0
    - ช้าเกิน 3 วัน: 0.75% ต่อวัน นับทุกวัน (รวม 3 วันแรก)
    - สูงสุด 15% ของยอดค้างชำระ
    ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float ปัดเศษแบบ half-up
    """
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days = amount * 75 * days / 10000
    # cap = amount * 15% = amount * 1500 / 10000
    numerator = min(amount * 75 * days_late, amount * 1500)
    return (numerator * 2 + 10000) // 20000  # round half up
