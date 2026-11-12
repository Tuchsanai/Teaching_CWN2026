def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (ปัดเศษครึ่งขึ้นเป็นสตางค์ ด้วยเลขจำนวนเต็มล้วน)
    grand = total + (total * tip_percent + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
