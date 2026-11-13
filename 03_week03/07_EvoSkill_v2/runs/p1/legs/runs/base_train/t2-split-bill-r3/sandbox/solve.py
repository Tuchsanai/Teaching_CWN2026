def split_bill(total, people, tip_percent):
    """หารบิลเป็นสตางค์ ทิปปัดเศษลง คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์"""
    grand = total + total * tip_percent // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
