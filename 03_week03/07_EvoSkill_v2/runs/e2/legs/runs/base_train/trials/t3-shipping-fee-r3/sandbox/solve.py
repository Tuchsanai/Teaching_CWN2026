from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นเมื่อท้ายสุด)"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(1500, 1000)
    if distance_km > 100:
        fee = fee * Fraction(6, 5)
    if express:
        fee = fee * Fraction(3, 2)
    return int((fee + Fraction(1, 2)) // 1)
