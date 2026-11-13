def bulk_price(unit_price, qty, coupon):
    """Total payable in integer satang. Exact integer math, rounded half-up once at the end."""
    # discount in permille: 3.5% -> 35, 7.5% -> 75 (single tier, not stacked)
    tier = 75 if qty >= 50 else 35 if qty >= 10 else 0
    num = unit_price * qty * (1000 - tier)
    den = 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107  # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)
