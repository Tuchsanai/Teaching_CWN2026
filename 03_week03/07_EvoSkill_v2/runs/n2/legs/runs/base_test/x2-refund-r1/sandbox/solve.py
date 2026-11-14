def refund(paid, used_percent, restock):
    """Refund in whole satang (rounded half up once, at the end, using exact integer math)."""
    if used_percent > 80:
        return 0
    # refund = paid * (100 - used)/100, minus 12.5% (i.e. x 7/8) if restock
    num = paid * (100 - used_percent) * (7 if restock else 8)
    den = 800
    return (2 * num + den) // (2 * den)
