def cafe_bill(items, member):
    """คิดยอดที่ต้องจ่าย (สตางค์, int) ด้วยเลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)

    num = total * 107          # VAT 7%
    den = 100
    if total >= 50000:         # ตั้งแต่ 500 บาท ลด 5%
        num *= 95
        den *= 100
    if member:                 # สมาชิกลดอีก 10%
        num *= 90
        den *= 100

    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
