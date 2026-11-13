def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (ปัดเศษสตางค์แบบ half-up ด้วยจำนวนเต็ม ไม่ใช้ float)
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
