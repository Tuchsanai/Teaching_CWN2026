def _rhu(n, d):
    # ปัดครึ่งขึ้นเป็นจำนวนเต็ม ด้วยเลขจำนวนเต็มล้วน
    return (2 * n + d) // (2 * d)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (กติกาปัดเศษแบบ C: ปัดครึ่งขึ้นทุกขั้น)"""
    # ค่าคงที่เป็นสตางค์
    if weight_g <= 1000:
        fee = 4000
    elif weight_g <= 5000:
        fee = 8000
    else:
        # ส่วนเกิน 15 บาท/กก. = 1500 สตางค์/1000 กรัม; ปัดครึ่งขึ้น
        fee = 8000 + _rhu((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:  # เกิน 100 = '>'
        fee = _rhu(fee * 120, 100)
    if express:
        fee = _rhu(fee * 150, 100)
    return int(fee)
