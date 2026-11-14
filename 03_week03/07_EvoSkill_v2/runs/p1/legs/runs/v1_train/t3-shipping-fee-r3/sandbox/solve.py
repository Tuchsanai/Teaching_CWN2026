from fractions import Fraction


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (ใช้หลังทุกขั้นที่เป็นจำนวนเงิน)"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def shipping_fee(weight_g, distance_km, express):
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = 4000
    elif w <= 5000:
        fee = 8000
    else:
        # 15 บาท/กก. = 1.5 สตางค์/กรัม
        fee = 8000 + _rnd((w - 5000) * Fraction(3, 2))

    if Fraction(distance_km) > 100:
        fee = _rnd(fee * Fraction(120, 100))
    if express:
        fee = _rnd(fee * Fraction(150, 100))
    return int(fee)
