def refund(paid, used_percent, restock):
    """Refund in whole satang (integer), computed exactly with integer math.

    - proportional to unused portion
    - used_percent > 80 -> 0
    - restock=True deducts 12.5% of the refund amount
    - final result rounded half up to an integer satang
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # 1 - 1/8 = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)
