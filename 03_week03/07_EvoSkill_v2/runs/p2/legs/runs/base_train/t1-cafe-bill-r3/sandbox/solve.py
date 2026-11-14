def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)
    p = 95 if total >= 50000 else 100   # 500 บาท = 50000 สตางค์
    m = 90 if member else 100
    num = total * p * m * 107
    den = 100 * 100 * 100
    return (num * 2 + den) // (den * 2)  # ปัดครึ่งขึ้น
