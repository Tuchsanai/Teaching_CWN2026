def refund(paid, used_percent, restock):
    """Refund in whole satang (integer), computed with exact integer math."""
    if used_percent > 80:
        return 0
    unused = 100 - used_percent
    if restock:
        # prorated * (1 - 12.5%) = paid * unused / 100 * 7 / 8
        return paid * unused * 7 // 800
    return paid * unused // 100
