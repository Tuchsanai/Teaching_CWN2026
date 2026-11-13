def cafe_bill(items, member):
    """คืนยอดชำระเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็ม ปัดครั้งเดียวตอนท้าย แบบ half-up)"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)
