def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer math, round half up once at the end)."""
    if qty >= 50:
        tier = 925
    elif qty >= 10:
        tier = 965
    else:
        tier = 1000
    num = unit_price * qty * tier
    den = 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
