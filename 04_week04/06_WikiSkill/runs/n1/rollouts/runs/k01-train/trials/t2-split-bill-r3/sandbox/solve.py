def split_bill(total, people, tip_percent):
    # ทิปคิดเป็นสตางค์จำนวนเต็ม (ปัดเศษลง)
    grand = total + total * tip_percent // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
