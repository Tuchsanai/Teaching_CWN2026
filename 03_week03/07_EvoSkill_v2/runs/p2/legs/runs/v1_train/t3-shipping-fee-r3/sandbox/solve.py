from fractions import Fraction
from math import floor

# นโยบายปัดเศษ r3: คำนวณแม่นยำด้วย Fraction ตลอดทาง แล้วปัดลง (floor) ครั้งเดียวตอนท้าย


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, Fraction)):
        raise ValueError("weight_g must be an integer")
    if weight_g != int(weight_g) or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g must be between 1 and 30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float, Fraction)):
        raise ValueError("distance_km must be a number")
    if distance_km != distance_km or distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be a bool")

    w = int(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((w - 5000) * 1500, 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int(floor(fee))
