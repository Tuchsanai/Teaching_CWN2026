def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (หน่วยสตางค์, คืนเป็นจำนวนเต็ม)

    - ช้า <= 3 วัน: 0
    - ช้า > 3 วัน: 0.75% ต่อวัน นับทุกวัน (รวม 3 วันแรก)
    - สูงสุด 15% ของยอดค้างชำระ
    ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงความคลาดเคลื่อนของ float
    ปัดเศษสตางค์แบบ half-up
    """
    if days_late <= 3:
        return 0
    # ค่าปรับ = amount * 0.75% * days  = amount * 75 * days / 10000
    # เพดาน   = amount * 15%           = amount * 1500 / 10000
    numerator = min(amount * 75 * days_late, amount * 1500)
    return (numerator * 2 + 10000) // 20000
