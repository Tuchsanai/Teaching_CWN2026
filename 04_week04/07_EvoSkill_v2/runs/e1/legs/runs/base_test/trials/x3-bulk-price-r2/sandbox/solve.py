def bulk_price(unit_price, qty, coupon):
    """Return the amount payable in whole satang (exact arithmetic, rounded half-up once at the end)."""
    d = 75 if qty >= 50 else 35 if qty >= 10 else 0   # per mille
    c = 25 if coupon else 0                           # per mille
    num = unit_price * qty * (1000 - d) * (1000 - c) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
