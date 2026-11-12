def split_bill(total, people, tip_percent):
    grand = total + total * tip_percent // 100  # ทิปปัดเศษลงเป็นสตางค์เต็ม
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
