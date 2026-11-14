def split_bill(total, people, tip_percent):
    # ทิป = total * tip_percent / 100 ปัดครึ่งขึ้นเป็นสตางค์ (คำนวณด้วยจำนวนเต็ม ไม่มี float)
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
