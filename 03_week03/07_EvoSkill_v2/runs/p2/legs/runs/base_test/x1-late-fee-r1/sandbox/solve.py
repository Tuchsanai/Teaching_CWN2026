def late_fee(amount, days_late):
    """Late fee in whole satang (integers only, no float error)."""
    if days_late <= 3:
        return 0
    # 0.75% per day = 75/10000; cap 15% = 1500/10000
    numer = min(amount * 75 * days_late, amount * 1500)
    return (numer + 5000) // 10000  # round half up
