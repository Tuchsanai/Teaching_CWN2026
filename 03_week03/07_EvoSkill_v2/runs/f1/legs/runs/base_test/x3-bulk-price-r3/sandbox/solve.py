def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer math, round half up at the end)."""
    if qty >= 50:
        d = 925
    elif qty >= 10:
        d = 965
    else:
        d = 1000
    c = 975 if coupon else 1000
    num = unit_price * qty * d * c * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
