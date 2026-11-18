def late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    # 0.75% per day = 75/10000; cap 15% = 1500/10000 (integer math, round down)
    return min(amount * 75 * days_late, amount * 1500) // 10000
