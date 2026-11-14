def bulk_price(unit_price, qty, coupon):
    """ราคาสุทธิ (สตางค์, จำนวนเต็ม) — คำนวณด้วยเลขจำนวนเต็ม ปัดครั้งเดียวตอนท้าย (half up)"""
    if qty >= 50:
        d = 925   # ลด 7.5%
    elif qty >= 10:
        d = 965   # ลด 3.5%
    else:
        d = 1000
    c = 975 if coupon else 1000  # คูปองลดอีก 2.5%
    num = unit_price * qty * d * c * 107  # VAT 7%
    den = 1000 * 1000 * 100
    return (num + den // 2) // den
