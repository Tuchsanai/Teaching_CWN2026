def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer arithmetic, round half up once at end)."""
    num, den = unit_price * qty, 1
    if qty >= 50:
        num, den = num * 925, den * 1000
    elif qty >= 10:
        num, den = num * 965, den * 1000
    if coupon:
        num, den = num * 975, den * 1000
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)
