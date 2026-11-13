def refund(paid, used_percent, restock):
    """Refund in whole satang (int).

    - proportional to the unused part of the course
    - used_percent > 80 -> 0
    - restock=True deducts a 12.5% fee from the refund amount
    Computed with exact integer arithmetic, rounded half up once at the end.
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # 1 - 12.5% = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)
