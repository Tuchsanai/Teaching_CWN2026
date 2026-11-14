def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (integer), exact arithmetic."""
    if qty >= 50:
        tier = 925      # 7.5% off
    elif qty >= 10:
        tier = 965      # 3.5% off
    else:
        tier = 1000
    cpn = 975 if coupon else 1000   # extra 2.5% off
    num = unit_price * qty * tier * cpn * 107   # VAT 7% last
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)         # round half up, once at the end
