def late_fee(amount, days_late):
    """Late fee in whole satang (integer arithmetic, no float error)."""
    if days_late <= 3:
        return 0
    # 0.75% per day = 75/10000; cap 15% = 1500/10000 (in units of 1/10000)
    rate = min(75 * days_late, 1500)
    num = amount * rate
    # round half up to whole satang
    return (num + 5000) // 10000
