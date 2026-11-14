def split_bill(total, people, tip_percent):
    """หารบิลให้ทุกคน (หน่วยสตางค์) คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว"""
    if people < 1:
        raise ValueError("people must be >= 1")
    if total < 0:
        raise ValueError("total must be >= 0")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be 0-100")
    # ทิปคำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นเป็นสตางค์
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
