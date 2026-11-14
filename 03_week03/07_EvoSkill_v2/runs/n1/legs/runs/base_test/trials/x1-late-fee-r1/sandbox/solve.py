def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (หน่วยสตางค์, คืนค่าเป็นจำนวนเต็ม)

    - ช้าไม่เกิน 3 วัน: ไม่คิดค่าปรับ
    - ช้าเกิน 3 วัน: วันละ 0.75% นับทุกวันที่ช้า (รวม 3 วันแรก)
    - สูงสุด 15% ของยอดค้างชำระ
    """
    if days_late <= 3:
        return 0
    # ใช้เลขจำนวนเต็มล้วน เลี่ยงความคลาดเคลื่อนของ float
    # fee = amount * days * 0.75% = amount * days * 75 / 10000
    fee_num = amount * days_late * 75          # ส่วนเป็น 10000
    cap_num = amount * 15 * 100                # 15% = 1500/10000
    fee_num = min(fee_num, cap_num)
    # ปัดเศษแบบครึ่งปัดขึ้น (round half up)
    return (fee_num + 5000) // 10000
