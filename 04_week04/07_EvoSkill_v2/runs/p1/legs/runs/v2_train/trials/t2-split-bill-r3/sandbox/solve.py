def split_bill(total, people, tip_percent):
    tip = -(-total * tip_percent // 100)  # ปัดขึ้นเป็นสตางค์เต็ม
    base, extra = divmod(total + tip, people)
    return [base + 1 if i < extra else base for i in range(people)]
