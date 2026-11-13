def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe คืนยอดสุทธิเป็นจำนวนเต็มสตางค์

    ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float และปัดเศษ (half up) ครั้งเดียวตอนท้าย
    """
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num, den = 1, 1
    if total >= 50000:  # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107  # VAT 7% ขั้นสุดท้าย
    den *= 100

    return (total * num * 2 + den) // (den * 2)  # ปัดครึ่งขึ้น
