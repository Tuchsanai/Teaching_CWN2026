from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    # แบบ H: Fraction ตลอด ปัดครึ่งขึ้นครั้งเดียวตอนท้าย + ตรวจอินพุต
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be in 1..30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)  # สตางค์
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return int((2 * fee.numerator + fee.denominator) // (2 * fee.denominator))
