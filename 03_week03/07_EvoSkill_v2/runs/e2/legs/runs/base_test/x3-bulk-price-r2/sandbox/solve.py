def bulk_price(unit_price, qty, coupon):
    """Return the amount payable in whole satang (integer arithmetic, round half up at the end)."""
    # rates in per-mille / percent as integers to avoid float error
    if qty >= 50:
        d = 75      # 7.5%
    elif qty >= 10:
        d = 35      # 3.5%
    else:
        d = 0
    num = unit_price * qty * (1000 - d)
    den = 1000
    if coupon:
        num *= 975  # additional 2.5%, applied after the volume discount
        den *= 1000
    num *= 107      # VAT 7% last
    den *= 100
    return (2 * num + den) // (2 * den)  # round half up
