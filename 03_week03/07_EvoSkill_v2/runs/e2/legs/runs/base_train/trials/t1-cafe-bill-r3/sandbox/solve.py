def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, int) คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = 1, 1
    if total >= 50000:  # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107
    den *= 100
    return (total * num * 2 + den) // (den * 2)
