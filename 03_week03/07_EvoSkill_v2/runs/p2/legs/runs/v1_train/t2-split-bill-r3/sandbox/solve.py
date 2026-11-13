def split_bill(total, people, tip_percent):
    # Rounding policy r3: exact arithmetic, floor once at the end.
    for v in (total, people, tip_percent):
        if type(v) is not int:
            raise ValueError("arguments must be int")
    if total < 0 or people < 1 or not 0 <= tip_percent <= 100:
        raise ValueError("argument out of range")
    amount = total * (100 + tip_percent) // 100
    base, extra = divmod(amount, people)
    return [base + 1 if i < extra else base for i in range(people)]
