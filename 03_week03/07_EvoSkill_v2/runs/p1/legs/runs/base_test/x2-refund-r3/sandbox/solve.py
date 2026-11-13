def refund(paid, used_percent, restock):
    """Refund in whole satang (integer), computed exactly with integers."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # keep 87.5% (= 7/8) of the refundable amount
        num *= 7
        den *= 8
    # round half up, single rounding at the end
    return (2 * num + den) // (2 * den)
