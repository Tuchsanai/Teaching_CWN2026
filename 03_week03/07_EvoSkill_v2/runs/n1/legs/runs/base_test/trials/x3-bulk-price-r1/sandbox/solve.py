def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (integer arithmetic, rounded half up once at the end)."""
    if qty >= 50:
        disc = 925      # 7.5% off (per 1000)
    elif qty >= 10:
        disc = 965      # 3.5% off
    else:
        disc = 1000
    cpn = 975 if coupon else 1000   # extra 2.5% off
    num = unit_price * qty * disc * cpn * 107   # VAT 7%
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
