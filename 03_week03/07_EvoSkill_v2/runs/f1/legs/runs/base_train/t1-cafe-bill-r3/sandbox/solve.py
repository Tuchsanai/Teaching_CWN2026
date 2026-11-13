def cafe_bill(items, member):
    """คิดเงินเป็นสตางค์ (จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float
    ปัดเศษ half-up ครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:          # 500 บาท = 50,000 สตางค์
        num *= 95; den *= 100   # ลด 5%
    if member:
        num *= 90; den *= 100   # ลดสมาชิก 10%
    num *= 107; den *= 100      # VAT 7%
    return (2 * num + den) // (2 * den)
