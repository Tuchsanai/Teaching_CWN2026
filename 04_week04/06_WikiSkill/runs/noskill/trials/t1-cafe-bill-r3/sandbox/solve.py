def cafe_bill(items, member):
    """คืนยอดชำระเป็นสตางค์ (int) ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยง float error"""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 บาท = 50000 สตางค์
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100  # VAT ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้นเมื่อจบ
