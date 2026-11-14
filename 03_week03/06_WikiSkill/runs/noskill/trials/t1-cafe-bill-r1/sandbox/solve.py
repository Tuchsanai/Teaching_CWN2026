def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe; ราคา/ผลลัพธ์เป็นสตางค์ (int)."""
    total = sum(i["price"] * i["qty"] for i in items)
    num = total * 107
    den = 100
    if total >= 50000:  # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ด้วยเลขจำนวนเต็มล้วน (ไม่มี float error)
    return (2 * num + den) // (2 * den)
