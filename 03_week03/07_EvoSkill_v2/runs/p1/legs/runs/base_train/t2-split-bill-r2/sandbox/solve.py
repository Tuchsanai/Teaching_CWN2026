def split_bill(total, people, tip_percent):
    """หารบิลรวมทิปเป็นสตางค์ คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว"""
    if people < 1:
        raise ValueError("people must be >= 1")
    if total < 0:
        raise ValueError("total must be >= 0")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # ทิปเป็นสตางค์ปัดครึ่งขึ้น (คำนวณด้วยจำนวนเต็มล้วน ไม่มีปัญหา float)
    tip = (total * tip_percent + 50) // 100
    grand = total + tip

    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
