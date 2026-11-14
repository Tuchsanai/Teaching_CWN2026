def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (ปัดทิปเป็นสตางค์เต็มแบบครึ่งปัดขึ้น ด้วยเลขจำนวนเต็มล้วน)
    grand = total + (total * tip_percent * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
