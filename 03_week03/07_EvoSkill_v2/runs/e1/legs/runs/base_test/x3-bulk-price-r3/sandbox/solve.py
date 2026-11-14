def bulk_price(unit_price, qty, coupon):
    # อัตราเป็นหน่วยต่อ 1000 เพื่อหลีกเลี่ยง float
    if qty >= 50:
        d = 75
    elif qty >= 10:
        d = 35
    else:
        d = 0
    num = unit_price * qty * (1000 - d)
    den = 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
    return (2 * num + den) // (2 * den)
