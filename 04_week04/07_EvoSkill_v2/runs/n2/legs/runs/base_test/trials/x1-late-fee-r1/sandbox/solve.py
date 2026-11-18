def late_fee(amount, days_late):
    """Late fee in whole satang.

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted), capped at 15%
    Uses integer math (no float error); rounds half up to whole satang.
    """
    if days_late <= 3:
        return 0
    rate_bp = min(75 * days_late, 1500)  # in 1/10000 of amount; 1500 = 15%
    return (amount * rate_bp + 5000) // 10000
