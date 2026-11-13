def split_bill(total, people, tip_percent):
    """หารบิลเท่ากัน (หน่วยสตางค์) คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว"""
    # ยอดรวมทิป ปัดครึ่งขึ้นเป็นสตางค์ ด้วยเลขจำนวนเต็มล้วน (เลี่ยง float)
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
