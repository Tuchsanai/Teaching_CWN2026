def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (ปัดครึ่งขึ้นเป็นสตางค์ด้วยเลขจำนวนเต็ม)
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
