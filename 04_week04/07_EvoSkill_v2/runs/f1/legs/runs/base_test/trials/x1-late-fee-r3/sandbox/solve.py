def late_fee(amount, days_late):
    """Late fee in whole satang (integer arithmetic, rounded down)."""
    if days_late <= 3:
        return 0
    fee = amount * 75 * days_late // 10000   # 0.75% per day, all late days
    cap = amount * 15 // 100                 # max 15%
    return min(fee, cap)
