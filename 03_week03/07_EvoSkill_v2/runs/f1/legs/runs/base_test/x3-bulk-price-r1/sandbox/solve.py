def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (จำนวนเต็มสตางค์) คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half up)"""
    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925; den *= 1000
    elif qty >= 10:
        num *= 965; den *= 1000
    if coupon:
        num *= 975; den *= 1000
    num *= 107; den *= 100
    return (2 * num + den) // (2 * den)
