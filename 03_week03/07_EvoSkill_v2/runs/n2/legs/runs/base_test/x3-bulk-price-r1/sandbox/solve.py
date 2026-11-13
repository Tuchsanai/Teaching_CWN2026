def bulk_price(unit_price, qty, coupon):
    """คืนยอดชำระเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half-up)."""
    if qty >= 50:
        tier = 75      # 7.5% (หน่วย 1/1000)
    elif qty >= 10:
        tier = 35      # 3.5%
    else:
        tier = 0
    c = 25 if coupon else 0  # 2.5%
    num = unit_price * qty * (1000 - tier) * (1000 - c) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
