def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:  # 500 บาท = 50000 สตางค์ (เช็คจากยอดรวมก่อนลด)
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย ด้วยจำนวนเต็มล้วน (ไม่มี float error)
    return (2 * num + den) // (2 * den)
