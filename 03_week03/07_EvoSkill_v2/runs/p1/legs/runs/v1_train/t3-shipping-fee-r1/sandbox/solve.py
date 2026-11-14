from fractions import Fraction


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (หลังทุกขั้นที่คูณเปอร์เซ็นต์)"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or isinstance(distance_km, bool):
        raise ValueError("invalid input")
    if not (1 <= weight_g <= 30000):
        raise ValueError("weight_g must be in 1..30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = 4000
    elif w <= 5000:
        fee = 8000
    else:
        # 15 บาท/กก. = 1.5 สตางค์/กรัม
        fee = _rnd(8000 + (w - 5000) * Fraction(3, 2))

    if distance_km > 100:
        fee = _rnd(fee * Fraction(12, 10))  # +20%
    if express:
        fee = _rnd(fee * Fraction(15, 10))  # +50% ต่อจากข้อก่อน
    return int(fee)
