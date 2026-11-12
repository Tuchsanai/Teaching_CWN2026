def split_bill(total, people, tip_percent):
    # ยอดรวมทิป (สตางค์) ปัดเศษครึ่งขึ้นด้วยเลขจำนวนเต็มล้วน
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
