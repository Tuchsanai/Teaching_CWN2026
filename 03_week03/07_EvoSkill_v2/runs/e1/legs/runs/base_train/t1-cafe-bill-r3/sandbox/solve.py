def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = 107, 100
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    # ปัดครึ่งขึ้น ครั้งเดียวที่ขั้นสุดท้าย (เลขจำนวนเต็มล้วน ไม่มี float error)
    return (total * num * 2 + den) // (den * 2)
