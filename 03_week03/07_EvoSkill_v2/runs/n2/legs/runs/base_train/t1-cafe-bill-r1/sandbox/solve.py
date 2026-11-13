def cafe_bill(items, member):
    """คิดเงินหน้าร้าน (หน่วยสตางค์) คืนจำนวนเต็มสตางค์"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ด้วยเลขจำนวนเต็มล้วน
    return (2 * num + den) // (2 * den)
