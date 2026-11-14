def late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    # 0.75% per day = 75/10000; cap 15% = 1500/10000 (all integer math)
    rate_bp100 = min(75 * days_late, 1500)  # in units of 1/10000
    # round half up to whole satang
    return (amount * rate_bp100 + 5000) // 10000
