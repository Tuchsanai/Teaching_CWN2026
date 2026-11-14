def bulk_price(unit_price, qty, coupon):
    """คืนยอดชำระเป็นจำนวนเต็มสตางค์ (ใช้เลขจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    # อัตราส่วนลด หน่วยเป็น 1/1000
    if qty >= 50:
        tier = 925   # ลด 7.5%
    elif qty >= 10:
        tier = 965   # ลด 3.5%
    else:
        tier = 1000
    coup = 975 if coupon else 1000  # ลดอีก 2.5%

    num = unit_price * qty * tier * coup * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
