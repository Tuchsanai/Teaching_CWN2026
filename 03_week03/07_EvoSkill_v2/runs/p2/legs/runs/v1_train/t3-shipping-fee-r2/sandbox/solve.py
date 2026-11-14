from fractions import Fraction


def _rhu(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x เป็น Fraction ไม่ติดลบ)"""
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def shipping_fee(weight_g, distance_km, express):
    # กติกา C: ปัดครึ่งขึ้นเป็นสตางค์เต็มทุกขั้นตอน
    w = Fraction(weight_g)
    if w <= 1000:
        fee = 4000
    elif w <= 5000:
        fee = 8000
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        fee = _rhu(8000 + (w - 5000) * Fraction(1500, 1000))
    if Fraction(distance_km) > 100:
        fee = _rhu(Fraction(fee) * Fraction(120, 100))
    if express:
        fee = _rhu(Fraction(fee) * Fraction(150, 100))
    return int(fee)
