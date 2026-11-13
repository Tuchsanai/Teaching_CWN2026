def split_bill(total, people, tip_percent):
    """หารบิล: คืน list ยอดจ่ายของแต่ละคน (สตางค์) คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว"""
    if people < 1:
        raise ValueError("people must be >= 1")
    if total < 0:
        raise ValueError("total must be >= 0")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be in 0..100")

    # ยอดรวมทิป ปัดเศษครึ่งขึ้นเป็นสตางค์ (ใช้จำนวนเต็มล้วน ไม่มีปัญหา float)
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
