def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe -> จำนวนเต็มสตางค์ (ปัดเศษครั้งเดียวตอนท้าย)"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์

    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107  # VAT 7%
    den *= 100

    # ปัดครึ่งขึ้นด้วยเลขจำนวนเต็ม (หลีกเลี่ยงความคลาดเคลื่อนของ float)
    return (2 * num + den) // (2 * den)
