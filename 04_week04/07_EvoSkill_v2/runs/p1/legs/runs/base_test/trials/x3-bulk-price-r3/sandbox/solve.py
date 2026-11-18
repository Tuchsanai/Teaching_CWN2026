def bulk_price(unit_price, qty, coupon):
    # Exact integer arithmetic (no float error); rounded half-up once at the end.
    if qty >= 50:
        d = 75      # 7.5% in tenths of a percent
    elif qty >= 10:
        d = 35      # 3.5%
    else:
        d = 0
    c = 25 if coupon else 0  # 2.5%
    num = unit_price * qty * (1000 - d) * (1000 - c) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
