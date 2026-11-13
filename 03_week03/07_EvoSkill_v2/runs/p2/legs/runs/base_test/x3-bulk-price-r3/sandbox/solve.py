def bulk_price(unit_price, qty, coupon):
    """Return payable amount in whole satang (exact integer math, round half up at the end)."""
    if qty >= 50:
        num, den = 925, 1000      # 7.5% off
    elif qty >= 10:
        num, den = 965, 1000      # 3.5% off
    else:
        num, den = 1, 1
    if coupon:
        num, den = num * 975, den * 1000   # further 2.5% off
    num, den = num * 107, den * 100        # VAT 7% last
    n = unit_price * qty * num
    return (2 * n + den) // (2 * den)      # round half up
