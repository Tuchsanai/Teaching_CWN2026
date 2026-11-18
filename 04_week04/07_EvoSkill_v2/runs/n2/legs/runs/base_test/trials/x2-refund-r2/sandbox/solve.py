def refund(paid, used_percent, restock):
    """Refund in whole satang (rounded down)."""
    if used_percent > 80:
        return 0
    num, den = paid * (100 - used_percent), 100
    if restock:  # fee 12.5% -> keep 87.5% = 7/8
        num, den = num * 7, den * 8
    return num // den
