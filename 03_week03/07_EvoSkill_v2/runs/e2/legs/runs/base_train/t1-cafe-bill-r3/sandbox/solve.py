def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float"""
    total = sum(i["price"] * i["qty"] for i in items)

    num, den = total, 1
    if total >= 50000:      # 500 บาท = 50000 สตางค์ (เทียบจากยอดรวมก่อนลด)
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107              # VAT 7% เป็นขั้นสุดท้าย
    den *= 100

    # ปัดเศษครึ่งขึ้น ครั้งเดียวตอนท้าย
    return (2 * num + den) // (2 * den)
