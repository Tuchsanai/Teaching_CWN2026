def bulk_price(unit_price, qty, coupon):
    """Return the amount payable in whole satang (integer), rounded half up.

    Uses exact integer arithmetic, rounding only once at the end.
    """
    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925   # 7.5% off
        den *= 1000
    elif qty >= 10:
        num *= 965   # 3.5% off
        den *= 1000
    if coupon:
        num *= 975   # 2.5% off
        den *= 1000
    num *= 107       # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)  # round half up
