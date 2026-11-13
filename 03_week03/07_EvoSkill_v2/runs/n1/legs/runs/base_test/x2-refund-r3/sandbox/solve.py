def refund(paid, used_percent, restock):
    """Refund in whole satang for a coffee course.

    Computed with exact integer arithmetic and rounded once (half up) at the end.
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # refund = num / 100
    den = 100
    if restock:
        num *= 7  # keep 87.5% = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)
