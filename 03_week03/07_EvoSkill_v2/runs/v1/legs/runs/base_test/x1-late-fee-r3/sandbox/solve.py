def late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    # rate in basis points: 0.75% = 75 bp per day, capped at 15% = 1500 bp
    bp = min(days_late * 75, 1500)
    # integer arithmetic, round half up to whole satang
    return (amount * bp + 5000) // 10000
