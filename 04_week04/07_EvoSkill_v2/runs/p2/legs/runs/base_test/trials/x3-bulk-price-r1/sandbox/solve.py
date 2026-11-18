def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (จำนวนเต็มสตางค์) คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half up)"""
    if qty >= 50:
        tier = 925   # ลด 7.5%
    elif qty >= 10:
        tier = 965   # ลด 3.5%
    else:
        tier = 1000
    cp = 975 if coupon else 1000  # ลดอีก 2.5%
    num = unit_price * qty * tier * cp * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
