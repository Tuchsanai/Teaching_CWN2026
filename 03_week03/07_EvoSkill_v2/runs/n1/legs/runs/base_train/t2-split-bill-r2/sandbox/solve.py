def split_bill(total, people, tip_percent):
    """หารบิลให้ทุกคน (หน่วยสตางค์) คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว"""
    # ยอดรวมทิป คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นเป็นสตางค์
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
