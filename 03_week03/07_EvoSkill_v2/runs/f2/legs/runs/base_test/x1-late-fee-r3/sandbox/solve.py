def late_fee(amount, days_late):
    """Late fee in satang (integer). Exact integer math, rounded half up."""
    if days_late <= 3 or amount <= 0:
        return 0
    num = min(amount * 75 * days_late, amount * 1500)  # in units of 1/10000 satang
    return (num + 5000) // 10000
