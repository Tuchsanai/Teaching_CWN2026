def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (สตางค์, จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half-up)"""
    if qty >= 50:
        disc = 75
    elif qty >= 10:
        disc = 35
    else:
        disc = 0
    num = unit_price * qty * (1000 - disc)
    den = 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
