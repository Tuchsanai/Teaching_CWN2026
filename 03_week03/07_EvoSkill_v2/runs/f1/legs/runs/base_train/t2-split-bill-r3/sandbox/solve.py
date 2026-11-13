def split_bill(total, people, tip_percent):
    # ทิปเป็นสตางค์ ปัดครึ่งขึ้น (ใช้จำนวนเต็มล้วน ไม่มีปัญหา float)
    tip = (total * tip_percent + 50) // 100
    amount = total + tip
    base, extra = divmod(amount, people)
    return [base + 1 if i < extra else base for i in range(people)]
