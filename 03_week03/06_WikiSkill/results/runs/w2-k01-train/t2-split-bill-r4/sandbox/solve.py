def split_bill(total, people, tip_percent):
    # tip in satang, rounded half up using integer math
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
