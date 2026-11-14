def _rhu(n, d):
    # ปัดครึ่งขึ้นเป็นจำนวนเต็ม (จำนวนเต็มล้วน)
    return (2 * n + d) // (2 * d)


def cafe_bill(items, member):
    # กติกา C: ปัดครึ่งขึ้นเป็นสตางค์ทุกขั้นตอน
    total = sum(i["price"] * i["qty"] for i in items)
    if total >= 50000:  # ตั้งแต่ 500 บาท (ก่อนลด) -> ลด 5%
        total = _rhu(total * 95, 100)
    if member:  # ลดอีก 10%
        total = _rhu(total * 90, 100)
    return _rhu(total * 107, 100)  # VAT 7% ขั้นสุดท้าย
