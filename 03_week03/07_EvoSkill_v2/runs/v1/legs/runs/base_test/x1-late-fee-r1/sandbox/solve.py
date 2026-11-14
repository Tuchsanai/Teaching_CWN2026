def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (หน่วยสตางค์, คืนค่าเป็น int)

    - ช้า <= 3 วัน: ไม่คิดค่าปรับ
    - ช้า > 3 วัน: 0.75% ต่อวัน นับทุกวันที่ช้า (รวม 3 วันแรก)
    - สูงสุด 15% ของยอดค้างชำระ
    - ปัดเศษแบบ half-up ด้วยเลขจำนวนเต็มล้วน (เลี่ยงปัญหา float)
    """
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days = amount * 75 * days / 10000
    # cap = amount * 15% = amount * 1500 / 10000
    numerator = min(amount * 75 * days_late, amount * 1500)
    return (numerator * 2 + 10000) // 20000
