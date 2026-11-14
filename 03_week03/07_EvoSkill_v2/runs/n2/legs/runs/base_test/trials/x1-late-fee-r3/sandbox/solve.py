def late_fee(amount, days_late):
    """Late fee in satang (integer).

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted)
    - capped at 15% of amount
    Uses exact integer arithmetic; fractional satang is rounded down.
    """
    if days_late <= 3:
        return 0
    # 0.75% = 75/10000, 15% = 1500/10000
    return min(amount * 75 * days_late, amount * 1500) // 10000
