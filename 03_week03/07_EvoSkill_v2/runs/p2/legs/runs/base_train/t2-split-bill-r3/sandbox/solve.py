def split_bill(total, people, tip_percent):
    # ยอดรวม = ยอดบิล + ทิป (ปัดทิปเป็นสตางค์เต็มแบบ half-up ด้วยจำนวนเต็ม)
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
