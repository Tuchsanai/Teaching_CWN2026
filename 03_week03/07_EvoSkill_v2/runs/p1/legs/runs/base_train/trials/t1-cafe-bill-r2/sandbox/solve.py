def cafe_bill(items, member):
    """คิดเงินเป็นสตางค์ (int) ใช้เลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    subtotal = sum(i["price"] * i["qty"] for i in items)
    num, den = subtotal, 1
    if subtotal >= 50000:      # 500 บาท
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100     # VAT 7%
    return (2 * num + den) // (2 * den)
