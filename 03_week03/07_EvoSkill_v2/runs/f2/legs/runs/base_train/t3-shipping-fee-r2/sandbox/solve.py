from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นที่ขั้นสุดท้าย)"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * 1500 / 1000  # 15 บาท/กก. = 1.5 สตางค์/กรัม
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(3, 2)
    return int(fee + Fraction(1, 2) // 1) if fee.denominator == 1 else int((fee + Fraction(1, 2)) // 1)
