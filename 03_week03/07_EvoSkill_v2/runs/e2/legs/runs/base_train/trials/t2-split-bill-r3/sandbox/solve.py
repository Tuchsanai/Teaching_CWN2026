def split_bill(total, people, tip_percent):
    # ทิปเป็นสตางค์ ปัดเศษครึ่งขึ้น (คำนวณด้วยจำนวนเต็มล้วน)
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
