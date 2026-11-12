def split_bill(total, people, tip_percent):
    # ทิปเป็นสตางค์ ปัดครึ่งขึ้นด้วยเลขจำนวนเต็ม (ไม่ใช้ float)
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
