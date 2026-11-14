def split_bill(total, people, tip_percent):
    if total < 0 or people < 1 or not 0 <= tip_percent <= 100:
        raise ValueError("invalid input")
    # ยอดรวม = บิล + ทิป (คำนวณด้วยจำนวนเต็ม ปัดครึ่งขึ้นเป็นสตางค์)
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
