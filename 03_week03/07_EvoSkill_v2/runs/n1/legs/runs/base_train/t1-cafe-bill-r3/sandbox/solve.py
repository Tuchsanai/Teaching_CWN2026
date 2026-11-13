def cafe_bill(items, member):
    """คิดเงินเป็นสตางค์ (จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107              # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)
