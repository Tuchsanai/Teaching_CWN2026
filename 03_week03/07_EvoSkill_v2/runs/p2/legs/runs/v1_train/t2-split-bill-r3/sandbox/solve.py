def split_bill(total, people, tip_percent):
    # กติกา C: ปัดครึ่งขึ้นเป็นสตางค์เต็มตอนคิดทิป
    tip = (2 * total * tip_percent + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
