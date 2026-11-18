def split_bill(total, people, tip_percent):
    """หารบิล: คืน list ของยอดที่แต่ละคนจ่าย (สตางค์) เรียงตามลำดับคน"""
    if people < 1:
        raise ValueError("people must be >= 1")
    if total < 0:
        raise ValueError("total must be >= 0")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # ยอดรวมหลังทิป (ใช้เลขจำนวนเต็มล้วน ปัดครึ่งขึ้นเป็นสตางค์)
    grand = (total * (100 + tip_percent) + 50) // 100

    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
