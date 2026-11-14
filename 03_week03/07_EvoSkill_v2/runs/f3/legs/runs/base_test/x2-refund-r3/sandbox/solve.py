def refund(paid, used_percent, restock):
    """Refund in whole satang (integer), computed with exact integer math.

    - Proportional to the unused part of the course.
    - Used more than 80% -> no refund.
    - restock=True -> deduct 12.5% of the refundable amount.
    - Result rounded to nearest satang (half rounds up).
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # keep 87.5% = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)
