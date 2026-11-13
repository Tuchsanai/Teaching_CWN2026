def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (ปัดเศษสตางค์แบบครึ่งขึ้น ด้วยเลขจำนวนเต็มล้วน)
    amount = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(amount, people)
    return [base + 1 if i < extra else base for i in range(people)]
