def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half-up)"""
    num = unit_price * qty
    den = 1

    if qty >= 50:
        num *= 925   # ลด 7.5%
        den *= 1000
    elif qty >= 10:
        num *= 965   # ลด 3.5%
        den *= 1000

    if coupon:
        num *= 975   # ลดอีก 2.5%
        den *= 1000

    num *= 107       # VAT 7%
    den *= 100

    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
