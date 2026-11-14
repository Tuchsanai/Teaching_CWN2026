def refund(paid, used_percent, restock):
    """Refund in satang (integer), rounded down once at the end."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # refund = num / 100
    if restock:
        # fee 12.5% -> keep 7/8
        return num * 7 // 800
    return num // 100
