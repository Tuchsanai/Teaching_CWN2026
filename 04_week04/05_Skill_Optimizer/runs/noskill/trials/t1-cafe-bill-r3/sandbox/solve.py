def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    ใช้เลขจำนวนเต็มล้วน ไม่มี float และปัดเศษ (half up) ครั้งเดียวตอนท้าย
    """
    subtotal = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num, den = subtotal, 1
    if subtotal >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย

    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
