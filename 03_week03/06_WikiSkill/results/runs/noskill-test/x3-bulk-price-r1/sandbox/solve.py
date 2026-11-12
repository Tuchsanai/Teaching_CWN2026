def bulk_price(unit_price, qty, coupon):
    """คืนยอดสุทธิ (สตางค์, จำนวนเต็ม) ปัดครึ่งขึ้นเมื่อสิ้นสุดการคำนวณเท่านั้น"""
    if qty >= 50:
        tier = 925   # ลด 7.5%
    elif qty >= 10:
        tier = 965   # ลด 3.5%
    else:
        tier = 1000
    coupon_f = 975 if coupon else 1000  # ลดอีก 2.5%
    num = unit_price * qty * tier * coupon_f * 107   # VAT 7% ขั้นสุดท้าย
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)  # round half up ด้วยจำนวนเต็มล้วน
