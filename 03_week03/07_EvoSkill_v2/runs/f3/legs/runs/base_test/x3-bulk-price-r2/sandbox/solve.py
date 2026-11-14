def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วน ไม่มีปัญหา float
    ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    if qty >= 50:
        disc_bp = 750      # 7.5% (หน่วย 1/10000)
    elif qty >= 10:
        disc_bp = 350      # 3.5%
    else:
        disc_bp = 0
    num = unit_price * qty * (10000 - disc_bp)
    den = 10000
    if coupon:
        num *= 975         # ลดอีก 2.5%
        den *= 1000
    num *= 107             # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)
