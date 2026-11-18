def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half up)"""
    if qty >= 50:
        disc = 75
    elif qty >= 10:
        disc = 35
    else:
        disc = 0
    coupon_disc = 25 if coupon else 0
    num = unit_price * qty * (1000 - disc) * (1000 - coupon_disc) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
