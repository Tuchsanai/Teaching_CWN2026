def late_fee(amount, days_late):
    """Late fee in satang (integer). 0.75%/day on all late days if days_late > 3, capped at 15%."""
    if days_late <= 3:
        return 0
    # work in units of 1/10000 satang to avoid float errors
    num = min(amount * 75 * days_late, amount * 1500)
    return (num + 5000) // 10000  # round half up
