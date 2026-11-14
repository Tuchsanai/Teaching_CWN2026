def refund(paid, used_percent, restock):
    """Refund in whole satang, computed with exact integer arithmetic."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # deduct 12.5% of the refund -> keep 87.5% = 7/8
        num *= 7
        den *= 8
    # round half up
    return (2 * num + den) // (2 * den)
