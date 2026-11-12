def cafe_bill(items, member):
    """คิดเงินเป็นสตางค์ ใช้เลขจำนวนเต็มล้วน ปัดเศษ (half up) ครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)
