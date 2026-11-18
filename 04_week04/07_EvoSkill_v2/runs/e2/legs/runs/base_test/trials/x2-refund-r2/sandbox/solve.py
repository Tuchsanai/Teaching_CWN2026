def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ปัดเศษลง ด้วยเลขจำนวนเต็มล้วน)"""
    if used_percent > 80:
        return 0
    remaining = 100 - used_percent
    if restock:
        # paid * remaining/100 * (1 - 12.5%) = paid * remaining * 7 / 800
        return paid * remaining * 7 // 800
    return paid * remaining // 100
