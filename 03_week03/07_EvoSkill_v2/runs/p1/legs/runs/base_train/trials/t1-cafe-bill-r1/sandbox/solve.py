def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์ (ใช้เลขจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย)"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 บาท = 50000 สตางค์ ลด 5%
        num *= 95
        den *= 100
    if member:              # สมาชิกลดอีก 10%
        num *= 90
        den *= 100
    num *= 107              # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
