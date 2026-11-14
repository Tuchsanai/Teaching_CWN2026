def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงความคลาดเคลื่อนของ float
    ปัดเศษครั้งเดียวตอนท้าย (half-up)"""
    if qty >= 50:
        qty_factor = 1000 - 75   # ลด 7.5%
    elif qty >= 10:
        qty_factor = 1000 - 35   # ลด 3.5%
    else:
        qty_factor = 1000
    coupon_factor = 975 if coupon else 1000  # ลดอีก 2.5%

    num = unit_price * qty * qty_factor * coupon_factor * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
