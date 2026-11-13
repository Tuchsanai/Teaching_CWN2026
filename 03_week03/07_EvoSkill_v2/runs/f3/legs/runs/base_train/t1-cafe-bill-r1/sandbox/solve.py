def cafe_bill(items, member):
    """คิดเงินร้าน BaanKafe -> จำนวนเต็มสตางค์ที่ลูกค้าต้องจ่าย

    ใช้เลขจำนวนเต็มล้วน (ไม่มี float error) ปัดเศษครั้งเดียวตอนท้าย (half up)
    """
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num = total
    den = 1
    if total >= 50000:  # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107  # VAT 7% ขั้นสุดท้าย
    den *= 100

    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
