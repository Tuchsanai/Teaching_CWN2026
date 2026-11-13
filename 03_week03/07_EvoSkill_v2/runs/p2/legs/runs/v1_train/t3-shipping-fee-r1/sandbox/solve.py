from fractions import Fraction
from math import isfinite

# นโยบายปัดเศษ r1: คำนวณแม่นยำด้วย Fraction แล้วปัดครึ่งขึ้น (half-up) ครั้งเดียวตอนท้าย


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, Fraction)) and not (
        isinstance(weight_g, float) and isfinite(weight_g)
    ):
        raise ValueError("weight_g must be a number")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float, Fraction)):
        raise ValueError("distance_km must be a number")
    if isinstance(distance_km, float) and not isfinite(distance_km):
        raise ValueError("distance_km must be finite")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if not (1 <= weight_g <= 30000):
        raise ValueError("weight_g must be in 1..30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        baht = Fraction(40)
    elif w <= 5000:
        baht = Fraction(80)
    else:
        baht = 80 + (w - 5000) * 15 / 1000  # 15 บาท/กก. ตามสัดส่วนกรัม

    fee = baht * 100  # สตางค์
    if distance_km > 100:
        fee = fee * 120 / 100
    if express:
        fee = fee * 150 / 100
    return int((fee * 2 + 1) // 2)  # half-up
