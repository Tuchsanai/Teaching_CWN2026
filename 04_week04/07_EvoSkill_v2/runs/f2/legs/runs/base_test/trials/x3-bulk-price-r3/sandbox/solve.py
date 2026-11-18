def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer math, round half up once at the end)."""
    if qty >= 50:
        tier = 925      # 7.5% off
    elif qty >= 10:
        tier = 965      # 3.5% off
    else:
        tier = 1000
    coupon_f = 975 if coupon else 1000  # extra 2.5% off
    num = unit_price * qty * tier * coupon_f * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
