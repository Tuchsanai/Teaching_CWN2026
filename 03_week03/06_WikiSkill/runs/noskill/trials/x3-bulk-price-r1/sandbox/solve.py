def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact arithmetic, round half up once at the end)."""
    if qty >= 50:
        d1 = 1000 - 75
    elif qty >= 10:
        d1 = 1000 - 35
    else:
        d1 = 1000
    d2 = 975 if coupon else 1000
    num = unit_price * qty * d1 * d2 * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
