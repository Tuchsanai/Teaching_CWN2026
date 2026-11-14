def split_bill(total, people, tip_percent):
    # Rounding rule A (r1): exact arithmetic, floor once at the end.
    grand = (total * (100 + tip_percent)) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
