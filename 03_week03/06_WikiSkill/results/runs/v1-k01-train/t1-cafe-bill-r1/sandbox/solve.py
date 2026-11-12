def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = 1, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย ด้วยเลขจำนวนเต็มล้วน
    return (total * num * 2 + den) // (den * 2)
