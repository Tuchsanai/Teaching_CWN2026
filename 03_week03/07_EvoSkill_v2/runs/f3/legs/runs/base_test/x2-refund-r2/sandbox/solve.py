def refund(paid, used_percent, restock):
    """Refund in whole satang (integer math, rounded down)."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:  # fee 12.5% of refund -> keep 87.5% = 7/8
        num *= 7
        den *= 8
    return num // den
