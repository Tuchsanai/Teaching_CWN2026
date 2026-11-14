def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float
    ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    if qty >= 50:
        disc = 75   # 7.5% (หน่วย 1/1000)
    elif qty >= 10:
        disc = 35   # 3.5%
    else:
        disc = 0
    coupon_disc = 25 if coupon else 0  # 2.5%

    num = unit_price * qty * (1000 - disc) * (1000 - coupon_disc) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
