def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer arithmetic,
    rounded half-up once at the end)."""
    if qty >= 50:
        a = 925      # 7.5% off (/1000)
    elif qty >= 10:
        a = 965      # 3.5% off
    else:
        a = 1000
    b = 975 if coupon else 1000   # extra 2.5% off, applied multiplicatively
    num = unit_price * qty * a * b * 107   # VAT 7% last
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
