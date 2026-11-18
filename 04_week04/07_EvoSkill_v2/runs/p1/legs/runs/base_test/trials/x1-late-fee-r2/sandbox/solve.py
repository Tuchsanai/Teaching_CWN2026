def late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days, capped at 15% of amount (integer math, round half up)
    num = amount * 75 * days_late          # over 10000
    cap = amount * 1500                    # 15% over 10000
    num = min(num, cap)
    return (num + 5000) // 10000
