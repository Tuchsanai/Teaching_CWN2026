# Rules: weight in grams (1..30000), distance km (>=0), express bool. Output: integer satang.
# base: <=1000g 40 baht; <=5000g 80 baht; >5000g 80 baht + 15 baht/kg for excess (prorated).
# distance > 100 -> x1.2 ; express -> x1.5 (compounded). Round half-up once at the end.
from fractions import Fraction
import math


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def _num(x, name):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise InvalidInput(f"{name} must be a number")
    if isinstance(x, float) and not math.isfinite(x):
        raise InvalidInput(f"{name} must be finite")
    return Fraction(x) if isinstance(x, int) else Fraction(str(x))


def shipping_fee(weight_g, distance_km, express):
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not isinstance(express, bool):
        raise InvalidInput("express must be bool")
    if w < 1 or w > 30000:
        raise InvalidInput("weight_g must be in 1..30000")
    if d < 0:
        raise InvalidInput("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)
    if d > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
