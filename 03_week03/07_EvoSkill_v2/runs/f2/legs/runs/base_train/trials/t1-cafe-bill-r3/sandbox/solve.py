def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe คืนยอดจ่ายเป็นจำนวนเต็มสตางค์

    ใช้เลขจำนวนเต็มล้วน (ไม่มี float error) และปัดเศษครั้งเดียวตอนท้าย (half-up)
    """
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7%

    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
