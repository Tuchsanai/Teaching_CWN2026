def cafe_bill(items, member):
    """คิดเงินร้าน BaanKafe คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์"""
    subtotal = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num, den = subtotal, 1
    if subtotal >= 50000:  # 500 บาท = 50,000 สตางค์
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย

    # ปัดเศษครั้งเดียวตอนท้าย (half up) ด้วยเลขจำนวนเต็มล้วน
    return (2 * num + den) // (2 * den)
