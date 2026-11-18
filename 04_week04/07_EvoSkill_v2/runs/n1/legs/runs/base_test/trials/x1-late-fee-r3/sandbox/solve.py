def late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    # 0.75% per day = 75/10000; cap 15% = 1500/10000 (integer math, round half up)
    rate = min(75 * days_late, 1500)
    return (amount * rate * 2 + 10000) // 20000
