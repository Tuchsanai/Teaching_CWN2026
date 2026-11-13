def bulk_price(unit_price, qty, coupon):
    """คืนยอดชำระเป็นสตางค์ (จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วน ปัดครึ่งขึ้นเมื่อจบขั้นสุดท้าย"""
    tier = 75 if qty >= 50 else 35 if qty >= 10 else 0  # หน่วย per-mille
    cpn = 25 if coupon else 0
    num = unit_price * qty * (1000 - tier) * (1000 - cpn) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
