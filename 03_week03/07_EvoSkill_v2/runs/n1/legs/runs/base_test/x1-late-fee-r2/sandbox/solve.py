def late_fee(amount, days_late):
    """Late fee in satang (integer).

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted), capped at 15%
    - result rounded half-up to whole satang (exact integer arithmetic)
    """
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days = amount * 75 * days / 10000
    # cap = amount * 15% = amount * 1500 / 10000
    rate_bp = min(75 * days_late, 1500)  # in units of 1/10000
    return (amount * rate_bp * 2 + 10000) // 20000
