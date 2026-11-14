def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    total = sum(i["price"] * i["qty"] for i in items)
    n = total * 107
    d = 100
    if total >= 50000:  # 500 บาท
        n *= 95
        d *= 100
    if member:
        n *= 90
        d *= 100
    return (2 * n + d) // (2 * d)
