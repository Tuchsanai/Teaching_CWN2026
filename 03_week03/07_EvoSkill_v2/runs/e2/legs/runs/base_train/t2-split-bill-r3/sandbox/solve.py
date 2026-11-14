def split_bill(total, people, tip_percent):
    """หารบิลให้ทุกคน (หน่วยสตางค์) คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว"""
    if people < 1:
        raise ValueError("people must be >= 1")
    # ยอดรวมทิป ปัดครึ่งขึ้นเป็นสตางค์เต็มโดยใช้เลขจำนวนเต็มล้วน
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
