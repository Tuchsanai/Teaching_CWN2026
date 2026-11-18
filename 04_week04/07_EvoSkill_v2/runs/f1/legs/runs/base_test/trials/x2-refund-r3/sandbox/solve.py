def refund(paid, used_percent, restock):
    """Refund in whole satang (integer), computed with exact integer math."""
    if used_percent > 80:
        return 0
    # proportional refund: paid * (100 - used) / 100
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # deduct 12.5% of the refund -> keep 87.5% = 7/8
        num *= 7
        den *= 8
    return num // den  # round down to whole satang
