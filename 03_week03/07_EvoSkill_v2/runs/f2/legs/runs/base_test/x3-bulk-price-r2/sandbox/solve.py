def bulk_price(unit_price, qty, coupon):
    """คิดราคาขายส่ง (สตางค์) ด้วยเลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half-up)."""
    tier = 1000          # 100.0%
    if qty >= 50:
        tier = 925       # ลด 7.5% (ไม่ซ้อนกับ 3.5%)
    elif qty >= 10:
        tier = 965       # ลด 3.5%
    cp = 975 if coupon else 1000   # คูปองลด 2.5%
    num = unit_price * qty * tier * cp * 107   # VAT 7%
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
