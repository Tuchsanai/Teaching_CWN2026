def cafe_bill(items, member):
    """คิดเงินเป็นสตางค์ (จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total * 107, 100
    if total >= 50000:      # 500 บาท = 50000 สตางค์
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    return (2 * num + den) // (2 * den)   # round half up
