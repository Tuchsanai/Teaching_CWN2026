def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half-up)"""
    subtotal = sum(i["price"] * i["qty"] for i in items)
    num, den = subtotal, 1
    if subtotal >= 50000:  # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
