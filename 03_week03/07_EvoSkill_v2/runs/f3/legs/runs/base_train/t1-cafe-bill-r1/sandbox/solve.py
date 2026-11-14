def cafe_bill(items, member):
    """คิดเงินเป็นสตางค์ (จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย (half-up)"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = 100, 100
    if total >= 50000:      # 500 บาท = 50000 สตางค์
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100  # VAT 7% ขั้นสุดท้าย
    return (total * num * 2 + den) // (den * 2)
