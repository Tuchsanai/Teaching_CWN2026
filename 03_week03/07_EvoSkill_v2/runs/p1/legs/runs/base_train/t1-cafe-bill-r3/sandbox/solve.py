def cafe_bill(items, member):
    """คืนยอดชำระเป็นสตางค์ (int) — คำนวณด้วยเลขจำนวนเต็ม ปัดเศษครั้งเดียวตอนท้าย (half up)"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = 100, 100
    if total >= 50000:      # 500 บาท = 50,000 สตางค์
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107              # VAT 7% ขั้นสุดท้าย
    den *= 100
    return (total * num * 2 + den) // (den * 2)
