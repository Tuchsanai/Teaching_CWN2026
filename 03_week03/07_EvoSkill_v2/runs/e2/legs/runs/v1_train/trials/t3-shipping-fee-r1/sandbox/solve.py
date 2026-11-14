from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be an int in 1..30000")
    if type(distance_km) not in (int, float) or isinstance(distance_km, bool):
        raise ValueError("distance_km must be a number >= 0")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km must be finite")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if type(express) is not bool:
        raise ValueError("express must be a bool")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if Fraction(distance_km) > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int((fee * 2 + 1) // 2)
