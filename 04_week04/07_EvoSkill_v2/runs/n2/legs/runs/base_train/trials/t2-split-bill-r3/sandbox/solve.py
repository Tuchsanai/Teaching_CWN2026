def split_bill(total, people, tip_percent):
    if people < 1:
        raise ValueError("people must be >= 1")
    if total < 0:
        raise ValueError("total must be >= 0")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be 0-100")

    # ทิปเป็นสตางค์ ปัดครึ่งขึ้น (ใช้จำนวนเต็มล้วน ไม่มีปัญหา float)
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip

    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
