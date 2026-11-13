def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    if qty >= 50:
        d1 = 1000 - 75   # ลด 7.5%
    elif qty >= 10:
        d1 = 1000 - 35   # ลด 3.5%
    else:
        d1 = 1000
    d2 = 975 if coupon else 1000  # คูปองลดอีก 2.5%

    num = unit_price * qty * d1 * d2 * 107  # VAT 7%
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
