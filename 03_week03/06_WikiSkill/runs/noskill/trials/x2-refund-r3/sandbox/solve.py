def refund(paid, used_percent, restock):
    """Refund in whole satang (integer arithmetic, rounded half up once at the end)."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # refund = num / 100
    den = 100
    if restock:  # deduct 12.5% -> keep 7/8
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)
