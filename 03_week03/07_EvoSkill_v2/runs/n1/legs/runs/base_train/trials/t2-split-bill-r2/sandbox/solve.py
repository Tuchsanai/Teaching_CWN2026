def split_bill(total, people, tip_percent):
    # ยอดรวมหลังทิป (สตางค์) ใช้เลขจำนวนเต็มล้วน ปัดครึ่งขึ้นถ้าทิปมีเศษสตางค์
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
