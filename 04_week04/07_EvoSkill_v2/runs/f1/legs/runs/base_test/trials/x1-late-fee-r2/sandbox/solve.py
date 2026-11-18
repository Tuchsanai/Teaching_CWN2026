def late_fee(amount, days_late):
    """Late fee in whole satang.

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted), capped at 15%
    - exact integer arithmetic, rounded half up to whole satang
    """
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days  ->  amount * 75 * days / 10000
    num = min(amount * 75 * days_late, amount * 1500)  # cap = 15% = 1500/10000
    return (num * 2 + 10000) // 20000  # round half up
