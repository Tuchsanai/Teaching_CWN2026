def refund(paid, used_percent, restock):
    """Refund in whole satang (integer), computed with exact integer math."""
    if used_percent > 80:
        return 0
    # refund = paid * (100 - used)/100, minus 12.5% (i.e. x 7/8) if restock
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7
        den *= 8
    # single rounding at the end, half up
    return (2 * num + den) // (2 * den)
