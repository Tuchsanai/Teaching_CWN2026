def split_bill(total, people, tip_percent):
    # ยอดรวม = บิล + ทิป (ปัดครึ่งขึ้นเป็นสตางค์เต็ม ใช้เลขจำนวนเต็มล้วน)
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
