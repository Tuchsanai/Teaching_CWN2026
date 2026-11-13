def refund(paid, used_percent, restock):
    """Refund in whole satang, using exact integer arithmetic."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # keep 87.5% = 7/8 (fee of 12.5%)
        den *= 8
    # single rounding at the end, half up
    return (2 * num + den) // (2 * den)
