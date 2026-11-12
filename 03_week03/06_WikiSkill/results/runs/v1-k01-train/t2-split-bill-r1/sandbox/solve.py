def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (คำนวณด้วยจำนวนเต็ม ปัดครึ่งขึ้นเป็นสตางค์)
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
