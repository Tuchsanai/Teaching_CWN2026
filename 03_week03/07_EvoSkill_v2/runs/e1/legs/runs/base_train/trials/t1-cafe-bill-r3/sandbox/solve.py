def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์

    คำนวณด้วยจำนวนเต็มล้วน (ไม่มี float error) และปัดเศษครั้งเดียวตอนท้าย
    (half-up)
    """
    subtotal = sum(i["price"] * i["qty"] for i in items)

    num, den = 1, 1
    if subtotal >= 50000:  # 500 บาท = 50,000 สตางค์
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย

    return (subtotal * num * 2 + den) // (den * 2)
