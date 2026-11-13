from fractions import Fraction

# นโยบายปัดเศษ r2: ปัดครึ่งขึ้นเป็นสตางค์ทุกขั้นที่ได้เงินใหม่


def _half_up(x):
    x = Fraction(x)
    return (x.numerator * 2 + x.denominator) // (x.denominator * 2)


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, int):
        raise ValueError("weight_g must be int")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be in 1..30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float, Fraction)):
        raise ValueError("distance_km must be a number")
    if distance_km != distance_km or distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")

    if weight_g <= 1000:
        fee = 4000
    elif weight_g <= 5000:
        fee = 8000
    else:
        fee = 8000 + _half_up(Fraction((weight_g - 5000) * 1500, 1000))
    if distance_km > 100:
        fee = _half_up(Fraction(fee) * 120 / 100)
    if express:
        fee = _half_up(Fraction(fee) * 150 / 100)
    return int(fee)
