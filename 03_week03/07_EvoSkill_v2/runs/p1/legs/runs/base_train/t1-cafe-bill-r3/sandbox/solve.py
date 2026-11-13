def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (จำนวนเต็มสตางค์) คำนวณด้วยจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7%
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
