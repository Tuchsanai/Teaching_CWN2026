def refund(paid, used_percent, restock):
    """Refund in whole satang (integer arithmetic, no float error)."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # refund = num / 100
    den = 100
    if restock:
        num *= 7  # keep 87.5% = 7/8 after 12.5% fee
        den *= 8
    return (2 * num + den) // (2 * den)  # round half up
