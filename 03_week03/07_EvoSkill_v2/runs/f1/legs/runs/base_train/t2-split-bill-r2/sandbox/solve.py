def split_bill(total, people, tip_percent):
    # tip in satang, rounded half up using integer math
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
