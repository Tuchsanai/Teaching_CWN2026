def split_bill(total, people, tip_percent):
    # ยอดรวมทิป (สตางค์) คำนวณด้วยจำนวนเต็ม ปัดครึ่งขึ้น
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
