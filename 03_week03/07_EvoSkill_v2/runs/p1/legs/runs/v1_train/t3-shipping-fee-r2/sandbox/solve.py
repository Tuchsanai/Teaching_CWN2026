from fractions import Fraction
import numbers


def _num(name, v):
    if isinstance(v, bool) or not isinstance(v, numbers.Real):
        raise ValueError(f"{name} must be a number, got {v!r}")
    if isinstance(v, numbers.Integral):
        return Fraction(int(v))
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite")
    return Fraction(str(v))


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang."""
    w = _num("weight_g", weight_g)
    d = _num("distance_km", distance_km)
    if not isinstance(express, bool):
        raise ValueError(f"express must be a bool, got {express!r}")
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be within 1..30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(3, 2)  # 1.5 satang/g
    if d > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)  # half-up, once
