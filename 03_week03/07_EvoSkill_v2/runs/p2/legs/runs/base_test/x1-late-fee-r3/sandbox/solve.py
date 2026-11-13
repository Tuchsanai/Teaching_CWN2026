def late_fee(amount, days_late):
    """Late fee in satang (integer).

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted), capped at 15%
    - result rounded half-up to whole satang (integer arithmetic, no float error)
    """
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days = amount * 75 * days / 10000
    # cap = amount * 15% = amount * 1500 / 10000
    numerator = min(amount * 75 * days_late, amount * 1500)
    return (numerator * 2 + 10000) // 20000  # round half up
