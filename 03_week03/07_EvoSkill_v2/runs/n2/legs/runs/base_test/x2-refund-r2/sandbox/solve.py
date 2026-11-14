def refund(paid, used_percent, restock):
    if used_percent > 80:
        return 0
    # numerator/denominator in exact integer arithmetic
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # keep 87.5% = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)  # round half up, single rounding
