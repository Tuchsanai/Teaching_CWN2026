def split_bill(total, people, tip_percent):
    # ทิปคิดเป็นจำนวนเต็มสตางค์ (ปัดเศษลง) ด้วยเลขจำนวนเต็มล้วน ไม่ใช้ float
    amount = total + total * tip_percent // 100
    base, extra = divmod(amount, people)
    return [base + 1 if i < extra else base for i in range(people)]
