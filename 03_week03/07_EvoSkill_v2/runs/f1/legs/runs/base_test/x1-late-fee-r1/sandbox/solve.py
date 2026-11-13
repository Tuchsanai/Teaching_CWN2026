def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์, จำนวนเต็ม)

    - ช้าไม่เกิน 3 วัน: 0
    - ช้าเกิน 3 วัน: 0.75% ต่อวัน นับทุกวันที่ช้า (รวม 3 วันแรก)
    - สูงสุด 15% ของยอดค้างชำระ
    คำนวณด้วยจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float ปัดเศษแบบ half-up
    """
    if days_late <= 3 or amount <= 0:
        return 0
    # หน่วย basis point: 0.75% = 75 bp, 15% = 1500 bp
    rate_bp = min(75 * days_late, 1500)
    return (amount * rate_bp * 2 + 10000) // 20000  # round half up of amount*rate_bp/10000
