def split_bill(total, people, tip_percent):
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be in 0..100")
    # ทิป = total*tip%/100 ปัดครึ่งขึ้นเป็นสตางค์เต็ม (จำนวนเต็มล้วน ไม่ใช้ float)
    tip = (2 * total * tip_percent + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
