def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (สตางค์, จำนวนเต็ม) — ใช้เลขจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half up)"""
    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925; den *= 1000      # ลด 7.5%
    elif qty >= 10:
        num *= 965; den *= 1000      # ลด 3.5%
    if coupon:
        num *= 975; den *= 1000      # ลดอีก 2.5%
    num *= 107; den *= 100           # VAT 7%
    return (2 * num + den) // (2 * den)
