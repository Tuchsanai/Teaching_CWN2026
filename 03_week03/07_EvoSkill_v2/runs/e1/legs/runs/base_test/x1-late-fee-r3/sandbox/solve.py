def late_fee(amount, days_late):
    """Late fee in satang (integer). 0.75%/day on all late days if days_late > 3, capped at 15%."""
    if days_late <= 3:
        return 0
    # units of 1/10000 satang: 75 bp per day, cap 1500 bp
    bp = min(75 * days_late, 1500)
    return (amount * bp + 5000) // 10000  # round half up, integer-only
