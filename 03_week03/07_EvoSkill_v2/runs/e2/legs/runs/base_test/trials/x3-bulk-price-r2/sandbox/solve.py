def bulk_price(unit_price, qty, coupon):
    """Return the amount payable in whole satang (round half up, once at the end)."""
    if qty >= 50:
        tier = 925      # 7.5% off (per 1000)
    elif qty >= 10:
        tier = 965      # 3.5% off
    else:
        tier = 1000
    cpn = 975 if coupon else 1000   # extra 2.5% off
    num = unit_price * qty * tier * cpn * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)   # exact integer round-half-up
