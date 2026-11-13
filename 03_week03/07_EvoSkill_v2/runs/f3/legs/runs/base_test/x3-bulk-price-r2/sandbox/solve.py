def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (integer arithmetic, round half up at the end)."""
    num = unit_price * qty * 1000          # tier denominator 1000
    den = 1000
    if qty >= 50:
        num *= 925
    elif qty >= 10:
        num *= 965
    else:
        num *= 1000
    den *= 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107                              # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)     # round half up
