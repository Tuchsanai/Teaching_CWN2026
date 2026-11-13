def bulk_price(unit_price, qty, coupon):
    """Total payable in integer satang (exact arithmetic, round half up at the end)."""
    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925; den *= 1000   # 7.5% off
    elif qty >= 10:
        num *= 965; den *= 1000   # 3.5% off
    if coupon:
        num *= 975; den *= 1000   # extra 2.5% off
    num *= 107; den *= 100        # VAT 7%
    return (2 * num + den) // (2 * den)
