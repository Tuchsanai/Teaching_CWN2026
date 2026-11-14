def cafe_bill(items, member):
    """คืนยอดชำระเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 บาท
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100  # VAT
    return (2 * num + den) // (2 * den)
