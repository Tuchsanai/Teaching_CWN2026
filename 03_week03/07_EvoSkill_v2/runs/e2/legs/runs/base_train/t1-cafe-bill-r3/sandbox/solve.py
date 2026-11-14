def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็ม ปัดครั้งเดียวตอนท้าย)"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = total, 1
    if total >= 50000:       # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107               # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
