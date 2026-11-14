def bulk_price(unit_price, qty, coupon):
    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925; den *= 1000
    elif qty >= 10:
        num *= 965; den *= 1000
    if coupon:
        num *= 975; den *= 1000
    num *= 107; den *= 100
    # round half up, exact integer arithmetic, only at the end
    return (2 * num + den) // (2 * den)
