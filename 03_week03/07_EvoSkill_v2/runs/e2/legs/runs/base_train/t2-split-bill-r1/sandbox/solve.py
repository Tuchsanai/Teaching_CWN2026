def split_bill(total, people, tip_percent):
    # ยอดรวมทิป (สตางค์) ปัดเศษครึ่งขึ้นด้วยเลขจำนวนเต็ม ไม่ใช้ float
    grand = (total * (100 + tip_percent) + 50) // 100
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
