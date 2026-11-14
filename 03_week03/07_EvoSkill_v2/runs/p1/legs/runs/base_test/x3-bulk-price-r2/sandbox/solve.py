def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์) ใช้เลขจำนวนเต็มล้วน ไม่มีคลาดเคลื่อนจาก float

    ลำดับ: ราคารวม -> ลดตามจำนวน (3.5% / 7.5% อัตราเดียว) -> คูปอง 2.5% (ลดต่อจากยอดที่ลดแล้ว)
    -> VAT 7% -> ปัดเศษเป็นสตางค์ครั้งเดียวตอนท้าย (half up)
    """
    if qty >= 50:
        tier_bp = 750
    elif qty >= 10:
        tier_bp = 350
    else:
        tier_bp = 0
    coupon_bp = 250 if coupon else 0

    numerator = (unit_price * qty
                 * (10000 - tier_bp)
                 * (10000 - coupon_bp)
                 * 10700)
    denominator = 10000 ** 3
    return (2 * numerator + denominator) // (2 * denominator)
