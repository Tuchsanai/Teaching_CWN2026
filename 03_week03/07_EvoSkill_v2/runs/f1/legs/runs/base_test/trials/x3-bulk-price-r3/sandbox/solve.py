def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (สตางค์, จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    if qty >= 50:
        disc = 925      # ลด 7.5%
    elif qty >= 10:
        disc = 965      # ลด 3.5%
    else:
        disc = 1000
    coupon_f = 975 if coupon else 1000  # ลดอีก 2.5%
    num = unit_price * qty * disc * coupon_f * 107   # VAT 7%
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
