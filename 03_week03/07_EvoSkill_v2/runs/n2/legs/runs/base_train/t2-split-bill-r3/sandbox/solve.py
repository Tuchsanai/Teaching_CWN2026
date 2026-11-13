def split_bill(total, people, tip_percent):
    """หารบิล (หน่วยสตางค์) คืน list ยอดที่แต่ละคนจ่าย"""
    if people < 1:
        raise ValueError("people must be >= 1")
    # ยอดรวมทิป ปัดครึ่งขึ้นเป็นสตางค์ (ใช้จำนวนเต็มล้วน ไม่มีปัญหา float)
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
