def late_fee(amount, days_late):
    """Late fee in satang (integer).

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted), capped at 15%
    Uses integer arithmetic (no float error); fractional satang is rounded down.
    """
    if days_late <= 3:
        return 0
    fee = amount * days_late * 75 // 10000
    cap = amount * 15 // 100
    return min(fee, cap)
