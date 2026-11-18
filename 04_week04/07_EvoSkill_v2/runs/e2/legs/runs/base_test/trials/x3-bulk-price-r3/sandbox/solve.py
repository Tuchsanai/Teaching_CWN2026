def bulk_price(unit_price, qty, coupon):
    # integer arithmetic (per-mille / percent) to avoid float errors
    if qty >= 50:
        d = 925
    elif qty >= 10:
        d = 965
    else:
        d = 1000
    c = 975 if coupon else 1000
    num = unit_price * qty * d * c * 107
    den = 1000 * 1000 * 100
    return (num * 2 + den) // (den * 2)  # round half up, only at the end
