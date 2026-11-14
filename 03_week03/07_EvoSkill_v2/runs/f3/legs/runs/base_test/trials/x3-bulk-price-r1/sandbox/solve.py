def bulk_price(unit_price, qty, coupon):
    # exact integer arithmetic; round half up once, at the very end
    if qty >= 50:
        d = 75
    elif qty >= 10:
        d = 35
    else:
        d = 0
    num = unit_price * qty * (1000 - d)
    den = 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
