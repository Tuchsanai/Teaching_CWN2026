def split_bill(total, people, tip_percent):
    # ยอดรวมทิป (สตางค์) ปัดเศษทิปลง
    grand = total + total * tip_percent // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
