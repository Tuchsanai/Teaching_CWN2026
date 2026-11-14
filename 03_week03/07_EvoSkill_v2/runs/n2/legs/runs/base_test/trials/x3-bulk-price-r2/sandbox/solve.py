def bulk_price(unit_price, qty, coupon):
    """Return total payable in whole satang (exact integer math, round half up)."""
    if qty >= 50:
        disc = 1000 - 75   # 7.5% off
    elif qty >= 10:
        disc = 1000 - 35   # 3.5% off
    else:
        disc = 1000
    coup = 975 if coupon else 1000  # extra 2.5% off
    num = unit_price * qty * disc * coup * 107   # VAT 7% last
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)
