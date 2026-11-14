def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num, den = 1, 1
    if total >= 50000:  # 500 บาทขึ้นไป ลด 5%
        num, den = num * 95, den * 100
    if member:  # สมาชิกลดอีก 10%
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย

    # คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นเมื่อจบขั้นตอนเดียว
    return (2 * total * num + den) // (2 * den)
