def bulk_price(unit_price, qty, coupon):
    """Return total payable in whole satang (round half up, once at the end)."""
    if qty >= 50:
        d = 750      # 7.5% in basis points
    elif qty >= 10:
        d = 350      # 3.5%
    else:
        d = 0
    c = 250 if coupon else 0
    num = unit_price * qty * (10000 - d) * (10000 - c) * 107
    den = 10000 * 10000 * 100
    return (2 * num + den) // (2 * den)
