def split_bill(total, people, tip_percent):
    # ยอดรวมรวมทิป (สตางค์) ปัดครึ่งขึ้นเป็นจำนวนเต็มด้วยเลขจำนวนเต็มล้วน
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
