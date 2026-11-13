def refund(paid, used_percent, restock):
    """Refund in whole satang (integer arithmetic, rounded half up once at the end)."""
    if used_percent > 80:
        return 0
    # refund = paid * (100 - used)/100, minus 12.5% fee if restock -> x 7/8
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)
