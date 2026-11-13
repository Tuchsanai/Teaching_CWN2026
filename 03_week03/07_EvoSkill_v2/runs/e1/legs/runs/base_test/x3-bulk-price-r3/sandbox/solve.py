def bulk_price(unit_price, qty, coupon):
    """Return amount payable in whole satang (exact integer math, rounded half-up once at the end)."""
    if qty >= 50:
        tier = 925   # 7.5% off (per 1000)
    elif qty >= 10:
        tier = 965   # 3.5% off
    else:
        tier = 1000
    coup = 975 if coupon else 1000  # extra 2.5% off
    vat = 1070                      # +7% VAT, applied last
    num = unit_price * qty * tier * coup * vat
    den = 1000 ** 3
    return (2 * num + den) // (2 * den)
