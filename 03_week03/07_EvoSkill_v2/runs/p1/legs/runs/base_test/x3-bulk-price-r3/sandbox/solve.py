def bulk_price(unit_price, qty, coupon):
    """Return the amount to pay in whole satang (integer).

    Uses exact integer arithmetic (rates in basis points) and rounds
    half-up once, at the very end, to avoid float errors.
    """
    # volume discount: 50+ -> 7.5%, 10+ -> 3.5% (single rate, not stacked)
    if qty >= 50:
        vol_bp = 750
    elif qty >= 10:
        vol_bp = 350
    else:
        vol_bp = 0
    coupon_bp = 250 if coupon else 0
    vat_bp = 10700  # 1 + 7%

    num = unit_price * qty * (10000 - vol_bp) * (10000 - coupon_bp) * vat_bp
    den = 10000 ** 3
    return (2 * num + den) // (2 * den)  # round half up
