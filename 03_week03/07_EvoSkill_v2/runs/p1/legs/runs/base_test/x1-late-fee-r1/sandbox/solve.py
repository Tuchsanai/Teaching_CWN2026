def late_fee(amount, days_late):
    """Late fee in satang (integer)."""
    if days_late <= 3:
        return 0
    # 0.75% per day = 75/10000 ; cap 15% = 1500/10000 (exact integer math)
    rate_bp100 = min(75 * days_late, 1500)
    # round half up
    return (amount * rate_bp100 + 5000) // 10000
