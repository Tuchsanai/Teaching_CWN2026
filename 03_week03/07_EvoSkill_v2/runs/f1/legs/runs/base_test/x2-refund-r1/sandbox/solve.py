def refund(paid, used_percent, restock):
    """Refund in whole satang (rounded half up, integer arithmetic only)."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # keep 87.5% (fee 12.5% = 1/8)
        den *= 8
    return (2 * num + den) // (2 * den)
