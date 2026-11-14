def late_fee(amount, days_late):
    """Late fee in satang (integer).

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted), capped at 15%
    Uses integer math (units of 1/10000 satang) to avoid float errors;
    result is rounded half up.
    """
    if days_late <= 3 or amount <= 0:
        return 0
    scaled = min(amount * 75 * days_late, amount * 1500)  # amount * bp / 10000
    return (scaled + 5000) // 10000
