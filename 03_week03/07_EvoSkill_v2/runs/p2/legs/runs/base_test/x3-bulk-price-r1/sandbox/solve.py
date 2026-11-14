def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยง float error
    ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    total = unit_price * qty
    # อัตราส่วนลดเป็นสัดส่วนของ 1000
    if qty >= 50:
        tier = 925   # ลด 7.5%
    elif qty >= 10:
        tier = 965   # ลด 3.5%
    else:
        tier = 1000
    cp = 975 if coupon else 1000  # คูปองลดอีก 2.5%
    num = total * tier * cp * 107  # VAT 7%
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
