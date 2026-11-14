def split_bill(total, people, tip_percent):
    """หารบิล: คืน list ยอดจ่ายของแต่ละคน (สตางค์) เรียงตามลำดับคน"""
    if people < 1:
        raise ValueError("people must be >= 1")
    # ทิปเป็นสตางค์ ปัดครึ่งขึ้น (ใช้เลขจำนวนเต็มล้วน ไม่มีปัญหา float)
    tip = (total * tip_percent + 50) // 100
    amount = total + tip
    base, extra = divmod(amount, people)
    return [base + 1 if i < extra else base for i in range(people)]
