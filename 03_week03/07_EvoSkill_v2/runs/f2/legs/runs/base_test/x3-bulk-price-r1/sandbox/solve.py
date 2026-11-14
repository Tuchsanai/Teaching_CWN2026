def bulk_price(unit_price, qty, coupon):
    """Return the amount payable in whole satang (exact integer math, round half up once at the end)."""
    # rates in per-mille
    if qty >= 50:
        tier = 75
    elif qty >= 10:
        tier = 35
    else:
        tier = 0
    num = unit_price * qty * (1000 - tier)
    den = 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
