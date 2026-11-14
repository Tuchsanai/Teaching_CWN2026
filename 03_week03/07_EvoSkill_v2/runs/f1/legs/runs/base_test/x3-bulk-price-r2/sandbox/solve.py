def bulk_price(unit_price, qty, coupon):
    """ราคาขายส่ง (สตางค์ จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย"""
    if qty >= 50:
        a = 1000 - 75
    elif qty >= 10:
        a = 1000 - 35
    else:
        a = 1000
    b = 975 if coupon else 1000
    num = unit_price * qty * a * b * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
