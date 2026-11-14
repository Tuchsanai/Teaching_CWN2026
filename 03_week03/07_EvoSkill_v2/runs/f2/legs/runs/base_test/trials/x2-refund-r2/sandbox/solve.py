def refund(paid, used_percent, restock):
    """Refund in whole satang (integer arithmetic, rounded down)."""
    if used_percent > 80:
        return 0
    remaining = 100 - used_percent
    if restock:
        # paid * remaining/100 * (1 - 0.125) = paid * remaining * 7 / 800
        return paid * remaining * 7 // 800
    return paid * remaining // 100
