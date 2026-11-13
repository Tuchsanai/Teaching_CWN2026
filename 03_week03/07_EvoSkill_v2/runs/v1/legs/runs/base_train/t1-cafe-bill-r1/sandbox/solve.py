def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe คืนยอดจ่ายเป็นจำนวนเต็มสตางค์

    ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float และปัดเศษ (half up) ครั้งเดียวตอนท้าย
    """
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย

    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
