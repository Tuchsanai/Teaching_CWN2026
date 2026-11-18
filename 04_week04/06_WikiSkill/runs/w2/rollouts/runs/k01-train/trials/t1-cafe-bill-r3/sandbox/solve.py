def cafe_bill(items, member):
    """คิดเงินหน้าร้าน (หน่วยสตางค์) คืนจำนวนเต็มสตางค์

    ใช้เลขจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half-up) เพื่อเลี่ยงปัญหา float
    """
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:          # 500 บาท = 50,000 สตางค์
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)
