def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, int) คำนวณแบบเศษส่วนเต็ม ปัดครั้งเดียวตอนท้าย (half up)"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 บาท = 50000 สตางค์
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)
