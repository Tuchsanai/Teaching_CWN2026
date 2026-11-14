def split_bill(total, people, tip_percent):
    """หารบิลรวมทิป คืน list ยอดที่แต่ละคนจ่าย (สตางค์)"""
    if people < 1:
        raise ValueError("people must be >= 1")
    # ทิปเป็นสตางค์ ปัดเศษครึ่งขึ้น (คำนวณด้วยจำนวนเต็มล้วน)
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
