def cafe_bill(items, member):
    """คิดเงินร้าน BaanKafe คืนยอดจ่ายเป็นจำนวนเต็มสตางค์

    ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float และปัดเศษ (half-up) ครั้งเดียวตอนท้าย
    """
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    pct_bulk = 95 if total >= 50000 else 100  # 500 บาท = 50000 สตางค์
    pct_member = 90 if member else 100
    pct_vat = 107

    num = total * pct_bulk * pct_member * pct_vat
    den = 100 ** 3
    return (2 * num + den) // (2 * den)
