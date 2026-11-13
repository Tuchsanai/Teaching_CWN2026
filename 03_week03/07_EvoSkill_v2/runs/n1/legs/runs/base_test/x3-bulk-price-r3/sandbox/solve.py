def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer math, rounded half-up once at the end)."""
    if qty >= 50:
        d = 925      # 7.5% off (per mille of price kept)
    elif qty >= 10:
        d = 965      # 3.5% off
    else:
        d = 1000
    c = 975 if coupon else 1000   # extra 2.5% off, applied after qty discount
    num = unit_price * qty * d * c * 107   # VAT 7%
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)    # round half up
