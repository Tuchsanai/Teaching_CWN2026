def late_fee(amount, days_late):
    """Late fee in satang (integer).

    - days_late <= 3: no fee
    - otherwise 0.75% of amount per late day (all days counted), capped at 15%
    - rounded half-up to whole satang, using integer math (no float error)
    """
    if days_late <= 3:
        return 0
    # rate in basis points (0.75% = 75 bp); cap 15% = 1500 bp
    bp = min(75 * days_late, 1500)
    return (amount * bp + 5000) // 10000
