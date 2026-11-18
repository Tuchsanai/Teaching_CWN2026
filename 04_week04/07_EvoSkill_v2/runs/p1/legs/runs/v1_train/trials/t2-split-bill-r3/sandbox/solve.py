def split_bill(total, people, tip_percent):
    tip = total * tip_percent // 100  # ทิปปัดลงเป็นสตางค์เต็ม
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
