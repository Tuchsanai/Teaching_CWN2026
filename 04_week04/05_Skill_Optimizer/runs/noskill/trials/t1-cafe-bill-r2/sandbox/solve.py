def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, int) คำนวณด้วยจำนวนเต็ม ปัดเศษครั้งเดียวตอนท้าย (half-up)"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 บาท = 50,000 สตางค์
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100  # VAT 7% ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)
