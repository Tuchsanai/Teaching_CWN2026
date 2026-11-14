def split_bill(total, people, tip_percent):
    # คำนวณด้วยจำนวนเต็มล้วน (ไม่ใช้ float); ทิปที่เป็นเศษสตางค์ปัดครึ่งขึ้น
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
