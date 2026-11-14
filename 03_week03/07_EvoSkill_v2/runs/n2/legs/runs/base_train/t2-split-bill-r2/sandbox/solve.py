def split_bill(total, people, tip_percent):
    """หารบิล: คืน list ยอดสตางค์ที่แต่ละคนจ่าย เรียงตามลำดับคน"""
    if people < 1:
        raise ValueError("people must be >= 1")
    # ยอดรวม = บิล + ทิป (ปัดครึ่งขึ้นเป็นสตางค์ ด้วยเลขจำนวนเต็มล้วน)
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
