"""BaanKafe shipping fee (result in integer satang)."""
import math
from fractions import Fraction


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be an int in 1..30000")
    if type(distance_km) is int:
        dist = Fraction(distance_km)
    elif type(distance_km) is float and math.isfinite(distance_km):
        dist = Fraction(distance_km)
    else:
        raise ValueError("distance_km must be a finite number >= 0")
    if dist < 0:
        raise ValueError("distance_km must be >= 0")
    if type(express) is not bool:
        raise ValueError("express must be a bool")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(weight_g - 5000, 1000) * 1500
    if dist > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return _half_up(fee)
