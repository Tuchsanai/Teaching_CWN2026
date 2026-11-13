from fractions import Fraction
import math


class InputError(ValueError, TypeError):
    """Invalid input (both ValueError and TypeError)."""


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def shipping_fee(weight_g, distance_km, express):
    """Shipping fee in integer satang.

    Assumptions: all math exact (Fraction); round half up once at the end;
    surcharges multiply: >100 km -> x1.2, express -> x1.5.
    """
    if isinstance(weight_g, bool) or not isinstance(weight_g, int):
        raise InputError(f"weight_g must be an int, got {weight_g!r}")
    if not 1 <= weight_g <= 30000:
        raise InputError("weight_g must be in 1..30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise InputError(f"distance_km must be a number, got {distance_km!r}")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise InputError("distance_km must be finite")
    if distance_km < 0:
        raise InputError("distance_km must be >= 0")
    if not isinstance(express, bool):
        raise InputError(f"express must be a bool, got {express!r}")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang/1000 g
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return _round_half_up(fee)
