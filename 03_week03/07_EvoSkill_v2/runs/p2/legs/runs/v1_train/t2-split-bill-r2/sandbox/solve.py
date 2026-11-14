def split_bill(total, people, tip_percent):
    # Rule B: exact arithmetic, ceil once at the end (total + tip in satang)
    grand = -((-total * (100 + tip_percent)) // 100)
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
