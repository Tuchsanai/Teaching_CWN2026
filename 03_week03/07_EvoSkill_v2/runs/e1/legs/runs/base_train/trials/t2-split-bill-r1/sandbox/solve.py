def split_bill(total, people, tip_percent):
    # ทิป = total * tip_percent / 100 ปัดครึ่งขึ้นเป็นสตางค์ (คำนวณด้วยจำนวนเต็มล้วน)
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
