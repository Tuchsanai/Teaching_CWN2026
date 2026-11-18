def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (integer arithmetic, round half up at the end only)."""
    if qty >= 50:
        tier = 1000 - 75   # 7.5% off
    elif qty >= 10:
        tier = 1000 - 35   # 3.5% off
    else:
        tier = 1000
    coup = 975 if coupon else 1000  # extra 2.5% off
    num = unit_price * qty * tier * coup * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
