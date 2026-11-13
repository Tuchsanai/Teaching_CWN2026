def late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    # 0.75%/day = 75/10000, cap 15% = 1500/10000 (integer math, no float error)
    num = amount * min(75 * days_late, 1500)
    return (num + 5000) // 10000  # round half up to whole satang
