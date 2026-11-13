def split_bill(total, people, tip_percent):
    # ยอดรวมทิป (สตางค์) ปัดครึ่งขึ้นด้วยเลขจำนวนเต็ม ไม่ใช้ float
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
