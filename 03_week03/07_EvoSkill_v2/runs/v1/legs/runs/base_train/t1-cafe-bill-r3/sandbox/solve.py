def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยง float"""
    subtotal = sum(i["price"] * i["qty"] for i in items)

    num, den = subtotal, 1
    if subtotal >= 50000:  # 500 บาท = 50000 สตางค์
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย

    # ปัดเศษครั้งเดียวตอนท้าย (half up)
    return (2 * num + den) // (2 * den)
