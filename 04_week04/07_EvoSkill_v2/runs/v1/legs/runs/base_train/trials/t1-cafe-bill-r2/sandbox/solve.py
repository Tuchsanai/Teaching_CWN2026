def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = 1, 1
    if total >= 50000:  # 500 บาท
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100
    # ปัดครึ่งขึ้น ด้วยจำนวนเต็มล้วน (ไม่มีปัญหา float)
    return (total * num * 2 + den) // (den * 2)
