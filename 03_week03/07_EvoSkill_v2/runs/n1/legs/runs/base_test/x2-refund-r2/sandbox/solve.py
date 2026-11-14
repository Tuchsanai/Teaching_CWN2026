def refund(paid, used_percent, restock):
    """Refund in whole satang (integer arithmetic, rounded half up once at the end)."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875  # keep 87.5% (deduct 12.5% fee)
        den *= 1000
    return (2 * num + den) // (2 * den)
