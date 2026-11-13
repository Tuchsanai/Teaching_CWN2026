def bulk_price(unit_price, qty, coupon):
    """ราคาขายส่ง (สตางค์, จำนวนเต็ม) — คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นที่ขั้นสุดท้าย"""
    if qty >= 50:
        tier = 925      # ลด 7.5%
    elif qty >= 10:
        tier = 965      # ลด 3.5%
    else:
        tier = 1000
    cpn = 975 if coupon else 1000   # ลดอีก 2.5%
    num = unit_price * qty * tier * cpn * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
