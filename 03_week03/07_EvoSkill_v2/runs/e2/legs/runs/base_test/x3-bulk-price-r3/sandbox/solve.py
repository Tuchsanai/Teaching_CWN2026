def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer math, round half up at the end)."""
    d = 75 if qty >= 50 else 35 if qty >= 10 else 0  # per-mille volume discount
    num = unit_price * qty * (1000 - d) * (975 if coupon else 1000) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
