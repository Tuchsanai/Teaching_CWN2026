def split_bill(total, people, tip_percent):
    """หารบิลเป็นจำนวนเต็มสตางค์ คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว"""
    # ทิปเป็นสตางค์ ปัดครึ่งขึ้น (ใช้เลขจำนวนเต็มล้วน ไม่มี float)
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
