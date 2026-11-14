def bulk_price(unit_price, qty, coupon):
    """Return the amount due in whole satang.

    Exact integer arithmetic; rounded half-up once, only at the end.
    """
    if qty >= 50:
        d1 = 1000 - 75   # 7.5% off
    elif qty >= 10:
        d1 = 1000 - 35   # 3.5% off
    else:
        d1 = 1000
    d2 = 975 if coupon else 1000  # extra 2.5% off
    num = unit_price * qty * d1 * d2 * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
